import os
from PyQt5.QtWidgets import QDialog, QMessageBox, QCheckBox # Cambiamos QWidget por QDialog
from PyQt5.QtCore import Qt
from PyQt5 import uic
from src.managers.auth_manager import AuthManager
"""
Clase que maneja la ventana de login, llama a los metodos de AuthManager para autenticar la operacion de
logear y registrar a los usuarios en la base de datos de Supabase
"""

ESTILO_LOGIN = """
    /* Fondo General */
    QDialog {
        background-color: #FAFAFA; /* Crema muy suave */
    }

    /* Textos y Etiquetas */
    QLabel {
        color: #4E342E; /* Marrón oscuro */
        font-family: 'Segoe UI', sans-serif;
        font-weight: bold;
        font-size: 14px;
    }

    /* Campos de Texto (Email / Password) */
    QLineEdit {
        background-color: #FFFFFF;
        border: 2px solid #D7CCC8; /* Borde marrón suave */
        border-radius: 8px;        /* Bordes redondeados modernos */
        padding: 10px 12px;        /* Más espacio interno (más cómodo) */
        font-size: 14px;
        color: #3E2723;
        selection-background-color: #FFB74D;
    }
    QLineEdit:focus {
        border: 2px solid #FFB74D; /* Foco Naranja Alaxa */
        background-color: #FFF8E1; /* Fondo amarillento muy sutil al escribir */
    }

    /* Botón de Entrar */
    QPushButton {
        background-color: #4E342E; /* Fondo Marrón */
        color: #FFB74D;            /* Texto Naranja */
        font-weight: bold;
        border-radius: 8px;
        padding: 12px;
        font-size: 15px;
        border: 1px solid #3E2723;
    }
    QPushButton:hover {
        background-color: #5D4037; /* Un poco más claro al pasar el ratón */
        color: #FFFFFF;            /* Texto blanco */
        border: 1px solid #FFB74D; /* Borde naranja brillante */
    }
    QPushButton:pressed {
        background-color: #3E2723; /* Oscuro al hacer clic */
        padding-top: 14px;         /* Pequeño efecto de hundimiento */
    }

    /* Checkbox "Mantener sesión" */
    QCheckBox {
        color: #5D4037;
        font-weight: bold;
        spacing: 8px; /* Espacio entre la cajita y el texto */
    }
    QCheckBox::indicator {
        width: 18px;
        height: 18px;
        border: 2px solid #D7CCC8;
        border-radius: 4px;
        background: white;
    }
    QCheckBox::indicator:checked {
        background-color: #FFB74D; /* Fondo Naranja al marcar */
        border: 2px solid #4E342E;
        image: none; /* (Opcional) Aquí podrías poner un icono de check personalizado */
    }
    QCheckBox::indicator:hover {
        border: 2px solid #FFB74D;
    }
"""

class LoginDialog(QDialog): # Hereda de QDialog
    def __init__(self):
        super().__init__()
        # Cargar UI (Asegúrate de que tu auth.ui sea un QDialog o QWidget, ambos funcionan aquí)
        ui_path = os.path.join(os.path.dirname(__file__), "..", "ui", "auth.ui")
        uic.loadUi(ui_path, self)

        # Aplica el estilo
        self.setStyleSheet(ESTILO_LOGIN)
        self.setWindowTitle("AlaxaFlow - Acceso")

        self.auth_manager = AuthManager()

        # Aquí guarda el rol para que el Main lo recoja
        self.rol_usuario = None 
        self.usuario_actual = None

        # Configuración inicial
        self.stackedWidget.setCurrentIndex(0) 
        self.input_login_pass.setEchoMode(2)

        self.input_login_email.setPlaceholderText("ejemplo@alaxa.es")
        self.input_login_pass.setPlaceholderText("••••••••")

        # Checkbox para mantener sesión iniciada
        self.check_mantener = QCheckBox("Mantener sesión iniciada")
        self.check_mantener.setCursor(Qt.PointingHandCursor)

        # Coloca el checkbox encima del botón de login
        layout_padre = self.btn_login.parentWidget().layout()
        if layout_padre:
            index_btn = layout_padre.indexOf(self.btn_login)
            layout_padre.insertWidget(index_btn, self.check_mantener)

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
        
        # Recolecta si se debe mantener la sesión
        recordar = self.check_mantener.isChecked()

        # Recoge el usuario y rol
        user, rol = self.auth_manager.login(email, password, recordar=recordar)

        if user:
            # Guarda el usuario y rol para pasarlo al main
            self.usuario_actual = user 
            self.rol_usuario = rol
            # VERIFICACION FINAL: accept() cierra la ventana y devuelve True (Accepted)
            self.accept() 
        else:
            QMessageBox.critical(self, "Error", "Credenciales incorrectas")