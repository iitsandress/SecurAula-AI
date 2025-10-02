#!/usr/bin/env python3
"""
Script de verificación para SecurAula-AI / EduMon
Verifica que todas las configuraciones sean consistentes
"""
import os
import json
import sys
import requests
from pathlib import Path

def check_api_keys():
    """Verificar consistencia de API keys"""
    print("🔑 Verificando API Keys...")
    
    # Archivos a verificar
    files_to_check = [
        "backend/app/core/config.py",
        "agent/config.example.json", 
        "agent/main_simple.py",
        "docker/.env",
        "server/control.py",
        "server/dashboard.py"
    ]
    
    api_keys = {}
    base_path = Path(__file__).parent.parent
    
    for file_path in files_to_check:
        full_path = base_path / file_path
        if full_path.exists():
            try:
                content = full_path.read_text(encoding='utf-8')
                if 'S1R4X' in content:
                    api_keys[file_path] = 'S1R4X'
                elif 'changeme' in content:
                    api_keys[file_path] = 'changeme'
                elif 'por-favor-cambie' in content:
                    api_keys[file_path] = 'por-favor-cambie'
            except Exception as e:
                print(f"  ⚠️  Error leyendo {file_path}: {e}")
    
    # Verificar consistencia
    unique_keys = set(api_keys.values())
    if len(unique_keys) == 1 and 'S1R4X' in unique_keys:
        print("  ✅ API Keys consistentes (S1R4X)")
        return True
    else:
        print("  ❌ API Keys inconsistentes:")
        for file, key in api_keys.items():
            print(f"    {file}: {key}")
        return False

def check_ports():
    """Verificar consistencia de puertos"""
    print("\n🔌 Verificando Puertos...")
    
    expected_ports = {
        "backend": 8000,
        "postgres": 5432,
        "pgadmin": 8080,
        "metabase": 3000
    }
    
    # Verificar docker-compose.yml
    compose_file = Path(__file__).parent.parent / "docker" / "docker-compose.yml"
    if compose_file.exists():
        content = compose_file.read_text()
        
        checks = {
            "backend": "8000:8000" in content,
            "postgres": "5432:5432" in content,
            "pgadmin": "8080:80" in content,
            "metabase": "3000:3000" in content
        }
        
        all_good = all(checks.values())
        if all_good:
            print("  ✅ Puertos configurados correctamente")
            return True
        else:
            print("  ❌ Problemas en configuración de puertos:")
            for service, ok in checks.items():
                status = "✅" if ok else "❌"
                print(f"    {status} {service}: {expected_ports[service]}")
            return False
    else:
        print("  ❌ docker-compose.yml no encontrado")
        return False

def check_database_config():
    """Verificar configuración de base de datos"""
    print("\n🗄️  Verificando Configuración de Base de Datos...")
    
    # Verificar .env
    env_file = Path(__file__).parent.parent / "docker" / ".env"
    if env_file.exists():
        content = env_file.read_text()
        
        required_vars = ["DB_USER", "DB_PASSWORD", "DB_NAME"]
        missing_vars = []
        
        for var in required_vars:
            if f"{var}=" not in content:
                missing_vars.append(var)
        
        if not missing_vars:
            print("  ✅ Variables de base de datos configuradas")
            return True
        else:
            print(f"  ❌ Variables faltantes: {', '.join(missing_vars)}")
            return False
    else:
        print("  ❌ Archivo .env no encontrado")
        return False

def check_agent_config():
    """Verificar configuración del agente"""
    print("\n🤖 Verificando Configuración del Agente...")
    
    config_file = Path(__file__).parent.parent / "agent" / "config.example.json"
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            checks = {
                "server_url": config.get("server_url", "").startswith("http://"),
                "api_key": config.get("api_key") == "S1R4X",
                "heartbeat_seconds": isinstance(config.get("heartbeat_seconds"), int)
            }
            
            all_good = all(checks.values())
            if all_good:
                print("  ✅ Configuración del agente correcta")
                return True
            else:
                print("  ❌ Problemas en configuración del agente:")
                for check, ok in checks.items():
                    status = "✅" if ok else "❌"
                    print(f"    {status} {check}")
                return False
        except Exception as e:
            print(f"  ❌ Error leyendo configuración: {e}")
            return False
    else:
        print("  ❌ config.example.json no encontrado")
        return False

def check_requirements():
    """Verificar archivos de requirements"""
    print("\n📦 Verificando Requirements...")
    
    req_files = [
        "backend/requirements.txt",
        "requirements-server.txt",
        "requirements-agent.txt"
    ]
    
    base_path = Path(__file__).parent.parent
    all_good = True
    
    for req_file in req_files:
        full_path = base_path / req_file
        if full_path.exists():
            print(f"  ✅ {req_file} existe")
        else:
            print(f"  ❌ {req_file} no encontrado")
            all_good = False
    
    return all_good

def test_server_connectivity():
    """Probar conectividad con el servidor (si está corriendo)"""
    print("\n🌐 Probando Conectividad del Servidor...")
    
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("  ✅ Servidor respondiendo correctamente")
            print(f"    Versión: {data.get('version', 'N/A')}")
            print(f"    API Key configurada: {data.get('api_key_configured', False)}")
            print(f"    Database Service: {data.get('database_service', False)}")
            return True
        else:
            print(f"  ⚠️  Servidor responde con código: {response.status_code}")
            return False
    except ImportError:
        print("  ℹ️  requests no disponible, saltando verificación")
        return True
    except requests.exceptions.ConnectionError:
        print("  ℹ️  Servidor no está corriendo (normal si no se ha iniciado)")
        return True  # No es un error si no está corriendo
    except Exception as e:
        print(f"  ❌ Error conectando: {e}")
        return False

def main():
    """Función principal"""
    print("🔍 VERIFICACIÓN DE CONFIGURACIÓN - SecurAula-AI / EduMon")
    print("=" * 60)
    
    checks = [
        check_api_keys,
        check_ports,
        check_database_config,
        check_agent_config,
        check_requirements,
        test_server_connectivity
    ]
    
    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            print(f"  ❌ Error en verificación: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print("🎉 ¡Todas las verificaciones pasaron!")
        print("✅ El sistema está listo para usar")
        return 0
    else:
        print(f"⚠️  {passed}/{total} verificaciones pasaron")
        print("❌ Revisa los problemas indicados arriba")
        return 1

if __name__ == "__main__":
    sys.exit(main())