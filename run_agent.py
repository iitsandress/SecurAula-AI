#!/usr/bin/env python3
"""
EduMon Agent Runner - PyQt6 Edition

Main entry point for the student's agent.
"""
import sys
import os
import subprocess

def check_and_install_dependencies():
    """Checks if dependencies are installed and installs them if not."""
    print("Verificando dependencias del agente...")
    req_path = os.path.join(os.path.dirname(__file__), 'edumon', 'requirements-agent.txt')
    try:
        import importlib.metadata
        with open(req_path, 'r') as f:
            requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        # Check each requirement
        missing_packages = []
        for req in requirements:
            # Parse package name (remove version specifiers)
            package_name = req.split('>=')[0].split('==')[0].split('[')[0].strip()
            try:
                importlib.metadata.version(package_name)
            except importlib.metadata.PackageNotFoundError:
                missing_packages.append(req)
        
        if missing_packages:
            print(f"⚠️  Dependencias faltantes: {', '.join(missing_packages)}. Instalando...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_path])
            print("✅ Dependencias instaladas.")
        else:
            print("✅ Dependencias satisfechas.")
    except (ImportError, FileNotFoundError):
        print("⚠️  Error verificando dependencias. Usando pip directamente.")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_path])
    except Exception as e:
        print(f"⚠️  Error verificando dependencias: {e}. Instalando...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_path])
        print("✅ Dependencias instaladas.")

if __name__ == "__main__":
    check_and_install_dependencies()

    # Imports are done after dependency check
    import json
    import socket
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import QObject, pyqtSignal, QThread

    # Adjust path to import from the edumon package
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

    from edumon.agent.agent import EduMonAgent
    from edumon.agent.ui.gui_pyqt import ModernGui

    CONFIG_FILE = "agent_config.json"

    class GuiController(QObject):
        """Controller to link the GUI and the Agent logic."""
        status_update = pyqtSignal(str)
        metrics_update = pyqtSignal(dict)
        connection_state_update = pyqtSignal(bool)

        def __init__(self, agent: EduMonAgent):
            super().__init__()
            self.agent = agent
            self.agent.on_status_update = self.status_update.emit
            self.agent.on_metrics_update = self.metrics_update.emit
            
            # Keep references to thread and worker to prevent garbage collection
            self.connect_thread = None
            self.connect_worker = None

        def connect_agent(self, config: dict):
            # Prevent multiple connection attempts
            if self.connect_thread and self.connect_thread.isRunning():
                print("Connection already in progress...")
                return
                
            # Run agent start in a separate thread to not block the GUI
            self.connect_thread = QThread()
            self.connect_worker = ConnectWorker(self.agent, config)
            self.connect_worker.moveToThread(self.connect_thread)
            
            # Connect signals
            self.connect_worker.finished.connect(self.connect_thread.quit)
            self.connect_worker.finished.connect(self.connect_worker.deleteLater)
            self.connect_thread.started.connect(self.connect_worker.run)
            self.connect_thread.finished.connect(self.connect_thread.deleteLater)
            
            # Clean up references when thread finishes
            self.connect_thread.finished.connect(self._cleanup_connect_thread)
            
            self.connect_thread.start()
            self.connection_state_update.emit(True)
        
        def _cleanup_connect_thread(self):
            """Clean up thread references after completion"""
            self.connect_thread = None
            self.connect_worker = None

        def disconnect_agent(self):
            self.agent.stop()
            self.connection_state_update.emit(False)
        
        def cleanup(self):
            """Clean up resources before application exit"""
            # Stop the agent first
            self.agent.stop()
            
            # Wait for connection thread to finish if it's running
            if self.connect_thread and self.connect_thread.isRunning():
                self.connect_thread.quit()
                self.connect_thread.wait(3000)  # Wait up to 3 seconds
                if self.connect_thread.isRunning():
                    print("Warning: Connection thread did not terminate gracefully")
                    self.connect_thread.terminate()
                    self.connect_thread.wait(1000)

    class ConnectWorker(QObject):
        finished = pyqtSignal()

        def __init__(self, agent, config):
            super().__init__()
            self.agent = agent
            self.config = config

        def run(self):
            # Rebuild the full URL
            full_config = self.config.copy()
            full_config['server_url'] = f"http://{self.config['server_ip']}:8000"
            if not self.agent.start(full_config):
                self.agent.on_status_update("🔴 Conexión fallida")
                # This is a simplification. A signal back to the controller would be better.
                print("Debug: Connection failed")
            self.finished.emit()

    def load_config() -> dict:
        if not os.path.exists(CONFIG_FILE):
            return {}
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError):
            return {}

    def save_config(config: dict):
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
        except IOError as e:
            print(f"Error guardando configuración: {e}")

    app = QApplication(sys.argv)
    initial_config = load_config()
    agent = EduMonAgent()
    controller = GuiController(agent)
    agent_info = {
        'device_id': agent.device_id,
        'username': socket.gethostname(),
        'hostname': socket.gethostname(),
    }
    gui = ModernGui(agent_info, initial_config)

    # Connect signals
    controller.status_update.connect(gui.update_status)
    controller.metrics_update.connect(gui.update_metrics)
    controller.connection_state_update.connect(gui.set_connection_state)
    gui.connect_pressed.connect(lambda config: (controller.connect_agent(config), save_config(config)))
    gui.disconnect_pressed.connect(controller.disconnect_agent)
    
    # Proper cleanup on application exit
    app.aboutToQuit.connect(controller.cleanup)

    gui.show()
    sys.exit(app.exec())
