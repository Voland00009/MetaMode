# Расхождение веток main/master из-за раздельного создания

## Context
GitHub репо создан с `main` веткой (публичная документация, example content). Локальная разработка велась на `master` с `git init`. Ветки не имеют общей истории — `git merge` и `gh pr create` отказывают с "no history in common". Баг-фиксы на master не попадают в main, публичные docs на main не попадают в master.

## Key Insight
Когда GitHub-репо инициализирован отдельно от локального (например через GitHub UI с README), возникают unrelated histories. Стандартные merge/PR не работают.

Варианты решения:
1. **`git merge --allow-unrelated-histories`** — объединяет обе истории, но создаёт хаотичный merge с конфликтами в каждом общем файле
2. **Force push рабочей ветки → main** — чисто, но теряет историю публичной ветки
3. **Cherry-pick нужных коммитов** — точечно, но трудоёмко при большом расхождении

Лучшая практика: при создании GitHub-репо для существующего проекта — не инициализировать с README на GitHub, а push-ить локальную ветку сразу как main.

## Example
```bash
# Проблема
gh pr create --base main --head master
# → "no history in common"

# Решение: merge с allow-unrelated-histories
git checkout master
git merge origin/main --allow-unrelated-histories
# разрешить конфликты → push
```
