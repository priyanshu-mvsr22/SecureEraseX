"""
report.py
Save wipe reports as JSON and CSV.
"""

import json
import csv
import datetime
import os

REPORT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def save_report(data: dict):
    data = dict(data)   # copy
    data["timestamp"] = datetime.datetime.now().isoformat()

    json_path = os.path.join(REPORT_DIR, "recycling_report.json")
    csv_path  = os.path.join(REPORT_DIR, "recycling_report.csv")

    with open(json_path, "w") as f:
        json.dump(data, f, indent=4)

    with open(csv_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(data.keys())
        w.writerow(data.values())
