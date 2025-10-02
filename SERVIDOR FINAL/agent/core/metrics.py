import psutil
import time
from typing import Dict, Any

def get_system_metrics() -> Dict[str, Any]:
    """Recopilar métricas del sistema."""
    try:
        metrics = {
            "cpu_percent": round(psutil.cpu_percent(interval=1), 1),
            "mem_percent": round(psutil.virtual_memory().percent, 1),
            "uptime_seconds": int(time.time() - psutil.boot_time())
        }
        try:
            metrics["disk_percent"] = round(psutil.disk_usage('/').percent, 1)
        except Exception:
            metrics["disk_percent"] = 0
        try:
            net_io = psutil.net_io_counters()
            metrics["network_sent"] = net_io.bytes_sent
            metrics["network_recv"] = net_io.bytes_recv
        except Exception:
            metrics["network_sent"] = 0
            metrics["network_recv"] = 0
        try:
            metrics["process_count"] = len(psutil.pids())
        except Exception:
            metrics["process_count"] = 0
        return metrics
    except Exception as e:
        print(f"Error recopilando métricas: {e}")
        return {
            "cpu_percent": 0.0,
            "mem_percent": 0.0,
            "uptime_seconds": 0,
            "disk_percent": 0.0,
            "network_sent": 0,
            "network_recv": 0,
            "process_count": 0
        }
