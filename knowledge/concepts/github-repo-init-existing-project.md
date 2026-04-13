---
title: "GitHub Repo Initialization for Existing Projects"
aliases: [github empty repo, push existing project, github init pitfall]
tags: [git, github, workflow]
category: "git"
sources:
  - "raw/git-unrelated-histories-branch-strategy.md"
created: 2026-04-13
updated: 2026-04-13
---

# GitHub Repo Initialization for Existing Projects

**Context:** When publishing an existing local project (already has `git init`, commits, and history) to a new GitHub repository.

**Problem:** GitHub's "Create repository" UI offers to initialize with README, .gitignore, and LICENSE. Checking any of these creates an initial commit on `main` — a commit that has no relationship to the local project's history. This creates unrelated histories that block all standard merge and PR operations.

**Lesson:** When creating a GitHub repo for an existing local project, always create it **empty** — uncheck all initialization options. Then push the local branch directly as `main`. This preserves a single continuous history.

## Key Points

- GitHub UI's "Add a README file" checkbox creates an initial commit on `main` — this is a separate history from your local project
- The resulting unrelated histories error is confusing because both repos "look" related (same project name) but Git sees them as independent
- The correct workflow: create empty repo → `git remote add origin <url>` → `git push -u origin master:main`
- If `.gitignore` or LICENSE is needed, add them locally before the first push — don't let GitHub generate them
- This is a one-time setup mistake with lasting consequences: every future merge or PR between the branches requires `--allow-unrelated-histories` or force operations

## Details

GitHub's repository creation flow is designed for new projects that don't exist yet. The initialization options (README, .gitignore, LICENSE) are convenient for starting fresh — they create a first commit so the repo isn't empty. But for existing projects, these options create a trap.

The trap is subtle because it doesn't fail immediately. The developer creates the repo with a README, adds it as a remote locally, and pushes their branch. The push succeeds (it's creating a new remote branch, not merging). The problem only surfaces when they try to merge `master` into `main` or create a PR — operations that require a common ancestor between the branches.

The correct workflow for existing projects:

```bash
# On GitHub: Create repository with NO initialization (no README, no .gitignore, no LICENSE)

# Locally:
git remote add origin https://github.com/user/repo.git
git push -u origin master:main    # Push local master as remote main
```

If the project needs a README, .gitignore, or LICENSE, create them locally as regular commits in the existing history before pushing. This keeps everything in a single linear history.

For projects where the mistake has already been made, see [[concepts/git-unrelated-histories]] for resolution strategies. The most common fix is `git merge --allow-unrelated-histories` followed by conflict resolution, but this is cleanup work that could have been avoided entirely with an empty repo initialization.

The MetaMode project encountered this exact scenario: `main` was created via GitHub UI with documentation content, while `master` was the local working branch. The resolution required `--allow-unrelated-histories` merge, producing a merge commit that joined both histories. Going forward, the project adopted a branch strategy where `master` is the working branch and `main` is kept in sync via regular merges (which now work because the histories were joined).

## Related Concepts

- [[concepts/git-unrelated-histories]] - The problem that arises when this best practice is not followed
- [[concepts/fork-dont-rewrite]] - Same principle of working with existing structures rather than creating parallel ones
