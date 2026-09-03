"""Frame-by-frame video analyzer for Style Match"""
import cv2
import numpy as np
from dataclasses import dataclass, field
from typing import List

@dataclass
class FrameData:
    frame_number: int
    timestamp: float
    brightness: float = 0.0
    motion_intensity: float = 0.0
    dominant_color: tuple = (0,0,0)
    pose_detected: bool = False
    face_detected: bool = False

@dataclass
class VideoAnalysis:
    duration: float
    fps: float
    width: int
    height: int
    total_frames: int
    avg_brightness: float
    avg_motion: float
    color_palette: List[tuple]
    frames: List[FrameData] = field(default_factory=list)

class VideoAnalyzer:
    def analyze(self, video_path: str, sample_rate: int = 5) -> VideoAnalysis:
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frames_data = []
        prev_gray = None
        colors = []
        idx = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            if idx % sample_rate == 0:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                brightness = np.mean(gray) / 255.0
                motion = 0.0
                if prev_gray is not None:
                    diff = cv2.absdiff(gray, prev_gray)
                    motion = np.mean(diff) / 255.0
                prev_gray = gray
                small = cv2.resize(frame, (10, 10))
                dc = tuple(int(c) for c in np.mean(small.reshape(-1,3), axis=0))
                colors.append(dc)
                frames_data.append(FrameData(
                    frame_number=idx, timestamp=idx/fps,
                    brightness=brightness, motion_intensity=motion,
                    dominant_color=dc
                ))
            idx += 1
        cap.release()
        avg_b = np.mean([f.brightness for f in frames_data]) if frames_data else 0
        avg_m = np.mean([f.motion_intensity for f in frames_data]) if frames_data else 0
        palette = list(set(colors))[:5] if colors else [(0,0,0)]
        return VideoAnalysis(
            duration=total/fps, fps=fps, width=w, height=h,
            total_frames=total, avg_brightness=float(avg_b),
            avg_motion=float(avg_m), color_palette=palette, frames=frames_data
        )
