"""Reheal Loop — Pipeline Validator"""
import os, cv2, numpy as np
from dataclasses import dataclass

@dataclass
class ValidationResult:
    valid: bool; stage: str; message: str; auto_fixed: bool = False

class PipelineValidator:
    def validate_input(self, path: str) -> ValidationResult:
        if not os.path.exists(path): return ValidationResult(False,"input","File not found")
        if os.path.getsize(path) == 0: return ValidationResult(False,"input","Empty file")
        cap = cv2.VideoCapture(path)
        if not cap.isOpened(): return ValidationResult(False,"input","Cannot open")
        fps = cap.get(cv2.CAP_PROP_FPS); frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        cap.release()
        if fps <= 0 or frames <= 0: return ValidationResult(False,"input","Bad metadata")
        return ValidationResult(True,"input","OK")

    def validate_frame(self, frame) -> ValidationResult:
        if frame is None or frame.size == 0: return ValidationResult(False,"frame","Empty")
        if np.all(frame == 0): return ValidationResult(False,"frame","All black")
        return ValidationResult(True,"frame","OK")

    def validate_output(self, path: str) -> ValidationResult:
        if not os.path.exists(path): return ValidationResult(False,"output","Not created")
        if os.path.getsize(path) < 1024: return ValidationResult(False,"output","Too small")
        cap = cv2.VideoCapture(path)
        ok = cap.isOpened(); cap.release()
        return ValidationResult(ok,"output","OK" if ok else "Not playable")
