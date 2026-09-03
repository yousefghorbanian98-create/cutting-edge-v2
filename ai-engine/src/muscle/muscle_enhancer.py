import argparse
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
from dataclasses import dataclass

@dataclass
class EnhancementSettings:
    intensity: float = 0.6
    muscle_contrast: float = 0.7
    dodge_burn_strength: float = 0.5
    protect_face: bool = True

class MuscleEnhancer:
    """Subtle, frame-local contrast enhancement; never changes body geometry."""
    def enhance_frame(self, frame: np.ndarray, settings: Optional[EnhancementSettings] = None) -> np.ndarray:
        s = settings or EnhancementSettings()
        if s.intensity <= 0:
            return frame
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        lightness, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=max(.1, 2.5 * s.muscle_contrast), tileGridSize=(8, 8))
        enhanced = cv2.cvtColor(cv2.merge([clahe.apply(lightness), a, b]), cv2.COLOR_LAB2BGR)
        return cv2.addWeighted(frame, 1 - s.intensity, enhanced, s.intensity, 0)

def enhance_video(input_path: Path, output_path: Path, intensity: float = .6) -> None:
    reader = cv2.VideoCapture(str(input_path))
    if not reader.isOpened():
        raise FileNotFoundError(f'Could not open video: {input_path}')
    width, height = int(reader.get(cv2.CAP_PROP_FRAME_WIDTH)), int(reader.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = reader.get(cv2.CAP_PROP_FPS) or 30.0
    frames = int(reader.get(cv2.CAP_PROP_FRAME_COUNT))
    writer = cv2.VideoWriter(str(output_path), cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))
    enhancer = MuscleEnhancer()
    try:
        while True:
            ok, frame = reader.read()
            if not ok:
                break
            writer.write(enhancer.enhance_frame(frame, EnhancementSettings(intensity=intensity)))
    finally:
        reader.release()
        writer.release()
    print(f'Wrote {output_path} ({frames} frames, {width}x{height} at {fps:.1f} fps)')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create a natural muscle-enhancement preview')
    parser.add_argument('input', nargs='?', default='test_workout.mp4')
    parser.add_argument('-o', '--output', default='test_workout_enhanced.mp4')
    parser.add_argument('--intensity', type=float, default=.6)
    args = parser.parse_args()
    enhance_video(Path(args.input), Path(args.output), max(0, min(1, args.intensity)))
