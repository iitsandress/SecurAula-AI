# SecurAula-AI - Sistema de Monitoreo Educativo

## 📁 Estructura del Proyecto

```
SERVIDOR FINAL/
├── server/                     # Servidor Node.js
│   ├── server.js              # Servidor principal (mejorado)
│   ├── server_original.js     # Servidor original (backup)
│   ├── package.json           # Dependencias Node.js
│   ├── package-lock.json      # Lock de dependencias
│   ├── dashboard.html         # Dashboard web
│   ├── start_server.bat       # Script de inicio automático
│   └── node_modules/          # Módulos Node.js instalados
├── agent/                     # Agente de monitoreo
│   ├── main.py               # Agente principal con GUI
│   ├── main_simple.py        # Agente simple sin GUI
│   ├── main_simple_windows.py # Agente compatible con Windows
│   ├── agent.py              # Lógica del agente
│   ├── config.json           # Configuración del agente
│   ├── config.example.json   # Ejemplo de configuración
│   ├── device_id.txt         # ID único del dispositivo
│   ├── README_AGENT.md       # Documentación del agente
│   ├── core/                 # Módulos principales
│   │   ├── agent_core.py     # Núcleo del agente
│   │   ├── api_client.py     # Cliente API
│   │   ├── config.py         # Gestión de configuración
│   │   ├── logging_config.py # Configuración de logs
│   │   └── metrics.py        # Recolección de métricas
│   └── ui/                   # Interfaz gráfica
│       ├── gui_pyqt.py       # GUI con PyQt
│       └── main_window.py    # Ventana principal
├── docs/                     # Documentación
│   ├── SERVER_MANAGEMENT.md  # Guía de gestión del servidor
│   └── EDUMON_SETUP_COMPLETE.md # Guía de configuración completa
└── README.md                 # Este archivo
```

## 🚀 Inicio Rápido

### 1. Iniciar el Servidor

```bash
cd server
# Opción 1: Script automático (recomendado)
start_server.bat

# Opción 2: Manual
node server.js

# Opción 3: Puerto personalizado
set PORT=3001 && node server.js
```

### 2. Configurar Ngrok (Túnel Público)

```bash
# En una nueva terminal
ngrok http 3000
```

Copia la URL pública (ej: `https://xxxx.ngrok-free.app`)

### 3. Ejecutar el Agente

```bash
cd agent
# Versión compatible con Windows (recomendado)
python main_simple_windows.py

# Versión simple original
python main_simple.py

# Versión completa con GUI
python main.py
```

## ⚙️ Configuración

### Servidor
- **Puerto**: 3000 (configurable con variable PORT)
- **API Key**: S1R4X
- **Dashboard**: Accesible en la URL del servidor

### Agente
Edita `agent/config.json`:
```json
{
  "server_url": "https://tu-ngrok-url.ngrok-free.app",
  "api_key": "S1R4X",
  "heartbeat_seconds": 15,
  "classroom_id": "Aula-1"
}
```

## 📊 Características

### Servidor
✅ **API RESTful** para registro y monitoreo de dispositivos
✅ **Dashboard web** con visualización en tiempo real
✅ **Gestión de sesiones** y autenticación por API key
✅ **Manejo de errores** mejorado y logs detallados
✅ **Compatibilidad con ngrok** para acceso público

### Agente
✅ **Recolección de métricas** del sistema (CPU, RAM, disco, red)
✅ **Consentimiento explícito** del usuario
✅ **Múltiples versiones** (GUI, consola, Windows-compatible)
✅ **Configuración flexible** via JSON
✅ **Desconexión limpia** con Ctrl+C

### Métricas Recolectadas
- **CPU**: Porcentaje de uso
- **Memoria**: Porcentaje de RAM utilizada
- **Disco**: Porcentaje de almacenamiento usado
- **Red**: Bytes enviados/recibidos
- **Procesos**: Cantidad de procesos activos
- **Uptime**: Tiempo de actividad del sistema
- **Información del dispositivo**: Hostname, usuario, ID único

## 🛡️ Privacidad y Seguridad

### ✅ Datos Recolectados
- Métricas de rendimiento del sistema
- Identificador anónimo del dispositivo
- Nombre del host y usuario del sistema
- Información de procesos (solo nombres)

### ❌ Datos NO Recolectados
- Capturas de pantalla
- Pulsaciones de teclado
- Contenido de archivos
- Historial de navegación
- Datos personales sensibles

### 🔒 Medidas de Seguridad
- Consentimiento explícito requerido
- API key para autenticación
- Comunicación HTTPS via ngrok
- Logs de auditoría locales
- Desconexión voluntaria disponible

## 🔧 Requisitos del Sistema

### Servidor
- **Node.js** 14+ 
- **npm** (incluido con Node.js)
- **Ngrok** (para acceso público)

### Agente
- **Python** 3.7+
- **Librerías**: `psutil`, `requests` (instaladas automáticamente)
- **Opcional**: `PyQt6` (para versión con GUI)

## 📱 Endpoints de la API

### Registro de Dispositivo
```
POST /api/v1/register
Content-Type: application/json
X-API-Key: S1R4X

{
  "device_id": "uuid",
  "hostname": "nombre-pc",
  "username": "usuario",
  "consent": true,
  "classroom_id": "Aula-1"
}
```

### Envío de Métricas
```
POST /api/v1/heartbeat
Content-Type: application/json
X-API-Key: S1R4X

{
  "device_id": "uuid",
  "session_id": "session-uuid",
  "metrics": {
    "cpu_percent": 25.5,
    "mem_percent": 60.2,
    "disk_percent": 45.0
  }
}
```

### Consulta de Dispositivos
```
GET /api/v1/devices
```

### Desregistro
```
POST /api/v1/unregister
Content-Type: application/json
X-API-Key: S1R4X

{
  "device_id": "uuid",
  "session_id": "session-uuid",
  "reason": "user_request"
}
```

## 🆘 Solución de Problemas

### Puerto en Uso
```bash
# Encontrar proceso
netstat -ano | findstr :3000

# Terminar proceso
taskkill /PID <PID> /F
```

### Agente No Conecta
1. Verificar que el servidor esté ejecutándose
2. Comprobar la URL de ngrok en `config.json`
3. Verificar la API key
4. Revisar conectividad de red

### Errores de Unicode (Windows)
Usar la versión compatible: `main_simple_windows.py`

## 📞 Soporte

Para problemas o preguntas:
1. Revisar la documentación en `docs/`
2. Verificar los logs del servidor y agente
3. Comprobar la configuración en `config.json`

## 📄 Licencia

Este proyecto es parte del sistema SecurAula-AI para monitoreo educativo.

---

**¡Sistema listo para usar en entornos educativos!** 🎓