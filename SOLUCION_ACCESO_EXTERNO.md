# 🌐 Solución: Acceso Externo al Dashboard EduMon

## 🎯 Problema Identificado

Tu servidor EduMon está corriendo correctamente con Docker, pero **no es accesible desde tu IP externa** (`190.84.119.196:8000`). El error "se tardó mucho en responder" indica que el servidor no está configurado para aceptar conexiones externas.

## 🔍 Causa Principal

El problema está en la configuración de Docker Compose. Los puertos están mapeados como:
```yaml
ports:
  - "8000:8000"  # ❌ Solo escucha en localhost
```

En lugar de:
```yaml
ports:
  - "0.0.0.0:8000:8000"  # ✅ Escucha en todas las interfaces
```

## 🚀 Solución Rápida (Recomendada)

### Opción 1: Script Automático
```bash
python fix_acceso_externo.py
```

Este script:
- ✅ Para los contenedores actuales
- ✅ Inicia con configuración de acceso externo
- ✅ Muestra comandos de firewall
- ✅ Crea script de gestión

### Opción 2: Manual
1. **Detener contenedores actuales:**
   ```bash
   cd edumon/docker
   docker compose down
   ```

2. **Usar configuración externa:**
   ```bash
   docker compose -f docker-compose-external.yml up -d --build
   ```

3. **Configurar firewall (Ubuntu/Debian):**
   ```bash
   sudo ufw allow 8000/tcp
   sudo ufw allow 8080/tcp
   sudo ufw allow 3000/tcp
   sudo ufw reload
   ```

## 🔧 Diagnóstico Completo

Para diagnosticar todos los aspectos del problema:
```bash
python diagnostico_servidor.py
```

Este script verifica:
- 🐳 Estado de Docker y contenedores
- 🔍 Conectividad local
- 🔌 Configuración de puertos
- 🔥 Estado del firewall
- 📋 Soluciones específicas

## 🌐 Configuración de Red Adicional

### 1. Firewall del Sistema

**Ubuntu/Debian (UFW):**
```bash
sudo ufw allow 8000/tcp
sudo ufw allow 8080/tcp
sudo ufw allow 3000/tcp
sudo ufw reload
```

**CentOS/RHEL/Fedora (firewalld):**
```bash
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --permanent --add-port=3000/tcp
sudo firewall-cmd --reload
```

**iptables:**
```bash
sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 3000 -j ACCEPT
sudo iptables-save > /etc/iptables/rules.v4
```

### 2. Router/NAT (Si estás detrás de un router)

Configurar **Port Forwarding** en tu router:
- Puerto externo: `8000` → IP interna: `[tu_ip_local]:8000`
- Puerto externo: `8080` → IP interna: `[tu_ip_local]:8080`
- Puerto externo: `3000` → IP interna: `[tu_ip_local]:3000`

### 3. Proveedor de Internet

Algunos proveedores bloquean ciertos puertos. Si el problema persiste:
- Contactar al proveedor para verificar si bloquean el puerto 8000
- Considerar usar un puerto alternativo (ej: 8443, 9000)

## 📊 URLs de Acceso Después de la Corrección

### Acceso Local:
- **Dashboard:** `http://[tu_ip_local]:8000/dashboard?api_key=S1R4X`
- **Health:** `http://[tu_ip_local]:8000/health`
- **pgAdmin:** `http://[tu_ip_local]:8080`
- **Metabase:** `http://[tu_ip_local]:3000`

### Acceso Externo:
- **Dashboard:** `http://190.84.119.196:8000/dashboard?api_key=S1R4X`
- **Health:** `http://190.84.119.196:8000/health`
- **pgAdmin:** `http://190.84.119.196:8080`
- **Metabase:** `http://190.84.119.196:3000`

## 🛠️ Gestión del Servidor

Después de aplicar la solución, usa el script de gestión:

```bash
# Iniciar servidor
./manage_edumon.sh start

# Detener servidor
./manage_edumon.sh stop

# Reiniciar servidor
./manage_edumon.sh restart

# Ver estado
./manage_edumon.sh status

# Ver logs
./manage_edumon.sh logs
```

## 🧪 Verificación

### 1. Prueba Local
```bash
curl http://localhost:8000/health
```

### 2. Prueba desde IP Local
```bash
curl http://[tu_ip_local]:8000/health
```

### 3. Prueba Externa
Desde otra máquina:
```bash
curl http://190.84.119.196:8000/health
```

## 🚨 Troubleshooting

### Si aún no funciona:

1. **Verificar que Docker escuche en 0.0.0.0:**
   ```bash
   netstat -tlnp | grep :8000
   # Debe mostrar: 0.0.0.0:8000
   ```

2. **Verificar logs del contenedor:**
   ```bash
   cd edumon/docker
   docker compose -f docker-compose-external.yml logs backend
   ```

3. **Verificar conectividad de red:**
   ```bash
   telnet 190.84.119.196 8000
   ```

4. **Verificar desde otra máquina en la misma red:**
   ```bash
   curl http://[tu_ip_local]:8000/health
   ```

## 🔒 Consideraciones de Seguridad

Al exponer el servidor externamente:

1. **Cambiar credenciales por defecto:**
   - API Key: Cambiar `S1R4X` por algo más seguro
   - pgAdmin: Cambiar `admin@edumon.com / admin123`

2. **Usar HTTPS en producción:**
   - Configurar certificados SSL/TLS
   - Usar un proxy reverso (nginx, traefik)

3. **Configurar autenticación adicional:**
   - Implementar autenticación de usuarios
   - Restringir acceso por IP si es posible

## 📁 Archivos Creados

- ✅ `docker-compose-external.yml` - Configuración corregida
- ✅ `fix_acceso_externo.py` - Script de solución automática
- ✅ `diagnostico_servidor.py` - Script de diagnóstico completo
- ✅ `manage_edumon.sh` - Script de gestión del servidor

## 🎉 Resultado Esperado

Después de aplicar la solución:
- ✅ Dashboard accesible desde `http://190.84.119.196:8000/dashboard?api_key=S1R4X`
- ✅ Agentes pueden conectarse desde otras máquinas
- ✅ Monitoreo en tiempo real funcionando
- ✅ Acceso a pgAdmin y Metabase desde externa

---

**¡Tu servidor EduMon estará completamente accesible desde cualquier ubicación! 🌐📊**