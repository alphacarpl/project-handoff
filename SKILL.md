---
name: project-handoff
description: Update a local project handoff state from Git metadata. Use when Codex is asked to prepare or refresh project handoff artifacts, Windows desktop.ini InfoTip metadata, a wiki onboarding README, estimated work-hours logs from git commit history, a handoff commit, or a post-commit hook that keeps those files current.
---

# Project Handoff

## Quick Start

Use `scripts/project_manager.py` to update three project artifacts:

- `desktop.ini` with a Windows Explorer `InfoTip` containing a short project description plus latest commit hash/date.
- `wiki/README.md` with an onboarding template, created only when missing.
- `hours/sesje_i_czas.md` with estimated work sessions from `git log`.

Run it from any workspace:

```bash
python "C:/Users/Wiktor/.codex/skills/project-handoff/scripts/project_manager.py" --project "C:/path/to/project" --description "Analiza danych klientow"
```

The description is truncated to 28 characters for the `desktop.ini` InfoTip.

## Handoff Mode

Use `--handoff` when the user asks to prepare a handoff commit. The script updates the handoff artifacts, stages only:

- `desktop.ini`
- `wiki/README.md`
- `hours/sesje_i_czas.md`

Then it creates a commit when those files changed:

```bash
python "C:/Users/Wiktor/.codex/skills/project-handoff/scripts/project_manager.py" --project "C:/path/to/project" --description "Analiza danych klientow" --handoff
```

Use `--handoff-message "docs: refresh handoff"` when the user wants a custom commit message.

## Workflow

1. Identify the target project root. Default to the current working directory when the user does not give a path.
2. Choose a concise description from the user's request or the project name.
3. Run the script with `--project` and `--description`.
4. Report which files were changed and whether Git metadata was available.

## Options

- Use `--gap-minutes 120` to control the maximum gap between commits that counts as one work session.
- Use `--skip-desktop-ini`, `--skip-wiki`, or `--skip-hours` for partial updates.
- Use `--install-post-commit-hook` to write `.git/hooks/post-commit` so the handoff files refresh after every commit.
- Use `--force-hook` only when the user explicitly wants to overwrite an existing hook.
- Use `--handoff` to stage and commit only generated handoff files.

## Global New-Project Hook

Use `scripts/install_git_template.py` when the user asks to install the workflow for every new Git project. It writes a `post-commit` hook into a Git template directory and configures global `init.templateDir`.

The generated hook uses the first line of `.project-handoff-description` as the project description. If the file is missing, it falls back to the project folder name.

## Notes

- `desktop.ini` is written as UTF-16 because Windows Explorer expects that encoding for shell metadata.
- The script applies Windows `attrib` flags when available and silently continues on non-Windows systems.
- The hours log is an estimate based on commit timestamps; Git does not store actual active work time.
- The wiki template is never overwritten when `wiki/README.md` already exists.
