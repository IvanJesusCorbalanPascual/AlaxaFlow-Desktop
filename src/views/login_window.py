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
        self.rol_usuario = None # Aquí guardaremos el rol para que el Main lo recoja
        self.usuario_actual = None

        self.btn_go_to_register.hide()
        self.stackedWidget.setCurrentIndex(0) # Mostrar pantalla de login por defecto
        self.btn_login.clicked.connect(self.login)

    def login(self):
        email = self.input_login_email.text()
        password = self.input_login_pass.text()

        # Manejo de errores
        if not email or not password:
            QMessageBox.critical(self, "Error", "Debes completar todos los campos")
            return

        user = self.auth_manager.login(email, password)
        if user:
            self.user = user # Guardamos el usuario para pasarlo al main
            # VERIFICACION FINAL: accept() cierra la ventana y devuelve True (Accepted)
            self.accept() 
        else:
            QMessageBox.critical(self, "Error", "Credenciales incorrectas")