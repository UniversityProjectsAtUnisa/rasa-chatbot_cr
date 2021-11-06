#!/usr/bin/python3
import json
from pathlib import Path

stories_results = "results/story_report.json"

errors = "errors/LUT.txt"
Path(errors).parent.mkdir(parents=True, exist_ok=True)

with open(stories_results) as jsonfile, open(errors, "w") as txtfile:
    report = json.load(jsonfile)
    for k, v in report.items():
        if "[" in str(k) and (v.get("precision", 1.0) != 1.0 or v.get("recall", 1.0) != 1.0):
            txtfile.write(f"{k}\n")
