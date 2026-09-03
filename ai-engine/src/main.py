import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .muscle.muscle_enhancer import enhance_video
from .reheal.auto_fixer import AutoFixer
from .reheal.health_monitor import HealthMonitor

load_dotenv(Path(__file__).resolve().parents[2] / '.env')
app = FastAPI(title='Cutting Edge AI Core v2')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])
monitor, fixer = HealthMonitor(), AutoFixer()

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    language: str = 'fa'

class EnhanceRequest(BaseModel):
    video_path: str
    intensity: float = Field(default=.6, ge=0, le=1)
    preset: str = 'natural_gym'

@app.get('/health')
def health():
    result = monitor.check_health()
    if not result.is_healthy:
        fixer.auto_fix_memory()
    return {'status': 'healthy' if result.is_healthy else 'warning', 'ram_percent': result.ram_percent, 'cpu_percent': result.cpu_percent, 'ai_connected': bool(os.getenv('OPENROUTER_API_KEY')), 'reheal_active': True}

@app.post('/ai/chat')
def ai_chat(req: ChatRequest):
    api_key = os.getenv('OPENROUTER_API_KEY', '')
    if not api_key:
        return {'error': 'OpenRouter API key is not configured.'}
    system = 'تو دستیار هوشمند ویرایش ویدیو هستی. به فارسی پاسخ بده. کوتاه و عملی.' if req.language == 'fa' else 'You are a smart video editing assistant. Be concise and actionable.'
    try:
        response = requests.post('https://openrouter.ai/api/v1/chat/completions', headers={'Authorization': f'Bearer {api_key}', 'HTTP-Referer': 'https://cutting-edge.app', 'X-Title': 'Cutting Edge'}, json={'model': 'meta-llama/llama-3.1-8b-instruct:free', 'messages': [{'role': 'system', 'content': system}, {'role': 'user', 'content': req.message}], 'max_tokens': 500}, timeout=15)
        response.raise_for_status()
        data = response.json()
        return {'reply': data['choices'][0]['message']['content'], 'model': 'llama-3.1-8b-free', 'cost': '$0.00'}
    except (requests.RequestException, KeyError, IndexError, ValueError) as exc:
        return {'error': f'AI provider error: {exc.__class__.__name__}'}

@app.post('/muscle/enhance')
def muscle_enhance(req: EnhanceRequest):
    source = Path(req.video_path)
    output = source.with_name(f'{source.stem}_enhanced{source.suffix or ".mp4"}')
    enhance_video(source, output, req.intensity)
    return {'status': 'done', 'output': str(output)}
