"""Emotion Color Engine — Auto color grading based on scene intensity"""
import cv2
import numpy as np

class EmotionColorEngine:
    PALETTES = {
        "intense": np.array([1.1, 0.95, 0.9]),   # Warm / High-contrast
        "calm":    np.array([0.95, 1.0, 1.1]),   # Cool / Soft
        "pump":    np.array([1.15, 1.05, 0.85]), # Golden / Saturated
    }

    def grade_frame(self, frame: np.ndarray, emotion_tag: str = "intense") -> np.ndarray:
        multipliers = self.PALETTES.get(emotion_tag, np.array([1.0, 1.0, 1.0]))
        f = frame.astype(np.float32)
        f[:, :, 0] = np.clip(f[:, :, 0] * multipliers[2], 0, 255) # B
        f[:, :, 1] = np.clip(f[:, :, 1] * multipliers[1], 0, 255) # G
        f[:, :, 2] = np.clip(f[:, :, 2] * multipliers[0], 0, 255) # R
        return f.astype(np.uint8)
