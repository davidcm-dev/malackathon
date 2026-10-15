"""Per scenario+market pass/fail log (JSONL) and screenshot evidence."""
from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone

RESULTS = "results"


def record(scenario: str, market: str, status: str, name: str, detail: str = "") -> None:
    os.makedirs(RESULTS, exist_ok=True)
    with open(f"{RESULTS}/checks-{market}.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps({"scenario": scenario, "market": market, "status": status, "name": name,
                            "detail": detail, "ts": datetime.now(timezone.utc).isoformat()}) + "\n")


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


class Checks:
    """Soft assertions: every check is logged; assert_all() fails the test at the end if any failed."""

    def __init__(self, scenario: str, market: str):
        self.scenario, self.market, self.failures = scenario, market, []

    def check(self, name: str, ok: bool, detail: str = "") -> None:
        record(self.scenario, self.market, "pass" if ok else "fail", name, detail)
        print(f"[{'PASS' if ok else 'FAIL'}] {name} - {detail}")
        if not ok:
            self.failures.append(f"{name} - {detail}")

    def info(self, name: str, detail: str = "") -> None:
        record(self.scenario, self.market, "info", name, detail)
        print(f"[INFO] {name} - {detail}")

    def assert_all(self) -> None:
        assert not self.failures, "Failed checks:\n  " + "\n  ".join(self.failures)


class Evidence:
    def __init__(self, market: str, scenario: str):
        self.dir = f"{RESULTS}/evidence/{market}/{slug(scenario)}"
        os.makedirs(self.dir, exist_ok=True)
        self.n = 0

    def snap(self, name: str, data: bytes) -> None:
        self.n += 1
        with open(f"{self.dir}/{self.n:02d}-{name}.png", "wb") as f:
            f.write(data)
