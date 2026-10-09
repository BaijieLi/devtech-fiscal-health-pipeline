"""Download PDF files from Supabase Storage into a local ignored folder.

Configuration is read from a local .env file or environment variables:

    SUPABASE_URL=https://your-project-ref.supabase.co
    SUPABASE_KEY=your-local-key
    SUPABASE_BUCKET=your-storage-bucket
    SUPABASE_PREFIX=optional/folder/prefix

The script intentionally does not print keys.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


DEFAULT_DEST = Path("data/raw/private/supabase_backup")
DEFAULT_MANIFEST = "download_manifest.csv"
PAGE_SIZE = 100


@dataclass(frozen=True)
class StorageObject:
    path: str
    size: int | None = None
    mimetype: str | None = None


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
        return json.loads(response.read().decode("utf-8"))


def list_buckets(supabase_url: str, key: str) -> list[dict[str, Any]]:
    """List Supabase Storage buckets visible to the configured key."""

    url = f"{supabase_url}/storage/v1/bucket"
    buckets = request_json(url, key)
    if not isinstance(buckets, list):
        raise RuntimeError("Unexpected bucket list response from Supabase")
    return buckets


def request_bytes(url: str, key: str) -> bytes:
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
    }
    request = Request(url, headers=headers, method="GET")
    with urlopen(request, timeout=120) as response:
        return response.read()


def item_is_folder(item: dict[str, Any]) -> bool:
    name = str(item.get("name", ""))
    metadata = item.get("metadata")
    item_id = item.get("id")
    if not name:
        return False
    if name.lower().endswith(".pdf"):
        return False
    if metadata is None and item_id is None:
        return True
    return "." not in Path(name).name


def item_to_object(prefix: str, item: dict[str, Any]) -> StorageObject:
    name = str(item["name"])
    path = f"{prefix.rstrip('/')}/{name}".strip("/") if prefix else name
    metadata = item.get("metadata") or {}
    size = metadata.get("size")
    mimetype = metadata.get("mimetype") or metadata.get("mimeType")
    return StorageObject(path=path, size=size, mimetype=mimetype)


def list_pdf_objects(
    supabase_url: str,
    key: str,
    bucket: str,
    prefix: str = "",
    limit: int | None = None,
) -> list[StorageObject]:
    """Recursively list PDF objects under a Supabase Storage prefix."""

    found: list[StorageObject] = []
    visited: set[str] = set()

    def walk(current_prefix: str) -> None:
        if limit is not None and len(found) >= limit:
            return
        if current_prefix in visited:
            return
        visited.add(current_prefix)

        offset = 0
        while True:
            payload = {
                "prefix": current_prefix.strip("/"),
                "limit": PAGE_SIZE,
                "offset": offset,
                "sortBy": {"column": "name", "order": "asc"},
            }
            url = f"{supabase_url}/storage/v1/object/list/{quote(bucket, safe='')}"
            items = request_json(url, key, method="POST", payload=payload)
            if not items:
                break

            for item in items:
                if limit is not None and len(found) >= limit:
                    return
                obj = item_to_object(current_prefix, item)
                if item_is_folder(item):
                    walk(obj.path)
                elif obj.path.lower().endswith(".pdf"):
                    found.append(obj)

            if len(items) < PAGE_SIZE:
                break
            offset += PAGE_SIZE

    walk(prefix)
    return found


def download_object(supabase_url: str, key: str, bucket: str, object_path: str) -> bytes:
    encoded_bucket = quote(bucket, safe="")
    encoded_path = quote(object_path, safe="/")
    urls = [
        f"{supabase_url}/storage/v1/object/{encoded_bucket}/{encoded_path}",
        f"{supabase_url}/storage/v1/object/authenticated/{encoded_bucket}/{encoded_path}",
    ]
    last_error: Exception | None = None
    for url in urls:
        try:
            return request_bytes(url, key)
        except HTTPError as exc:
            last_error = exc
            if exc.code not in {400, 401, 403, 404}:
                raise
        except URLError as exc:
            last_error = exc
            raise
    raise RuntimeError(f"Could not download {object_path}: {last_error}")


def safe_local_path(dest: Path, object_path: str) -> Path:
    relative = Path(*[part for part in object_path.split("/") if part])
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"Unsafe storage path: {object_path}")
    return dest / relative


def write_manifest(dest: Path, rows: list[dict[str, Any]]) -> None:
    manifest_path = dest / DEFAULT_MANIFEST
    fieldnames = ["bucket", "storage_path", "local_path", "bytes_written", "status"]
    with manifest_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def download_pdfs(
    supabase_url: str,
    key: str,
    bucket: str,
    prefix: str,
    dest: Path,
    limit: int | None = None,
    dry_run: bool = False,
) -> list[dict[str, Any]]:
    objects = list_pdf_objects(supabase_url, key, bucket, prefix, limit=limit)
    dest.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []

    for index, obj in enumerate(objects, start=1):
        local_path = safe_local_path(dest, obj.path)
        if dry_run:
            print(f"[{index}/{len(objects)}] would download {obj.path}")
            rows.append(
                {
                    "bucket": bucket,
                    "storage_path": obj.path,
                    "local_path": str(local_path),
                    "bytes_written": "",
                    "status": "dry-run",
                }
            )
            continue

        local_path.parent.mkdir(parents=True, exist_ok=True)
        content = download_object(supabase_url, key, bucket, obj.path)
        local_path.write_bytes(content)
        print(f"[{index}/{len(objects)}] downloaded {obj.path}")
        rows.append(
            {
                "bucket": bucket,
                "storage_path": obj.path,
                "local_path": str(local_path),
                "bytes_written": len(content),
                "status": "downloaded",
            }
        )

    write_manifest(dest, rows)
    return rows


def download_all_buckets(
    supabase_url: str,
    key: str,
    prefix: str,
    dest: Path,
    limit: int | None = None,
    dry_run: bool = False,
) -> list[dict[str, Any]]:
    """Download PDFs from every visible bucket into per-bucket folders."""

    rows: list[dict[str, Any]] = []
    for bucket in list_buckets(supabase_url, key):
        bucket_name = bucket.get("name") or bucket.get("id")
        if not bucket_name:
            continue
        bucket_dest = dest / str(bucket_name)
        remaining = None if limit is None else max(limit - len(rows), 0)
        if remaining == 0:
            break
        bucket_rows = download_pdfs(
            supabase_url=supabase_url,
            key=key,
            bucket=str(bucket_name),
            prefix=prefix,
            dest=bucket_dest,
            limit=remaining,
            dry_run=dry_run,
        )
        rows.extend(bucket_rows)

    write_manifest(dest, rows)
    return rows


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Download PDF files from Supabase Storage into data/raw/private."
    )
    parser.add_argument("--env-file", default=".env", help="Path to local .env file.")
    parser.add_argument("--bucket", help="Supabase Storage bucket name.")
    parser.add_argument(
        "--list-buckets",
        action="store_true",
        help="Print visible Storage bucket names and exit.",
    )
    parser.add_argument(
        "--all-buckets",
        action="store_true",
        help="Download PDFs from every visible Storage bucket.",
    )
    parser.add_argument("--prefix", help="Optional folder prefix inside the bucket.")
    parser.add_argument("--dest", default=str(DEFAULT_DEST), help="Download folder.")
    parser.add_argument("--limit", type=int, help="Maximum number of PDFs to download.")
    parser.add_argument("--dry-run", action="store_true", help="List PDFs only.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    load_dotenv(Path(args.env_file))
    supabase_url = normalize_supabase_url(env_required("SUPABASE_URL"))
    key = env_required("SUPABASE_KEY")

    if args.list_buckets:
        try:
            buckets = list_buckets(supabase_url, key)
        except (HTTPError, URLError, RuntimeError) as exc:
            print(f"Bucket listing failed: {exc}", file=sys.stderr)
            return 1
        for bucket in buckets:
            name = bucket.get("name") or bucket.get("id") or "<unnamed>"
            public = bucket.get("public")
            print(f"{name} public={public}")
        return 0

    bucket = args.bucket or os.getenv("SUPABASE_BUCKET", "").strip()
    if not bucket and not args.all_buckets:
        raise RuntimeError("Missing bucket. Set SUPABASE_BUCKET or pass --bucket.")
    prefix = args.prefix if args.prefix is not None else os.getenv("SUPABASE_PREFIX", "")

    try:
        if args.all_buckets:
            rows = download_all_buckets(
                supabase_url=supabase_url,
                key=key,
                prefix=prefix,
                dest=Path(args.dest),
                limit=args.limit,
                dry_run=args.dry_run,
            )
        else:
            rows = download_pdfs(
                supabase_url=supabase_url,
                key=key,
                bucket=bucket,
                prefix=prefix,
                dest=Path(args.dest),
                limit=args.limit,
                dry_run=args.dry_run,
            )
    except (HTTPError, URLError, RuntimeError) as exc:
        print(f"Download failed: {exc}", file=sys.stderr)
        return 1

    mode = "listed" if args.dry_run else "downloaded"
    print(f"Done: {mode} {len(rows)} PDF file(s).")
    print(f"Manifest: {Path(args.dest) / DEFAULT_MANIFEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
