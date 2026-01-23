import os
from PyQt5.QtWidgets import QDialog, QMessageBox # Cambiamos QWidget por QDialog
from PyQt5 import uic
from src.managers.auth_manager import AuthManager
"""
Clase que maneja la ventana de login, llama a los metodos de AuthManager para autenticar la operacion de
logear y registrar a los usuarios en la base de datos de Supabase
"""
class LoginDialog(QDialog): # Hereda de QDialog
    def __init__(self):
        super().__init__()
        # Cargar UI (Asegúrate de que tu auth.ui sea un QDialog o QWidget, ambos funcionan aquí)
        ui_path = os.path.join(os.path.dirname(__file__), "..", "ui", "auth.ui")
        uic.loadUi(ui_path, self)

        self.auth_manager = AuthManager()

        # Aquí guarda el rol para que el Main lo recoja
        self.rol_usuario = None 
        self.usuario_actual = None

        # Configuración inicial
        self.stackedWidget.setCurrentIndex(0) 
        self.input_login_pass.setEchoMode(2)

        # Conexiones
        self.btn_login.clicked.connect(self.login)
        # Oculta del botón de registrar
        if hasattr(self, 'btn_go_to_register'):
            self.btn_go_to_register.hide()

    def login(self):
        email = self.input_login_email.text()
        password = self.input_login_pass.text()

        # Manejo de errores
        if not email or not password:
            QMessageBox.critical(self, "Atención", "Debes completar todos los campos")
            return

        # Recoge el usuario y rol
        user, rol = self.auth_manager.login(email, password)

        if user:
            # Guarda el usuario y rol para pasarlo al main
            self.usuario_actual = user 
            self.rol_usuario = rol
            # VERIFICACION FINAL: accept() cierra la ventana y devuelve True (Accepted)
            self.accept() 
        else:
            QMessageBox.critical(self, "Error", "Credenciales incorrectas")