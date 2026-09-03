import cv2
import numpy as np
from dataclasses import dataclass
from typing import List

@dataclass
class MoodDNA:
    avg_energy: float
    color_mood: str
    cut_rhythm_avg: float
    style_tags: List[str]

class MoodDNAExtractor:
    def extract(self, video_path: str) -> MoodDNA:
        cap, energies = cv2.VideoCapture(video_path), []
        while cap.isOpened():
            ok, frame = cap.read()
            if not ok: break
            energies.append(float(np.std(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)) / 128))
        cap.release()
        energy = float(np.mean(energies)) if energies else .5
        return MoodDNA(energy, 'dark-moody' if energy > .4 else 'bright-clean', 2.5, ['gym', 'cinematic'])
