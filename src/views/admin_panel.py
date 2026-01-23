import os
from PyQt5.QtWidgets import (QMainWindow, QTableWidgetItem, QHeaderView, 
                             QDialog, QFormLayout, QLineEdit, QComboBox, 
                             QPushButton, QMessageBox, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTableWidget, QAbstractItemView, QMenu, QAction)
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
        
        # Pestañas extra según rol
        self.setup_extra_tabs()

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
        
        # Lógica de jerarquía de roles
        # Necesitamos saber el rol del usuario actual que está creando al nuevo usuario
        rol_actual = 'trabajador' # valor por defecto seguro
        
        # Intentamos obtener el rol desde self.parent_window.rol si existe
        if self.parent_window and hasattr(self.parent_window, 'rol'):
            rol_actual = self.parent_window.rol
        elif self.usuario and hasattr(self.usuario, 'nivel_acceso'):
             # Fallback si el objeto usuario tiene el atributo
             rol_actual = self.usuario.nivel_acceso
             
        # Definimos qué puede crear cada uno
        roles_permitidos = []
        if rol_actual == 'admin':
            roles_permitidos = ["admin", "manager", "lider_equipo", "trabajador"]
        elif rol_actual == 'manager':
            roles_permitidos = ["lider_equipo", "trabajador"]
        elif rol_actual == 'lider_equipo':
            roles_permitidos = ["trabajador"]
        
        rol.addItems(roles_permitidos) 

        combo_dept = QComboBox()
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

        combo_equipo = QComboBox()
        combo_equipo.addItem("Sin equipo (Opcional)", None)

        # Logica cargar equipos
        try:
            res_eq = db.client.table('equipos').select('id, nombre, lider_id').execute()
            if res_eq.data:
                for eq in res_eq.data:
                    # Guardamos el lider_id tambien en la data como tupla o dict si hiciera falta, 
                    # pero aqui solo el ID del equipo. Consultaremos lider luego.
                    combo_equipo.addItem(eq['nombre'], eq['id'])
        except Exception:
            pass

        # Filas del formulario
        layout.addRow("Nombre:", nombre)
        layout.addRow("Apellidos:", apellidos)
        layout.addRow("Email (Usuario):", email)
        layout.addRow("Contraseña:", pwd)
        layout.addRow("Departamento:", combo_dept)
        layout.addRow("Rol:", rol)
        layout.addRow("Equipo:", combo_equipo)
        
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
            
            equipo_id = combo_equipo.currentData()
            rol_elegido = rol.currentText()
            
            # --- LOGICA DE CONFLICTO LIDER ---
            if equipo_id and rol_elegido == 'lider_equipo':
                # Comprobar si ya hay lider en ese equipo
                try:
                    eq_data = db.client.table('equipos').select('lider_id').eq('id', equipo_id).single().execute()
                    if eq_data.data and eq_data.data.get('lider_id'):
                        lider_actual_id = eq_data.data['lider_id']
                        
                        # Preguntar al usuario
                        msg = "Este equipo ya tiene un líder asignado.\n¿Deseas transformar al líder actual en 'trabajador' y reemplazarlo?"
                        reply = QMessageBox.question(self, "Conflicto de Líder", msg, QMessageBox.Yes | QMessageBox.No)
                        
                        if reply == QMessageBox.Yes:
                            # Democion del lider actual
                            db.client.table('perfiles').update({'nivel_acceso': 'trabajador'}).eq('id', lider_actual_id).execute()
                            # (Opcional) Le quitamos el equipo? No, lo dejamos como miembro normal (trabajador) del mismo equipo.
                        else:
                            # Cancelar operacion
                            return 
                except Exception as e:
                    print(f"Error comprobando lider: {e}")

            # LLama al auth manager para registrar con todos los datos
            nuevo_usuario = self.auth_manager.registro(
                email=email.text(), 
                password=pwd.text(), 
                nombre=nombre.text(), 
                apellidos=apellidos.text(), 
                departamento_id=dep_id, 
                nivel=rol_elegido,
                equipo_id=equipo_id 
            )

            if nuevo_usuario:
                # Si es lider, actualizamos la tabla equipos
                if equipo_id and rol_elegido == 'lider_equipo':
                    try:
                        db.client.table('equipos').update({'lider_id': nuevo_usuario.id}).eq('id', equipo_id).execute()
                    except Exception as e:
                        print(f"Error asignando lider en tabla equipos: {e}")

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

    # --- IMPLEMENTACIÓN DE PESTAÑAS EXTRA (Departamentos y Equipos) ---
    def setup_extra_tabs(self):
        # Determinamos rol
        rol_actual = 'trabajador'
        if self.parent_window and hasattr(self.parent_window, 'rol'):
            rol_actual = self.parent_window.rol
        elif self.usuario and hasattr(self.usuario, 'nivel_acceso'):
            rol_actual = self.usuario.nivel_acceso

        # 1. Pestaña DEPARTAMENTOS (Solo Admin y Manager)
        if rol_actual in ['admin', 'manager']:
            self.tab_dept = QWidget()
            self.tabWidget.addTab(self.tab_dept, "🏢 Gestión Departamentos")
            self.construir_tab_departamentos()
        
        # 2. Pestaña EQUIPOS (Admin, Manager, Lider)
        if rol_actual in ['admin', 'manager', 'lider_equipo']:
            self.tab_equipos = QWidget()
            self.tabWidget.addTab(self.tab_equipos, "⚔️ Gestión Equipos")
            self.construir_tab_equipos()

    def construir_tab_departamentos(self):
        layout = QVBoxLayout(self.tab_dept)
        
        # Header botones
        h_layout = QHBoxLayout()
        btn_add = QPushButton("+ Nuevo Dept.")
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.setStyleSheet("background-color: #009688; color: white; padding: 6px 12px; border-radius: 4px; font-weight: bold;")
        btn_add.clicked.connect(self.crear_departamento_dialog)
        
        btn_refresh = QPushButton("🔄 Recargar")
        btn_refresh.setCursor(Qt.PointingHandCursor)
        btn_refresh.clicked.connect(self.cargar_departamentos)
        
        h_layout.addWidget(btn_add)
        h_layout.addStretch()
        h_layout.addWidget(btn_refresh)
        
        layout.addLayout(h_layout)
        
        # Tabla
        self.table_depts = QTableWidget()
        self.table_depts.setColumnCount(3)
        self.table_depts.setHorizontalHeaderLabels(["ID", "Nombre", "Descripción"])
        self.table_depts.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_depts.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_depts.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_depts.setAlternatingRowColors(True)
        # Menu contextual para borrar
        self.table_depts.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_depts.customContextMenuRequested.connect(self.menu_contextual_dept)
        
        layout.addWidget(self.table_depts)
        self.cargar_departamentos()

    def construir_tab_equipos(self):
        layout = QVBoxLayout(self.tab_equipos)
        
        # Header botones
        h_layout = QHBoxLayout()
        btn_add = QPushButton("+ Nuevo Equipo")
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.setStyleSheet("background-color: #673AB7; color: white; padding: 6px 12px; border-radius: 4px; font-weight: bold;")
        btn_add.clicked.connect(self.crear_equipo_dialog)

        btn_refresh = QPushButton("🔄 Recargar")
        btn_refresh.setCursor(Qt.PointingHandCursor)
        btn_refresh.clicked.connect(self.cargar_equipos)
        
        h_layout.addWidget(btn_add)
        h_layout.addStretch()
        h_layout.addWidget(btn_refresh)
        
        layout.addLayout(h_layout)

        # Tabla
        self.table_teams = QTableWidget()
        self.table_teams.setColumnCount(4)
        self.table_teams.setHorizontalHeaderLabels(["ID", "Nombre", "Departamento", "Líder (ID)"])
        self.table_teams.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_teams.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_teams.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_teams.setAlternatingRowColors(True)
        
        # Menu contextual para borrar
        self.table_teams.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_teams.customContextMenuRequested.connect(self.menu_contextual_equipo)

        layout.addWidget(self.table_teams)
        self.cargar_equipos()

    # --- LOGICA DEPARTAMENTOS ---
    def cargar_departamentos(self):
        data = self.task_manager.obtener_departamentos()
        self.table_depts.setRowCount(0)
        self.table_depts.setRowCount(len(data))
        for row, d in enumerate(data):
            self.table_depts.setItem(row, 0, QTableWidgetItem(str(d.get('id'))))
            self.table_depts.setItem(row, 1, QTableWidgetItem(d.get('nombre', '')))
            self.table_depts.setItem(row, 2, QTableWidgetItem(d.get('descripcion', '')))

    def crear_departamento_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Nuevo Departamento")
        dialog.setFixedWidth(300)
        layout = QFormLayout(dialog)
        
        nombre = QLineEdit()
        desc = QLineEdit()
        
        layout.addRow("Nombre:", nombre)
        layout.addRow("Descripción:", desc)
        
        btn = QPushButton("Crear")
        btn.clicked.connect(dialog.accept)
        layout.addRow(btn)
        
        if dialog.exec_():
            if not nombre.text(): return
            if self.task_manager.crear_departamento(nombre.text(), desc.text()):
                self.cargar_departamentos()
                QMessageBox.information(self, "Éxito", "Departamento creado.")
            else:
                QMessageBox.critical(self, "Error", "Fallo al crear departamento.")

    def menu_contextual_dept(self, pos):
        menu = QMenu()
        action_del = QAction("Eliminar Departamento", self)
        action_del.triggered.connect(self.borrar_dept_seleccionado)
        menu.addAction(action_del)
        menu.exec_(self.table_depts.viewport().mapToGlobal(pos))

    def borrar_dept_seleccionado(self):
        row = self.table_depts.currentRow()
        if row < 0: return
        id_dept = self.table_depts.item(row, 0).text()
        
        reply = QMessageBox.question(self, "Borrar", "¿Eliminar este departamento?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.task_manager.eliminar_departamento(id_dept):
                self.cargar_departamentos()
            else:
                QMessageBox.critical(self, "Error", "No se pudo borrar (puede tener usuarios asignados).")

    # --- LOGICA EQUIPOS ---
    def cargar_equipos(self):
        data = self.task_manager.obtener_equipos()
        # Necesitamos mapa de departamentos para mostrar nombres
        depts = self.task_manager.obtener_departamentos()
        dept_map = {d['id']: d['nombre'] for d in depts}

        self.table_teams.setRowCount(0)
        self.table_teams.setRowCount(len(data))
        for row, t in enumerate(data):
            self.table_teams.setItem(row, 0, QTableWidgetItem(str(t.get('id'))))
            self.table_teams.setItem(row, 1, QTableWidgetItem(t.get('nombre', '')))
            
            d_id = t.get('departamento_id')
            d_name = dept_map.get(d_id, d_id)
            self.table_teams.setItem(row, 2, QTableWidgetItem(str(d_name)))
            
            l_id = t.get('lider_id', 'Sin Líder')
            self.table_teams.setItem(row, 3, QTableWidgetItem(str(l_id)))

    def crear_equipo_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Nuevo Equipo")
        layout = QFormLayout(dialog)
        
        nombre = QLineEdit()
        desc = QLineEdit()
        
        combo_d = QComboBox()
        depts = self.task_manager.obtener_departamentos()
        for d in depts:
            combo_d.addItem(d['nombre'], d['id'])
            
        combo_l = QComboBox()
        combo_l.addItem("Sin líder inicialmente", None)
        # Podriamos cargar usuarios candidatos a lider, pero por simplicidad dejaremos asignar luego 
        # o cargar todos los usuarios.
        users = self.task_manager.obtener_todos_usuarios()
        for u in users:
            # Solo mostramos lideres potenciales? Dejemos a todos por flexibilidad
            combo_l.addItem(f"{u['email']} ({u['nivel_acceso']})", u['id'])

        layout.addRow("Nombre:", nombre)
        layout.addRow("Descripción:", desc)
        layout.addRow("Departamento:", combo_d)
        layout.addRow("Líder Inicial:", combo_l)
        
        btn = QPushButton("Crear")
        btn.clicked.connect(dialog.accept)
        layout.addRow(btn)
        
        if dialog.exec_():
            if not nombre.text(): return
            d_id = combo_d.currentData()
            l_id = combo_l.currentData()
            
            if self.task_manager.crear_equipo(nombre.text(), d_id, l_id, desc.text()):
                self.cargar_equipos()
                QMessageBox.information(self, "Éxito", "Equipo creado.")
            else:
                QMessageBox.critical(self, "Error", "Fallo al crear equipo.")

    def menu_contextual_equipo(self, pos):
        menu = QMenu()
        action_del = QAction("Eliminar Equipo", self)
        action_del.triggered.connect(self.borrar_equipo_seleccionado)
        menu.addAction(action_del)
        menu.exec_(self.table_teams.viewport().mapToGlobal(pos))

    def borrar_equipo_seleccionado(self):
        row = self.table_teams.currentRow()
        if row < 0: return
        id_eq = self.table_teams.item(row, 0).text()
        
        reply = QMessageBox.question(self, "Borrar", "¿Eliminar este equipo?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.task_manager.eliminar_equipo(id_eq):
                self.cargar_equipos()
            else:
                QMessageBox.critical(self, "Error", "No se pudo borrar (puede tener usuarios asignados).")