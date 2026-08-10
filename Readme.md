# envcheck

Scan your codebase for environment variables actually used in code, and diff them against your `.env.example` (or any env file). Catches broken deploys before they happen.

## Install

```bash
pip install cli-envcheck
```

Or run locally:

```bash
git clone https://github.com/yourname/envcheck-cli
cd envcheck-cli
pip install -e .
```

## Usage

```bash
envcheck .
```

Check against a different env file:

```bash
envcheck . --env-file .env
```

## What it does

- Scans `.py`, `.js`, `.ts`, `.jsx`, `.tsx` files for env var reads
  (`os.getenv`, `os.environ[...]`, `process.env.X`)
- Compares against keys declared in `.env.example`
- Reports:
  - ❌ **MISSING** — used in code but not declared
  - ⚠️ **UNUSED** — declared but never used
- Exits with code `1` if any vars are missing (CI-friendly)

## Example output

```
envcheck .

┌──────────────────┬────────────────────────────────┐
│ Variable          │ Status                          │
├──────────────────┼────────────────────────────────┤
│ STRIPE_SECRET_KEY │ MISSING (used, not declared)    │
│ OLD_API_URL       │ UNUSED (declared, not used)     │
└──────────────────┴────────────────────────────────┘

Used in code: 12  |  Declared in .env.example: 11
```

## Why

Env var mismatches are a common source of "works on my machine" deploy failures. `envcheck` catches them in seconds, locally or in CI.

## License

MIT
