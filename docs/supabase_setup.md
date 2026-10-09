# Supabase Setup

This project can later download a small set of private CAFR/ACFR PDFs from
Supabase Storage for local extraction testing.

## Key Safety

- Do not commit real Supabase keys.
- Do not paste secret keys into GitHub, README files, screenshots, or public
  notebooks.
- Keep real values only in a local `.env` file.
- If a secret key is exposed, rotate it in Supabase before continuing.

The publishable key is intended for client-side use only when Row Level Security
and policies are configured correctly. The secret key has privileged access and
should be treated like a password.

## Local `.env`

Create a local `.env` file from the example:

```bash
cp .env.example .env
```

Then fill in:

```text
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_KEY=your-local-key
SUPABASE_BUCKET=your-storage-bucket
SUPABASE_PREFIX=optional/folder/prefix
```

The repository `.gitignore` already excludes `.env`, `data/raw/`, and
`data/private/`.

## Recommended PDF Test Set

Start with a small sample before building large-batch extraction:

- 3 to 5 public or approved PDFs
- 2 to 3 localities
- 1 to 2 fiscal years each
- Filenames that include locality and fiscal year when possible

Store downloaded files locally under:

```text
data/raw/private/
```

That folder is intentionally ignored by Git.

## Download Command

After filling in `.env`, list matching PDFs first:

```bash
python scripts/download_supabase_pdfs.py --dry-run
```

If you do not know the bucket name yet, list visible buckets:

```bash
python scripts/download_supabase_pdfs.py --list-buckets
```

To back up PDFs from every visible bucket:

```bash
python scripts/download_supabase_pdfs.py --all-buckets
```

Then download the PDFs:

```bash
python scripts/download_supabase_pdfs.py
```

By default files are saved under:

```text
data/raw/private/supabase_backup/
```

The script also writes a local manifest:

```text
data/raw/private/supabase_backup/download_manifest.csv
```
