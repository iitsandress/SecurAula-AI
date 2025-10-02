import os
import time
import uuid
import platform
from typing import Dict, Any, Optional

try:
    import psutil
except Exception:
    psutil = None  # manejaremos la ausencia de psutil devolviendo métricas por defecto


def _safe_call(fn, default=None):
    try:
        return fn()
    except Exception:
        return default


class MetricsCollector:
    """
    Clase que provee varias APIs esperadas por la UI y el core:
      - get_device_id()
      - get_system_info()
      - collect_all_metrics(config_optional)
      - get_basic_metrics()
      - get_process_metrics()
      - get_network_metrics()
    """

    def __init__(self):
        # base_dir apunta a la carpeta `agent/`
        self.base_dir = os.path.dirname(os.path.dirname(__file__))
        self.device_file = os.path.join(self.base_dir, "device_id.txt")
        self._ensure_device_id()
        self._last_net = self._read_net_counters()
        self._last_net_time = time.time()

    def _ensure_device_id(self):
        if not os.path.exists(self.device_file):
            try:
                with open(self.device_file, "w", encoding="utf-8") as f:
                    f.write(str(uuid.uuid4()))
            except Exception:
                pass

    def get_device_id(self) -> str:
        try:
            with open(self.device_file, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception:
            # fallback: generar un id temporal (no se persiste)
            return str(uuid.uuid4())

    def get_system_info(self) -> Dict[str, str]:
        """Devuelve info básica del sistema (plataforma, release)."""
        return {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "platform_version": platform.version(),
            "machine": platform.machine(),
        }

    def collect_all_metrics(self, config: Optional[Any] = None) -> Dict[str, Any]:
        """
        Devuelve un diccionario con métricas principales. `config` es opcional
        y puede contener banderas como collect_disk_metrics, collect_network_metrics, etc.
        Si no se provee, asumimos que se recopilan las métricas disponibles.
        """
        cfg = config or {}
        collect_disk = getattr(cfg, "collect_disk_metrics", True)
        collect_network = getattr(cfg, "collect_network_metrics", True)
        collect_process = getattr(cfg, "collect_process_metrics", True)

        # CPU y memoria
        cpu_percent = _safe_call(lambda: round(psutil.cpu_percent(interval=0.5), 1), 0.0) if psutil else 0.0
        mem = _safe_call(lambda: psutil.virtual_memory(), None) if psutil else None
        mem_percent = round(mem.percent, 1) if mem else 0.0

        # uptime
        uptime_seconds = _safe_call(lambda: int(time.time() - psutil.boot_time()), 0) if psutil else 0

        metrics: Dict[str, Any] = {
            "cpu_percent": cpu_percent,
            "mem_percent": mem_percent,
            "uptime_seconds": uptime_seconds,
        }

        # disco
        if collect_disk and psutil:
            try:
                metrics["disk_percent"] = round(psutil.disk_usage("/").percent, 1)
            except Exception:
                metrics["disk_percent"] = 0.0
        else:
            metrics["disk_percent"] = 0.0

        # red (totales)
        if collect_network and psutil:
            try:
                net_io = psutil.net_io_counters()
                metrics["network_sent"] = net_io.bytes_sent
                metrics["network_recv"] = net_io.bytes_recv
            except Exception:
                metrics["network_sent"] = 0
                metrics["network_recv"] = 0
        else:
            metrics["network_sent"] = 0
            metrics["network_recv"] = 0

        # procesos
        if collect_process and psutil:
            try:
                metrics["process_count"] = len(psutil.pids())
            except Exception:
                metrics["process_count"] = 0
        else:
            metrics["process_count"] = 0

        return metrics

    def get_basic_metrics(self) -> Dict[str, Any]:
        """API usada por la UI para mostrar métricas simplificadas."""
        if not psutil:
            return {
                "cpu_percent": 0.0,
                "memory_percent": 0.0,
                "memory_used": 0,
                "memory_total": 0,
                "uptime_seconds": 0
            }

        cpu = _safe_call(lambda: round(psutil.cpu_percent(interval=0.1), 1), 0.0)
        vm = _safe_call(lambda: psutil.virtual_memory(), None)
        if vm:
            mem_percent = round(vm.percent, 1)
            mem_used = vm.used
            mem_total = vm.total
        else:
            mem_percent = 0.0
            mem_used = 0
            mem_total = 0

        uptime = _safe_call(lambda: int(time.time() - psutil.boot_time()), 0)

        return {
            "cpu_percent": cpu,
            "memory_percent": mem_percent,
            "memory_used": mem_used,
            "memory_total": mem_total,
            "uptime_seconds": uptime
        }

    def get_process_metrics(self) -> Dict[str, Any]:
        if not psutil:
            return {"process_count": 0}
        try:
            return {"process_count": len(psutil.pids())}
        except Exception:
            return {"process_count": 0}

    def _read_net_counters(self):
        if not psutil:
            return None
        try:
            return psutil.net_io_counters()
        except Exception:
            return None

    def get_network_metrics(self) -> Dict[str, Any]:
        """
        Devuelve tasas de red (bytes/s) calculadas desde la última llamada.
        También devuelve los contadores totales actuales.
        """
        now = time.time()
        current = self._read_net_counters()
        result = {
            "network_sent_rate": 0.0,
            "network_recv_rate": 0.0,
            "network_sent": 0,
            "network_recv": 0
        }
        if current and self._last_net:
            dt = max(0.001, now - self._last_net_time)
            try:
                sent_rate = (current.bytes_sent - self._last_net.bytes_sent) / dt
                recv_rate = (current.bytes_recv - self._last_net.bytes_recv) / dt
            except Exception:
                sent_rate = 0.0
                recv_rate = 0.0

            result.update({
                "network_sent_rate": sent_rate,
                "network_recv_rate": recv_rate,
                "network_sent": current.bytes_sent,
                "network_recv": current.bytes_recv
            })

        # actualizar últimas referencias
        self._last_net = current
        self._last_net_time = now

        return result


# Función retrocompatible utilizada en versiones antiguas del agente
def get_system_metrics() -> Dict[str, Any]:
    collector = MetricsCollector()
    return collector.collect_all_metrics()
