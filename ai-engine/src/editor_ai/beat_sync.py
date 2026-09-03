"""Beat Sync Engine — Real audio extraction + beat detection"""
import os
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

    def extract_audio_from_video(self, video_path: str) -> str:
        """استخراج صدا از ویدیو با moviepy (حل باگ MP4)"""
        audio_path = video_path.rsplit(".", 1)[0] + "_audio.wav"
        if os.path.exists(audio_path):
            return audio_path
        try:
            from moviepy.editor import VideoFileClip
            clip = VideoFileClip(video_path)
            if clip.audio is None:
                clip.close()
                return ""
            clip.audio.write_audiofile(audio_path, fps=22050, nbytes=2, verbose=False, logger=None)
            clip.close()
            return audio_path
        except Exception as e:
            print(f"Audio extraction failed: {e}")
            return ""

    def analyze_audio(self, audio_or_video_path: str) -> List[BeatMarker]:
        """تحلیل ضرب — اگر MP4 باشد، ابتدا صدا را استخراج می‌کند"""
        path = audio_or_video_path

        # اگر ویدیو است، صدا را استخراج کن
        ext = path.rsplit(".", 1)[-1].lower() if "." in path else ""
        if ext in ("mp4", "mov", "avi", "mkv", "webm"):
            path = self.extract_audio_from_video(path)
            if not path:
                print("No audio track found. Generating dummy beats.")
                self.beats = [BeatMarker(i * 0.5, 0.7, i % 4 == 0) for i in range(20)]
                self.tempo_bpm = 120.0
                return self.beats

        try:
            import librosa
        except ImportError:
            print("librosa not installed. Dummy beats.")
            self.beats = [BeatMarker(i * 0.5, 0.7, i % 4 == 0) for i in range(20)]
            return self.beats

        try:
            y, sr = librosa.load(path, sr=22050, mono=True)
        except Exception as e:
            print(f"librosa.load failed: {e}")
            self.beats = [BeatMarker(i * 0.5, 0.7, i % 4 == 0) for i in range(20)]
            return self.beats

        if len(y) < sr:  # کمتر از ۱ ثانیه
            self.beats = [BeatMarker(0, 0.8, True)]
            return self.beats

        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        beat_times = librosa.frames_to_time(beat_frames, sr=sr)
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)

        self.tempo_bpm = float(tempo) if np.isscalar(tempo) else float(tempo[0])
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
