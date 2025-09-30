import os
import json
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, Any

DATA_DIR = os.environ.get("EDUMON_DATA_DIR", os.path.join(os.path.dirname(__file__), "data"))
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
CLIENTS_FILE = os.path.join(DATA_DIR, "clients.json")
AUDIT_LOG = os.path.join(LOG_DIR, "audit.log")

# Retención por defecto (segundos). Cambiar vía variables de entorno si se desea
CLIENTS_TTL_SECONDS = int(os.environ.get("EDUMON_CLIENTS_TTL_SECONDS", "2592000"))  # 30 días
LOG_TTL_SECONDS = int(os.environ.get("EDUMON_LOG_TTL_SECONDS", "2592000"))  # 30 días


def _safe_load_clients() -> Dict[str, Any]:
    if not os.path.exists(CLIENTS_FILE):
        return {}
    try:
        with open(CLIENTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def _safe_save_clients(clients: Dict[str, Any]) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    tmp = CLIENTS_FILE + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(clients, f, ensure_ascii=False, indent=2)
    os.replace(tmp, CLIENTS_FILE)


def purge_old_clients(now: float | None = None) -> int:
    now = now or time.time()
    cutoff = datetime.fromtimestamp(now - CLIENTS_TTL_SECONDS, tz=timezone.utc).isoformat()
    clients = _safe_load_clients()
    before = len(clients)
    # Eliminar clientes cuya última actividad sea anterior al cutoff
    to_delete = []
    for dev, c in clients.items():
        last_seen = c.get('last_seen')
        if not last_seen:
            continue
        if last_seen < cutoff:
            to_delete.append(dev)
    for dev in to_delete:
        clients.pop(dev, None)
    if to_delete:
        _safe_save_clients(clients)
    return before - len(clients)


def rotate_audit_log(now: float | None = None) -> bool:
    """Borra entradas antiguas del audit.log según TTL.
    Para simplicidad, si el archivo es muy grande, se reescribe filtrando por cutoff.
    """
    now = now or time.time()
    cutoff_ts = now - LOG_TTL_SECONDS
    if not os.path.exists(AUDIT_LOG):
        return False
    changed = False
    kept: list[str] = []
    with open(AUDIT_LOG, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                import json
                obj = json.loads(line)
                ts = obj.get('ts')
                if not ts:
                    continue
                # Intentar parsear ISO
                from datetime import datetime
                dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                if dt.timestamp() >= cutoff_ts:
                    kept.append(line)
            except Exception:
                kept.append(line)
    with open(AUDIT_LOG, 'w', encoding='utf-8') as f:
        f.writelines(kept)
        changed = True
    return changed
