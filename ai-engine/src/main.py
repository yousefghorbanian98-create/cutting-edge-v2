"""Cutting Edge AI Core v2 — FULLY WIRED to real AI modules.

Run as a package so the relative imports below resolve:
    uvicorn ai_engine.main:app
(see scripts/dev-backend.sh / scripts/dev-backend.ps1 and the S-002 card).
"""
import os
import tempfile
import shutil
import requests
import psutil

from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from ai_engine.core.storage import (
    Storage,
    MediaTypeError,
    PayloadTooLargeError,
    PathTraversalError,
)

# Load ai-engine/.env before anything reads config (S-002: python-dotenv).
# When run as an installed package the working dir is still ai-engine/, so a
# plain load_dotenv() picks up .env; fall back to the package-relative path.
load_dotenv()
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

app = FastAPI(title="Cutting Edge AI Core v2")
# S-003: tighten CORS to the known local/tauri origins only (was "*").
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "tauri://localhost",
        "https://tauri.localhost",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)
API_KEY = os.getenv("OPENROUTER_API_KEY", "")

# S-003: all uploads go through the safe Storage (whitelist, size limit, UUID,
# path-traversal-safe resolve). Max size is configurable for tests/CI.
TEMP_DIR = tempfile.mkdtemp(prefix="ce_")
storage = Storage(
    base_dir=TEMP_DIR,
    max_upload_bytes=int(os.getenv("CE_MAX_UPLOAD_MB", "2048")) * 1024 * 1024,
)


def save_upload(file: UploadFile) -> str:
    """Store an upload safely and return its absolute path (S-003)."""
    return storage.save_upload(file)


# ── Exception handlers (S-003) ──
@app.exception_handler(MediaTypeError)
async def _media_type_handler(request: Request, exc: MediaTypeError):
    return JSONResponse(status_code=415, content={"error": str(exc)})


@app.exception_handler(PayloadTooLargeError)
async def _payload_too_large_handler(request: Request, exc: PayloadTooLargeError):
    return JSONResponse(status_code=413, content={"error": str(exc)})


@app.exception_handler(PathTraversalError)
async def _path_traversal_handler(request: Request, exc: PathTraversalError):
    return JSONResponse(status_code=404, content={"error": "File not found"})

# ── Models ──
class ChatReq(BaseModel):
    message: str
    language: str = "fa"

class VoiceReq(BaseModel):
    text: str

# ══════════════════════════════════════════
# HEALTH
# ══════════════════════════════════════════
@app.get("/health")
def health():
    ram = psutil.virtual_memory().percent
    cpu = psutil.cpu_percent(interval=0.1)
    gpu_mem = 0
    try:
        import GPUtil
        g = GPUtil.getGPUs()
        if g: gpu_mem = g[0].memoryUsed
    except: pass
    return {
        "status": "healthy" if ram < 88 and gpu_mem < 3500 else "warning",
        "ram": ram, "cpu": cpu, "gpu_mem": gpu_mem,
        "ai": bool(API_KEY), "reheal": True
    }

# ══════════════════════════════════════════
# AI CHAT (OpenRouter Free)
# ══════════════════════════════════════════
@app.post("/ai/chat")
def chat(req: ChatReq):
    if not API_KEY:
        return {"reply": "کلید OpenRouter تنظیم نشده. در فایل ai-engine/.env مقدار OPENROUTER_API_KEY را وارد کنید.", "model": "offline"}
    sys_p = "تو دستیار هوشمند ویرایش ویدیوی ورزشی هستی. به فارسی پاسخ بده. کوتاه، عملی و تخصصی." if req.language == "fa" else "You are a workout video editing assistant. Be concise."
    try:
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {API_KEY}", "HTTP-Referer": "https://cutting-edge.app"},
            json={
                "model": "meta-llama/llama-3.1-8b-instruct:free",
                "messages": [{"role": "system", "content": sys_p}, {"role": "user", "content": req.message}],
                "max_tokens": 500
            }, timeout=15
        )
        return {"reply": r.json()["choices"][0]["message"]["content"], "model": "llama-3.1-8b-free", "cost": "$0"}
    except Exception as e:
        return {"reply": f"خطا در ارتباط با AI: {e}", "model": "error"}

# ══════════════════════════════════════════
# BEAT SYNC (Fixed: extracts audio from MP4 first)
# ══════════════════════════════════════════
@app.post("/editor/beat-sync")
async def beat_sync(file: UploadFile = File(...)):
    path = save_upload(file)  # validate type/size first (S-003 fail-fast)
    from .editor_ai.beat_sync import BeatSyncEngine
    engine = BeatSyncEngine()

    # analyze_audio now handles MP4 → WAV extraction internally
    beats = engine.analyze_audio(path)
    bpm = engine.tempo_bpm

    clips = []
    for i in range(0, len(beats) - 3, 4):
        start = beats[i].time
        end = beats[min(i + 4, len(beats) - 1)].time
        if end <= start:
            continue
        energy = sum(b.strength for b in beats[i:i+4]) / 4
        clips.append({
            "id": f"beat-{i}",
            "start": round(start, 2),
            "end": round(end, 2),
            "energyLevel": round(min(max(energy, 0.1), 1.0), 2),
            "emotionTag": "intense" if energy > 0.6 else "calm"
        })

    return {
        "status": "success",
        "bpm": round(bpm, 1),
        "total_beats": len(beats),
        "clips": clips[:20]
    }

