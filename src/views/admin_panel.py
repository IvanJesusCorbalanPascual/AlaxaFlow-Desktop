import os
from PyQt5.QtWidgets import (QMainWindow, QTableWidgetItem, QHeaderView, 
                             QDialog, QFormLayout, QLineEdit, QComboBox, 
                             QPushButton, QMessageBox)
from PyQt5 import uic
from PyQt5.QtCore import Qt
from src.managers.task_manager import TaskManager
from src.managers.auth_manager import AuthManager
from src.bd.conexion import db

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

        # Recupera los nombres de departamentos para mostrarlos sin IDs
        dept_map = {}
        try:
            res = db.client.table('departamentos').select('id, nombre').execute()
            if res.data:
                for d in res.data:
                    dept_map[d['id']] = d['nombre']
        except Exception:
            print("Error al cargar diccionario de departamentos")

        self.table_users.setRowCount(0) # Limpiar
        self.table_users.setRowCount(len(usuarios))
        
        for row, u in enumerate(usuarios):
            self.table_users.setItem(row, 0, QTableWidgetItem(str(u.get('id'))))
            self.table_users.setItem(row, 1, QTableWidgetItem(u.get('nombre', '')))
            self.table_users.setItem(row, 2, QTableWidgetItem(u.get('apellidos', '')))
            self.table_users.setItem(row, 3, QTableWidgetItem(u.get('email', '')))
            # Usa el mapa de departamentos para mostrar el nombre
            dept_id = u.get('departamento_id')
            nombre_dept = dept_map.get(dept_id, "Sin Asignar")
            self.table_users.setItem(row, 4, QTableWidgetItem(nombre_dept))
            self.table_users.setItem(row, 5, QTableWidgetItem(u.get('nivel_acceso', 'trabajador')))

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
        dialog.setWindowTitle("Registrar Nuevo Usuario")
        dialog.setFixedWidth(400)
        # Estilo forzado para asegurar que se ve bien
        dialog.setStyleSheet("background: #FAFAFA; color: #333;")
        
        layout = QFormLayout(dialog)

        nombre = QLineEdit()
        apellidos = QLineEdit()   
        email = QLineEdit()
        
        pwd = QLineEdit()
        pwd.setEchoMode(QLineEdit.Password)
        pwd.setPlaceholderText("Mínimo 6 caracteres")


        rol = QComboBox()
        # De momento los roles que hay son estos
        rol.addItems(["trabajador", "manager", "admin"]) 

        combo_dept = QComboBox()
        # Placeholder
        combo_dept.addItem("Cargar departamentos...", None)  

        # Logica para cargar departamentos desde la BD
        try:
            res = db.client.table('departamentos').select('id, nombre').execute()
            combo_dept.clear()
            if res.data:
                for dep in res.data:
                    combo_dept.addItem(dep['nombre'], dep['id'])
            else:
                combo_dept.addItem("No hay departamentos", None)
        except Exception as e:
            combo_dept.clear()
            combo_dept.addItem("Error de conexión", None)

        # Filas del formulario
        layout.addRow("Nombre:", nombre)
        layout.addRow("Apellidos:", apellidos)
        layout.addRow("Email (Usuario):", email)
        layout.addRow("Contraseña:", pwd)
        layout.addRow("Departamento:", combo_dept)
        layout.addRow("Rol:", rol)
        
        # Botone de acción
        btn = QPushButton("Registrar Empleado")
        btn.setStyleSheet("background: #4CAF50; color: white; padding: 8px; font-weight: bold; border-radius: 4px;")
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(dialog.accept)
        layout.addRow(btn)
        
        # Ejecuta el diálogo y procesa los datos si se acepta
        if dialog.exec_():
            # Llamamos al AuthManager para crear
            if not email.text() or not pwd.text() or len(pwd.text()) < 6:
                QMessageBox.warning(self, "Error", "El email y una contraseña de mín. 6 caracteres son obligatorios")
                return
            
            dep_id = combo_dept.currentData()
            if not dep_id:
                QMessageBox.warning(self, "Error", "Debes seleccionar un departamento.")
                return
            
            # LLama al auth manager para registrar con todos los datos
            exito = self.auth_manager.registro(
                email=email.text(), 
                password=pwd.text(), 
                nombre=nombre.text(), 
                apellidos=apellidos.text(), 
                departamento_id=dep_id, 
                nivel=rol.currentText()
            )

            if exito:
                QMessageBox.information(self, "Empleado Registrado", f"El usuario {email.text()} ha sido creado correctamente")
                self.cargar_usuarios()
            else:
                QMessageBox.critical(self, "Error", "No se pudo registrar el usuario, puede que el email ya exista")

    # Dialogo para crear un tablero con su nombre y descripcion, y asignarlo a un usuario
    def crear_tablero_dialog(self): 
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