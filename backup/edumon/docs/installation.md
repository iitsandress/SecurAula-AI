# Guía de Instalación - EduMon v2.0

## Requisitos del Sistema

### Servidor
- **Sistema Operativo**: Linux (Ubuntu 20.04+, CentOS 8+), Windows 10+, macOS 10.15+
- **Python**: 3.11 o superior
- **RAM**: Mínimo 2GB, recomendado 4GB
- **Disco**: Mínimo 1GB de espacio libre
- **Red**: Puerto 8000 disponible (configurable)

### Agente
- **Sistema Operativo**: Windows 10+, Linux (Ubuntu 18.04+), macOS 10.14+
- **RAM**: Mínimo 512MB
- **Disco**: 100MB de espacio libre
- **Red**: Acceso HTTP/HTTPS al servidor

## Instalación del Servidor

### Opción 1: Docker (Recomendado)

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/edumon.git
cd edumon

# 2. Configurar variables de entorno
cp docker/.env.example docker/.env
# Editar docker/.env con tus configuraciones

# 3. Construir y ejecutar
docker-compose -f docker/docker-compose.yml up -d

# 4. Verificar instalación
curl http://localhost:8000/health
```

### Opción 2: Instalación Manual

```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/edumon.git
cd edumon

# 2. Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# o
.venv\Scripts\activate     # Windows

# 3. Instalar dependencias
cd backend
pip install -r requirements.txt

# 4. Configurar variables de entorno
export EDUMON_API_KEY="tu-clave-api-segura"
export SECRET_KEY="tu-clave-secreta-jwt"

# 5. Inicializar base de datos
python -c "from app.core.database import create_tables; create_tables()"

# 6. Ejecutar servidor
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Opción 3: Usando Makefile

```bash
# 1. Clonar e instalar
git clone https://github.com/tu-usuario/edumon.git
cd edumon
make install-dev

# 2. Configurar base de datos
make db-init

# 3. Ejecutar en desarrollo
make run-dev
```

## Instalación del Agente

### Windows

