# EduMon v2.0 - Sistema Educativo de Monitoreo

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com/)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.5+-red.svg)](https://www.riverbankcomputing.com/software/pyqt/)

## 🎯 Descripción

EduMon es un sistema educativo de monitoreo con consentimiento explícito, diseñado para aulas de informática. Permite a los docentes obtener un panorama básico del estado de los equipos durante las clases, respetando la privacidad y con total transparencia.

### ✨ Características Principales

- **🔒 Privacidad por diseño**: Consentimiento explícito, datos mínimos, transparencia total
- **📊 Monitoreo en tiempo real**: CPU, RAM, disco, red, procesos
- **🎓 Enfoque educativo**: Diseñado específicamente para entornos de aprendizaje
- **🔍 Auditoría completa**: Registro detallado de todas las acciones
- **🌐 Interfaz moderna**: Dashboard web responsive y agente PyQt6
- **🐳 Containerizado**: Despliegue fácil con Docker
- **🧪 Probado**: Suite completa de tests unitarios

## 🏗️ Arquitectura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │    Database     │
│   (React/HTML)  │◄──►│   (FastAPI)     │◄──►│  (SQLite/PG)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                ▲
                                │ HTTPS/WSS
                                ▼
                       ┌─────────────────┐
                       │     Agent       │
                       │    (PyQt6)      │
                       └─────────────────┘
```

### 🔧 Componentes

- **Backend**: FastAPI con SQLAlchemy, autenticación JWT, WebSockets
- **Frontend**: Interfaz web moderna (HTML/CSS/JS o React)
- **Agent**: Aplicación PyQt6 con interfaz gráfica avanzada
- **Database**: SQLite (desarrollo) / PostgreSQL (producción)
- **Monitoring**: Prometheus + Grafana (opcional)

## 🚀 Instalación Rápida

### Prerrequisitos

- Python 3.11+
- Docker y Docker Compose (opcional)
- Git

### 1. Clonar el repositorio

```bash
git clone <repository-url>
cd edumon
```

### 2. Opción A: Desarrollo Local

```bash
# Instalar dependencias
make install-dev

# Configurar base de datos
make db-init

# Ejecutar servidor
make run-dev

# En otra terminal, ejecutar agente
make run-agent
```

### 3. Opción B: Docker (Recomendado)

```bash
# Configurar variables de entorno
make setup-env
# Editar docker/.env con tus configuraciones

# Construir y ejecutar
make build-docker
make run-prod
```

## 📖 Guía de Uso

### Para Docentes

1. **Acceder al dashboard**: `http://localhost:8000/dashboard`
2. **Configurar aula**: Crear aula en la sección de administración
3. **Monitorear estudiantes**: Ver métricas en tiempo real
4. **Controlar sesiones**: Detener/permitir agentes individualmente

### Para Estudiantes

1. **Ejecutar agente**: Doble clic en `EduMonAgent.exe`
2. **Dar consentimiento**: Leer y aceptar términos
3. **Monitorear estado**: Ver métricas locales en la interfaz
4. **Detener cuando desee**: Botón "Detener Sesión"

## 🔧 Configuración

### Variables de Entorno

```bash
# Seguridad
EDUMON_API_KEY=tu-clave-api-segura
SECRET_KEY=tu-clave-secreta-jwt

# Base de datos
DATABASE_URL=sqlite:///./edumon.db
# o para PostgreSQL:
# DATABASE_URL=postgresql://user:pass@localhost/edumon

# SSL/TLS (producción)
SSL_CERTFILE=/path/to/cert.pem
SSL_KEYFILE=/path/to/key.pem

# Retención de datos
DATA_RETENTION_DAYS=30
METRICS_RETENTION_DAYS=7
```

### Configuración del Agente

```json
{
  "server_url": "https://tu-servidor.com:8000",
  "api_key": "tu-clave-api",
  "classroom_id": "Aula-1",
  "heartbeat_seconds": 15,
  "collect_disk_metrics": true,
  "collect_network_metrics": true,
  "collect_process_metrics": true,
  "minimize_to_tray": true
}
```

## 🧪 Testing

```bash
# Ejecutar todos los tests
make test

# Tests con cobertura
make test-coverage

# Linting
make lint

# Formateo de código
make format
```

## 📦 Construcción

### Agente Ejecutable

```bash
# Construir ejecutable del agente
make build-agent

# El ejecutable estará en agent/dist/EduMonAgent/
```

### Imágenes Docker

```bash
# Construir imágenes
make build-docker

# Ejecutar en producción
make run-prod
```

## 🔒 Seguridad

### Datos Recopilados

- ✅ Identificador de dispositivo (hash anónimo)
- ✅ Nombre de host y usuario del sistema
- ✅ Métricas de CPU, RAM, disco, red
- ✅ Tiempo de actividad del sistema
- ✅ Procesos activos (solo nombres, no contenido)

### Datos NO Recopilados

- ❌ Capturas de pantalla
- ❌ Pulsaciones de teclado
- ❌ Contenido de archivos
- ❌ Historial de navegación
- ❌ Datos personales

### Medidas de Seguridad

- 🔐 Comunicación HTTPS/TLS
- 🔑 Autenticación con JWT y API Keys
- 📝 Auditoría completa de acciones
- 🕐 Retención limitada de datos
- 🚫 Principio de mínimos privilegios

## 📊 Monitoreo y Métricas

### Dashboard Principal

- Vista en tiempo real de todos los clientes
- Filtros por aula
- Alertas de rendimiento
- Estadísticas agregadas

### Métricas Disponibles

- **Sistema**: CPU, RAM, disco, temperatura
- **Red**: Tráfico enviado/recibido, velocidad
- **Procesos**: Cantidad, top procesos por CPU/RAM
- **Sesión**: Duración, estado, usuario

## 🔧 Desarrollo

### Estructura del Proyecto

```
edumon/
├── backend/           # API FastAPI
│   ├── app/
│   │   ├── api/      # Endpoints REST
│   │   ├── core/     # Configuración, DB, seguridad
│   │   ├── models/   # Modelos SQLAlchemy
│   │   └── services/ # Lógica de negocio
│   └── tests/        # Tests unitarios
├── agent/            # Agente PyQt6
│   ├── core/         # Lógica principal
│   ├── ui/           # Interfaz gráfica
│   └── tests/        # Tests del agente
├── frontend/         # Frontend web
├── docker/           # Configuración Docker
└── docs/             # Documentación
```

### Contribuir

1. Fork del repositorio
2. Crear rama feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -am 'Agregar nueva funcionalidad'`
4. Push a la rama: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

## 📋 Roadmap

### v2.1 (Próximo)
- [ ] Frontend React completo
- [ ] WebSockets para tiempo real
- [ ] Notificaciones push
- [ ] Exportación de reportes PDF

### v2.2 (Futuro)
- [ ] Integración con LMS (Moodle, Canvas)
- [ ] Modo examen con restricciones
- [ ] Análisis predictivo
- [ ] App móvil para docentes

## 🆘 Soporte

### Documentación
- [Manual de Usuario](docs/user-guide.md)
- [Guía de Instalación](docs/installation.md)
- [API Reference](docs/api.md)
- [Troubleshooting](docs/troubleshooting.md)

### Contacto
- 📧 Email: soporte@edumon.com
- 🐛 Issues: [GitHub Issues](https://github.com/tu-usuario/edumon/issues)
- 💬 Discusiones: [GitHub Discussions](https://github.com/tu-usuario/edumon/discussions)

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

## 🙏 Agradecimientos

- [FastAPI](https://fastapi.tiangolo.com/) - Framework web moderno
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - Interfaz gráfica
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM Python
- [psutil](https://github.com/giampaolo/psutil) - Métricas del sistema

---

**⚠️ Uso Responsable**: Este software está diseñado para uso educativo con consentimiento explícito. El uso indebido o sin consentimiento va contra el propósito del proyecto y puede violar leyes de privacidad.