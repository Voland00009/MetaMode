---
title: "Git Unrelated Histories: Merging Branches Without Common Ancestor"
aliases: [unrelated histories, allow-unrelated-histories, no common history]
tags: [git, github, debugging]
category: "git"
sources:
  - "raw/git-unrelated-histories-branch-strategy.md"
created: 2026-04-13
updated: 2026-04-13
---

# Git Unrelated Histories: Merging Branches Without Common Ancestor

**Context:** When a GitHub repository was initialized separately from the local repository — e.g., GitHub UI created `main` with a README while local development started with `git init` on `master`. The two branches have completely independent commit histories.

**Problem:** `git merge`, `git rebase`, and `gh pr create` all refuse to operate on branches with no common ancestor. The error message is "refusing to merge unrelated histories" or "no history in common." Bug fixes on one branch can't reach the other, and standard Git workflows break entirely.

**Lesson:** Git tracks ancestry through commit parents. Two branches created independently (separate `git init` or GitHub UI initialization) have no shared ancestor, making all standard merge operations fail. The fix is `git merge --allow-unrelated-histories`, but the real lesson is prevention: never initialize a GitHub repo with content when pushing an existing local project.

## Key Points

- Two `git init` operations (one local, one via GitHub UI) create independent DAGs — Git sees them as completely separate projects
- `git merge origin/main` fails with "refusing to merge unrelated histories" — this is a safety check, not a bug
- `gh pr create --base main --head master` also fails because PRs require a merge-base between the two refs
- `--allow-unrelated-histories` forces the merge by creating a synthetic merge commit joining both DAGs, but produces conflicts in every file that exists in both branches
- Force-pushing the working branch to main is cleaner but destroys the remote branch's history — only acceptable when that history is disposable (e.g., a single initial commit with README)

## Details

Git's merge algorithm starts by finding the "merge base" — the most recent common ancestor of the two branches being merged. All three-way merge logic (which lines changed, where conflicts exist) depends on this base. When two branches have no common ancestor at all, Git has no base to compare against and refuses the operation entirely.

This situation arises most commonly when a developer creates a GitHub repository through the web UI (which generates an initial commit with README.md, .gitignore, or LICENSE) and then separately runs `git init` locally to start development. The local repository has its own initial commit, completely independent from GitHub's. When the developer adds the GitHub repo as a remote and tries to merge or create a PR, Git discovers the two histories are unrelated.

```bash
# The problem manifests at merge time
git fetch origin
git merge origin/main
# fatal: refusing to merge unrelated histories

# Or when trying to create a PR
gh pr create --base main --head master
# error: no history in common
```

There are three resolution strategies, each with tradeoffs:

**Strategy 1: `--allow-unrelated-histories`** merges both histories into a single DAG by creating a merge commit with two parent commits that have no common ancestor. This preserves all history from both branches but creates a messy merge — every file present in both branches will conflict, even if the content is unrelated. For small divergences (README + LICENSE on main, actual code on master), the conflicts are manageable. For large divergences, it's painful.

```bash
git checkout master
git merge origin/main --allow-unrelated-histories
# Resolve conflicts in README.md, .gitignore, etc.
git add .
git commit -m "merge: unify main and master histories"
git push origin master:main
```

**Strategy 2: Force push** replaces the remote branch entirely with the local branch. `git push --force origin master:main` overwrites main with master's history, discarding everything that was on main. This is clean and simple but destructive — the remote history is gone. Acceptable when main only had auto-generated content (README, LICENSE), dangerous when it had real work.

**Strategy 3: Cherry-pick** selectively copies individual commits from one branch to the other. This is the most surgical approach but also the most labor-intensive, especially when the divergence spans many commits. Best used when only a few specific commits need to cross the boundary.

The best practice is prevention: when creating a GitHub repository for an existing local project, create it **empty** (no README, no .gitignore, no LICENSE) and push the local branch directly as main. This ensures a single continuous history from the start.

## Related Concepts

- [[concepts/github-repo-init-existing-project]] - The prevention strategy: how to correctly set up a GitHub repo for existing code
- [[connections/windows-shell-boundary-failures]] - Similar pattern: tooling boundary mismatch that produces confusing errors rather than working transparently
