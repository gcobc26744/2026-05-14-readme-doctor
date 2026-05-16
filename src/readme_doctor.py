from __future__ import annotations

import argparse
import pathlib
import re
import sys
from dataclasses import dataclass


TEMPLATE = """# <Project name>

## What it is
1-2 sentences.

## Why it exists
What problem you wanted to solve / practice.

## How to run
```bash
<one command>
```

## Example
Input:
- ...

Output:
- ...

## Next steps
- [ ] ...
"""


RE_HEADING = re.compile(r"^(?P<hashes>#{1,6})\s+(?P<title>.+?)\s*$")


@dataclass(frozen=True)
class CheckResult:
    readme_path: pathlib.Path
    found_titles: set[str]
    missing_sections: list[str]


def _normalize_title(title: str) -> str:
    return re.sub(r"\s+", " ", title.strip()).casefold()


def _collect_headings(markdown_text: str) -> set[str]:
    found: set[str] = set()
    for line in markdown_text.splitlines():
        match = RE_HEADING.match(line)
        if not match:
            continue
        found.add(_normalize_title(match.group("title")))
    return found


def _resolve_readme_path(target: str) -> pathlib.Path:
    path = pathlib.Path(target).expanduser()
    if path.is_dir():
        return path / "README.md"
    return path


def check_readme(readme_path: pathlib.Path) -> CheckResult:
    if not readme_path.exists():
        return CheckResult(readme_path=readme_path, found_titles=set(), missing_sections=["README not found"])

    markdown_text = readme_path.read_text(encoding="utf-8", errors="replace")
    found_titles = _collect_headings(markdown_text)

    required = [
        "what it is",
        "why it exists",
        "how to run",
        "example",
        "next steps",
    ]
    missing = [section for section in required if section not in found_titles]

    return CheckResult(readme_path=readme_path, found_titles=found_titles, missing_sections=missing)


def _apply_fix(readme_path: pathlib.Path, missing_sections: list[str]) -> None:
    if not missing_sections:
        return
    existing = readme_path.read_text(encoding="utf-8", errors="replace")
    additions = []
    for section in missing_sections:
        if section == "README not found":
            continue
        pretty = section.title()
        additions.append(f"\n## {pretty}\n\n(TODO)\n")
    if not additions:
        return
    readme_path.write_text(existing.rstrip() + "".join(additions) + "\n", encoding="utf-8")


def _print_report(result: CheckResult) -> int:
    if result.missing_sections == ["README not found"]:
        print(f"README not found: {result.readme_path}")
        return 2

    if not result.missing_sections:
        print(f"OK: {result.readme_path}")
        return 0

    print(f"Missing sections in {result.readme_path}:")
    for section in result.missing_sections:
        print(f"- {section}")
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check a README.md for a beginner-friendly structure.")
    parser.add_argument(
        "target",
        nargs="?",
        default="README.md",
        help="Path to README.md or a folder containing README.md (default: README.md).",
    )
    parser.add_argument("--template", action="store_true", help="Print a README template to stdout.")
    parser.add_argument("--fix", action="store_true", help="Append missing section headings to the README.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with code 2 if any required section is missing (CI-friendly).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.template:
        sys.stdout.write(TEMPLATE)
        return 0

    readme_path = _resolve_readme_path(args.target)
    result = check_readme(readme_path)

    exit_code = _print_report(result)
    if args.strict and exit_code == 1:
        exit_code = 2
    if args.fix and exit_code in (1, 0) and result.missing_sections and readme_path.exists():
        _apply_fix(readme_path, result.missing_sections)
        print("Applied: appended missing headings.")
        return 0

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
