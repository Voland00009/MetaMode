## Issue #6 — run_quality_audit observability — Design Spec

**Date:** 2026-04-14
**Status:** Draft (awaiting user sign-off)
**Issue:** [Voland00009/MetaMode#6](https://github.com/Voland00009/MetaMode/issues/6)
**Variant:** B (flush.log + HTML comment in daily log)

---

## Problem

`run_flush` получил нормальную диагностику SDK-ошибок ([flush.py:131-146](../../../scripts/flush.py#L131-L146)): ловит `ClaudeSDKError`, логирует `exit_code`/`stderr`/traceback, возвращает error-строку с пометкой.

`run_quality_audit` [flush.py:220-222](../../../scripts/flush.py#L220-L222) ловит голый `except Exception`, пишет `logging.warning` без деталей и возвращает `None` — сбой маскируется под "quality OK". При реальной SDK-ошибке (см. [claude-agent-sdk-python#515](https://github.com/anthropics/claude-agent-sdk-python/issues/515): Haiku `exit_code=1`) контент сохраняется как будто audit прошёл успешно.

## Goals

1. В `scripts/flush.log` при сбое audit видны `exit_code`, `stderr`, traceback (как в `run_flush`).
2. В daily log над сохранённым контентом появляется HTML-коммент-маркер `<!-- AUDIT_SDK_ERROR: exit=N -->`, чтобы упавший audit не маскировался под успех при обычном чтении лога.
3. Контент **никогда не теряется** — на любой ошибке audit сохраняем (политика уже зафиксирована в [flush.py:222](../../../scripts/flush.py#L222) комментарием «never lose data»).

## Non-goals

- Не унифицировать `flush` и audit в общий error-хелпер (scope creep — отдельная идея репортера про `doctor`).
- Не менять поведение при `AUDIT_REJECT` (low-quality quality-флаг уже работает).
- Не добавлять retry/alert — только наблюдаемость.

## Design

### 1. Return type: `AuditOutcome` (NamedTuple)

Текущий контракт `run_quality_audit` возвращает `str | None`: `None` = OK, `str` = reason для quality-reject. Для B нужен третий сигнал — "SDK упал, вот маркер для daily log".

Рассмотрел три варианта:

| Вариант | Плюсы | Минусы |
|---|---|---|
| Особая строка-маркер (`"AUDIT_SDK_ERROR: exit=1"` вместо `None`) | Контракт не меняется | Хрупкий — callers должны парсить префикс; путает "reason string" и "marker string" |
| Tuple `(reason, sdk_err)` | Stdlib | Разваливается на unpack в каждом caller |
| **NamedTuple `AuditOutcome`** ⭐ | Именованные поля, typed, расширяемо | +1 определение в файле |

Выбор: `NamedTuple`.

```python
from typing import NamedTuple

class AuditOutcome(NamedTuple):
    reject_reason: str | None = None    # quality-reject reason (existing flow)
    sdk_error_marker: str | None = None # e.g. "AUDIT_SDK_ERROR: exit=1 type=ProcessError"
```

Семантика (взаимоисключающие):
- `AuditOutcome()` (оба None) → audit прошёл, quality OK
- `AuditOutcome(reject_reason="...")` → quality low, существующий `AUDIT_FLAG`
- `AuditOutcome(sdk_error_marker="...")` → audit упал, новый `AUDIT_SDK_ERROR` маркер

### 2. Изменение в `run_quality_audit`

```python
# Импорт (добавить ClaudeSDKError):
from claude_agent_sdk import (
    AssistantMessage,
    ClaudeSDKError,
    ResultMessage,
    TextBlock,
    query,
)

# Обработка ошибок (было flush.py:220-222):
except ClaudeSDKError as e:
    import traceback
    stderr_text = getattr(e, "stderr", None) or ""
    exit_code = getattr(e, "exit_code", None)
    logging.error(
        "Quality audit SDK error (exit=%s): %s\nstderr: %s\n%s",
        exit_code, e, stderr_text, traceback.format_exc(),
    )
    if stderr_text:
        for line in str(stderr_text).splitlines():
            logging.error("  SDK stderr: %s", line)
    marker = f"AUDIT_SDK_ERROR: exit={exit_code} type={type(e).__name__}"
    return AuditOutcome(sdk_error_marker=marker)
except Exception as e:
    import traceback
    logging.error("Quality audit error: %s\n%s", e, traceback.format_exc())
    marker = f"AUDIT_SDK_ERROR: exit=None type={type(e).__name__}"
    return AuditOutcome(sdk_error_marker=marker)
```

Успех/reject меняются минимально:
```python
response = response.strip()
if response.startswith("AUDIT_REJECT:"):
    reason = response[len("AUDIT_REJECT:"):].strip()
    return AuditOutcome(reject_reason=reason)
return AuditOutcome()
```

### 3. Новая константа рядом с `AUDIT_FLAG`

```python
AUDIT_FLAG = "<!-- AUDIT_FLAG:"                  # existing
AUDIT_SDK_ERROR_FLAG = "<!-- AUDIT_SDK_ERROR:"   # new, symmetric naming
```

### 4. Изменение в `main()` ([flush.py:320-329](../../../scripts/flush.py#L320-L329))

Было:
```python
audit_reason = asyncio.run(run_quality_audit(response))
if audit_reason:
    logging.info("Audit flagged (%d chars): %s", len(response), audit_reason)
    flagged_content = f"{AUDIT_FLAG} {audit_reason} -->\n{response}"
    append_to_daily_log(flagged_content, f"Session {session_id[:8]}")
else:
    logging.info("Result: saved to daily log (%d chars)", len(response))
    append_to_daily_log(response, f"Session {session_id[:8]}")
```

Стало:
```python
outcome = asyncio.run(run_quality_audit(response))
if outcome.sdk_error_marker:
    logging.info("Audit SDK-failed, content saved with marker (%d chars)", len(response))
    flagged_content = f"<!-- {outcome.sdk_error_marker} -->\n{response}"
    append_to_daily_log(flagged_content, f"Session {session_id[:8]}")
elif outcome.reject_reason:
    logging.info("Audit flagged (%d chars): %s", len(response), outcome.reject_reason)
    flagged_content = f"{AUDIT_FLAG} {outcome.reject_reason} -->\n{response}"
    append_to_daily_log(flagged_content, f"Session {session_id[:8]}")
else:
    logging.info("Result: saved to daily log (%d chars)", len(response))
    append_to_daily_log(response, f"Session {session_id[:8]}")
```

## Tests

### Обновить существующие (сигнатура возврата изменилась)

| Тест | Было | Стало |
|---|---|---|
| `test_run_quality_audit_ok` [test_flush.py:59-64](../../../tests/test_flush.py#L59-L64) | `result is None` | `result == AuditOutcome()` |
| `test_run_quality_audit_reject` [test_flush.py:68-73](../../../tests/test_flush.py#L68-L73) | `result == "Only routine file reads"` | `result.reject_reason == "..."` и `result.sdk_error_marker is None` |
| `test_run_quality_audit_error_returns_none` [test_flush.py:77-85](../../../tests/test_flush.py#L77-L85) | Переименовать в `test_run_quality_audit_generic_error_sets_marker` → проверить `result.sdk_error_marker` не None и содержит `RuntimeError` |

### Новые (TDD RED → GREEN)

1. **`test_run_quality_audit_handles_process_error`** (копия шаблона [test_flush.py:120-133](../../../tests/test_flush.py#L120-L133)):
   - Arrange: mock `query` бросает `ProcessError("CLI failed", exit_code=1, stderr="boom stderr line")`
   - Assert: `result.sdk_error_marker` содержит `exit=1` и `ProcessError`
   - Assert (caplog): error-лог содержит `exit=1`, `boom stderr line`, `Quality audit SDK error`

2. **`test_main_writes_sdk_error_marker_to_daily_log`** (интеграционный):
   - Arrange: замокать `run_flush` → вернуть непустой response; замокать `run_quality_audit` → вернуть `AuditOutcome(sdk_error_marker="AUDIT_SDK_ERROR: exit=1 type=ProcessError")`; указать `DAILY_DIR` → `tmp_path`.
   - Запустить `main()` с подготовленным `context_file.md` + `session_id`.
   - Assert: файл `daily/YYYY-MM-DD.md` содержит `<!-- AUDIT_SDK_ERROR: exit=1 type=ProcessError -->` над контентом.

## Backwards compatibility

- `run_quality_audit` — приватная функция модуля, внешних call-сайтов нет (проверено: импортируется только в `tests/test_flush.py`). Смена сигнатуры с `str | None` на `AuditOutcome` безопасна.
- Внутри `main()` единственный call-сайт обновлён.
- Daily log / wiki consumers (compile.py, etc.) уже умеют игнорировать `AUDIT_FLAG`-коммент — для нового `AUDIT_SDK_ERROR` HTML-комментарий по той же форме, markdown-рендереры пропустят его автоматически.

## Верификация (after implementation)

1. `uv run pytest tests/test_flush.py -v` — все тесты зелёные, включая 2 новых.
2. Ручная проверка вызова `main()` на созданном fake-context-файле — daily log получает маркер.
3. `grep` по коду — нет оставшихся мест с ожиданием `str | None` от `run_quality_audit`.

## Out of scope (future — вынесено репортером ub3dqy)

1. Унифицированный `doctor` command с `quick`/`full` режимами.
2. Strict provenance/schema lint для wiki.

Оба — отдельные issues после закрытия #6.

## Риски

| Риск | Вероятность | Митигация |
|---|---|---|
| `caplog` в pytest не ловит логи из `logging.error` в нашей конфигурации (basicConfig с filename) | Средняя | Настроить `caplog.set_level(logging.ERROR)` или `propagate=True`; проверить в RED-фазе первого нового теста |
| Длинный stderr раздувает запись в flush.log | Низкая | Пишем построчно (как `run_flush` [flush.py:140-142](../../../scripts/flush.py#L140-L142)) — ротация/анализ проще |
| Parse-regression у consumers daily log | Низкая | HTML-комментарий → невидим в markdown-рендере; `AUDIT_SDK_ERROR` — уникальный префикс, не пересекается с `AUDIT_FLAG` |
