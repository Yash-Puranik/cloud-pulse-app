from typing import Any, Dict
import psutil


def collect_metrics() -> Dict[str, Any]:
    """Collects CPU, memory, disk usage, and active process count."""
    return {
        "cpu_usage_percent": psutil.cpu_percent(interval=None),
        "memory_usage_percent": psutil.virtual_memory().percent,
        "disk_usage_percent": psutil.disk_usage("/").percent,
        "active_pids": len(psutil.pids()),
        "status": "healthy",
    }
