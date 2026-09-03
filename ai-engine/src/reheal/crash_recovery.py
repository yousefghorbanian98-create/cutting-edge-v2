import json, time
from pathlib import Path

class CrashRecovery:
    def __init__(self, dir_path='.cutting-edge/checkpoints'):
        self.dir = Path(dir_path)
        self.dir.mkdir(parents=True, exist_ok=True)
    def save_checkpoint(self, state: dict):
        (self.dir / 'latest.json').write_text(json.dumps({'timestamp': time.time(), 'state': state}), encoding='utf-8')
    def load_checkpoint(self):
        path = self.dir / 'latest.json'
        return json.loads(path.read_text(encoding='utf-8'))['state'] if path.exists() else None
