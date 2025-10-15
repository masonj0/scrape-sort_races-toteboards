# python_service/health.py
from datetime import datetime
from typing import Dict
from typing import List

import psutil
import structlog
from fastapi import APIRouter

router = APIRouter()
log = structlog.get_logger(__name__)


class HealthMonitor:
    def __init__(self):
        self.adapter_health: Dict[str, Dict] = {}
        self.system_metrics: List[Dict] = []
        self.max_metrics_history = 100

    def record_adapter_response(self, adapter_name: str, success: bool, duration: float):
        if adapter_name not in self.adapter_health:
            self.adapter_health[adapter_name] = {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "avg_response_time": 0.0,
                "last_success": None,
                "last_failure": None,
            }

        health = self.adapter_health[adapter_name]
        health["total_requests"] += 1

        if success:
            health["successful_requests"] += 1
            health["last_success"] = datetime.now().isoformat()
        else:
            health["failed_requests"] += 1
            health["last_failure"] = datetime.now().isoformat()

        health["avg_response_time"] = (
            health["avg_response_time"] * (health["total_requests"] - 1) + duration
        ) / health["total_requests"]

    def get_system_metrics(self) -> Dict:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        metrics = {
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available_gb": round(memory.available / (1024**3), 2),
            "disk_percent": disk.percent,
            "disk_free_gb": round(disk.free / (1024**3), 2),
        }

        self.system_metrics.append(metrics)
        if len(self.system_metrics) > self.max_metrics_history:
            self.system_metrics.pop(0)

        return metrics

    def get_health_report(self) -> Dict:
        system_metrics = self.get_system_metrics()
        return {
            "status": "healthy" if self.is_system_healthy() else "degraded",
            "timestamp": datetime.now().isoformat(),
            "system": system_metrics,
            "adapters": self.adapter_health,
            "metrics_history": self.system_metrics[-10:],
        }

    def is_system_healthy(self) -> bool:
        if not self.system_metrics:
            return True
        latest = self.system_metrics[-1]
        return latest["cpu_percent"] < 80 and latest["memory_percent"] < 85 and latest["disk_percent"] < 90


# Global instance for the application to use
health_monitor = HealthMonitor()


@router.get("/health/detailed", tags=["Health"])
async def get_detailed_health():
    """Provides a comprehensive health check of the system."""
    return health_monitor.get_health_report()


@router.get("/health", tags=["Health"])
async def get_basic_health():
    """Provides a basic health check for load balancers and uptime monitoring."""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}
