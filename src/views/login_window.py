import os
from PyQt5.QtWidgets import QDialog, QMessageBox # Cambiamos QWidget por QDialog
from PyQt5 import uic
from src.managers.auth_manager import AuthManager
from src.bd.conexion import db
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
        self.btn_register_action.clicked.connect(self.registrar)

        self.btn_go_to_register.clicked.connect(self.ir_a_registro)
        self.btn_go_to_login.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))

    # Carga la lista de departamentos al entrar a registro
    def ir_a_registro(self):
        self.cargar_departamentos()
        self.stackedWidget.setCurrentIndex(1)

    def cargar_departamentos(self):
        # Limpia items antiguos para evitar problemas
        self.combo_reg_departamento.clear()
        # Placeholder antes de elegir un departamento
        self.combo_reg_departamento.addItem("Selecciona un departamento...", None)
        try:
            res = db.client.table('departamentos').select('id, nombre').execute()

            if res.data:
                for dep in res.data:
                    # Añade el nomnbre visible y el ID oculto
                    self.combo_reg_departamento.addItem(dep['nombre'], dep['id'])
            else:
                self.combo_reg_departamento.addItem("No hay departamentos disponibles", None)
        except Exception as e:
            print(f"Error al cargar los departamentos: {e}")
            self.combo_reg_departamento.addItem("Error de conexión", None)

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
            
    def registrar(self):
        nombre = self.input_reg_nombre.text()
        apellidos = self.input_reg_apellidos.text()
        email = self.input_reg_email.text()
        password = self.input_reg_pass.text()
        departamento_id = self.combo_reg_departamento.currentData()

        # Valida los campos
        if not nombre or not email or not password:
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios")
            return
        
        if not departamento_id:
             QMessageBox.warning(self, "Error", "Debes seleccionar un departamento válido.")
             return
        
        # Si la longitud de la contraseña es menor a 6, avisa al usuario para que la cambie
        if len(password) < 6:
            QMessageBox.warning(self, "Contraseña insegura", "La contraseña debe tener al menos 6 caracteres.")
            return
        
        # Llama al manager y crea por defecto el rol trabajador
        nuevo_usuario = self.auth_manager.registro(email, password, nombre, apellidos, departamento_id)

        if nuevo_usuario:
            QMessageBox.information(self, "Éxito", "Usuario creado. Ahora debes iniciar sesión")
            # Vuelve al login
            self.stackedWidget.setCurrentIndex(0) 
        else:
            QMessageBox.critical(self, "Error", "No se pudo crear el usuario (Verifica que no este registrado ya el email)")