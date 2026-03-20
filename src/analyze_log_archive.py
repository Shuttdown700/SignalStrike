#!/usr/bin/env python3
"""
Analyze most recent RF targeting logs from archived .zip files.
Generates visual analytics and CSV summaries.

Expected log line example:
2025-11-11 14:25:09 - targeting - INFO - FIX at grid AB1234 freq=2437MHz err=2.3
"""

import os
import re
import zipfile
import shutil
import csv
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt

# === CONFIG ===
ARCHIVE_DIR = Path(__file__).parent.parent / "logs_archived"
EXTRACT_DIR = Path(__file__).parent.parent / "tmp_extracted"
ANALYTICS_DIR = Path(__file__).parent.parent / "analytics"
DATE_FORMAT = "%Y%m%d%H%M%S"
TARGET_LOG_NAME = "targeting.log"

# Regex patterns for parsing
GRID_RE = re.compile(r"grid\s+([A-Z]{2}\d{2,4})", re.IGNORECASE)
FREQ_RE = re.compile(r"freq[=:]?\s*([\d.]+)\s*MHz", re.IGNORECASE)
ERR_RE = re.compile(r"err(?:or)?[=:]?\s*([\d.]+)", re.IGNORECASE)


def find_latest_archive() -> Path:
    archives = list(ARCHIVE_DIR.glob("*.zip"))
    if not archives:
        raise FileNotFoundError("No archived logs found in ./logs_archived")

    def extract_ts(f):
        try:
            return datetime.strptime(f.name.split("_")[0], DATE_FORMAT)
        except Exception:
            return datetime.min

    latest = max(archives, key=extract_ts)
    print(f"[INFO] Latest archive: {latest.name}")
    return latest


def extract_archive(zip_path: Path, extract_to: Path):
    if extract_to.exists():
        shutil.rmtree(extract_to)
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(extract_to)
    print(f"[INFO] Extracted {zip_path.name} to {extract_to}")


def find_target_logs(extract_dir: Path):
    return list(extract_dir.glob(f"app/*/{TARGET_LOG_NAME}"))


def parse_targeting_log(file_path: Path):
    entries = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                ts_str, remainder = line.split(" - targeting - INFO - ", 1)
                ts = datetime.strptime(ts_str.strip(), "%Y-%m-%d %H:%M:%S")
            except ValueError:
                continue

            grid = GRID_RE.search(remainder)
            freq = FREQ_RE.search(remainder)
            err = ERR_RE.search(remainder)

            entries.append({
                "timestamp": ts,
                "message": remainder,
                "grid": grid.group(1) if grid else None,
                "freq": float(freq.group(1)) if freq else None,
                "error": float(err.group(1)) if err else None,
            })
    return entries


def analyze_entries(entries):
    fix_count = sum("FIX" in e["message"] for e in entries)
    lob_count = sum("3 LOB" in e["message"] for e in entries)
    timestamps = [e["timestamp"] for e in entries]
    freqs = [e["freq"] for e in entries if e["freq"]]
    grid_data = [(e["grid"], e["error"], e["timestamp"])
                 for e in entries if e["grid"]]

    return {
        "fix_count": fix_count,
        "lob_count": lob_count,
        "timestamps": timestamps,
        "freqs": freqs,
        "grid_data": grid_data,
    }


def ensure_analytics_dir() -> Path:
    ts = datetime.now().strftime(DATE_FORMAT)
    dir_path = ANALYTICS_DIR / ts
    dir_path.mkdir(parents=True, exist_ok=True)
    print(f"[INFO] Analytics directory: {dir_path}")
    return dir_path


def plot_results(stats, out_dir: Path):
    print("[INFO] Generating visualizations...")

    # Detection type summary
    plt.figure()
    plt.bar(["FIX", "3 LOB"], [stats["fix_count"], stats["lob_count"]])
    plt.title("Detection Type Counts")
    plt.xlabel("Detection Type")
    plt.ylabel("Occurrences")
    plt.tight_layout()
    plt.savefig(out_dir / "detection_summary.png")
    plt.close()

    # Detections over time
    if stats["timestamps"]:
        plt.figure()
        plt.hist(stats["timestamps"], bins=30)
        plt.title("Detections Over Time")
        plt.xlabel("Timestamp")
        plt.ylabel("Count")
        plt.tight_layout()
        plt.savefig(out_dir / "detections_timeline.png")
        plt.close()

    # Frequencies targeted
    if stats["freqs"]:
        plt.figure()
        plt.hist(stats["freqs"], bins=20)
        plt.title("Frequencies Targeted")
        plt.xlabel("Frequency (MHz)")
        plt.ylabel("Count")
        plt.tight_layout()
        plt.savefig(out_dir / "frequencies_targeted.png")
        plt.close()

    print("[INFO] Saved plots to:", out_dir)


def save_grid_data_csv(grid_data, out_dir: Path):
    if not grid_data:
        print("[WARN] No grid data found for CSV export.")
        return

    csv_path = out_dir / "grid_errors.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Grid", "Error", "Timestamp"])
        for grid, err, ts in grid_data:
            writer.writerow([grid, err if err is not None else "", ts])
    print(f"[INFO] Saved grid error data: {csv_path}")


def main():
    latest_zip = find_latest_archive()
    extract_archive(latest_zip, EXTRACT_DIR)

    log_files = find_target_logs(EXTRACT_DIR)
    if not log_files:
        print("[WARN] No targeting.log files found in archive.")
        return

    print(f"[INFO] Found {len(log_files)} targeting.log files")

    all_entries = []
    for log in log_files:
        all_entries.extend(parse_targeting_log(log))
    all_entries.sort(key=lambda x: x["timestamp"])

    print(f"[INFO] Parsed {len(all_entries)} total log entries")
    if all_entries:
        print(f"[INFO] Time range: {all_entries[0]['timestamp']} → {all_entries[-1]['timestamp']}")

    stats = analyze_entries(all_entries)
    out_dir = ensure_analytics_dir()
    plot_results(stats, out_dir)
    save_grid_data_csv(stats["grid_data"], out_dir)

    # Cleanup temp folder
    if EXTRACT_DIR.exists():
        shutil.rmtree(EXTRACT_DIR)
        print(f"[INFO] Removed temporary directory: {EXTRACT_DIR}")

    print("[INFO] Analysis complete.")


if __name__ == "__main__":
    main()
