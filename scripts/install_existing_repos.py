#!/usr/bin/env python3
"""Install Project Handoff hooks into existing Git repositories."""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


HOOK_TEMPLATE = """#!/bin/sh

PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
if [ -z "$PROJECT_ROOT" ]; then
  exit 0
fi

DESCRIPTION_FILE="$PROJECT_ROOT/.project-handoff-description"
if [ -f "$DESCRIPTION_FILE" ]; then
  DESCRIPTION="$(head -n 1 "$DESCRIPTION_FILE")"
else
  DESCRIPTION="$(basename "$PROJECT_ROOT")"
fi

python "{script_path}" --project "$PROJECT_ROOT" --description "$DESCRIPTION"
"""


@dataclass
class InstallResult:
    status: str
    repo: Path
    detail: str = ""


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Find existing Git repositories and install the Project Handoff post-commit hook."
    )
    parser.add_argument("--root", required=True, help="Folder to scan for Git repositories.")
    parser.add_argument(
        "--project-manager",
        default=str(Path(__file__).resolve().parent / "project_manager.py"),
        help="Path to project_manager.py used by generated hooks.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen without changing files.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing post-commit hooks.")
    parser.add_argument(
        "--max-depth",
        type=int,
        default=6,
        help="Maximum folder depth below --root to scan. Defaults to 6.",
    )
    parser.add_argument(
        "--include-bare",
        action="store_true",
        help="Also include bare repositories where the folder itself is a Git directory.",
    )
    return parser.parse_args(argv)


def find_repos(root: Path, max_depth: int, include_bare: bool) -> list[Path]:
    root = root.resolve()
    repos: list[Path] = []

    def walk(path: Path, depth: int) -> None:
        if depth > max_depth:
            return

        git_path = path / ".git"
        if git_path.is_dir() or git_path.is_file():
            repos.append(path)
            return

        if include_bare and (path / "HEAD").is_file() and (path / "objects").is_dir() and (path / "refs").is_dir():
            repos.append(path)
            return

        try:
            children = [child for child in path.iterdir() if child.is_dir()]
        except (OSError, PermissionError):
            return

        for child in children:
            if child.name in {".git", "node_modules", ".venv", "venv", "__pycache__"}:
                continue
            walk(child, depth + 1)

    walk(root, 0)
    return sorted(set(repos), key=lambda item: str(item).lower())


def hook_path_for_repo(repo: Path) -> Path:
    result = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "--git-path", "hooks/post-commit"],
        capture_output=True,
        text=True,
        check=True,
    )
    hook_path = Path(result.stdout.strip())
    if not hook_path.is_absolute():
        hook_path = repo / hook_path
    return hook_path.resolve()


def install_hook(repo: Path, project_manager: Path, dry_run: bool, force: bool) -> InstallResult:
    try:
        hook_path = hook_path_for_repo(repo)
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        return InstallResult("failed", repo, f"cannot resolve hook path: {exc}")

    if hook_path.exists() and not force:
        return InstallResult("skipped", repo, "post-commit already exists")

    action = "would overwrite" if hook_path.exists() else "would install"
    if dry_run:
        return InstallResult("dry-run", repo, f"{action}: {hook_path}")

    try:
        hook_path.parent.mkdir(parents=True, exist_ok=True)
        hook_path.write_text(HOOK_TEMPLATE.format(script_path=project_manager.as_posix()), encoding="utf-8")
        try:
            hook_path.chmod(0o755)
        except OSError:
            pass
    except OSError as exc:
        return InstallResult("failed", repo, str(exc))

    if force and hook_path.exists():
        return InstallResult("installed", repo, f"wrote: {hook_path}")
    return InstallResult("installed", repo, f"wrote: {hook_path}")


def print_report(results: list[InstallResult]) -> None:
    counts: dict[str, int] = {}
    for result in results:
        counts[result.status] = counts.get(result.status, 0) + 1

    print("# Project Handoff hook installation report")
    print()
    if not results:
        print("No Git repositories found.")
        return

    for result in results:
        detail = f" - {result.detail}" if result.detail else ""
        print(f"[{result.status}] {result.repo}{detail}")

    print()
    print("Summary:")
    for status in sorted(counts):
        print(f"- {status}: {counts[status]}")


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    root = Path(args.root).expanduser().resolve()
    project_manager = Path(args.project_manager).expanduser().resolve()

    if not root.exists():
        print(f"error: root does not exist: {root}", file=sys.stderr)
        return 1
    if not project_manager.exists():
        print(f"error: project_manager.py does not exist: {project_manager}", file=sys.stderr)
        return 1

    repos = find_repos(root, args.max_depth, args.include_bare)
    results = [install_hook(repo, project_manager, args.dry_run, args.force) for repo in repos]
    print_report(results)

    return 1 if any(result.status == "failed" for result in results) else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
