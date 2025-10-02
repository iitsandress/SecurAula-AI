# EduMon Agent Configuration Guide

This guide will help you configure the EduMon agent to connect to your ngrok-exposed server.

## Prerequisites

1. **Python 3.10+** installed on your system
2. **Node.js server** running (from `new_nodejs_server` directory)
3. **ngrok** tunnel active and exposing your Node.js server

## Step 1: Navigate to the Agent Directory

```bash
cd backup/edumon/agent
```

## Step 2: Install Python Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

If you don't have pip, you can install the dependencies manually:

```bash
pip install requests psutil PyQt6
```

**Note:** PyQt6 is optional - if it's not available, the agent will run in headless mode.

## Step 3: Configure the Agent

The agent configuration file `config.json` is already present with the correct API key. You just need to update the server URL with your ngrok URL.

### Current Configuration:
```json
{
  "server_url": "<YOUR_NGROK_URL>",
  "api_key": "S1R4X"
}
```

### Update the Server URL:

1. **Get your ngrok URL**: When you run ngrok, it will display a URL like:
   ```
   https://xxxx-xxxx-xxxx-xxxx.ngrok-free.app
   ```

2. **Update config.json**: Replace `<YOUR_NGROK_URL>` with your actual ngrok URL:
   ```json
   {
     "server_url": "https://xxxx-xxxx-xxxx-xxxx.ngrok-free.app",
     "api_key": "S1R4X"
   }
   ```

### Example Configuration Update:

If your ngrok URL is `https://1234-5678-9abc-def0.ngrok-free.app`, your `config.json` should look like:

```json
{
  "server_url": "https://1234-5678-9abc-def0.ngrok-free.app",
  "api_key": "S1R4X"
}
```

## Step 4: Run the EduMon Agent

You have two options to run the agent:

### Option A: Full Agent (with GUI if available)
```bash
python main.py
```

### Option B: Simple Agent (headless mode)
```bash
python main_simple.py
```

**Recommended:** Start with `main_simple.py` as it has fewer dependencies and is easier to troubleshoot.

## Step 5: Verify Connection

When you run the agent, you should see output similar to:

```
🎓 EduMon Agent - Versión Simple
========================================

🎓 EDUMON - CONSENTIMIENTO PARA MONITOREO EDUCATIVO
============================================================

Este agente enviará ÚNICAMENTE los siguientes datos:
✅ Identificador del equipo (anónimo)
✅ Nombre del host y usuario del sistema
✅ Métricas de rendimiento: CPU, RAM, disco, red
✅ Tiempo de actividad del sistema
✅ Información de procesos (solo nombres)

❌ NUNCA se capturan:
❌ Capturas de pantalla
❌ Pulsaciones de teclado
❌ Contenido de archivos
❌ Historial de navegación
❌ Datos personales

🛑 Puedes detener el monitoreo en cualquier momento con Ctrl+C
============================================================

¿Acepta participar en esta sesión de monitoreo? (si/no): si

🔗 Conectando con servidor: https://your-ngrok-url.ngrok-free.app
✅ Registro exitoso. Session ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

🚀 AGENTE INICIADO
========================================
🆔 Device ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
🔗 Servidor: https://your-ngrok-url.ngrok-free.app
🏫 Aula: Aula-1
⏱️  Intervalo: 15 segundos

⚠️  Presiona Ctrl+C para detener
========================================

📊 Métricas enviadas - CPU: 15.2% RAM: 45.8%
```

## Step 6: Access the Dashboard

Open your web browser and navigate to your ngrok URL (the same one you configured in the agent). You should see the EduMon dashboard displaying the connected agents and their metrics.

## Troubleshooting

### Common Issues:

1. **Connection Refused**: 
   - Verify your Node.js server is running
   - Check that ngrok is active and the URL is correct
   - Ensure the ngrok URL in `config.json` matches exactly

2. **API Key Error**:
   - The API key is already correctly set to "S1R4X"
   - If you modified the server, ensure it expects the same API key

3. **Python Dependencies**:
   - Install missing packages: `pip install requests psutil`
   - For GUI mode: `pip install PyQt6`

4. **Permission Issues**:
   - Run the command prompt/terminal as administrator if needed
   - Ensure Python has network access permissions

### Configuration Options:

You can extend the `config.json` with additional options from `config.example.json`:

```json
{
  "server_url": "https://your-ngrok-url.ngrok-free.app",
  "api_key": "S1R4X",
  "classroom_id": "Aula-1",
  "heartbeat_seconds": 15,
  "auto_start": false,
  "minimize_to_tray": true,
  "enable_notifications": true,
  "log_level": "INFO",
  "collect_disk_metrics": true,
  "collect_network_metrics": true,
  "collect_process_metrics": true,
  "collect_temperature": false,
  "verify_ssl": true,
  "timeout_seconds": 10
}
```

## Security Notes

- The agent only collects system performance metrics
- No personal data, screenshots, or keystrokes are captured
- All data transmission uses the configured API key for authentication
- You can stop the agent at any time with Ctrl+C

## Next Steps

Once the agent is running and connected:

1. **Monitor the dashboard** - Check that your device appears in the web interface
2. **Test metrics** - Verify that CPU, RAM, and other metrics are being displayed
3. **Multiple agents** - You can run this setup on multiple computers to monitor a classroom

---

**Important**: Remember to replace `<YOUR_NGROK_URL>` in the `config.json` file with your actual ngrok URL before running the agent!