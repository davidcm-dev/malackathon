"""Pixel-based spin detection: motion => the game reacted; stillness => the spin settled."""
from __future__ import annotations

import io
import time
from dataclasses import dataclass
from typing import Callable

import numpy as np
from PIL import Image

Region = tuple[float, float, float, float]  # left, top, width, height as fractions


def _signature(img: bytes, r: Region) -> np.ndarray:
    im = Image.open(io.BytesIO(img)).convert("L")
    w, h = im.size
    box = (int(w * r[0]), int(h * r[1]), int(w * (r[0] + r[2])), int(h * (r[1] + r[3])))
    return np.asarray(im.crop(box).resize((128, 72)), dtype=np.float32)


def _diff(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.abs(a - b).mean() / 255.0)


@dataclass
class SpinObservation:
    started: bool
    settled: bool
    peak_motion: float
    noise_floor: float
    duration_ms: int
    started_frame: bytes | None = None
    final_frame: bytes | None = None


def observe_spin(grab: Callable[[], bytes], trigger: Callable[[], None], region: Region = (0.08, 0.08, 0.84, 0.68),
                 timeout_s: float = 45, still_s: float = 1.5, no_start_s: float = 6) -> SpinObservation:
    prev = grab()
    prev_sig = _signature(prev, region)
    noise = 0.0
    for _ in range(4):                       # idle noise floor (ambient animations)
        time.sleep(0.15)
        prev = grab()
        s = _signature(prev, region)
        noise = max(noise, _diff(prev_sig, s))
        prev_sig = s
    start_thr, still_thr = max(0.03, noise * 5), max(0.006, noise * 2)

    t0 = time.time()
    trigger()
    started = settled = False
    peak, moving, still_since, started_frame = 0.0, 0, 0.0, None
    while time.time() - t0 < timeout_s:
        time.sleep(0.12)
        prev = grab()
        s = _signature(prev, region)
        d = _diff(prev_sig, s)
        prev_sig = s
        peak = max(peak, d)
        if not started:
            if d > start_thr:
                moving += 1
                if moving >= 2:
                    started, started_frame = True, prev
            else:
                moving = 0
            if time.time() - t0 > no_start_s:
                break
        elif d < still_thr:
            still_since = still_since or time.time()
            if time.time() - still_since >= still_s:
                settled = True
                break
        else:
            still_since = 0.0
    return SpinObservation(started, settled, peak, noise, int((time.time() - t0) * 1000), started_frame, prev)
