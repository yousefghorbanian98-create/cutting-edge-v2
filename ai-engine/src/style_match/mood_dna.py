"""Mood DNA Extraction — Visual DNA of a video"""
import json
import numpy as np
from dataclasses import dataclass, asdict
from typing import List
from ..analyzer.video_analyzer import VideoAnalyzer

@dataclass
class MoodDNA:
    avg_energy: float
    energy_variance: float
    color_mood: str
    dominant_palette: List[str]
    color_temperature: float
    cut_rhythm_avg: float
    bpm: float
    camera_angles: dict
    motion_style: str
    lighting_style: str
    avg_brightness: float
    contrast_level: float
    transition_dna: dict
    emotional_arc: str
    style_tags: List[str]
    match_score: float = 0.0

class MoodDNAExtractor:
    def __init__(self):
        self.analyzer = VideoAnalyzer()

    def extract(self, video_path: str) -> MoodDNA:
        analysis = self.analyzer.analyze(video_path)
        energies = [f.motion_intensity for f in analysis.frames]
        avg_e = float(np.mean(energies)) if energies else 0.5
        var_e = float(np.var(energies)) if energies else 0.0
        avg_b = analysis.avg_brightness
        palette_hex = [f"#{c[0]:02x}{c[1]:02x}{c[2]:02x}" for c in analysis.color_palette]
        temp = float((analysis.color_palette[0][2] - analysis.color_palette[0][0]) / 255) if analysis.color_palette else 0
        tags = []
        if avg_e > 0.5: tags.append("high-energy")
        if avg_b < 0.3: tags.append("dark-moody")
        else: tags.append("bright-clean")
        tags.append("gym-workout")
        return MoodDNA(
            avg_energy=avg_e, energy_variance=var_e,
            color_mood="dark-moody" if avg_b < 0.3 else "bright-clean",
            dominant_palette=palette_hex, color_temperature=temp,
            cut_rhythm_avg=2.5, bpm=120.0,
            camera_angles={"close-up":0.4,"medium":0.35,"wide":0.25},
            motion_style="fast" if avg_e > 0.6 else "realtime",
            lighting_style="dramatic" if avg_b < 0.3 else "natural",
            avg_brightness=avg_b, contrast_level=0.6,
            transition_dna={"cut":0.7,"whip":0.2,"fade":0.1},
            emotional_arc="tension-release" if var_e > 0.1 else "flat",
            style_tags=tags
        )

    def calculate_match(self, dna1: MoodDNA, dna2: MoodDNA) -> float:
        scores = []
        scores.append((1 - abs(dna1.avg_energy - dna2.avg_energy)) * 25)
        scores.append((1 - abs(dna1.color_temperature - dna2.color_temperature)) * 25)
        scores.append((1 - abs(dna1.avg_brightness - dna2.avg_brightness)) * 20)
        scores.append((1 - abs(dna1.contrast_level - dna2.contrast_level)) * 15)
        scores.append((1 - min(abs(dna1.cut_rhythm_avg - dna2.cut_rhythm_avg)/5, 1)) * 15)
        score = round(sum(scores), 1)
        dna2.match_score = score
        return score

    def save(self, dna: MoodDNA, path: str):
        with open(path, "w") as f:
            json.dump(asdict(dna), f, indent=2)
