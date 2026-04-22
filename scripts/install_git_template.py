#!/usr/bin/env python3
"""Install the Project Handoff post-commit hook for newly initialized Git repos."""

from __future__ import annotations

import argparse
import subprocess
import sys
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


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Configure Git so new repositories include the Project Handoff post-commit hook."
    )
    parser.add_argument(
        "--template-dir",
        default=str(Path.home() / ".codex" / "git-template"),
        help="Git template directory to create and configure globally.",
    )
    parser.add_argument(
        "--project-manager",
        default=str(Path(__file__).resolve().parent / "project_manager.py"),
        help="Path to project_manager.py used by the generated hook.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    template_dir = Path(args.template_dir).expanduser().resolve()
    hooks_dir = template_dir / "hooks"
    hook_path = hooks_dir / "post-commit"
    project_manager = Path(args.project_manager).expanduser().resolve().as_posix()

    hooks_dir.mkdir(parents=True, exist_ok=True)
    hook_path.write_text(HOOK_TEMPLATE.format(script_path=project_manager), encoding="utf-8")

    try:
        hook_path.chmod(0o755)
    except OSError:
        pass

    subprocess.run(["git", "config", "--global", "init.templateDir", str(template_dir)], check=True)

    print(f"installed: {hook_path}")
    print(f"configured: git init.templateDir={template_dir}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
