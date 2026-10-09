"""Upload local PDF backups to Supabase Storage.

Configuration is read from a local .env file or environment variables:

    SUPABASE_URL=https://your-project-ref.supabase.co
    SUPABASE_KEY=your-local-key
    SUPABASE_BUCKET=testing_subset

The script preserves paths relative to the source directory. It intentionally
does not print keys.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


DEFAULT_SOURCE = Path("data/raw/private/supabase_backup/testing_subset")
DEFAULT_MANIFEST = "upload_manifest.csv"


def load_dotenv(path: Path) -> None:
    """Load simple KEY=VALUE lines into os.environ when not already set."""

    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def env_required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def normalize_supabase_url(url: str) -> str:
    url = url.strip().rstrip("/")
    for suffix in ("/rest/v1", "/storage/v1"):
        if url.endswith(suffix):
            url = url[: -len(suffix)]
    return url.rstrip("/")


def request_json(url: str, key: str, method: str = "GET", payload: Any = None) -> Any:
    data = None
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    request = Request(url, data=data, headers=headers, method=method)
    with urlopen(request, timeout=60) as response:
        text = response.read().decode("utf-8")
        return json.loads(text) if text else {}


def list_buckets(supabase_url: str, key: str) -> list[dict[str, Any]]:
    url = f"{supabase_url}/storage/v1/bucket"
    buckets = request_json(url, key)
    if not isinstance(buckets, list):
        raise RuntimeError("Unexpected bucket list response from Supabase")
    return buckets


def bucket_exists(supabase_url: str, key: str, bucket: str) -> bool:
    return any((item.get("name") or item.get("id")) == bucket for item in list_buckets(supabase_url, key))


def create_bucket(supabase_url: str, key: str, bucket: str, public: bool = False) -> None:
    if bucket_exists(supabase_url, key, bucket):
        return
    url = f"{supabase_url}/storage/v1/bucket"
    payload = {"id": bucket, "name": bucket, "public": public}
    request_json(url, key, method="POST", payload=payload)


def upload_pdf(
    supabase_url: str,
    key: str,
    bucket: str,
    local_path: Path,
    object_path: str,
    upsert: bool = True,
) -> int:
    encoded_bucket = quote(bucket, safe="")
    encoded_path = quote(object_path, safe="/")
    url = f"{supabase_url}/storage/v1/object/{encoded_bucket}/{encoded_path}"
    content = local_path.read_bytes()
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/pdf",
        "x-upsert": "true" if upsert else "false",
    }
    request = Request(url, data=content, headers=headers, method="POST")
    with urlopen(request, timeout=180) as response:
        response.read()
    return len(content)


def object_path_for_file(source: Path, file_path: Path, prefix: str = "") -> str:
    relative = file_path.relative_to(source).as_posix()
    if prefix:
        return f"{prefix.strip('/')}/{relative}"
    return relative


def write_manifest(source: Path, rows: list[dict[str, Any]]) -> Path:
    manifest_path = source / DEFAULT_MANIFEST
    fieldnames = ["bucket", "object_path", "local_path", "bytes_uploaded", "status"]
    with manifest_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return manifest_path


def upload_directory(
    supabase_url: str,
    key: str,
    bucket: str,
    source: Path,
    prefix: str = "",
    limit: int | None = None,
    dry_run: bool = False,
    create_missing_bucket: bool = False,
) -> list[dict[str, Any]]:
    if not source.exists():
        raise RuntimeError(f"Source directory does not exist: {source}")

    files = sorted(source.rglob("*.pdf"))
    if limit is not None:
        files = files[:limit]

    if create_missing_bucket and not dry_run:
        create_bucket(supabase_url, key, bucket, public=False)

    rows: list[dict[str, Any]] = []
    for index, file_path in enumerate(files, start=1):
        object_path = object_path_for_file(source, file_path, prefix)
        if dry_run:
            print(f"[{index}/{len(files)}] would upload {object_path}")
            rows.append(
                {
                    "bucket": bucket,
                    "object_path": object_path,
                    "local_path": str(file_path),
                    "bytes_uploaded": "",
                    "status": "dry-run",
                }
            )
            continue

        bytes_uploaded = upload_pdf(supabase_url, key, bucket, file_path, object_path)
        print(f"[{index}/{len(files)}] uploaded {object_path}")
        rows.append(
            {
                "bucket": bucket,
                "object_path": object_path,
                "local_path": str(file_path),
                "bytes_uploaded": bytes_uploaded,
                "status": "uploaded",
            }
        )

    write_manifest(source, rows)
    return rows


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Upload local PDF backups to Supabase Storage."
    )
    parser.add_argument("--env-file", default=".env", help="Path to local .env file.")
    parser.add_argument("--source", default=str(DEFAULT_SOURCE), help="Local PDF root.")
    parser.add_argument("--bucket", help="Target Supabase Storage bucket name.")
    parser.add_argument("--prefix", default="", help="Optional target path prefix.")
    parser.add_argument("--limit", type=int, help="Maximum number of PDFs to upload.")
    parser.add_argument("--dry-run", action="store_true", help="List uploads only.")
    parser.add_argument(
        "--create-bucket",
        action="store_true",
        help="Create the bucket if it does not exist.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    load_dotenv(Path(args.env_file))
    supabase_url = normalize_supabase_url(env_required("SUPABASE_URL"))
    key = env_required("SUPABASE_KEY")
    bucket = args.bucket or os.getenv("SUPABASE_BUCKET", "").strip()
    if not bucket:
        raise RuntimeError("Missing bucket. Set SUPABASE_BUCKET or pass --bucket.")

    try:
        rows = upload_directory(
            supabase_url=supabase_url,
            key=key,
            bucket=bucket,
            source=Path(args.source),
            prefix=args.prefix,
            limit=args.limit,
            dry_run=args.dry_run,
            create_missing_bucket=args.create_bucket,
        )
    except (HTTPError, URLError, RuntimeError) as exc:
        print(f"Upload failed: {exc}", file=sys.stderr)
        return 1

    mode = "listed" if args.dry_run else "uploaded"
    print(f"Done: {mode} {len(rows)} PDF file(s).")
    print(f"Manifest: {Path(args.source) / DEFAULT_MANIFEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
