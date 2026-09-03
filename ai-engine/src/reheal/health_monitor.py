"""Reheal Loop — Health Monitor (checks every 3s)"""
import psutil
import time
import logging
import threading
from dataclasses import dataclass
from typing import List, Callable

logger = logging.getLogger("reheal")

@dataclass
class HealthSnapshot:
    ram_percent: float
    cpu_percent: float
    gpu_mem_mb: float
    gpu_temp: float
    is_healthy: bool

@dataclass
class Alert:
    severity: str
    component: str
    message: str
    auto_fixable: bool

class HealthMonitor:
    def __init__(self):
        self.alerts: List[Alert] = []
        self.history: List[HealthSnapshot] = []
        self.callbacks: List[Callable] = []
        self._running = False

    def start(self):
        self._running = True
        threading.Thread(target=self._loop, daemon=True).start()
        logger.info("Reheal Health Monitor started")

    def stop(self): self._running = False

    def on_alert(self, cb): self.callbacks.append(cb)

    def check_health(self) -> HealthSnapshot:
        ram = psutil.virtual_memory().percent
        cpu = psutil.cpu_percent(interval=0.1)
        gpu_mem, gpu_temp = 0, 0
        try:
            import GPUtil
            g = GPUtil.getGPUs()
            if g: gpu_mem, gpu_temp = g[0].memoryUsed, g[0].temperature
        except Exception: pass
        healthy = ram < 88 and cpu < 95 and gpu_temp < 85
        snap = HealthSnapshot(ram, cpu, gpu_mem, gpu_temp, healthy)
        self.history.append(snap)
        if len(self.history) > 100: self.history = self.history[-100:]
        if ram > 85: self._emit("critical","RAM",f"RAM {ram:.0f}%",True)
        if cpu > 90: self._emit("warning","CPU",f"CPU {cpu:.0f}%",True)
        if gpu_temp > 80: self._emit("critical","GPU",f"GPU {gpu_temp}C",True)
        return snap

    def _loop(self):
        while self._running:
            self.check_health()
            time.sleep(3)

    def _emit(self, sev, comp, msg, fixable):
        a = Alert(sev, comp, msg, fixable)
        self.alerts.append(a)
        logger.warning(f"Reheal: {msg}")
        for cb in self.callbacks:
            try: cb(a)
            except: pass
