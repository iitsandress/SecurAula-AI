# 🚀 SecurAula-AI / EduMon - Servidor Automatizado

## 📋 Descripción

Este sistema automatiza completamente el levantamiento del servidor EduMon con Docker. **Un solo click** para tener todo funcionando.

## 🎯 Características

✅ **Verificación automática** de Docker y dependencias  
✅ **Construcción automática** de contenedores  
✅ **Levantamiento automático** de todos los servicios  
✅ **Verificación de salud** de los servicios  
✅ **URLs de acceso** mostradas automáticamente  
✅ **Gestión interactiva** del servidor  

## 🚀 Uso Rápido

### Windows
```bash
# Doble click en:
INICIAR_SERVIDOR.bat
```

### Linux/Mac
```bash
# Ejecutar en terminal:
./iniciar_servidor.sh
```

### Manual (cualquier sistema)
```bash
python run_server.py
```

## 📋 Requisitos Previos

1. **Docker Desktop** instalado y corriendo
   - Windows/Mac: https://www.docker.com/products/docker-desktop
   - Linux: https://docs.docker.com/engine/install/

2. **Python 3.7+** instalado
   - https://www.python.org/downloads/

## 🔧 Lo que hace automáticamente

1. **Verifica Docker** - Comprueba que Docker esté instalado y corriendo
2. **Verifica archivos** - Confirma que todos los archivos necesarios existan
3. **Para contenedores** - Detiene contenedores existentes si los hay
4. **Construye imágenes** - Construye las imágenes Docker necesarias
5. **Levanta servicios** - Inicia todos los contenedores (PostgreSQL, Backend, pgAdmin, Metabase)
6. **Verifica salud** - Comprueba que todos los servicios respondan
7. **Muestra URLs** - Proporciona todas las URLs de acceso

## 🌐 Servicios Incluidos

| Servicio | Puerto | URL | Descripción |
|----------|--------|-----|-------------|
| **Backend API** | 8000 | http://localhost:8000 | API principal del servidor |
| **Dashboard** | 8000 | http://localhost:8000/dashboard?api_key=S1R4X | Panel de control del profesor |
| **PostgreSQL** | 5432 | - | Base de datos principal |
| **pgAdmin** | 8080 | http://localhost:8080 | Administración de base de datos |
| **Metabase** | 3000 | http://localhost:3000 | Analytics y reportes |

## 🔑 Credenciales

### API Key
```
S1R4X
```

### pgAdmin
```
Email: admin@edumon.com
Password: admin123
```

### PostgreSQL
```
Usuario: edumon
Password: edumon123
Base de datos: edumon
```

## 🛠️ Gestión del Servidor

Una vez iniciado, el script ofrece opciones interactivas:

1. **Ver logs en tiempo real** - Monitorea la actividad del servidor
2. **Parar servidor** - Detiene todos los contenedores
3. **Reiniciar servidor** - Reinicia todos los servicios
4. **Salir** - Deja el servidor corriendo en segundo plano

## 📊 Comandos Útiles

### Ver estado de contenedores
```bash
cd edumon/docker
docker compose ps
```

### Ver logs
```bash
cd edumon/docker
docker compose logs -f
```

### Parar servidor
```bash
cd edumon/docker
docker compose down
```

### Reiniciar servidor
```bash
cd edumon/docker
docker compose restart
```

## 🤖 Para Agentes Estudiantes

Los agentes deben conectarse a:
- **URL**: `http://<ip-del-servidor>:8000`
- **API Key**: `S1R4X`

## ⚠️ Solución de Problemas

### Docker no está corriendo
```bash
# Inicia Docker Desktop y vuelve a ejecutar el script
```

### Puerto 8000 ocupado
```bash
# Verifica qué está usando el puerto:
netstat -ano | findstr :8000

# O modifica el puerto en docker-compose.yml
```

### Contenedores no inician
```bash
# Limpia contenedores y vuelve a intentar:
cd edumon/docker
docker compose down -v
docker system prune -f
```

### Problemas de permisos (Linux/Mac)
```bash
# Ejecuta con sudo si es necesario:
sudo ./iniciar_servidor.sh
```

## 📝 Logs

Los logs se muestran automáticamente durante el inicio. Para ver logs después:

```bash
cd edumon/docker
docker compose logs -f backend    # Solo backend
docker compose logs -f postgres   # Solo base de datos
docker compose logs -f            # Todos los servicios
```

## 🔄 Actualizaciones

Para actualizar el servidor:

1. Para el servidor actual
2. Ejecuta `git pull` para obtener cambios
3. Vuelve a ejecutar el script de inicio

## 📞 Soporte

Si tienes problemas:

1. Verifica que Docker Desktop esté corriendo
2. Revisa los logs para errores específicos
3. Asegúrate de que los puertos no estén ocupados
4. Consulta la documentación de Docker si hay problemas de contenedores

---

**¡Con este sistema automatizado, tener EduMon funcionando es tan fácil como un click!** 🎉