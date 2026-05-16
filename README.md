# README Doctor

## What it is
`readme_doctor.py` is a tiny CLI that checks a `README.md` for a few beginner-friendly sections (so your repos look consistent and are easy to run).

## Why it exists
When doing daily side projects, it’s easy to forget to document:
- the “one command” to run
- a minimal example
- next steps / TODOs

This tool quickly tells you what’s missing and can optionally append missing headings.

## How to run
Requirements: Python 3.10+

### Option A: run from source

```bash
cd projects/2026-05-14-readme-doctor
python src/readme_doctor.py ..\\..\\README.md
```

### Option B: install the CLI (editable)

```bash
cd projects/2026-05-14-readme-doctor
python -m pip install -e .
readme-doctor ..\\..\\README.md
```

## Examples

Check a project README:

```bash
readme-doctor ..\\2026-05-08-utf8-scout\\README.md
```

Print a template you can paste into a new README:

```bash
readme-doctor --template
```

Append missing headings to a README (safe: only adds headings that are missing):

```bash
readme-doctor ..\\2026-05-08-utf8-scout\\README.md --fix
```

Strict mode (CI-friendly): exit code `2` if anything is missing:

```bash
readme-doctor ..\\2026-05-08-utf8-scout\\README.md --strict
```

## Next steps
- [ ] Support custom section sets via a JSON config
