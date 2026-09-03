"""Smart Captioner + Translator using Whisper (local, free)"""
from typing import List
import os

class SmartCaptioner:
    def __init__(self, model_size="small"):
        self.model = None
        self.model_size = model_size

    def _load_model(self):
        if self.model: return
        try:
            from faster_whisper import WhisperModel
            self.model = WhisperModel(self.model_size, device="cuda", compute_type="float16")
        except Exception:
            try:
                from faster_whisper import WhisperModel
                self.model = WhisperModel("tiny", device="cpu")
            except ImportError:
                print("faster-whisper not installed.")

    def generate_captions(self, video_path: str, source_lang="en", translate_to="fa") -> List[dict]:
        self._load_model()
        if not self.model:
            return [{"start":0,"end":5,"text":"[Whisper not available]","translated":""}]
        segments, info = self.model.transcribe(video_path, language=source_lang, beam_size=5, vad_filter=True)
        captions = []
        for seg in segments:
            cap = {"start":round(seg.start,2),"end":round(seg.end,2),"text":seg.text.strip()}
            if source_lang != translate_to:
                t_segs, _ = self.model.transcribe(video_path, language=source_lang, task="translate")
                cap["translated"] = " ".join(s.text for s in t_segs)
            captions.append(cap)
        return captions

    def export_srt(self, captions: List[dict], path: str):
        with open(path, "w", encoding="utf-8") as f:
            for i, c in enumerate(captions, 1):
                s = self._fmt(c["start"]); e = self._fmt(c["end"])
                t = c.get("translated", c["text"])
                f.write(f"{i}\n{s} --> {e}\n{t}\n\n")

    def _fmt(self, sec):
        h=int(sec//3600); m=int((sec%3600)//60); s=int(sec%60); ms=int((sec%1)*1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
