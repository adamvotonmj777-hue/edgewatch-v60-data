"""Create one stateless EdgeWatch snapshot for a GitHub Actions artifact."""
from __future__ import annotations
import argparse
import gzip
import json
import os
from datetime import datetime, timezone
from collector import ASSETS, collect_snapshot

CAMPAIGN_ID = "edgewatch-v6-github-five-day-20260920"

def normalize_snapshot(snapshot):
    return {
        "meta": {key: snapshot.get(key) for key in (
            "schema_version", "captured_at", "captured_ts", "source",
            "orders_enabled", "complete_assets",
        )},
        "metadata": snapshot.get("metadata"),
        "assets": snapshot.get("assets"),
    }

def write_artifact(output_dir, snapshot=None):
    raw = collect_snapshot() if snapshot is None else snapshot
    normalized = normalize_snapshot(raw)
    captured_ts = float(normalized["meta"]["captured_ts"])
    stamp = datetime.fromtimestamp(captured_ts, timezone.utc).strftime("%Y%m%d_%H%M%S")
    os.makedirs(output_dir, exist_ok=True)
    snapshot_name = f"snapshot_{stamp}.json.gz"
    with gzip.open(os.path.join(output_dir, snapshot_name), "wt", encoding="utf-8", compresslevel=9) as handle:
        json.dump(normalized, handle, separators=(",", ":"), sort_keys=True)
    complete_assets = int(normalized["meta"].get("complete_assets") or 0)
    manifest = {
        "schema_version": "edgewatch.github_artifact_manifest.v1",
        "campaign_id": CAMPAIGN_ID,
        "captured_at": normalized["meta"]["captured_at"],
        "captured_ts": captured_ts,
        "snapshot_file": snapshot_name,
        "complete_assets": complete_assets,
        "expected_assets": len(ASSETS),
        "valid_for_research": complete_assets == len(ASSETS),
        "orders_enabled": False,
    }
    with open(os.path.join(output_dir, "run_manifest.json"), "w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True)
    return manifest

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="artifact")
    args = parser.parse_args(argv)
    manifest = write_artifact(os.path.abspath(args.output))
    print(json.dumps(manifest, sort_keys=True))
    return 0 if manifest["valid_for_research"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
