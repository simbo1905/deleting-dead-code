#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Package the deleting-dead-code Agent Skill into release artifacts.

Produces in --out-dir (default: build-output/):
  deleting-dead-code-<tag>.zip      -- universal format
  deleting-dead-code-<tag>.tar.gz   -- Unix format; same internal structure
  metadata.json                     -- machine-readable manifest with SHA-256 hashes

Archive internal structure (Verdent drop-in compatible):
  deleting-dead-code-<tag>/
    SKILL.md
    LICENSE
    README.md

Extract and rename the top-level folder to `deleting-dead-code` under
`.verdent/skills/` (or the equivalent skills directory for your agent) to
get a working skill install.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tarfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

# Files included in release archives (minimal distributable set).
# Excludes: dist/, .github/, .verdent/, .env.sample, .gitignore, build-output/
INCLUDE_FILES = ["SKILL.md", "LICENSE", "README.md"]


def git_full_sha() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build(tag: str, out_dir: Path, repo_root: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    prefix = f"deleting-dead-code-{tag}"

    sources: list[Path] = []
    for name in INCLUDE_FILES:
        candidate = repo_root / name
        if not candidate.exists():
            print(f"WARNING: {name} not found at {candidate}, skipping", file=sys.stderr)
            continue
        sources.append(candidate)

    if not sources:
        print("ERROR: No source files found", file=sys.stderr)
        sys.exit(1)

    zip_path = out_dir / f"{prefix}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for src in sources:
            zf.write(src, f"{prefix}/{src.name}")
    print(f"Created: {zip_path}")

    tar_path = out_dir / f"{prefix}.tar.gz"
    with tarfile.open(tar_path, "w:gz") as tf:
        for src in sources:
            tf.add(src, arcname=f"{prefix}/{src.name}")
    print(f"Created: {tar_path}")

    meta = {
        "name": "deleting-dead-code",
        "tag": tag,
        "commit": git_full_sha(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "files": {src.name: {"sha256": sha256_file(src)} for src in sources},
        "artifacts": {},
    }
    for artifact in (zip_path, tar_path):
        meta["artifacts"][artifact.name] = {"sha256": sha256_file(artifact)}

    meta_path = out_dir / "metadata.json"
    meta_path.write_text(json.dumps(meta, indent=2) + "\n")
    print(f"Created: {meta_path}")

    return [zip_path, tar_path, meta_path]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", required=True, help="Release tag (e.g., 2025.07.14-a1b2c3d)")
    parser.add_argument("--out-dir", default="build-output", help="Output directory")
    args = parser.parse_args()

    repo_root = Path(
        subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
    )

    artifacts = build(args.tag, Path(args.out_dir), repo_root)
    print(f"\n{len(artifacts)} artifacts ready in {args.out_dir}/")


if __name__ == "__main__":
    main()
