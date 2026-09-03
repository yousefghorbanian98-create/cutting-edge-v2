"""Beat Sync Engine — Auto-cut on music beats"""
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class BeatMarker:
    time: float
    strength: float
    is_downbeat: bool

class BeatSyncEngine:
    def __init__(self):
        self.beats: List[BeatMarker] = []
        self.tempo_bpm: float = 120.0

    def analyze_audio(self, audio_path: str) -> List[BeatMarker]:
        try:
            import librosa
        except ImportError:
            print("librosa not installed. Returning dummy beats.")
            self.beats = [BeatMarker(i*0.5, 0.8, i%4==0) for i in range(20)]
            return self.beats
        y, sr = librosa.load(audio_path, sr=22050)
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        beat_times = librosa.frames_to_time(beat_frames, sr=sr)
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        self.tempo_bpm = float(tempo) if hasattr(tempo, '__float__') else 120.0
        self.beats = []
        max_onset = np.max(onset_env) if len(onset_env) > 0 else 1
        for i, t in enumerate(beat_times):
            fi = min(int(t * sr / 512), len(onset_env) - 1)
            strength = float(onset_env[fi]) / max_onset if fi >= 0 else 0.5
            self.beats.append(BeatMarker(float(t), min(strength, 1.0), i % 4 == 0))
        return self.beats

    def sync_clips(self, clip_durations: List[float]) -> List[Tuple[float, float]]:
        if not self.beats: return []
        cuts = []
        bi = 0
        for dur in clip_durations:
            start = self.beats[bi].time
            target = start + dur
            ei = bi + 1
            while ei < len(self.beats) - 1 and self.beats[ei + 1].time < target:
                ei += 1
            cuts.append((start, self.beats[ei].time))
            bi = ei
        return cuts
