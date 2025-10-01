#!/usr/bin/env python3
"""
EduMon Agent GUI - PyQt6 Edition
"""
import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QFrame, QGridLayout, QMessageBox
)
from PyQt6.QtGui import QIcon, QFont, QPalette, QColor
from PyQt6.QtCore import Qt, pyqtSignal

class ModernGui(QWidget):
    # Signals
    connect_pressed = pyqtSignal(dict)
    disconnect_pressed = pyqtSignal()

    def __init__(self, agent_info: dict, initial_config: dict):
        super().__init__()
        self.agent_info = agent_info
        self.initial_config = initial_config
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("EduMon Agent")
        self.setWindowIcon(QIcon.fromTheme("education"))
        self.setGeometry(0, 0, 450, 550)
        self.center_window()

        # --- Layouts ---
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        header_frame = QFrame(self)
        header_frame.setObjectName("header_frame")
        header_layout = QVBoxLayout(header_frame)

        content_frame = QFrame(self)
        content_frame.setObjectName("content_frame")
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(25, 25, 25, 25)

        # --- Header ---
        title = QLabel("🎓 EduMon Agent")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label = QLabel("⚪ Desconectado")
        self.status_label.setObjectName("status_label")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title)
        header_layout.addWidget(self.status_label)

        # --- Connection Form ---
        form_layout = QGridLayout()
        form_layout.setSpacing(15)
        self.server_ip_input = self.create_line_edit(self.initial_config.get('server_ip', '190.84.119.196'))
        self.api_key_input = self.create_line_edit(self.initial_config.get('api_key', ''), is_password=True)
        self.classroom_input = self.create_line_edit(self.initial_config.get('classroom_id', 'Aula-1'))
        form_layout.addWidget(QLabel("IP del Servidor:"), 0, 0)
        form_layout.addWidget(self.server_ip_input, 0, 1)
        form_layout.addWidget(QLabel("Clave de Acceso:"), 1, 0)
        form_layout.addWidget(self.api_key_input, 1, 1)
        form_layout.addWidget(QLabel("Aula (Opcional):"), 2, 0)
        form_layout.addWidget(self.classroom_input, 2, 1)

        # --- Metrics Display ---
        metrics_frame = QFrame(); metrics_frame.setObjectName("metrics_frame")
        metrics_layout = QGridLayout(metrics_frame)
        self.cpu_label = QLabel("CPU: --%")
        self.mem_label = QLabel("RAM: --%")
        metrics_layout.addWidget(self.cpu_label, 0, 0)
        metrics_layout.addWidget(self.mem_label, 0, 1)

        # --- Agent Info ---
        info_frame = QFrame(); info_frame.setObjectName("info_frame")
        info_layout = QVBoxLayout(info_frame)
        info_layout.addWidget(QLabel(f"<b>Device ID:</b> {self.agent_info['device_id'][:8]}..."))
        info_layout.addWidget(QLabel(f"<b>Usuario:</b> {self.agent_info['username']}"))
        info_layout.addWidget(QLabel(f"<b>Hostname:</b> {self.agent_info['hostname']}"))

        # --- Buttons ---
        button_layout = QHBoxLayout()
        self.connect_button = QPushButton("🚀 Conectar")
        self.connect_button.setObjectName("connect_button")
        self.disconnect_button = QPushButton("🛑 Desconectar")
        self.disconnect_button.setObjectName("disconnect_button")
        self.disconnect_button.setEnabled(False)
        button_layout.addWidget(self.connect_button)
        button_layout.addWidget(self.disconnect_button)

        # --- Assemble Content Layout ---
        content_layout.addLayout(form_layout)
        content_layout.addSpacing(20)
        content_layout.addWidget(metrics_frame)
        content_layout.addSpacing(20)
        content_layout.addWidget(info_frame)
        content_layout.addStretch()
        content_layout.addLayout(button_layout)

        # --- Assemble Main Layout ---
        main_layout.addWidget(header_frame)
        main_layout.addWidget(content_frame)

        # --- Stylesheet ---
        self.set_stylesheet()

        # --- Signals ---
        self.connect_button.clicked.connect(self.on_connect_click)
        self.disconnect_button.clicked.connect(self.on_disconnect_click)

    def create_line_edit(self, text, is_password=False):
        line_edit = QLineEdit(text)
        if is_password:
            line_edit.setEchoMode(QLineEdit.EchoMode.Password)
        return line_edit

    def on_connect_click(self):
        if self.show_consent():
            config = {
                "server_ip": self.server_ip_input.text().strip(),
                "api_key": self.api_key_input.text().strip(),
                "classroom_id": self.classroom_input.text().strip(),
            }
            if not config["server_ip"] or not config["api_key"]:
                self.show_error("La IP del servidor y la Clave de Acceso son obligatorias.")
                return
            self.connect_pressed.emit(config)

    def on_disconnect_click(self):
        self.disconnect_pressed.emit()

    def set_connection_state(self, is_connected: bool):
        self.connect_button.setEnabled(not is_connected)
        self.disconnect_button.setEnabled(is_connected)
        self.server_ip_input.setDisabled(is_connected)
        self.api_key_input.setDisabled(is_connected)
        self.classroom_input.setDisabled(is_connected)

    def update_status(self, status: str):
        self.status_label.setText(status)

    def update_metrics(self, metrics: dict):
        self.cpu_label.setText(f"CPU: {metrics.get('cpu_percent', 0)}%")
        self.mem_label.setText(f"RAM: {metrics.get('mem_percent', 0)}%")

    def show_error(self, message: str):
        QMessageBox.critical(self, "Error de Conexión", message)

    def show_consent(self) -> bool:
        consent_text = """
        <b>🎓 CONSENTIMIENTO PARA MONITOREO EDUCATIVO</b>
        <p>Este programa enviará métricas de rendimiento (CPU, RAM) y datos de identificación básicos (hostname, username) a tu profesor con fines educativos.</p>
        <p><b>NO se enviarán:</b> capturas de pantalla, pulsaciones de teclado, contenido de archivos o datos personales.</p>
        <p>Puedes detener el monitoreo en cualquier momento.</p>
        <p>¿Aceptas participar?</p>
        """
        reply = QMessageBox.question(self, "Consentimiento de EduMon", consent_text, 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                     QMessageBox.StandardButton.No)
        return reply == QMessageBox.StandardButton.Yes

    def center_window(self):
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def set_stylesheet(self):
        self.setStyleSheet("""
            #header_frame { 
                background-color: #6E44FF; 
                color: white; 
                padding: 20px;
            }
            #title { font-size: 24px; font-weight: bold; }
            #status_label { font-size: 14px; color: #E0E0E0; }
            #content_frame { background-color: #FDFDFD; }
            #metrics_frame, #info_frame { 
                background-color: #F4F6F8; 
                border-radius: 8px; 
                padding: 15px;
            }
            QLabel { font-size: 14px; }
            QLineEdit { 
                padding: 8px; 
                border: 1px solid #CCC; 
                border-radius: 4px; 
                font-size: 14px;
            }
            QPushButton { 
                padding: 12px; 
                border: none; 
                border-radius: 4px; 
                font-size: 16px; 
                font-weight: bold;
                cursor: pointer;
            }
            #connect_button { background-color: #4CAF50; color: white; }
            #disconnect_button { background-color: #F44336; color: white; }
            QPushButton:disabled { background-color: #BDBDBD; }
        """)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Dummy data for testing
    agent_info = {'device_id': 'test-id', 'username': 'test-user', 'hostname': 'test-host'}
    initial_config = {'server_ip': '190.84.119.196'}
    ex = ModernGui(agent_info, initial_config)
    ex.show()
    sys.exit(app.exec())
