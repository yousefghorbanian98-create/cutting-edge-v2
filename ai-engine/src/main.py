"""Cutting Edge AI Core — FastAPI Server with Reheal Loop"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os, requests, psutil

app = FastAPI(title="Cutting Edge AI Core v2")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
API_KEY = os.getenv("OPENROUTER_API_KEY", "")

class ChatReq(BaseModel):
    message: str; language: str = "fa"

class EnhanceReq(BaseModel):
    video_path: str; intensity: float = 0.6; preset: str = "natural_gym"

@app.get("/health")
def health():
    ram = psutil.virtual_memory().percent
    cpu = psutil.cpu_percent(interval=0.1)
    return {"status":"healthy" if ram<88 else "warning","ram":ram,"cpu":cpu,"ai":bool(API_KEY),"reheal":True}

@app.post("/ai/chat")
def chat(req: ChatReq):
    if not API_KEY: return {"error":"Set OPENROUTER_API_KEY in .env"}
    sys_p = "تو دستیار هوشمند ویرایش ویدیو هستی. به فارسی پاسخ بده. کوتاه و عملی." if req.language=="fa" else "You are a video editing assistant. Be concise."
    try:
        r = requests.post("https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization":f"Bearer {API_KEY}","HTTP-Referer":"https://cutting-edge.app"},
            json={"model":"meta-llama/llama-3.1-8b-instruct:free",
                  "messages":[{"role":"system","content":sys_p},{"role":"user","content":req.message}],
                  "max_tokens":500}, timeout=15)
        return {"reply":r.json()["choices"][0]["message"]["content"],"model":"llama-3.1-8b-free","cost":"$0"}
    except Exception as e: return {"error":str(e)}

@app.post("/muscle/enhance")
def enhance(req: EnhanceReq):
    from .muscle.muscle_enhancer import MuscleEnhancer, EnhancementSettings, PRESETS
    e = MuscleEnhancer()
    s = PRESETS.get(req.preset, EnhancementSettings(intensity=req.intensity))
    out = req.video_path.replace(".mp4","_enhanced.mp4")
    e.enhance_video(req.video_path, out, s)
    return {"status":"done","output":out}

@app.get("/mood-dna/{video_path:path}")
def mood_dna(video_path: str):
    from .style_match.mood_dna import MoodDNAExtractor
    from dataclasses import asdict
    dna = MoodDNAExtractor().extract(video_path)
    return asdict(dna)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
