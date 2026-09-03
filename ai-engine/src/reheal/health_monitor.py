import logging
import psutil
from dataclasses import dataclass

logger = logging.getLogger('reheal')

@dataclass
class SystemHealth:
    ram_percent: float
    cpu_percent: float
    is_healthy: bool

class HealthMonitor:
    def check_health(self) -> SystemHealth:
        ram = psutil.virtual_memory().percent
        cpu = psutil.cpu_percent(interval=0.1)
        healthy = ram < 88.0 and cpu < 95.0
        if not healthy:
            logger.warning('System pressure: RAM %.1f%%, CPU %.1f%%', ram, cpu)
        return SystemHealth(ram, cpu, healthy)
