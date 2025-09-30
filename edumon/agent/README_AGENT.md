EduMon Agente - Guía rápida

Requisitos
- Python 3.10+
- En Windows, Tkinter suele venir con Python oficial. Si no, el agente funcionará en modo consola.

Instalación
1) cd edumon/agent
2) pip install -r requirements.txt
3) Copie config.example.json a config.json y edite:
   - server_url: URL del servidor (p. ej., http://127.0.0.1:8000)
   - api_key: misma clave que EDUMON_API_KEY en el servidor
   - heartbeat_seconds: intervalo entre envíos (ej. 15)

Ejecución
- python main.py

Privacidad
- Muestra diálogo de consentimiento. Si se rechaza, el agente termina.
- Ventana visible con botón “Detener” para finalizar la sesión (envía unregister).
- Solo envía: CPU %, RAM %, uptime, hostname, usuario e ID de dispositivo anon.
- Logs locales en agent/logs/agent_audit.log
