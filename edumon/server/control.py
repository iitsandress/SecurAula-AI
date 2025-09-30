import os
import json
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Header

API_KEY = os.environ.get("EDUMON_API_KEY", "S1R4X")
DATA_DIR = os.environ.get("EDUMON_DATA_DIR", os.path.join(os.path.dirname(__file__), "data"))
CONTROL_FILE = os.path.join(DATA_DIR, "control.json")

router = APIRouter()

def _load_control() -> Dict[str, Any]:
    if not os.path.exists(CONTROL_FILE):
        return {"stop_all": False, "stop_list": []}
    try:
        with open(CONTROL_FILE, "r", encoding="utf-8") as f:
            obj = json.load(f)
        obj.setdefault("stop_all", False)
        obj.setdefault("stop_list", [])
        return obj
    except Exception:
        return {"stop_all": False, "stop_list": []}


def _save_control(obj: Dict[str, Any]) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    tmp = CONTROL_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    os.replace(tmp, CONTROL_FILE)


async def _require_api_key(x_api_key: Optional[str] = Header(default=None, alias="X-API-Key")) -> str:
    if not API_KEY or API_KEY == "changeme":
        pass
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return x_api_key


@router.get("/api/v1/control")
async def get_control(_: str = Depends(_require_api_key)) -> Dict[str, Any]:
    return _load_control()


@router.post("/api/v1/control/stop_all")
async def set_stop_all(payload: Dict[str, Any], _: str = Depends(_require_api_key)) -> Dict[str, Any]:
    value = bool(payload.get("value", False))
    obj = _load_control()
    obj["stop_all"] = value
    _save_control(obj)
    return obj


@router.post("/api/v1/control/stop_device")
async def stop_device(payload: Dict[str, Any], _: str = Depends(_require_api_key)) -> Dict[str, Any]:
    device_id = payload.get("device_id")
    if not device_id:
        raise HTTPException(status_code=400, detail="device_id required")
    obj = _load_control()
    if device_id not in obj["stop_list"]:
        obj["stop_list"].append(device_id)
    _save_control(obj)
    return obj


@router.post("/api/v1/control/clear_device")
async def clear_device(payload: Dict[str, Any], _: str = Depends(_require_api_key)) -> Dict[str, Any]:
    device_id = payload.get("device_id")
    if not device_id:
        raise HTTPException(status_code=400, detail="device_id required")
    obj = _load_control()
    obj["stop_list"] = [d for d in obj["stop_list"] if d != device_id]
    _save_control(obj)
    return obj
