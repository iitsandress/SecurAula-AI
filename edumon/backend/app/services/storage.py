import os
import json
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import aiofiles

from ..core.config import settings

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

async def audit_log(action: str, actor: str, ip: Optional[str] = None, details: Optional[Dict[str, Any]] = None) -> None:
    await aiofiles.os.makedirs(settings.LOG_DIR, exist_ok=True)
    entry = {
        "ts": now_iso(),
        "action": action,
        "actor": actor,
        "ip": ip,
        "details": details or {},
    }
    async with aiofiles.open(settings.AUDIT_LOG_FILE, "a", encoding="utf-8") as f:
        await f.write(json.dumps(entry, ensure_ascii=False) + "\n")

async def load_clients() -> Dict[str, Any]:
    if not os.path.exists(settings.CLIENTS_FILE):
        return {}
    try:
        async with aiofiles.open(settings.CLIENTS_FILE, "r", encoding="utf-8") as f:
            content = await f.read()
            return json.loads(content)
    except (json.JSONDecodeError, IOError):
        return {}

async def save_clients(clients: Dict[str, Any]) -> None:
    await aiofiles.os.makedirs(settings.DATA_DIR, exist_ok=True)
    tmp_path = settings.CLIENTS_FILE + ".tmp"
    async with aiofiles.open(tmp_path, "w", encoding="utf-8") as f:
        await f.write(json.dumps(clients, ensure_ascii=False, indent=2))
    await aiofiles.os.replace(tmp_path, settings.CLIENTS_FILE)