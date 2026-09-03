"""Workout Form Analyzer — Pose depth and posture evaluation"""
from typing import Dict, Any

class FormAnalyzer:
    def evaluate_squat(self, knee_angle: float, back_angle: float) -> Dict[str, Any]:
        score = 100
        feedback = []
        
        if knee_angle > 110:
            score -= 25
            feedback.append("عمق اسکات ناکافی است (پایین‌تر بروید)")
        if back_angle > 45:
            score -= 30
            feedback.append("خمیدگی بیش از حد در ستون فقرات")
            
        return {
            "score": max(20, score),
            "feedback": feedback if feedback else ["فرم حرکت عالی و بی‌نقص است!"],
            "is_valid": score >= 70
        }
