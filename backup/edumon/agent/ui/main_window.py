"""
Modern PyQt6 interface for EduMon Agent
"""
import sys
import os
from typing import Optional
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QGroupBox, QProgressBar,
    QSystemTrayIcon, QMenu, QMessageBox, QTabWidget, QFormLayout,
    QLineEdit, QSpinBox, QCheckBox, QComboBox
)
from PyQt6.QtCore import QTimer, QThread, pyqtSignal, Qt
from PyQt6.QtGui import QIcon, QPixmap, QFont, QAction
import json
import time
from ..core.config import AgentConfig, save_config
from ..core.metrics import MetricsCollector


class ConsentDialog(QMessageBox):
    """Consent dialog for user approval"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("EduMon - Consentimiento")
        self.setIcon(QMessageBox.Icon.Question)
        
        text = (
            "Este agente de aula (EduMon) enviará SOLO los siguientes datos "
            "al docente mientras dure la sesión:\n\n"
            "• Identificador del equipo, nombre del host y usuario\n"
            "• Porcentaje de uso de CPU y RAM\n"
            "• Tiempo de actividad (uptime)\n"
            "• Métricas adicionales del sistema (opcional)\n\n"
            "Nunca captura pantalla, teclado, archivos ni historial.\n"
            "Puede detener el envío en cualquier momento.\n\n"
            "¿Acepta participar durante esta clase?"
        )
        
        self.setText(text)
        self.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        self.setDefaultButton(QMessageBox.StandardButton.No)
        
        # Customize button text
        self.button(QMessageBox.StandardButton.Yes).setText("Aceptar")
        self.button(QMessageBox.StandardButton.No).setText("Rechazar")


class MetricsWidget(QWidget):
    """Widget to display real-time metrics"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.metrics_collector = MetricsCollector()
        
        # Timer for updating metrics
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_metrics)
        self.update_timer.start(2000)  # Update every 2 seconds
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # CPU metrics
        cpu_group = QGroupBox("CPU")
        cpu_layout = QFormLayout()
        
        self.cpu_label = QLabel("0%")
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setRange(0, 100)
        
        cpu_layout.addRow("Uso:", self.cpu_label)
        cpu_layout.addRow("", self.cpu_progress)
        cpu_group.setLayout(cpu_layout)
        
        # Memory metrics
        memory_group = QGroupBox("Memoria")
        memory_layout = QFormLayout()
        
        self.memory_label = QLabel("0%")
        self.memory_progress = QProgressBar()
        self.memory_progress.setRange(0, 100)
        self.memory_details = QLabel("0 MB / 0 MB")
        
        memory_layout.addRow("Uso:", self.memory_label)
        memory_layout.addRow("", self.memory_progress)
        memory_layout.addRow("Detalles:", self.memory_details)
        memory_group.setLayout(memory_layout)
        
        # System info
        system_group = QGroupBox("Sistema")
        system_layout = QFormLayout()
        
        self.uptime_label = QLabel("0s")
        self.processes_label = QLabel("0")
        self.network_label = QLabel("0 B/s ↑ 0 B/s ↓")
        
        system_layout.addRow("Tiempo activo:", self.uptime_label)
        system_layout.addRow("Procesos:", self.processes_label)
        system_layout.addRow("Red:", self.network_label)
        system_group.setLayout(system_layout)
        
        layout.addWidget(cpu_group)
        layout.addWidget(memory_group)
        layout.addWidget(system_group)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def update_metrics(self):
        """Update metrics display"""
        try:
            # Get basic metrics
            metrics = self.metrics_collector.get_basic_metrics()
            
            # Update CPU
            cpu_percent = metrics.get('cpu_percent', 0)
            self.cpu_label.setText(f"{cpu_percent:.1f}%")
            self.cpu_progress.setValue(int(cpu_percent))
            
            # Update Memory
            memory_percent = metrics.get('memory_percent', 0)
            memory_used = metrics.get('memory_used', 0)
            memory_total = metrics.get('memory_total', 0)
            
            self.memory_label.setText(f"{memory_percent:.1f}%")
            self.memory_progress.setValue(int(memory_percent))
            self.memory_details.setText(
                f"{memory_used // (1024*1024)} MB / {memory_total // (1024*1024)} MB"
            )
            
            # Update uptime
            uptime = metrics.get('uptime_seconds', 0)
            hours, remainder = divmod(uptime, 3600)
            minutes, seconds = divmod(remainder, 60)
            self.uptime_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
            
            # Get additional metrics
            process_metrics = self.metrics_collector.get_process_metrics()
            self.processes_label.setText(str(process_metrics.get('process_count', 0)))
            
            network_metrics = self.metrics_collector.get_network_metrics()
            sent_rate = network_metrics.get('network_sent_rate', 0)
            recv_rate = network_metrics.get('network_recv_rate', 0)
            self.network_label.setText(
                f"{self.format_bytes(sent_rate)}/s ↑ {self.format_bytes(recv_rate)}/s ↓"
            )
            
        except Exception as e:
            print(f"Error updating metrics: {e}")
    
    def format_bytes(self, bytes_value):
        """Format bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} TB"


class ConfigWidget(QWidget):
    """Configuration widget"""
    
    def __init__(self, config: AgentConfig):
        super().__init__()
        self.config = config
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Server settings
        server_group = QGroupBox("Configuración del Servidor")
        server_layout = QFormLayout()
        
        self.server_url_edit = QLineEdit(self.config.server_url)
        self.api_key_edit = QLineEdit(self.config.api_key)
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.classroom_edit = QLineEdit(self.config.classroom_id or "")
        self.heartbeat_spin = QSpinBox()
        self.heartbeat_spin.setRange(5, 300)
        self.heartbeat_spin.setValue(self.config.heartbeat_seconds)
        self.heartbeat_spin.setSuffix(" segundos")
        
        server_layout.addRow("URL del servidor:", self.server_url_edit)
        server_layout.addRow("Clave API:", self.api_key_edit)
        server_layout.addRow("ID del aula:", self.classroom_edit)
        server_layout.addRow("Intervalo heartbeat:", self.heartbeat_spin)
        server_group.setLayout(server_layout)
        
        # Metrics settings
        metrics_group = QGroupBox("Métricas a Recopilar")
        metrics_layout = QFormLayout()
        
        self.disk_check = QCheckBox()
        self.disk_check.setChecked(self.config.collect_disk_metrics)
        self.network_check = QCheckBox()
        self.network_check.setChecked(self.config.collect_network_metrics)
        self.process_check = QCheckBox()
        self.process_check.setChecked(self.config.collect_process_metrics)
        self.temp_check = QCheckBox()
        self.temp_check.setChecked(self.config.collect_temperature)
        
        metrics_layout.addRow("Métricas de disco:", self.disk_check)
        metrics_layout.addRow("Métricas de red:", self.network_check)
        metrics_layout.addRow("Métricas de procesos:", self.process_check)
        metrics_layout.addRow("Temperatura CPU:", self.temp_check)
        metrics_group.setLayout(metrics_layout)
        
        # UI settings
        ui_group = QGroupBox("Interfaz")
        ui_layout = QFormLayout()
        
        self.auto_start_check = QCheckBox()
        self.auto_start_check.setChecked(self.config.auto_start)
        self.minimize_check = QCheckBox()
        self.minimize_check.setChecked(self.config.minimize_to_tray)
        self.notifications_check = QCheckBox()
        self.notifications_check.setChecked(self.config.enable_notifications)
        
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self.log_level_combo.setCurrentText(self.config.log_level)
        
        ui_layout.addRow("Inicio automático:", self.auto_start_check)
        ui_layout.addRow("Minimizar a bandeja:", self.minimize_check)
        ui_layout.addRow("Notificaciones:", self.notifications_check)
        ui_layout.addRow("Nivel de log:", self.log_level_combo)
        ui_group.setLayout(ui_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Guardar")
        self.reset_button = QPushButton("Restablecer")
        
        self.save_button.clicked.connect(self.save_config)
        self.reset_button.clicked.connect(self.reset_config)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.reset_button)
        button_layout.addStretch()
        
        layout.addWidget(server_group)
        layout.addWidget(metrics_group)
        layout.addWidget(ui_group)
        layout.addLayout(button_layout)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def save_config(self):
        """Save configuration"""
        self.config.server_url = self.server_url_edit.text().strip()
        self.config.api_key = self.api_key_edit.text().strip()
        self.config.classroom_id = self.classroom_edit.text().strip() or None
        self.config.heartbeat_seconds = self.heartbeat_spin.value()
        
        self.config.collect_disk_metrics = self.disk_check.isChecked()
        self.config.collect_network_metrics = self.network_check.isChecked()
        self.config.collect_process_metrics = self.process_check.isChecked()
        self.config.collect_temperature = self.temp_check.isChecked()
        
        self.config.auto_start = self.auto_start_check.isChecked()
        self.config.minimize_to_tray = self.minimize_check.isChecked()
        self.config.enable_notifications = self.notifications_check.isChecked()
        self.config.log_level = self.log_level_combo.currentText()
        
        if save_config(self.config):
            QMessageBox.information(self, "Éxito", "Configuración guardada correctamente")
        else:
            QMessageBox.warning(self, "Error", "No se pudo guardar la configuración")
    
    def reset_config(self):
        """Reset configuration to defaults"""
        reply = QMessageBox.question(
            self, "Confirmar", "¿Restablecer configuración a valores por defecto?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.config = AgentConfig()
            self.init_ui()


class LogWidget(QWidget):
    """Log display widget"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumBlockCount(1000)  # Limit log size
        
        # Buttons
        button_layout = QHBoxLayout()
        self.clear_button = QPushButton("Limpiar")
        self.save_button = QPushButton("Guardar Log")
        
        self.clear_button.clicked.connect(self.clear_log)
        self.save_button.clicked.connect(self.save_log)
        
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.save_button)
        button_layout.addStretch()
        
        layout.addWidget(self.log_text)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def add_log(self, message: str):
        """Add log message"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
    
    def clear_log(self):
        """Clear log"""
        self.log_text.clear()
    
    def save_log(self):
        """Save log to file"""
        # Implementation for saving log
        pass


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self, config: AgentConfig):
        super().__init__()
        self.config = config
        self.session_active = False
        self.session_id = None
        self.init_ui()
        self.init_tray()
    
    def init_ui(self):
        self.setWindowTitle("EduMon Agent")
        self.setGeometry(100, 100, 600, 500)
        
        # Central widget with tabs
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # Status bar
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Desconectado")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        
        self.start_button = QPushButton("Iniciar Sesión")
        self.stop_button = QPushButton("Detener Sesión")
        self.stop_button.setEnabled(False)
        
        self.start_button.clicked.connect(self.start_session)
        self.stop_button.clicked.connect(self.stop_session)
        
        status_layout.addWidget(QLabel("Estado:"))
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.start_button)
        status_layout.addWidget(self.stop_button)
        
        # Tabs
        self.tabs = QTabWidget()
        
        # Metrics tab
        self.metrics_widget = MetricsWidget()
        self.tabs.addTab(self.metrics_widget, "Métricas")
        
        # Config tab
        self.config_widget = ConfigWidget(self.config)
        self.tabs.addTab(self.config_widget, "Configuración")
        
        # Log tab
        self.log_widget = LogWidget()
        self.tabs.addTab(self.log_widget, "Registro")
        
        layout.addLayout(status_layout)
        layout.addWidget(self.tabs)
        
        central_widget.setLayout(layout)
    
    def init_tray(self):
        """Initialize system tray"""
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon(self)
            
            # Create tray menu
            tray_menu = QMenu()
            
            show_action = QAction("Mostrar", self)
            show_action.triggered.connect(self.show)
            
            quit_action = QAction("Salir", self)
            quit_action.triggered.connect(self.close)
            
            tray_menu.addAction(show_action)
            tray_menu.addSeparator()
            tray_menu.addAction(quit_action)
            
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.activated.connect(self.tray_activated)
            
            # Set icon (you would need to provide an actual icon file)
            # self.tray_icon.setIcon(QIcon("icon.png"))
            
            self.tray_icon.show()
    
    def tray_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show()
    
    def start_session(self):
        """Start monitoring session"""
        # Show consent dialog
        consent_dialog = ConsentDialog(self)
        if consent_dialog.exec() != QMessageBox.StandardButton.Yes:
            self.log_widget.add_log("Consentimiento denegado")
            return
        
        # TODO: Implement actual session start logic
        self.session_active = True
        self.session_id = "test-session-id"
        
        self.status_label.setText("Conectado")
        self.status_label.setStyleSheet("color: green; font-weight: bold;")
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        
        self.log_widget.add_log("Sesión iniciada")
        
        if self.config.minimize_to_tray and hasattr(self, 'tray_icon'):
            self.hide()
    
    def stop_session(self):
        """Stop monitoring session"""
        # TODO: Implement actual session stop logic
        self.session_active = False
        self.session_id = None
        
        self.status_label.setText("Desconectado")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        self.log_widget.add_log("Sesión detenida")
    
    def closeEvent(self, event):
        """Handle close event"""
        if self.session_active:
            reply = QMessageBox.question(
                self, "Confirmar", "¿Detener la sesión y salir?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.stop_session()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


def main():
    """Main entry point for the agent UI"""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    # Load configuration
    from ..core.config import load_config
    config = load_config()
    
    # Create and show main window
    window = MainWindow(config)
    window.show()
    
    sys.exit(app.exec())