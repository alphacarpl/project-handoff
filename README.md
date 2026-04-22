# Project Handoff Skill

Project Handoff is a Codex skill that keeps lightweight project handoff artifacts in sync with Git metadata.

Polish beginner-friendly documentation: [README.pl.md](README.pl.md).

It can update:

- `desktop.ini` with a Windows Explorer `InfoTip` that includes a short project description and the latest commit hash/date.
- `wiki/README.md` with an onboarding template, created only when the file does not already exist.
- `hours/sesje_i_czas.md` with estimated work sessions based on commit timestamps.
- `.git/hooks/post-commit` so the generated files refresh automatically after every commit.

## Installation

Place this folder in your Codex skills directory:

```powershell
C:\Users\<you>\.codex\skills\project-handoff
```

Codex will discover the skill automatically on the next session or skill refresh.

## Usage

Refresh handoff files for a project:

```powershell
python "C:\Users\<you>\.codex\skills\project-handoff\scripts\project_manager.py" --project "C:\path\to\project" --description "Customer data analysis"
```

Create a handoff commit containing only the generated handoff files:

```powershell
python "C:\Users\<you>\.codex\skills\project-handoff\scripts\project_manager.py" --project "C:\path\to\project" --description "Customer data analysis" --handoff
```

Install a project-local post-commit hook:

```powershell
python "C:\Users\<you>\.codex\skills\project-handoff\scripts\project_manager.py" --project "C:\path\to\project" --description "Customer data analysis" --install-post-commit-hook
```

Install the hook template globally for every new repository created with `git init`:

```powershell
python "C:\Users\<you>\.codex\skills\project-handoff\scripts\install_git_template.py"
```

For a custom project description in a new repo, create `.project-handoff-description` at the project root. The hook uses the first line of that file; otherwise it falls back to the folder name.

Install hooks into existing repositories under a folder:

```powershell
python "C:\Users\<you>\.codex\skills\project-handoff\scripts\install_existing_repos.py" --root "C:\path\to\projects" --dry-run
python "C:\Users\<you>\.codex\skills\project-handoff\scripts\install_existing_repos.py" --root "C:\path\to\projects"
```

The batch installer skips repositories that already have `.git/hooks/post-commit`. Use `--force` only when you intentionally want to replace existing hooks.

## Options

- `--gap-minutes 120` changes the maximum gap between commits counted as one work session.
- `--skip-desktop-ini`, `--skip-wiki`, and `--skip-hours` run only part of the update.
- `--handoff-message "docs: refresh handoff"` customizes the handoff commit message.
- `--force-hook` overwrites an existing project-local `post-commit` hook.
- `install_existing_repos.py --dry-run` previews batch installation for existing repositories.
- `install_existing_repos.py --force` overwrites existing `post-commit` hooks during batch installation.

## Notes

The hours log is an estimate. Git stores commit timestamps, not actual active work time.

The `desktop.ini` file is written as UTF-16 because Windows Explorer expects that encoding for shell metadata.
