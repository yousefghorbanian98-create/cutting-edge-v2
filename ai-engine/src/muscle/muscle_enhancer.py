"""
Muscle Enhancer AI — Natural muscle definition for video
100% natural | No body reshaping | GTX 1650 Compatible
Usage: python muscle_enhancer.py input.mp4 --output out.mp4 --intensity 0.7
"""
import cv2
import numpy as np
import argparse
import sys
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class EnhancementSettings:
    intensity: float = 0.6
    muscle_contrast: float = 0.7
    muscle_contrast_clip: float = 2.5
    dodge_burn_strength: float = 0.5
    dodge_burn_radius: int = 15
    edge_sharpness: float = 0.6
    edge_threshold: int = 30
    skin_texture: float = 0.4
    midtone_sculpt: float = 0.5
    protect_face: bool = True

PRESETS = {
    "competition": EnhancementSettings(0.8, 0.85, 3.0, 0.7, 15, 0.75, 25, 0.5, 0.7),
    "natural_gym": EnhancementSettings(0.4, 0.5, 2.0, 0.3, 15, 0.4, 30, 0.3, 0.3),
    "cinematic":   EnhancementSettings(0.6, 0.6, 2.5, 0.7, 15, 0.5, 30, 0.4, 0.6),
    "instagram":   EnhancementSettings(0.5, 0.6, 2.5, 0.4, 15, 0.7, 25, 0.2, 0.4),
}

