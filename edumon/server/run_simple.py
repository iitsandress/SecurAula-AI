#!/usr/bin/env python3
"""
Script simple para ejecutar el servidor EduMon
"""
import os
import sys

# Configurar variables de entorno
os.environ["EDUMON_API_KEY"] = "S1R4X"

print("🎓 EduMon Server - Programa del Profesor")
print("=" * 40)
print(f"🔑 API Key: {os.environ.get('EDUMON_API_KEY')}")
print(f"📁 Directorio: {os.getcwd()}")
print("🚀 Iniciando servidor...")
print()
print("📊 Dashboard: http://190.84.119.196:8000/dashboard")
print("🔧 API Docs:  http://190.84.119.196:8000/docs")
print("❤️  Health:   http://190.84.119.196:8000/health")
print()
print("⚠️  Presiona Ctrl+C para detener")
print("=" * 40)

try:
    import uvicorn
    from main import app
    
    # Ejecutar el servidor
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
    
except ImportError as e:
    print(f"❌ Error: Falta dependencia {e}")
    print("💡 Ejecuta: pip install fastapi uvicorn pydantic")
    sys.exit(1)
except KeyboardInterrupt:
    print("\n🛑 Servidor detenido")
    sys.exit(0)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)