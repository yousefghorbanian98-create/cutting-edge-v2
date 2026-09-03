"""Reheal Loop — Memory Guard with LRU Cache"""
import gc, threading
from collections import OrderedDict

class LRUCache:
    def __init__(self, max_mb=500):
        self.max_bytes = max_mb * 1024 * 1024
        self.cache = OrderedDict()
        self.size = 0
        self.lock = threading.Lock()

    def put(self, key, data, nbytes):
        with self.lock:
            if key in self.cache: self.size -= self.cache[key][1]; del self.cache[key]
            while self.size + nbytes > self.max_bytes and self.cache:
                _, (_, s) = self.cache.popitem(last=False); self.size -= s
            self.cache[key] = (data, nbytes); self.size += nbytes

    def get(self, key):
        with self.lock:
            if key not in self.cache: return None
            self.cache.move_to_end(key); return self.cache[key][0]

class MemoryGuard:
    def __init__(self, max_ram_mb=12000):
        self.max_ram = max_ram_mb
        self.cache = LRUCache(300)

    def check(self, needed_mb: int) -> bool:
        import psutil
        used = psutil.virtual_memory().used / 1024 / 1024
        if used + needed_mb > self.max_ram:
            self.emergency_cleanup(); return False
        return True

    def emergency_cleanup(self):
        self.cache = LRUCache(100); gc.collect()
        try:
            import torch
            if torch.cuda.is_available(): torch.cuda.empty_cache()
        except: pass
