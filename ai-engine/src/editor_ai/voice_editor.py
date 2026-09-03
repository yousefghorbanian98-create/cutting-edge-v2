"""Voice Command Parser — Natural Persian Voice to Video Actions"""
import re
from typing import Dict, Any

class VoiceEditor:
    def parse_command(self, text: str) -> Dict[str, Any]:
        text = text.strip().lower()
        
        # 1. Cut Command
        if any(w in text for w in ["برش", "کات", "حذف"]):
            nums = [int(s) for s in re.findall(r'\d+', text)]
            return {
                "action": "cut",
                "start": nums[0] if len(nums) > 0 else 0,
                "end": nums[1] if len(nums) > 1 else 5,
                "confidence": 0.95
            }
        
        # 2. Slow Motion
        if any(w in text for w in ["اسلو", "آهسته", "اسلوموشن"]):
            return {"action": "slowmo", "speed": 0.5, "confidence": 0.9}
            
        # 3. Muscle Enhance
        if any(w in text for w in ["عضله", "عضلات", "شارپ"]):
            return {"action": "muscle_enhance", "intensity": 0.7, "confidence": 0.92}
            
        # 4. Beat Sync
        if any(w in text for w in ["ریتم", "موزیک", "بیت", "سینک"]):
            return {"action": "beat_sync", "confidence": 0.98}

        return {"action": "chat", "query": text, "confidence": 0.7}
