import os
from PyQt5.QtWidgets import (QMainWindow, QTableWidgetItem, QHeaderView, 
                             QDialog, QFormLayout, QLineEdit, QComboBox, 
                             QPushButton, QMessageBox)
from PyQt5 import uic
from PyQt5.QtCore import Qt
from src.managers.task_manager import TaskManager
from src.managers.auth_manager import AuthManager

class AdminWindow(QMainWindow):
    def __init__(self, usuario_actual, parent_window=None):
        super().__init__()
        self.usuario = usuario_actual
        self.parent_window = parent_window  
        self.task_manager = TaskManager()
        self.auth_manager = AuthManager()
        
        # --- CARGAR EL ARCHIVO XML (.ui) ---
        ui_path = os.path.join(os.path.dirname(__file__), "../ui/admin.ui")
        uic.loadUi(ui_path, self)
        
        self.setup_tables()
        self.conectar_botones()
        
        # Cargar datos iniciales
        self.cargar_usuarios()
        self.cargar_tableros()

    def setup_tables(self):
        # Ajustar ancho de columnas para que se vean bonitas
        self.table_users.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_boards.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def conectar_botones(self):
        self.btn_back.clicked.connect(self.volver)
        
        # Pestaña Usuarios
        self.btn_add_user.clicked.connect(self.crear_usuario_dialog)
        self.btn_refresh_users.clicked.connect(self.cargar_usuarios)
        
        # Pestaña Tableros
        self.btn_add_board.clicked.connect(self.crear_tablero_dialog)
        self.btn_refresh_boards.clicked.connect(self.cargar_tableros)

    def volver(self):
        if self.parent_window:
            self.parent_window.show()
        self.close()

    # --- LÓGICA DE CARGA DE DATOS ---
    def cargar_usuarios(self):
        usuarios = self.task_manager.obtener_todos_usuarios()
        self.table_users.setRowCount(0) # Limpiar
        self.table_users.setRowCount(len(usuarios))
        
        for row, u in enumerate(usuarios):
            self.table_users.setItem(row, 0, QTableWidgetItem(str(u.get('id'))))
            self.table_users.setItem(row, 1, QTableWidgetItem(u.get('nombre', '')))
            self.table_users.setItem(row, 2, QTableWidgetItem(u.get('email', '')))
            self.table_users.setItem(row, 3, QTableWidgetItem(u.get('nivel_acceso', 'trabajador')))

    def cargar_tableros(self):
        tableros = self.task_manager.obtener_todos_tableros()
        self.table_boards.setRowCount(0)
        self.table_boards.setRowCount(len(tableros))
        
        for row, t in enumerate(tableros):
            self.table_boards.setItem(row, 0, QTableWidgetItem(str(t.get('id'))))
            self.table_boards.setItem(row, 1, QTableWidgetItem(t.get('titulo', '')))
            self.table_boards.setItem(row, 2, QTableWidgetItem(t.get('descripcion', '')))
            self.table_boards.setItem(row, 3, QTableWidgetItem(str(t.get('creado_por'))))

    # --- DIÁLOGOS DE CREACIÓN ---
    def crear_usuario_dialog(self): # Dialogo para crear un usuario con su nombre, email, contraseña y rol
        dialog = QDialog(self)
        dialog.setWindowTitle("Nuevo Usuario")
        dialog.setFixedWidth(300)
        # Estilo forzado para asegurar que se ve bien
        dialog.setStyleSheet("background: #FAFAFA; color: #333;")
        
        layout = QFormLayout(dialog)
        nombre = QLineEdit()
        email = QLineEdit()
        pwd = QLineEdit()
        pwd.setEchoMode(QLineEdit.Password)
        rol = QComboBox()
        rol.addItems(["trabajador", "manager", "admin"]) # De momento los roles que hay son estos
        
        layout.addRow("Nombre:", nombre)
        layout.addRow("Email:", email)
        layout.addRow("Contraseña:", pwd)
        layout.addRow("Rol:", rol)
        
        btn = QPushButton("Crear")
        btn.setStyleSheet("background: #4CAF50; color: white; padding: 5px;")
        btn.clicked.connect(dialog.accept)
        layout.addRow(btn)
        
        if dialog.exec_():
            # Llamamos al AuthManager para crear
            if self.auth_manager.registro(email.text(), pwd.text(), nombre.text(), rol.currentText()):
                QMessageBox.information(self, "Éxito", "Usuario creado.")
                self.cargar_usuarios()
            else:
                QMessageBox.critical(self, "Error", "Fallo al crear usuario.")

    def crear_tablero_dialog(self): # Dialogo para crear un tablero con su nombre y descripcion, y asignarlo a un usuario
        usuarios = self.task_manager.obtener_todos_usuarios()
        if not usuarios: return

        dialog = QDialog(self)
        dialog.setWindowTitle("Nuevo Tablero")
        dialog.setStyleSheet("background: #FAFAFA; color: #333;")
        layout = QFormLayout(dialog)
        
        titulo = QLineEdit()
        desc = QLineEdit()
        combo_owner = QComboBox()
        
        for u in usuarios:
            combo_owner.addItem(f"{u['email']} ({u['nombre']})", u['id'])
            
        layout.addRow("Título:", titulo)
        layout.addRow("Descripción:", desc)
        layout.addRow("Asignar a:", combo_owner)
        
        btn = QPushButton("Crear Tablero")
        btn.setStyleSheet("background: #FF9800; color: white; padding: 5px;")
        btn.clicked.connect(dialog.accept)
        layout.addRow(btn)
        
        if dialog.exec_():
            owner_id = combo_owner.currentData()
            if self.task_manager.crear_tablero_admin(titulo.text(), desc.text(), owner_id):
                 QMessageBox.information(self, "Éxito", "Tablero creado.")
                 self.cargar_tableros()
            else:
                QMessageBox.critical(self, "Error", "Fallo al crear tablero.")