1. **Descargar ejecutable**:
   - Ir a [Releases](https://github.com/tu-usuario/edumon/releases)
   - Descargar `EduMonAgent-Setup-x.x.x.exe`

2. **Instalar**:
   ```cmd
   # Ejecutar instalador
   EduMonAgent-Setup-2.0.0.exe
   ```

3. **Configurar**:
   - Ejecutar "EduMon Agent" desde el menú inicio
   - Ir a la pestaña "Configuración"
   - Configurar URL del servidor y clave API

### Linux

1. **Descargar paquete**:
   ```bash
   wget https://github.com/tu-usuario/edumon/releases/download/v2.0.0/edumon-agent-2.0.0-linux.tar.gz
   ```

2. **Extraer e instalar**:
   ```bash
   tar -xzf edumon-agent-2.0.0-linux.tar.gz
   sudo mv edumon-agent /opt/
   sudo ln -s /opt/edumon-agent/EduMonAgent /usr/local/bin/edumon-agent
   ```

3. **Configurar**:
   ```bash
   edumon-agent --config-wizard
   ```

### macOS

1. **Descargar DMG**:
   - Descargar `EduMon-Agent-2.0.0.dmg`

2. **Instalar**:
   - Montar DMG y arrastrar a Applications

3. **Configurar**:
   - Ejecutar desde Applications
   - Configurar en Preferencias

### Compilación desde Código Fuente

```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/edumon.git
cd edumon/agent

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar directamente
python main.py

# 4. O construir ejecutable
cd ..
python scripts/build_agent_advanced.py --windowed --installer
```

## Configuración Inicial

### Servidor

1. **Variables de Entorno**:
   ```bash
   # Seguridad (OBLIGATORIO cambiar en producción)
   EDUMON_API_KEY=tu-clave-api-muy-segura
   SECRET_KEY=tu-clave-secreta-jwt-muy-larga
   
   # Base de datos
   DATABASE_URL=sqlite:///./edumon.db
   # o PostgreSQL:
   # DATABASE_URL=postgresql://user:pass@localhost/edumon
   
   # SSL/TLS (producción)
   SSL_CERTFILE=/path/to/cert.pem
   SSL_KEYFILE=/path/to/key.pem
   ```

2. **Crear Usuario Administrador**:
   ```bash
   python -c "
   from app.core.database import SessionLocal
   from app.models.user import User, UserRole
   from app.core.security import get_password_hash
   
   db = SessionLocal()
   admin = User(
       username='admin',
       email='admin@edumon.local',
       hashed_password=get_password_hash('admin123'),
       full_name='Administrador',
       role=UserRole.ADMIN
   )
   db.add(admin)
   db.commit()
   print('Usuario admin creado')
   "
   ```

### Agente

1. **Configuración Básica** (`config.json`):
   ```json
   {
     "server_url": "https://tu-servidor.com:8000",
     "api_key": "tu-clave-api-muy-segura",
     "classroom_id": "Aula-1",
     "heartbeat_seconds": 15,
     "collect_disk_metrics": true,
     "collect_network_metrics": true,
     "collect_process_metrics": true,
     "minimize_to_tray": true,
     "verify_ssl": true
   }
   ```

2. **Configuración Avanzada**:
   ```json
   {
     "server_url": "https://edumon.escuela.edu:8000",
     "api_key": "clave-api-super-segura-2024",
     "classroom_id": "Informatica-Lab1",
     "heartbeat_seconds": 10,
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

## Configuración de Red

### Firewall

**Servidor**:
```bash
# Ubuntu/Debian
sudo ufw allow 8000/tcp

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload

# Windows
netsh advfirewall firewall add rule name="EduMon Server" dir=in action=allow protocol=TCP localport=8000
```

**Agente**: No requiere puertos entrantes.

### Proxy/Load Balancer

**Nginx** (`/etc/nginx/sites-available/edumon`):
```nginx
server {
    listen 80;
    server_name edumon.tu-escuela.edu;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name edumon.tu-escuela.edu;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## SSL/TLS

### Certificados Autofirmados (Desarrollo)

```bash
# Generar certificados
make generate-ssl

# O manualmente:
openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes \
    -subj "/C=ES/ST=Madrid/L=Madrid/O=EduMon/CN=localhost"
```

### Let's Encrypt (Producción)

```bash
# Instalar certbot
sudo apt install certbot

# Obtener certificado
sudo certbot certonly --standalone -d edumon.tu-escuela.edu

# Configurar renovación automática
sudo crontab -e
# Agregar: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Base de Datos

### SQLite (Desarrollo)
- Configuración automática
- Archivo: `edumon.db`
- Sin configuración adicional

### PostgreSQL (Producción)

```bash
# Instalar PostgreSQL
sudo apt install postgresql postgresql-contrib

# Crear base de datos
sudo -u postgres createuser edumon
sudo -u postgres createdb edumon -O edumon
sudo -u postgres psql -c "ALTER USER edumon PASSWORD 'password123';"

# Configurar variable de entorno
export DATABASE_URL="postgresql://edumon:password123@localhost/edumon"
```

## Verificación de Instalación

### Servidor

```bash
# Health check
curl http://localhost:8000/health

# API check
curl -H "X-API-Key: tu-clave-api" http://localhost:8000/api/v1/clients/statistics

# Dashboard
# Abrir http://localhost:8000/dashboard en navegador
```

### Agente

```bash
# Modo headless
edumon-agent --headless

# Con GUI
edumon-agent

# Verificar configuración
edumon-agent --config-wizard
```

## Solución de Problemas

### Errores Comunes

1. **Puerto 8000 en uso**:
   ```bash
   # Cambiar puerto
   uvicorn app.main:app --port 8080
   ```

2. **Error de permisos SQLite**:
   ```bash
   # Dar permisos al directorio
   chmod 755 /path/to/edumon
   chmod 664 /path/to/edumon/edumon.db
   ```

3. **Agente no conecta**:
   - Verificar URL del servidor
   - Verificar clave API
   - Verificar firewall
   - Verificar certificados SSL

### Logs

**Servidor**:
```bash
# Logs de aplicación
tail -f logs/edumon.log

# Logs de auditoría
tail -f logs/audit.log
```

**Agente**:
```bash
# Logs del agente
tail -f logs/agent_YYYYMMDD.log

# Logs de auditoría
tail -f logs/audit.log
```

## Actualización

### Servidor

```bash
# Docker
docker-compose -f docker/docker-compose.yml pull
docker-compose -f docker/docker-compose.yml up -d

# Manual
git pull
pip install -r backend/requirements.txt
# Reiniciar servicio
```

### Agente

1. Descargar nueva versión
2. Detener agente actual
3. Instalar nueva versión
4. Verificar configuración
5. Iniciar nuevo agente

## Desinstalación

### Servidor

```bash
# Docker
docker-compose -f docker/docker-compose.yml down -v

# Manual
# Detener servicio
# Eliminar directorio del proyecto
# Eliminar base de datos si es necesario
```

### Agente

**Windows**: Panel de Control > Programas > Desinstalar EduMon Agent

**Linux/macOS**: 
```bash
sudo rm -rf /opt/edumon-agent
sudo rm /usr/local/bin/edumon-agent
```