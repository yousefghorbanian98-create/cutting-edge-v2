"""One-Click Viral Cut — Finds the best 30s for Reels / Shorts"""
import numpy as np
from typing import List, Tuple

class ViralCutFinder:
    def find_best_segment(self, motion_energies: List[float], fps: float = 30.0, target_duration_sec: int = 30) -> Tuple[int, int]:
        window_size = int(fps * target_duration_sec)
        if len(motion_energies) <= window_size:
            return 0, len(motion_energies)
            
        # Moving window sum of motion energies
        sums = np.convolve(motion_energies, np.ones(window_size), mode='valid')
        best_start = int(np.argmax(sums))
        return best_start, best_start + window_size
