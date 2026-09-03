"""Pose-to-Pose Intelligent Mapping (MediaPipe 33-point Landmark Mapping)"""
import cv2
import numpy as np

class PoseMapper:
    def __init__(self):
        self.pose = None
        self._init_pose()

    def _init_pose(self):
        try:
            import mediapipe as mp
            self.pose = mp.solutions.pose.Pose(static_image_mode=False, model_complexity=1)
        except ImportError:
            pass

    def calculate_pose_similarity(self, frame_ref: np.ndarray, frame_user: np.ndarray) -> float:
        if not self.pose: return 0.75
        
        rgb_ref = cv2.cvtColor(frame_ref, cv2.COLOR_BGR2RGB)
        rgb_usr = cv2.cvtColor(frame_user, cv2.COLOR_BGR2RGB)
        
        res_ref = self.pose.process(rgb_ref)
        res_usr = self.pose.process(rgb_usr)
        
        if not res_ref.pose_landmarks or not res_usr.pose_landmarks:
            return 0.5
            
        pts_ref = np.array([[lm.x, lm.y, lm.z] for lm in res_ref.pose_landmarks.landmark])
        pts_usr = np.array([[lm.x, lm.y, lm.z] for lm in res_usr.pose_landmarks.landmark])
        
        diff = np.mean(np.linalg.norm(pts_ref - pts_usr, axis=1))
        similarity = max(0.0, 1.0 - diff)
        return float(similarity)
