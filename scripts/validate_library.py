"""Deterministic structural checks for the instruction library."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_FILES = sorted(
    path
    for path in ROOT.rglob("*.md")
    if ".git" not in path.parts
)

FORBIDDEN = {
    "NEXT_PUBLIC_REQUEST_SIGNING_SECRET": "browser-exposed signing secret",
    "REACT_APP_SIGNING_SECRET": "browser-exposed signing secret",
    "APP_SIGNING_SECRET": "obsolete universal signing contract",
    "REQUEST_SIGNING_SECRET same on both sides": "shared client/server secret",
    "image: traefik:v3.0": "unsupported Traefik baseline",
    '"lint":       "next lint"': "removed Next.js lint command",
    "├── middleware.ts": "obsolete Next.js 16 middleware filename",
    "Django>=5.0,<6.0": "stale Django constraint",
    "<version>3.3.0</version>": "stale Spring Boot parent",
}

REQUIRED_BY_FILE = {
    "Frontend/NEXTJS_FRONTEND_STRUCTURE.md": (
        "MIGRATION PRIME DIRECTIVE",
        "Next.js 16.4",
        "proxy.ts",
        "BACKEND_API_URL",
    ),
    "Frontend/REACTJS_FRONTEND_STRUCTURE.md": (
        "MIGRATION PRIME DIRECTIVE",
        "React 19.3",
        "Vite 8",
    ),
    "Frontend/ANGULARJS_FRONTEND_STRUCTURE.md": (
        "MIGRATION PRIME DIRECTIVE",
        "Angular 22",
        "TypeScript 6.0",
    ),
    "Frontend/FLUTTER_STRUCTURE.md": (
        "MIGRATION PRIME DIRECTIVE",
        "Flutter 3.47",
        "GoRouter 18",
    ),
    "Security/SECURITY_LAYER.md": (
        "Never put a shared secret in browser JavaScript",
        "trusted server-to-server calls only",
        "traefik:v3.7.15",
    ),
    "Database/DATABASE_STRUCTURE.md": (
        "Exactly one system may own application DDL",
        "PostgreSQL 18",
        "allow_destructive_cli",
    ),
}


def fence_errors(path: Path, text: str) -> list[str]:
    errors: list[str] = []
    open_fence: tuple[str, int] | None = None
    for number, line in enumerate(text.splitlines(), start=1):
        match = re.match(r"^\s*(`{3,}|~{3,})", line)
        if not match:
            continue
        marker = match.group(1)
        family = marker[0]
        if open_fence is None:
            open_fence = (family, number)
        elif open_fence[0] == family:
            open_fence = None
    if open_fence is not None:
        errors.append(f"unclosed code fence opened on line {open_fence[1]}")
    return errors


def main() -> int:
    errors: list[str] = []
    texts: dict[str, str] = {}

    for path in MARKDOWN_FILES:
        relative = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8")
        texts[relative] = text
        errors.extend(f"{relative}: {error}" for error in fence_errors(path, text))

        for needle, reason in FORBIDDEN.items():
            if needle in text:
                errors.append(f"{relative}: forbidden {reason}: {needle!r}")

    for relative, needles in REQUIRED_BY_FILE.items():
        text = texts.get(relative)
        if text is None:
            errors.append(f"missing required file: {relative}")
            continue
        for needle in needles:
            if needle not in text:
                errors.append(f"{relative}: missing required marker {needle!r}")

    if errors:
        print("Library validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Library validation passed: {len(MARKDOWN_FILES)} Markdown files checked.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
