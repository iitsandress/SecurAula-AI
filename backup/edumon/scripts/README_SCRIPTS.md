Scripts de ayuda (Windows)

- scripts/install_windows.ps1
  Instala dependencias del servidor y del agente con el Python por defecto.
  Uso: PowerShell
    ./scripts/install_windows.ps1

- scripts/run_server_windows.ps1
  Lanza el servidor (requiere EDUMON_API_KEY).
  Uso: PowerShell
    $env:EDUMON_API_KEY="su-clave"
    ./scripts/run_server_windows.ps1 -Port 8000

- scripts/run_agent_windows.ps1
  Lanza el agente (requiere agent/config.json).
  Uso: PowerShell
    ./scripts/run_agent_windows.ps1

- scripts/build_agent_windows.ps1
  Empaqueta el agente en un ejecutable con PyInstaller (one-dir) para facilitar su despliegue en varios equipos. Puede incluir un config.json junto al ejecutable.
  Uso: PowerShell
    ./scripts/build_agent_windows.ps1
