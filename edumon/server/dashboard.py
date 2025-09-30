import os
import json
from datetime import datetime, timezone, timedelta
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.responses import HTMLResponse

API_KEY = os.environ.get("EDUMON_API_KEY", "S1R4X")
DATA_DIR = os.environ.get("EDUMON_DATA_DIR", os.path.join(os.path.dirname(__file__), "data"))
CLIENTS_FILE = os.path.join(DATA_DIR, "clients.json")

router = APIRouter()


def _load_clients() -> Dict[str, Any]:
    if not os.path.exists(CLIENTS_FILE):
        return {}
    try:
        with open(CLIENTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


async def _require_api_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")) -> str:
    if not API_KEY or API_KEY == "changeme":
        pass
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return x_api_key


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(_: str = Depends(_require_api_key), classroom: str | None = None) -> HTMLResponse:
    clients = _load_clients()
    # build simple table UI (no external assets)
    rows = []
    now = datetime.now(timezone.utc)

    def _parse_iso(ts: str | None) -> datetime | None:
        if not ts:
            return None
        try:
            return datetime.fromisoformat(ts.replace('Z', '+00:00'))
        except Exception:
            return None

    def _humanize(seconds: int | None) -> str:
        if seconds is None:
            return '-'
        if seconds < 60:
            return f"{seconds}s"
        minutes, sec = divmod(seconds, 60)
        if minutes < 60:
            return f"{minutes}m {sec}s"
        hours, rem = divmod(minutes, 60)
        return f"{hours}h {rem}m"

    total = online = idle = offline = 0

    for dev_id, c in clients.items():
        if classroom and c.get('classroom_id') != classroom:
            continue
        total += 1
        m = c.get("metrics") or {}
        last_seen = c.get("last_seen")
        dt = _parse_iso(last_seen)
        secs_ago = None if not dt else int((now - dt).total_seconds())
        status_class = 'status-gray'
        status_label = 'desconocido'
        if secs_ago is not None:
            if secs_ago <= 30:
                status_class = 'status-green'
                status_label = 'en línea'
                online += 1
            elif secs_ago <= 90:
                status_class = 'status-yellow'
                status_label = 'inactivo'
                idle += 1
            else:
                status_class = 'status-red'
                status_label = 'desconectado'
                offline += 1
        human_ago = _humanize(secs_ago)
        last = last_seen or '-'
        rows.append(
            f"<tr>"
            f"<td style='font-family:monospace'>{dev_id}</td>"
            f"<td>{c.get('hostname','')}</td>"
            f"<td>{c.get('username','')}</td>"
            f"<td>{c.get('classroom_id','')}</td>"
            f"<td>{m.get('cpu_percent','-')}</td>"
            f"<td>{m.get('mem_percent','-')}</td>"
            f"<td>{m.get('uptime_seconds','-')}</td>"
            f"<td><span class='dot {status_class}'></span> {status_label}</td>"
            f"<td>{human_ago}</td>"
            f"<td>{last}</td>"
            f"<td><button class='btn btn-stop' data-dev='{dev_id}'>Detener</button> <button class='btn btn-clear' data-dev='{dev_id}'>Permitir</button></td>"
            f"</tr>"
        )

    summary = f"Total: {total} | En línea: {online} | Inactivo: {idle} | Desconectado: {offline}"

    html = f"""
    <!doctype html>
    <html lang='es'>
    <head>
        <meta charset='utf-8'/>
        <meta name='viewport' content='width=device-width, initial-scale=1'/>
        <meta http-equiv='refresh' content='15'>
        <title>EduMon Dashboard</title>
        <style>
            body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial; margin: 24px; background: #fafafa; }}
            h1 {{ font-size: 20px; }}
            table {{ border-collapse: collapse; width: 100%; background: #fff; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; font-size: 14px; }}
            th {{ background: #f0f0f0; text-align: left; }}
            .muted {{ color: #666; font-size: 12px; }}
            .dot {{ display:inline-block; width:10px; height:10px; border-radius:50%; margin-right:6px; vertical-align:middle; }}
            .status-green {{ background:#19c37d; }}
            .status-yellow {{ background:#f6c744; }}
            .status-red {{ background:#ef4444; }}
            .status-gray {{ background:#9ca3af; }}
            .btn {{ background:#2563eb; color:#fff; border:none; padding:6px 10px; border-radius:4px; cursor:pointer; margin-right:6px; }}
            .btn:hover {{ background:#1d4ed8; }}
            .toolbar {{ margin:8px 0 12px; }}
        </style>
    </head>
    <body>
        <h1>EduMon - Panel de aula</h1>
        <p class='muted'>Solo métricas mínimas. Última actualización: {datetime.now(timezone.utc).isoformat()}</p>
        <p>{summary}</p>
        <form method='get' action='/dashboard' style='margin:8px 0;'>
            <label for='classroom'>Filtrar por aula:</label>
            <input type='text' name='classroom' id='classroom' placeholder='Sala-1' value='{classroom or ""}' />
            <button type='submit'>Filtrar</button>
        </form>
        <div class='toolbar'>
            <label>API Key: <input id='apiKey' type='password' placeholder='Clave...' /></label>
            <button type='button' class='btn' id='saveKey'>Guardar</button>
            <button type='button' class='btn' id='toggleStopAll'>Stop All: <span id='stopAllStatus'>-</span></button>
            <button type='button' class='btn' id='downloadCsv'>Descargar CSV</button>
        </div>
        <table>
            <thead>
                <tr>
                    <th>Device ID</th>
                    <th>Host</th>
                    <th>Usuario</th>
                    <th>Aula</th>
                    <th>CPU %</th>
                    <th>RAM %</th>
                    <th>Uptime (s)</th>
                    <th>Estado</th>
                    <th>Hace</th>
                    <th>Visto</th>
                    <th>Acciones</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
        <script>
        (function(){{
            const apiKeyInput = document.getElementById('apiKey');
            const saveBtn = document.getElementById('saveKey');
            const stopAllBtn = document.getElementById('toggleStopAll');
            const stopAllStatus = document.getElementById('stopAllStatus');
            const dlBtn = document.getElementById('downloadCsv');

            function getKey(){{ return localStorage.getItem('edumon_api_key') || ''; }}
            function setKey(k){{ localStorage.setItem('edumon_api_key', k); }}
            function headers(){{ return {{ 'X-API-Key': getKey(), 'Content-Type': 'application/json' }}; }}

            async function refreshControl(){{
                const k = getKey();
                if(!k){{ stopAllStatus.textContent = '-'; return; }}
                try{{
                    const r = await fetch('/api/v1/control', {{headers: headers()}});
                    if(!r.ok){{ stopAllStatus.textContent = 'error'; return; }}
                    const obj = await r.json();
                    stopAllStatus.textContent = obj.stop_all ? 'ON' : 'OFF';
                    stopAllBtn.dataset.state = obj.stop_all ? 'on' : 'off';
                }}catch(e){{ stopAllStatus.textContent = 'error'; }}
            }}

            async function toggleStopAll(){{
                const state = stopAllBtn.dataset.state === 'on';
                const payload = {{ value: !state }};
                const r = await fetch('/api/v1/control/stop_all', {{method: 'POST', headers: headers(), body: JSON.stringify(payload)}});
                if(r.ok){{ await refreshControl(); }}
            }}

            async function postDevice(path, dev){{
                const r = await fetch(path, {{method:'POST', headers: headers(), body: JSON.stringify({{device_id: dev}})}});
                return r.ok;
            }}

            function exportCsv(){{
                const table = document.querySelector('table');
                const rows = Array.from(table.querySelectorAll('tr'));
                const csv = rows.map((tr, idx) => {{
                    const cells = Array.from(tr.querySelectorAll(idx === 0 ? 'th' : 'td'));
                    // Omitir la última columna (Acciones)
                    const sel = cells.slice(0, Math.max(0, cells.length - 1));
                    return sel.map(td => '"' + (td.innerText||'').replace(/"/g,'""') + '"').join(',');
                }}).join('\\n');
                const blob = new Blob([csv], {{type: 'text/csv;charset=utf-8;'}});
                const a = document.createElement('a');
                a.href = URL.createObjectURL(blob);
                a.download = 'edumon_dashboard.csv';
                document.body.appendChild(a);
                a.click();
                a.remove();
            }}

            // Event wiring
            saveBtn.addEventListener('click', () => {{ setKey(apiKeyInput.value.trim()); refreshControl(); }});
            stopAllBtn.addEventListener('click', toggleStopAll);
            dlBtn.addEventListener('click', exportCsv);
            document.addEventListener('click', async (e) => {{
                const t = e.target;
                if(t.classList.contains('btn-stop')){{
                    const dev = t.getAttribute('data-dev');
                    await postDevice('/api/v1/control/stop_device', dev);
                    await refreshControl();
                }} else if(t.classList.contains('btn-clear')){{
                    const dev = t.getAttribute('data-dev');
                    await postDevice('/api/v1/control/clear_device', dev);
                    await refreshControl();
                }}
            }});

            // Initialize
            apiKeyInput.value = getKey();
            refreshControl();
        }})();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)
