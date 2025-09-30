#!/usr/bin/env python3
"""
Test simple sin emojis para verificar que el sistema funciona
Compatible con Windows
"""
import sys
import os

# Fix encoding for Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def test_imports():
    """Probar importaciones críticas"""
    print("[TEST] Probando importaciones...")
    
    try:
        # Test basic imports
        import uuid
        import json
        from datetime import datetime, timezone
        print("  [OK] Importaciones basicas")
        
        # Test FastAPI
        from fastapi import FastAPI
        print("  [OK] FastAPI")
        
        # Test SQLAlchemy
        from sqlalchemy import create_engine
        print("  [OK] SQLAlchemy")
        
        # Test backend imports
        sys.path.insert(0, 'edumon')
        from backend.app.core.config import settings
        print(f"  [OK] Config - API Key: {settings.EDUMON_API_KEY}")
        
        from backend.app.models import schemas
        print("  [OK] Schemas")
        
        try:
            from backend.app.services.database_service import db_service
            print("  [OK] Database Service")
        except ImportError as e:
            print(f"  [WARN] Database Service: {e}")
        
        return True
        
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False

def test_docker_files():
    """Verificar archivos de Docker"""
    print("\n[TEST] Verificando archivos Docker...")
    
    files = [
        "edumon/docker/docker-compose.yml",
        "edumon/docker/.env",
        "edumon/docker/Dockerfile.backend",
        "edumon/backend/requirements.txt"
    ]
    
    all_ok = True
    for file in files:
        if os.path.exists(file):
            print(f"  [OK] {file}")
        else:
            print(f"  [ERROR] {file} - FALTANTE")
            all_ok = False
    
    return all_ok

def main():
    """Función principal"""
    print("TEST SIMPLE - SecurAula-AI / EduMon")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_docker_files
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"[ERROR] Error en test: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print("[SUCCESS] Todos los tests pasaron!")
        print("[OK] El sistema deberia funcionar correctamente")
        print("\nPuedes ejecutar:")
        print("  python run_server.py")
        print("  INICIAR_SERVIDOR.bat")
        return 0
    else:
        print(f"[WARN] {passed}/{total} tests pasaron")
        print("[ERROR] Revisa los errores arriba")
        return 1

if __name__ == "__main__":
    sys.exit(main())