# ══════════════════════════════════════════
# VIRAL CUT (Fixed: handles short videos)
# ══════════════════════════════════════════
@app.post("/editor/viral-cut")
async def viral_cut(
    file: UploadFile = File(...),
    target_duration: int = Form(30)
):
    path = save_upload(file)  # validate type/size first (S-003 fail-fast)
    from .editor_ai.viral_cut import ViralCutFinder
    from .analyzer.video_analyzer import VideoAnalyzer

    analyzer = VideoAnalyzer()
    analysis = analyzer.analyze(path, sample_rate=10)
    energies = [f.motion_intensity for f in analysis.frames]
    fps = analysis.fps if analysis.fps > 0 else 30.0

    finder = ViralCutFinder()
    start_frame, end_frame = finder.find_best_segment(energies, fps, target_duration)

    start_sec = round(start_frame / fps, 2)
    end_sec = round(end_frame / fps, 2)
    actual_dur = round(end_sec - start_sec, 2)

    virality = finder.calculate_virality_score(energies, start_frame, end_frame, fps)

    return {
        "status": "success",
        "start": start_sec,
        "end": end_sec,
        "duration": actual_dur,
        "virality_score": virality["score"],
        "hook_energy": virality["hook"],
        "sustain_energy": virality["sustain"],
        "message": f"بهترین بخش {actual_dur}s | قلاب: {int(virality['hook']*100)}% | انرژی: {int(virality['sustain']*100)}%"
    }

# ══════════════════════════════════════════
# MOOD DNA (Real frame-by-frame extraction)
# ══════════════════════════════════════════
@app.post("/mood-dna")
async def mood_dna(file: UploadFile = File(...)):
    path = save_upload(file)  # validate type/size first (S-003 fail-fast)
    from .style_match.mood_dna import MoodDNAExtractor
    from dataclasses import asdict
    extractor = MoodDNAExtractor()
    dna = extractor.extract(path)
    return asdict(dna)

# ══════════════════════════════════════════
# MUSCLE ENHANCE (Real OpenCV processing)
# ══════════════════════════════════════════
@app.post("/muscle/enhance")
async def muscle_enhance(
    file: UploadFile = File(...),
    intensity: float = Form(0.6),
    preset: str = Form("natural_gym")
):
    path = save_upload(file)  # validate type/size first (S-003 fail-fast)
    out_path, out_name = storage.save_output(file.filename or "output.mp4")

    from .muscle.muscle_enhancer import MuscleEnhancer, EnhancementSettings, PRESETS

    settings = PRESETS.get(preset, EnhancementSettings(intensity=intensity))
    enhancer = MuscleEnhancer()
    enhancer.enhance_video(path, out_path, settings)

    return {
        "status": "done",
        "output_filename": out_name,
        "preset": preset,
        "intensity": intensity,
        "message": f"عضلات با پریست {preset} و شدت {int(intensity*100)}% تقویت شدند."
    }

@app.get("/muscle/download/{filename}")
def download_enhanced(filename: str):
    # S-003: resolved strictly inside the storage dir (path traversal → 404).
    path = storage.resolve_download(filename)
    if not path.is_file():
        return JSONResponse(status_code=404, content={"error": "File not found"})
    return FileResponse(path, media_type="video/mp4", filename=path.name)

# ══════════════════════════════════════════
# VOICE COMMAND
# ══════════════════════════════════════════
@app.post("/editor/voice-command")
def voice_command(req: VoiceReq):
    from .editor_ai.voice_editor import VoiceEditor
    parser = VoiceEditor()
    action = parser.parse_command(req.text)
    return {"status": "success", "parsed": action}

# ══════════════════════════════════════════
# STYLE MATCH (Compare two videos)
# ══════════════════════════════════════════
@app.post("/style-match/compare")
async def style_compare(
    reference: UploadFile = File(...),
    source: UploadFile = File(...)
):
    ref_path = save_upload(reference)  # validate type/size first (S-003 fail-fast)
    src_path = save_upload(source)
    from .style_match.mood_dna import MoodDNAExtractor
    from dataclasses import asdict
    extractor = MoodDNAExtractor()
    ref_dna = extractor.extract(ref_path)
    src_dna = extractor.extract(src_path)
    score = extractor.calculate_match(ref_dna, src_dna)
    return {
        "reference": asdict(ref_dna),
        "source": asdict(src_dna),
        "match_score": score
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=os.getenv("CE_HOST", "127.0.0.1"), port=int(os.getenv("CE_PORT", "8001")))
