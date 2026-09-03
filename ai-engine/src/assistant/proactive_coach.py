"""Proactive AI Coach — Suggests improvements without being asked"""
import requests
from typing import List
from dataclasses import dataclass

@dataclass
class Suggestion:
    priority: str
    category: str
    message: str
    action_type: str
    confidence: float

class ProactiveCoach:
    def __init__(self, api_key=""):
        self.api_key = api_key

    def analyze(self, mood_dna: dict, scene_count: int) -> List[Suggestion]:
        suggestions = []
        if mood_dna.get("avg_brightness", 0.5) < 0.25:
            suggestions.append(Suggestion("important","lighting","ویدیو خیلی تاریکه. روشن‌ترش کنم؟","auto_fix",0.9))
        if mood_dna.get("cut_rhythm_avg", 5) > 5:
            suggestions.append(Suggestion("important","rhythm","کات‌ها خیلی کند هستند. Beat Sync فعال کنم؟","auto_fix",0.85))
        if mood_dna.get("avg_energy", 0.5) < 0.3:
            suggestions.append(Suggestion("critical","content","انرژی ویدیو پایینه. ۳ ثانیه اول را انفجاری کن!","manual",0.9))
        if self.api_key:
            try:
                r = requests.post("https://openrouter.ai/api/v1/chat/completions",
                    headers={"Authorization":f"Bearer {self.api_key}"},
                    json={"model":"meta-llama/llama-3.1-8b-instruct:free",
                          "messages":[{"role":"user","content":f"Give 2 short video editing tips in Persian for a gym video with energy {mood_dna.get('avg_energy',0.5):.1f}"}],
                          "max_tokens":200}, timeout=10)
                text = r.json()["choices"][0]["message"]["content"]
                suggestions.append(Suggestion("nice-to-have","ai",text,"info",0.7))
            except Exception: pass
        return suggestions
