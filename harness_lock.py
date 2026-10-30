import hashlib
import json
import os
import sys
from pathlib import Path

TARGET_PATHS = ["tests/conftest.py", "tests/fixtures/", "core/validation_gate.py"]
MANIFEST_FILE = os.environ.get("HARNESS_MANIFEST", ".harness_lock.json")


def calculate_sha256(path: Path) -> str:
    sha256_hash = hashlib.sha256()
    if path.is_file():
        with open(path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
    elif path.is_dir():
        # Hash relative path plus content so renames, swaps, and additions are caught.
        for child in sorted(path.rglob("*")):
            if child.is_file():
                rel = child.relative_to(path).as_posix().encode()
                sha256_hash.update(len(rel).to_bytes(8, "big") + rel)
                data = child.read_bytes()
                sha256_hash.update(len(data).to_bytes(8, "big") + data)
    return sha256_hash.hexdigest()


def create_lock_manifest():
    manifest = {p: calculate_sha256(Path(p)) for p in TARGET_PATHS if Path(p).exists()}
    if not manifest:
        print("harness_lock: no protected paths found; nothing locked", file=sys.stderr)
        sys.exit(1)
    with open(MANIFEST_FILE, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"harness_lock: locked {len(manifest)} path(s) to {MANIFEST_FILE}")


def verify_lock_manifest():
    if not os.path.exists(MANIFEST_FILE):
        print("harness_lock: manifest missing", file=sys.stderr)
        sys.exit(1)
    with open(MANIFEST_FILE, "r") as f:
        baseline = json.load(f)
    for p_str, expected_hash in baseline.items():
        p = Path(p_str)
        if not p.exists() or calculate_sha256(p) != expected_hash:
            print(f"harness_lock: TAMPER DETECTED in {p_str}", file=sys.stderr)
            sys.exit(2)
    print("harness_lock: all protected paths intact")
    sys.exit(0)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "verify":
        verify_lock_manifest()
    else:
        create_lock_manifest()
