# 🚀 Instalación Rápida - SecurAula-AI / EduMon

## 📋 Requisitos Previos

1. **Python 3.7+** instalado
   - Windows/Mac/Linux: https://www.python.org/downloads/
   
2. **Docker Desktop** instalado y corriendo
   - Windows/Mac: https://www.docker.com/products/docker-desktop
   - Linux: https://docs.docker.com/engine/install/

## ⚡ Instalación en 2 Pasos

### **Paso 1: Instalar Dependencias**

#### Windows
```bash
# Doble click en:
INSTALAR_DEPENDENCIAS.bat
```

#### Linux/Mac
```bash
# Ejecutar en terminal:
chmod +x instalar_dependencias.sh
./instalar_dependencias.sh
```

#### Manual (cualquier sistema)
```bash
python install_dependencies.py
```

### **Paso 2: Iniciar Servidor**

#### Windows
```bash
# Doble click en:
INICIAR_SERVIDOR.bat
```

#### Linux/Mac
```bash
# Ejecutar en terminal:
./iniciar_servidor.sh
```

#### Manual (cualquier sistema)
```bash
python run_server.py
```

## 🎯 ¡Listo!

Después de estos 2 pasos tendrás:

- ✅ **Backend API** corriendo en http://localhost:8000
- ✅ **Dashboard** disponible en http://localhost:8000/dashboard?api_key=S1R4X
- ✅ **PostgreSQL** base de datos funcionando
- ✅ **pgAdmin** en http://localhost:8080
- ✅ **Metabase** en http://localhost:3000

## 🔑 Credenciales

- **API Key**: `S1R4X`
- **pgAdmin**: `admin@edumon.com / admin123`
- **PostgreSQL**: `edumon / edumon123`

## 🤖 Para Agentes Estudiantes

Los agentes deben conectarse a:
- **URL**: `http://<ip-del-servidor>:8000`
- **API Key**: `S1R4X`

## ⚠️ Solución de Problemas

### Error: "No module named 'sqlalchemy'"
```bash
# Ejecutar el instalador de dependencias:
python install_dependencies.py
```

### Error: "Docker no está corriendo"
```bash
# Iniciar Docker Desktop y volver a intentar
```

### Puerto 8000 ocupado
```bash
# Verificar qué está usando el puerto:
netstat -ano | findstr :8000

# O cambiar el puerto en docker-compose.yml
```

### Problemas de permisos (Linux/Mac)
```bash
# Ejecutar con sudo si es necesario:
sudo ./iniciar_servidor.sh
```

## 📞 Soporte

Si tienes problemas:

1. Ejecuta `python test_quick.py` para diagnosticar
2. Revisa los logs con `docker compose logs -f`
3. Verifica que Docker Desktop esté corriendo
4. Asegúrate de que Python 3.7+ esté instalado

---

**¡Con estos 2 pasos simples tendrás EduMon funcionando completamente!** 🎉