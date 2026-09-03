# Cutting Edge v2.0
World-Class Desktop Video Editor + AI Style Match + Muscle Enhancer

## Quick Start (Windows PowerShell)
```powershell
git clone <your-repo-url>
cd cutting-edge-v2

# AI Backend
cd ai-engine
python -m venv venv
venv\Scripts\activate
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
pip install -r requirements.txt
python -m uvicorn src.main:app --port 8001 --reload

# Frontend (new terminal)
cd apps/desktop
npm install -g pnpm
pnpm install
pnpm add framer-motion lucide-react
pnpm dev
```

## Architecture
- **Desktop**: Tauri 2.0 (Rust) + Next.js 15 (React 19)
- **AI Core**: Python FastAPI + MediaPipe + Whisper + OpenRouter Free
- **Self-Healing**: Reheal Loop (7-layer auto-recovery)
- **Hardware**: Optimized for 16GB RAM | GTX 1650 4GB
