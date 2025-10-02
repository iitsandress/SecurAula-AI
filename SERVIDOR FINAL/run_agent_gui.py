import runpy
import os
import sys

# Sitúa la carpeta padre en sys.path para que Python encuentre el paquete `agent`
root = os.path.abspath(os.path.dirname(__file__))
if root not in sys.path:
    sys.path.insert(0, root)

# Ejecuta el módulo `agent.main` como módulo para preservar el contexto de paquete
# Esto evita errores de importación relativa cuando el usuario ejecuta el script directamente.
runpy.run_module('agent.main', run_name="__main__", alter_sys=True)