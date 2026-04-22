#!/usr/bin/env python3
"""Update project handoff files from Git metadata."""

from __future__ import annotations

import argparse
import datetime as dt
import platform
import subprocess
import sys
from pathlib import Path


class ProjectManager:
    def __init__(self, project_path: Path, description: str, gap_minutes: int = 120) -> None:
        self.root = project_path.resolve()
        self.description = description.lstrip("\ufeff").strip()[:28]
        self.gap_seconds = gap_minutes * 60
        self.wiki_dir = self.root / "wiki"
        self.hours_dir = self.root / "hours"
        self.changed: list[Path] = []
        self.notes: list[str] = []

        self.wiki_dir.mkdir(parents=True, exist_ok=True)
        self.hours_dir.mkdir(parents=True, exist_ok=True)

    def run_git(self, args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args],
            cwd=self.root,
            capture_output=True,
            text=True,
            check=check,
        )

    def get_git_status(self) -> tuple[str | None, str]:
        try:
            self.run_git(["rev-parse", "--is-inside-work-tree"])
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None, "no-git"

        try:
            result = self.run_git(["log", "-1", "--format=%h|%cd", "--date=format:%d-%m-%y"])
            parts = result.stdout.strip().split("|", 1)
            if len(parts) != 2 or not parts[0]:
                return None, "no-commit"
            return parts[0], parts[1]
        except subprocess.CalledProcessError:
            return None, "no-commit"

    def update_desktop_ini(self) -> None:
        hash_value, date_value = self.get_git_status()

        if date_value == "no-git":
            infotip = f"{self.description} || no-git"
        elif date_value == "no-commit":
            infotip = f"{self.description} || no-commit"
        else:
            infotip = f"{self.description} || {hash_value} {date_value}"

        ini_path = self.root / "desktop.ini"
        if platform.system().lower() == "windows" and ini_path.exists():
            self._attrib(["-s", "-h", str(ini_path)])

        ini_path.write_text(f"[.ShellClassInfo]\nInfoTip={infotip}\n", encoding="utf-16")
        self.changed.append(ini_path)

        if platform.system().lower() == "windows":
            self._attrib(["+s", "+h", str(ini_path)])
            self._attrib(["+r", str(self.root)])

    def _attrib(self, args: list[str]) -> None:
        try:
            subprocess.run(["attrib", *args], capture_output=True, check=False)
        except FileNotFoundError:
            self.notes.append("attrib unavailable; skipped Windows Explorer attributes")

    def update_wiki(self) -> None:
        wiki_file = self.wiki_dir / "README.md"
        if wiki_file.exists():
            self.notes.append("wiki/README.md already exists; left unchanged")
            return

        wiki_file.write_text(
            f"# Dokumentacja Projektu: {self.description}\n\n"
            "## Przeznaczenie\n"
            "[Opisz cel projektu dla innych dzialow]\n\n"
            "## Kluczowe umiejetnosci\n"
            "[Wymagane technologie/wiedza]\n\n"
            "## Kontakty\n"
            "[Osoby decyzyjne]\n",
            encoding="utf-8",
        )
        self.changed.append(wiki_file)

    def update_hours(self) -> None:
        hours_file = self.hours_dir / "sesje_i_czas.md"

        try:
            result = self.run_git(["log", "--reverse", "--format=%ct|%s"])
            entries = [line for line in result.stdout.splitlines() if line.strip()]
        except (subprocess.CalledProcessError, FileNotFoundError):
            hours_file.write_text("Brak danych Git do obliczenia czasu.\n", encoding="utf-8")
            self.changed.append(hours_file)
            return

        if not entries:
            hours_file.write_text("Brak danych Git do obliczenia czasu.\n", encoding="utf-8")
            self.changed.append(hours_file)
            return

        total_seconds = 0
        lines = ["# Historia pracy i czas\n"]
        last_time: int | None = None

        for entry in entries:
            timestamp, message = entry.split("|", 1)
            current_time = int(timestamp)
            stamp = dt.datetime.fromtimestamp(current_time).strftime("%d-%m-%y %H:%M")

            if last_time is None:
                lines.append(f"- {stamp} | Start: {message}")
            else:
                diff = current_time - last_time
                if diff < self.gap_seconds:
                    total_seconds += diff
                    lines.append(f"- {stamp} | Commit: {message} (+ {int(diff / 60)} min)")
                else:
                    lines.append(f"- {stamp} | Nowa sesja: {message}")

            last_time = current_time

        lines.append(f"\n## Podsumowanie\nSzacunkowy czas pracy: {round(total_seconds / 3600, 2)} h")
        hours_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        self.changed.append(hours_file)

    def install_post_commit_hook(self, force: bool = False) -> Path:
        git_dir = self.root / ".git"
        hooks_dir = git_dir / "hooks"
        hook_path = hooks_dir / "post-commit"

        if not git_dir.exists():
            raise RuntimeError("Cannot install hook because .git does not exist")

        hooks_dir.mkdir(parents=True, exist_ok=True)

        if hook_path.exists() and not force:
            raise RuntimeError("post-commit hook already exists; rerun with --force-hook to replace it")

        script_path = Path(__file__).resolve().as_posix()
        project_path = self.root.as_posix()
        description = self.description.replace('"', '\\"')
        hook_path.write_text(
            "#!/bin/sh\n"
            f'python "{script_path}" --project "{project_path}" --description "{description}"\n',
            encoding="utf-8",
        )
        try:
            hook_path.chmod(0o755)
        except OSError:
            pass

        self.changed.append(hook_path)
        return hook_path

    def handoff_files(self) -> list[Path]:
        return [
            self.root / "desktop.ini",
            self.wiki_dir / "README.md",
            self.hours_dir / "sesje_i_czas.md",
        ]

    def create_handoff_commit(self, message: str) -> bool:
        try:
            self.run_git(["rev-parse", "--is-inside-work-tree"])
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError("Cannot create handoff commit because this is not a Git repository")

        existing_files = [path for path in self.handoff_files() if path.exists()]
        if not existing_files:
            self.notes.append("no handoff files exist; nothing to commit")
            return False

        rel_paths = [path.relative_to(self.root).as_posix() for path in existing_files]
        self.run_git(["add", "--", *rel_paths])

        status = self.run_git(["status", "--porcelain", "--", *rel_paths]).stdout.strip()
        if not status:
            self.notes.append("handoff files already clean; no commit created")
            return False

        self.run_git(["commit", "-m", message])
        self.notes.append(f"created handoff commit: {message}")
        return True


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Update project handoff files from Git metadata.")
    parser.add_argument("--project", default=".", help="Project root path. Defaults to current directory.")
    parser.add_argument("--description", required=True, help="Short project description for desktop.ini and wiki.")
    parser.add_argument("--gap-minutes", type=int, default=120, help="Max gap between commits counted as work time.")
    parser.add_argument("--skip-desktop-ini", action="store_true", help="Do not update desktop.ini.")
    parser.add_argument("--skip-wiki", action="store_true", help="Do not create wiki/README.md.")
    parser.add_argument("--skip-hours", action="store_true", help="Do not update hours/sesje_i_czas.md.")
    parser.add_argument("--install-post-commit-hook", action="store_true", help="Install .git/hooks/post-commit.")
    parser.add_argument("--force-hook", action="store_true", help="Overwrite an existing post-commit hook.")
    parser.add_argument("--handoff", action="store_true", help="Stage and commit only the handoff artifacts.")
    parser.add_argument(
        "--handoff-message",
        default="chore: update project handoff",
        help="Commit message used with --handoff.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    manager = ProjectManager(Path(args.project), args.description, args.gap_minutes)

    if not args.skip_desktop_ini:
        manager.update_desktop_ini()
    if not args.skip_wiki:
        manager.update_wiki()
    if not args.skip_hours:
        manager.update_hours()
    if args.install_post_commit_hook:
        manager.install_post_commit_hook(force=args.force_hook)
    if args.handoff:
        manager.create_handoff_commit(args.handoff_message)

    for changed in manager.changed:
        print(f"updated: {changed}")
    for note in manager.notes:
        print(f"note: {note}")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
