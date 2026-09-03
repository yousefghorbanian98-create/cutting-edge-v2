"""Content Strategy AI — Virality Score Predictor"""
from typing import Dict, Any

class ContentStrategyAI:
    def predict_virality(self, hook_energy: float, cut_rhythm: float, duration_sec: float) -> Dict[str, Any]:
        score = 50
        
        # 1. Hook Power (First 3 seconds)
        if hook_energy > 0.6: score += 25
        elif hook_energy < 0.3: score -= 15
        
        # 2. Cut Rhythm (Optimal: 1.5 - 3.0 sec)
        if 1.5 <= cut_rhythm <= 3.0: score += 20
        elif cut_rhythm > 5.0: score -= 20
        
        # 3. Duration
        if 15 <= duration_sec <= 45: score += 15
        
        final_score = min(98, max(15, score))
        return {
            "virality_score": final_score,
            "tier": "Viral Potential" if final_score > 75 else "Standard",
            "recommendation": "قلاب اول ویدیو عالی است!" if hook_energy > 0.6 else "ثانیه‌های اول را پرانرژی‌تر کنید."
        }
