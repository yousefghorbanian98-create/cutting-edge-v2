"""One-Click Viral Cut — Finds the best segment for Reels/Shorts"""
import numpy as np
from typing import List, Tuple

class ViralCutFinder:
    def find_best_segment(
        self,
        motion_energies: List[float],
        fps: float = 30.0,
        target_duration_sec: int = 30
    ) -> Tuple[int, int]:
        """
        پیدا کردن پرانرژی‌ترین بخش ویدیو
        Edge cases:
        - ویدیو کوتاه‌تر از target → کل ویدیو
        - ویدیو بدون حرکت → وسط ویدیو
        - fps صفر → fallback
        """
        n = len(motion_energies)
        if n == 0:
            return (0, 0)

        effective_fps = max(fps, 1.0)
        window_size = int(effective_fps * target_duration_sec)

        # اگر ویدیو کوتاه‌تر از پنجره است → کل ویدیو
        if n <= window_size:
            return (0, n)

        # اگر همه انرژی‌ها صفر هستند → وسط ویدیو
        if max(motion_energies) == 0:
            mid = n // 2
            half = window_size // 2
            return (max(0, mid - half), min(n, mid + half))

        # Moving window sum
        energies = np.array(motion_energies, dtype=np.float32)
        kernel = np.ones(window_size, dtype=np.float32)
        sums = np.convolve(energies, kernel, mode='valid')

        if len(sums) == 0:
            return (0, n)

        best_start = int(np.argmax(sums))
        best_end = min(best_start + window_size, n)

        return (best_start, best_end)

    def calculate_virality_score(
        self,
        energies: List[float],
        start: int,
        end: int,
        fps: float = 30.0
    ) -> dict:
        """محاسبه امتیاز وایرال بر اساس بخش انتخاب‌شده"""
        if not energies:
            return {"score": 50, "hook": 0, "sustain": 0}

        segment = energies[start:end]
        if not segment:
            return {"score": 50, "hook": 0, "sustain": 0}

        # Hook: انرژی ۳ ثانیه اول
        hook_frames = min(int(fps * 3), len(segment))
        hook_energy = float(np.mean(segment[:hook_frames])) if hook_frames > 0 else 0

        # Sustain: انرژی کل بخش
        sustain_energy = float(np.mean(segment))

        # Variance: تنوع (خیلی یکنواخت = خسته‌کننده)
        variance = float(np.std(segment))

        # Score calculation
        score = 40
        score += min(hook_energy * 40, 25)      # قلاب قوی = +25
        score += min(sustain_energy * 30, 20)    # انرژی پایدار = +20
        score += min(variance * 50, 15)          # تنوع = +15

        return {
            "score": min(98, max(15, int(score))),
            "hook": round(hook_energy, 2),
            "sustain": round(sustain_energy, 2),
            "variance": round(variance, 2)
        }
