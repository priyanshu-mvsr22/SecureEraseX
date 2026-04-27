"""
logging.py
Append-only structured event log.
"""

import json
import datetime
import os

LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "secureerasex.log")


def log_event(event: str, details: dict):
    entry = {
        "time":    datetime.datetime.now().isoformat(),
        "event":   event,
        "details": details,
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
