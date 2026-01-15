import os
from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal
from src.managers.auth_manager import AuthManager

class LoginWindow(QWidget):
    # Señal personalizada: Avisa al Main.py de que el login fue exitoso
    login_exitoso = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        uic.loadUi("src/ui/auth.ui", self)
        self.auth_manager = AuthManager()
        self.setup_ui()
    
    def setup_ui(self):
        self.btn_login_action.clicked.connect(self.handle_login)
        self.btn_go_to_register.clicked.connect(self.handle_register)
    
    def handle_login(self):
        email = self.input_login_email.text()
        password = self.input_login_pass.text()
        try:
            response = self.auth_manager.iniciar_sesion(email, password)
            if response.get("user"):
                self.login_exitoso.emit()
            else:
                QMessageBox.warning(self, "Error", "Credenciales incorrectas")
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
        
    def handle_register(self):
        nombre = self.input_reg_nombre.text()
        email = self.input_reg_email.text()
        password = self.input_reg_pass.text()

        if not nombre or not email or not password:
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios")
            return
        
        try:
            response = self.auth_manager.registrar_usuario(email, password)
            if response.get("user"):
                self.login_exitoso.emit()
            else:
                QMessageBox.warning(self, "Error", "Error al registrar el usuario")
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))