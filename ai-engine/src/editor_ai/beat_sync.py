"""Beat Sync Engine — FFmpeg-first audio extraction + beat detection (S-004)."""
import os
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple

from ai_engine.core.ffmpeg import extract_audio, FFmpegNotFoundError

@dataclass
class BeatMarker:
    time: float
    strength: float
    is_downbeat: bool

class BeatSyncEngine:
    def __init__(self):
        self.beats: List[BeatMarker] = []
        self.tempo_bpm: float = 120.0

    def extract_audio_from_video(self, video_path: str) -> str:
        """استخراج صدا از ویدیو با FFmpeg (اولویت اصلی) و MoviePy 2 (fallback)."""
        audio_path = video_path.rsplit(".", 1)[0] + "_audio.wav"
        if os.path.exists(audio_path):
            return audio_path
        if not os.path.exists(video_path):
            return ""
        try:
            return extract_audio(video_path, audio_path, sample_rate=22050, mono=True)
        except (FFmpegNotFoundError, RuntimeError) as e:
            print(f"Audio extraction failed: {e}")
            return ""

    def analyze_audio(self, audio_or_video_path: str) -> List[BeatMarker]:
        """تحلیل ضرب — اگر MP4 باشد، ابتدا صدا را استخراج می‌کند"""
        path = audio_or_video_path

        # اگر ویدیو است، صدا را استخراج کن (FFmpeg-first؛ MoviePy fallback)
        ext = path.rsplit(".", 1)[-1].lower() if "." in path else ""
        if ext in ("mp4", "mov", "avi", "mkv", "webm"):
            path = self.extract_audio_from_video(path)
            if not path:
                print("No audio track found.")
                self.beats = []
                self.tempo_bpm = 0.0
                return self.beats

        try:
            import librosa
        except ImportError:
            print("librosa not installed.")
            self.beats = []
            self.tempo_bpm = 0.0
            return self.beats

        try:
            y, sr = librosa.load(path, sr=22050, mono=True)
        except Exception as e:
            print(f"librosa.load failed: {e}")
            self.beats = []
            self.tempo_bpm = 0.0
            return self.beats

        # Silence / too short → genuinely no beats (BUG-4 real test expects []).
        if len(y) < sr * 0.5 or float(np.max(np.abs(y))) < 1e-6:
            self.beats = []
            self.tempo_bpm = 0.0
            return self.beats

        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        tempo_val = float(np.atleast_1d(tempo)[0])
        # librosa may return NaN/degenerate tempo for silent input.
        if not np.isfinite(tempo_val) or tempo_val <= 0:
            self.beats = []
            self.tempo_bpm = 0.0
            return self.beats
        beat_times = librosa.frames_to_time(beat_frames, sr=sr)
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)

        self.tempo_bpm = tempo_val
        max_onset = float(np.max(onset_env)) if len(onset_env) > 0 else 1.0

        self.beats = []
        for i, t in enumerate(beat_times):
            fi = min(int(t * sr / 512), len(onset_env) - 1)
            strength = float(onset_env[max(fi, 0)]) / max_onset if max_onset > 0 else 0.5
            self.beats.append(BeatMarker(
                time=float(t),
                strength=min(max(strength, 0.0), 1.0),
                is_downbeat=(i % 4 == 0)
            ))

        # پاکسازی فایل صوتی موقت
        if path != audio_or_video_path and os.path.exists(path):
            try:
                os.remove(path)
            except:
                pass

        return self.beats

    def sync_clips(self, clip_durations: List[float]) -> List[Tuple[float, float]]:
        if not self.beats:
            return []
        cuts = []
        bi = 0
        for dur in clip_durations:
            start = self.beats[bi].time
            target = start + dur
            ei = bi + 1
            while ei < len(self.beats) - 1 and self.beats[ei + 1].time < target:
                ei += 1
            cuts.append((start, self.beats[ei].time))
            bi = min(ei, len(self.beats) - 1)
        return cuts