class MuscleEnhancer:
    def __init__(self):
        self.pose = None
        self.face_mesh = None
        self._init_mediapipe()

    def _init_mediapipe(self):
        try:
            import mediapipe as mp
            self.pose = mp.solutions.pose.Pose(model_complexity=1, min_detection_confidence=0.5)
            self.face_mesh = mp.solutions.face_mesh.FaceMesh(max_num_faces=1, min_detection_confidence=0.5)
        except ImportError:
            print("Warning: mediapipe not installed. Face protection disabled.")

    def enhance_frame(self, frame: np.ndarray, s: Optional[EnhancementSettings] = None) -> np.ndarray:
        s = s or EnhancementSettings()
        if s.intensity == 0:
            return frame
        result = frame.copy()
        h, w = result.shape[:2]
        body_mask = self._create_body_mask(result, h, w)

        # 1. Muscle-Aware CLAHE
        lab = cv2.cvtColor(result, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clip = s.muscle_contrast_clip * s.muscle_contrast
        clahe_strong = cv2.createCLAHE(clipLimit=max(1.0, clip), tileGridSize=(8, 8))
        clahe_mild = cv2.createCLAHE(clipLimit=1.2, tileGridSize=(8, 8))
        l_strong = clahe_strong.apply(l)
        l_mild = clahe_mild.apply(l)
        l_final = (l_strong * body_mask + l_mild * (1 - body_mask)).astype(np.uint8)
        result = cv2.cvtColor(cv2.merge([l_final, a, b]), cv2.COLOR_LAB2BGR)

        # 2. Dodge & Burn
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).astype(np.float32)
        blurred = cv2.GaussianBlur(gray, (s.dodge_burn_radius*2+1, s.dodge_burn_radius*2+1), s.dodge_burn_radius)
        detail = gray - blurred
        dodge = np.clip(detail * s.dodge_burn_strength * 0.5, 0, 30)
        burn = np.clip(-detail * s.dodge_burn_strength * 0.3, 0, 20)
        db = np.stack([dodge - burn] * 3, axis=-1) * np.stack([body_mask]*3, axis=-1)
        result = np.clip(result.astype(np.float32) + db, 0, 255).astype(np.uint8)

        # 3. Edge-Aware Sharpening
        blurred_sharp = cv2.GaussianBlur(result, (0, 0), 3)
        sharpened = cv2.addWeighted(result, 1.0 + s.edge_sharpness, blurred_sharp, -s.edge_sharpness, 0)
        edges = cv2.Canny(cv2.cvtColor(result, cv2.COLOR_BGR2GRAY), s.edge_threshold, s.edge_threshold*3)
        edge_mask = cv2.GaussianBlur(edges, (5, 5), 1.5) / 255.0 * body_mask
        em3 = np.stack([edge_mask]*3, axis=-1)
        result = (result * (1 - em3) + sharpened * em3).astype(np.uint8)

        # 4. Midtone Sculpting
        gray2 = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY).astype(np.float32)
        mid_mask = np.exp(-((gray2 - 128)**2) / (2 * 40**2)) * body_mask * s.midtone_sculpt
        mid3 = np.stack([mid_mask]*3, axis=-1)
        result = np.clip(result.astype(np.float32) + (result.astype(np.float32) - 128) * mid3 * 0.3, 0, 255).astype(np.uint8)

        # 5. Face Protection
        if s.protect_face and self.face_mesh:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            fr = self.face_mesh.process(rgb)
            if fr.multi_face_landmarks:
                fm = np.zeros((h, w), dtype=np.float32)
                pts = []
                for idx in [10,338,297,332,284,251,389,356,454,323,361,288,397,365,379,378,400,377,152,148,176,149,150,136,172,58,132,93,234,127,162,21,54,103]:
                    lm = fr.multi_face_landmarks[0].landmark[idx]
                    pts.append([int(lm.x*w), int(lm.y*h)])
                cv2.fillConvexPoly(fm, np.array(pts, np.int32), 1.0)
                fm = cv2.GaussianBlur(fm, (61, 61), 20)
                fm3 = np.stack([fm]*3, axis=-1)
                result = (frame * fm3 + result * (1 - fm3)).astype(np.uint8)

        # Final blend
        return cv2.addWeighted(frame, 1.0 - s.intensity, result, s.intensity, 0)

    def _create_body_mask(self, frame, h, w):
        mask = np.ones((h, w), dtype=np.float32) * 0.3
        if not self.pose:
            return mask
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = self.pose.process(rgb)
        if not res.pose_landmarks:
            return mask
        lm = res.pose_landmarks.landmark
        regions = [
            (11,13,15,0.06),(12,14,16,0.06),
            (11,12,23,0.12),(12,23,24,0.12),
            (23,25,27,0.07),(24,26,28,0.07),
        ]
        for p1,p2,p3,r in regions:
            pts = np.array([[int(lm[p1].x*w),int(lm[p1].y*h)],
                           [int(lm[p2].x*w),int(lm[p2].y*h)],
                           [int(lm[p3].x*w),int(lm[p3].y*h)]], np.int32)
            cv2.fillConvexPoly(mask, pts, 1.0)
            for s,e in [(p1,p2),(p2,p3)]:
                cv2.line(mask,(int(lm[s].x*w),int(lm[s].y*h)),(int(lm[e].x*w),int(lm[e].y*h)),1.0,int(r*w))
        return cv2.GaussianBlur(mask, (31, 31), 10)

    def enhance_video(self, input_path, output_path, settings=None):
        if not os.path.exists(input_path):
            print(f"Error: {input_path} not found"); return
        cap = cv2.VideoCapture(input_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))
        idx = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            out.write(self.enhance_frame(frame, settings))
            idx += 1
            if idx % 30 == 0:
                print(f"  Processing: {idx}/{total} ({idx/total*100:.0f}%)")
        cap.release(); out.release()
        print(f"Done: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Muscle Enhancer AI")
    parser.add_argument("input", nargs="?", default="test_workout.mp4")
    parser.add_argument("--output", "-o", default=None)
    parser.add_argument("--intensity", "-i", type=float, default=0.6)
    parser.add_argument("--preset", "-p", choices=PRESETS.keys(), default=None)
    args = parser.parse_args()
    output = args.output or args.input.replace(".mp4", "_enhanced.mp4")
    settings = PRESETS.get(args.preset, EnhancementSettings(intensity=args.intensity))
    enhancer = MuscleEnhancer()
    enhancer.enhance_video(args.input, output, settings)
