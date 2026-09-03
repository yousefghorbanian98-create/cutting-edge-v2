"""Reheal Loop — Crash Recovery with checkpoints"""
import json, time
from pathlib import Path

class CrashRecovery:
    def __init__(self, d=".cutting-edge/checkpoints"):
        self.dir = Path(d); self.dir.mkdir(parents=True, exist_ok=True)

    def save(self, state: dict):
        p = self.dir / "latest.json"
        bk = self.dir / f"bk_{int(time.time())}.json"
        if p.exists():
            import shutil; shutil.copy2(p, bk)
        with open(p, "w", encoding="utf-8") as f:
            json.dump({"ts": time.time(), "state": state}, f)
        for old in sorted(self.dir.glob("bk_*.json"))[:-5]: old.unlink()

    def load(self):
        p = self.dir / "latest.json"
        if not p.exists(): return None
        d = json.load(open(p, encoding="utf-8"))
        if time.time() - d["ts"] > 3600: return None
        return d["state"]
