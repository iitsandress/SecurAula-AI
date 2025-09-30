EduMon Servidor - Guía rápida

Requisitos
- Python 3.10+

Instalación
1) cd edumon/server
2) pip install -r requirements.txt
3) Configure variables:
   - EDUMON_API_KEY (obligatoria)
   - EDUMON_DATA_DIR (opcional, por defecto ./data)
   - EDUMON_CLIENTS_TTL_SECONDS (opcional, por defecto 30 días)
   - EDUMON_LOG_TTL_SECONDS (opcional, por defecto 30 días)

Ejecución
- Uvicorn (desarrollo):
  uvicorn main:app --reload --host 0.0.0.0 --port 8000

Endpoints
- GET /health
- POST /api/v1/register
- POST /api/v1/heartbeat
- POST /api/v1/unregister
- GET /api/v1/clients
- GET /dashboard (HTML, protegido por X-API-Key)

Seguridad
- Todas las rutas (excepto /health) requieren X-API-Key.
- Datos mínimos, auditoría en logs/audit.log (JSONL)

Retención
- Limpieza ligera al consultar /api/v1/clients (purga por TTL y rotación simple de audit.log)
