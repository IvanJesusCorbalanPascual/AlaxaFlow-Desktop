import os
from PyQt5.QtWidgets import (QMainWindow, QTableWidgetItem, QHeaderView, 
                             QDialog, QFormLayout, QLineEdit, QComboBox, 
                             QPushButton, QMessageBox, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTableWidget, QAbstractItemView, QMenu, QAction, QListWidget, QLabel)
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
        self.table_users.setColumnHidden(2, True) # Ocultar Apellidos (sobra)
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
        combo_dept.addItem("Seleccionar departamento...", None) 
        combo_equipo = QComboBox()
        combo_equipo.addItem("Seleccionar equipo...", None) 

        # Logica para cargar departamentos desde la BD
        try:
            res = db.client.table('departamentos').select('id, nombre').execute()
            combo_dept.clear()
            if res.data:
                for dep in res.data:
                    combo_dept.addItem(dep['nombre'], dep['id'])
        except Exception as e:
            pass

        # Logica cargar equipos (se podria filtrar por departamento mas adelante si se desea)
        # Por simplicidad cargamos todos, podriamos implementar filtro dinamico en update_ui_state tambien
        combo_equipo = QComboBox()
        combo_equipo.addItem("Sin equipo (Opcional)", None)

        # Logica cargar equipos 
        equipos_data = [] # Lista temporal para filtrar
        try:
            res_eq = db.client.table('equipos').select('id, nombre, departamento_id').execute()
            if res_eq.data:
                equipos_data = res_eq.data
        except Exception:
            pass

        # Labels para controlar visibilidad
        lbl_dept = QLabel("Departamento:")
        lbl_equipo = QLabel("Equipo:")
        
        # Filas del formulario
        layout.addRow("Nombre:", nombre)
        layout.addRow("Apellidos:", apellidos)
        layout.addRow("Email (Usuario):", email)
        layout.addRow("Contraseña:", pwd)
        layout.addRow("Rol:", rol)
        layout.addRow(lbl_dept, combo_dept)
        layout.addRow(lbl_equipo, combo_equipo)
        
        def filtrar_equipos():
            dept_id = combo_dept.currentData()
            combo_equipo.clear()
            # Siempre opción por defecto (especialmente util para roles que no requieren equipo o previo a seleccionar)
            # Pero logica de negocio dice Lider/Trabajador requires equipo. 
            # Dejamos "Seleccionar equipo..." como placeholder.
            combo_equipo.addItem("Seleccionar equipo...", None)
            
            if not dept_id:
                return

            for eq in equipos_data:
                # Filtrar por departamento
                if eq.get('departamento_id') == dept_id:
                    combo_equipo.addItem(eq['nombre'], eq['id'])

        # Conectar cambios
        combo_dept.currentIndexChanged.connect(filtrar_equipos)

        def update_ui_state():
            r = rol.currentText()
            # Admin: No dept, no team
            # Manager: Dept, no team
            # Lider/Trabajador: Dept, Team
            
            if r == 'admin':
                lbl_dept.hide()
                combo_dept.hide()
                lbl_equipo.hide()
                combo_equipo.hide()
            elif r == 'manager':
                lbl_dept.show()
                combo_dept.show()
                lbl_equipo.hide()
                combo_equipo.hide()
            else:
                lbl_dept.show()
                combo_dept.show()
                lbl_equipo.show()
                combo_equipo.show()
                
        rol.currentIndexChanged.connect(update_ui_state)
        update_ui_state() # estado inicial UI roles
        filtrar_equipos() # estado inicial Equipos (vacío o dept default)
        
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
            equipo_id = combo_equipo.currentData()
            rol_elegido = rol.currentText()

            # Validaciones por Rol (UI Rules)
            # Manager: Requiere Dept
            if rol_elegido == 'manager':
                if not dep_id:
                    QMessageBox.warning(self, "Error", "El rol Manager requiere seleccionar un Departamento.")
                    return
            # Lider/Trabajador: Requiere Dept y Equipo
            elif rol_elegido in ['lider_equipo', 'trabajador']:
                if not dep_id:
                     QMessageBox.warning(self, "Error", "Este rol requiere seleccionar un Departamento.")
                     return
                if not equipo_id:
                     QMessageBox.warning(self, "Error", "Este rol requiere seleccionar un Equipo.")
                     return
            
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
                            # REFACTOR: Usar metodo manager para mover de tabla
                            if hasattr(self, 'task_manager'):
                                self.task_manager._mover_usuario_de_tabla(lider_actual_id, 'trabajador')
                            else:
                                # Fallback si no tenemos referencia (rara vez)
                                print("Error: No task_manager ref")
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

        # 1. Pestaña DEPARTAMENTOS (Solo Admin)
        if rol_actual == 'admin':
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
        # Doble clic para editar
        self.table_depts.itemDoubleClicked.connect(self.abrir_detalle_departamento)
        
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
        self.table_teams.setColumnCount(5) # ID, Nombre, Dept, Lider, Manager
        self.table_teams.setHorizontalHeaderLabels(["ID", "Nombre", "Departamento", "Líder (ID)", "Manager (ID)"])
        self.table_teams.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_teams.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_teams.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_teams.setAlternatingRowColors(True)
        
        # Menu contextual para borrar
        self.table_teams.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_teams.customContextMenuRequested.connect(self.menu_contextual_equipo)
        # Doble clic para editar
        self.table_teams.itemDoubleClicked.connect(self.abrir_detalle_equipo)

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

    def abrir_detalle_departamento(self, item):
        row = item.row()
        id_dept = self.table_depts.item(row, 0).text()
        nombre_actual = self.table_depts.item(row, 1).text()
        desc_actual = self.table_depts.item(row, 2).text()
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Editar Departamento: {nombre_actual}")
        dialog.setFixedWidth(400)
        layout = QVBoxLayout(dialog)
        
        form_layout = QFormLayout()
        nombre_edit = QLineEdit(nombre_actual)
        desc_edit = QLineEdit(desc_actual)
        form_layout.addRow("Nombre:", nombre_edit)
        form_layout.addRow("Descripción:", desc_edit)
        layout.addLayout(form_layout)
        
        # Lista de Managers
        layout.addWidget(QLabel("<b>Managers actuales:</b>"))
        list_managers = QListWidget()
        list_managers.setFixedHeight(100)
        
        def refresh_managers_list():
            list_managers.clear()
            # Cargar managers de este depto
            users = self.task_manager.obtener_todos_usuarios()
            managers_dept = [u for u in users if u['nivel_acceso'] == 'manager' and str(u.get('departamento_id')) == str(id_dept)]
            
            if not managers_dept:
                list_managers.addItem("No hay managers asignados")
            else:
                for m in managers_dept:
                    list_managers.addItem(f"{m['email']} ({m.get('nombre', '')} {m.get('apellidos', '')})")
        
        refresh_managers_list()
        layout.addWidget(list_managers)
        
        # Boton Promover Manager
        btn_promover = QPushButton("Añadir Manager al Departamento")
        btn_promover.setStyleSheet("background-color: #2196F3; color: white;")
        
        def open_promote_dialog():
            self.promover_manager_dialog(id_dept)
            refresh_managers_list()
            
        btn_promover.clicked.connect(open_promote_dialog)
        layout.addWidget(btn_promover)
        
        btn_save = QPushButton("Guardar Cambios")
        btn_save.setStyleSheet("background: #4CAF50; color: white;")
        btn_save.clicked.connect(dialog.accept)
        layout.addWidget(btn_save)
        
        if dialog.exec_():
            if self.task_manager.editar_departamento(id_dept, nombre_edit.text(), desc_edit.text()):
                self.cargar_departamentos()
                QMessageBox.information(self, "Éxito", "Departamento actualizado.")
            else:
                QMessageBox.critical(self, "Error", "Error al actualizar departamento.")

    def promover_manager_dialog(self, dept_id):
        # Dialogo para seleccionar un usuario y hacerlo manager de este departamento
        d = QDialog(self)
        d.setWindowTitle("Promover a Manager")
        l = QVBoxLayout(d)
        l.addWidget(QLabel("Selecciona un empleado del departamento para ascender:"))
        
        combo = QComboBox()
        users = self.task_manager.obtener_todos_usuarios()
        
        # Filtrar: solo lideres o trabajadores DEL DEPARTAMENTO
        candidatos = []
        for u in users:
            if str(u.get('departamento_id')) == str(dept_id) and u['nivel_acceso'] in ['trabajador', 'lider_equipo']:
                 candidatos.append(u)
                 combo.addItem(f"{u['email']} ({u['nivel_acceso']})", u['id'])
        
        if not candidatos:
            combo.addItem("No hay candidatos elegibles en este departamento", None)
            
        l.addWidget(combo)
        btn = QPushButton("Promover")
        
        def realizar_promocion():
            user_id = combo.currentData()
            if not user_id: return
            
            # Verificar si es lider de algun equipo
            # Necesitamos consultar equipos. Ojo, un usuario podria ser lider de varios (teoricamente)
            # Simplificamos asumiendo 1.
            equipos = self.task_manager.obtener_equipos() # Seria mejor query filtrada pero vale
            equipos_liderados = [eq for eq in equipos if str(eq.get('lider_id')) == str(user_id)]
            
            for eq in equipos_liderados:
                msg = f"El usuario es actualmente líder del equipo '{eq['nombre']}'.\nEl puesto quedará vacante.\n¿Deseas seleccionar un sustituto ahora?"
                reply = QMessageBox.question(d, "Vacante de Líder", msg, QMessageBox.Yes | QMessageBox.No)
                
                if reply == QMessageBox.Yes:
                    # Dialogo anidado para sustituto
                    self.seleccionar_sustituto_lider(eq, dept_id, user_id)

            if self.task_manager.promover_a_manager(user_id, dept_id):
                QMessageBox.information(d, "Éxito", "Usuario promovido a Manager.")
                self.cargar_usuarios() 
                d.accept()
            else:
                QMessageBox.critical(d, "Error", "Fallo al promover usuario.")

        btn.clicked.connect(realizar_promocion)
        l.addWidget(btn)
        d.exec_()

    def seleccionar_sustituto_lider(self, equipo, dept_id, old_lider_id):
        # Dialogo para elegir nuevo lider para el equipo dado
        # Filtro: trabajadores del mismo departamento
        sd = QDialog(self)
        sd.setWindowTitle(f"Sustituto para: {equipo['nombre']}")
        sl = QVBoxLayout(sd)
        sl.addWidget(QLabel(f"Selecciona nuevo líder para '{equipo['nombre']}':"))
        
        s_combo = QComboBox()
        users = self.task_manager.obtener_todos_usuarios()
        
        count = 0
        for u in users:
            # No puede ser el que estamos promoviendo (old_lider_id)
            # Debe ser trabajador del depto
            if str(u.get('id')) != str(old_lider_id) and \
               str(u.get('departamento_id')) == str(dept_id) and \
               u['nivel_acceso'] == 'trabajador':
                   s_combo.addItem(f"{u['email']}", u['id'])
                   count += 1
        
        if count == 0:
            s_combo.addItem("No hay sustitutos disponibles", None)
        
        sl.addWidget(s_combo)
        s_btn = QPushButton("Asignar Nuevo Líder")
        s_btn.clicked.connect(sd.accept)
        sl.addWidget(s_btn)
        
        if sd.exec_():
            new_lider_id = s_combo.currentData()
            if new_lider_id:
                # Update equipo with new lider
                # Update new lider profile to 'lider_equipo' (auto handled by editar_equipologic?)
                # No, llamamos a editar_equipo o update directo. 
                # El task_manager.editar_equipo hace auto-promote.
                # Pero necesitamos mantener el resto de datos del equipo.
                try:
                    self.task_manager.editar_equipo(
                        equipo['id'], 
                        equipo['nombre'], 
                        equipo['departamento_id'], 
                        new_lider_id, 
                        equipo.get('manager_id'), 
                        equipo.get('descripcion')
                    )
                except Exception as e:
                    print(f"Error asignando sustituto: {e}")
            else:
                # Si no selecciona nadie, el equipo se queda sin lider?
                # O mantenemos el anterior (que ahora es manager)? 
                # El requisito dice "se quedara vacio". Asi que update lider_id = None
                 try:
                    db.client.table('equipos').update({'lider_id': None}).eq('id', equipo['id']).execute()
                 except: pass

    # --- LOGICA EQUIPOS ---
    def cargar_equipos(self):
        data = self.task_manager.obtener_equipos()
        # Necesitamos mapa de departamentos para mostrar nombres
        depts = self.task_manager.obtener_departamentos()
        dept_map = {d['id']: d['nombre'] for d in depts}
        
        # Mapa de nombres de usuarios para Lider y Manager
        users = self.task_manager.obtener_todos_usuarios()
        user_map = {u['id']: u['email'] for u in users}

        self.table_teams.setRowCount(0)
        self.table_teams.setRowCount(len(data))
        for row, t in enumerate(data):
            self.table_teams.setItem(row, 0, QTableWidgetItem(str(t.get('id'))))
            self.table_teams.setItem(row, 1, QTableWidgetItem(t.get('nombre', '')))
            
            d_id = t.get('departamento_id')
            d_name = dept_map.get(d_id, str(d_id))
            self.table_teams.setItem(row, 2, QTableWidgetItem(str(d_name)))
            
            l_id = t.get('lider_id')
            l_name = user_map.get(l_id, "Sin Líder") if l_id else "Sin Líder"
            self.table_teams.setItem(row, 3, QTableWidgetItem(l_name))
            
            m_id = t.get('manager_id')
            m_name = user_map.get(m_id, "Sin Manager") if m_id else "Sin Manager"
            self.table_teams.setItem(row, 4, QTableWidgetItem(m_name))

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
        # Se cargara dinamicamente al cambiar de departamento
        
        combo_m = QComboBox()
        
        # Logica: si soy admin, elijo manager. Si soy manager, me asigno yo.
        rol_actual = 'trabajador'
        if self.parent_window and hasattr(self.parent_window, 'rol'):
            rol_actual = self.parent_window.rol
        elif self.usuario and hasattr(self.usuario, 'nivel_acceso'):
            rol_actual = self.usuario.nivel_acceso
            
        users = self.task_manager.obtener_todos_usuarios()
        
        # Llenar Combo Manager (Solo visible para Admin)
        if rol_actual == 'admin':
             combo_m.addItem("Sin manager asignado", None)
             for u in users:
                 if u['nivel_acceso'] in ['manager', 'admin']:
                     combo_m.addItem(f"{u['email']} ({u['nivel_acceso']})", u['id'])
        else:
             # Si no soy admin (soy manager), el combo no se muestra o queda deshabilitado
             # Ocultaremos el widget en el layout mas abajo
             pass

        # Funcion para filtrar lideres del departamento seleccionado
        def actualizar_lideres():
             dept_id = combo_d.currentData()
             combo_l.clear()
             combo_l.addItem("Sin líder inicialmente", None)
             
             if not dept_id: return
             
             for u in users:
                 # Filtro: debe ser 'trabajador' y pertenecer al departamento
                 # (Opcional: permitir tambien a quien ya sea lider_equipo pero no tenga equipo? 
                 #  Por ahora estricto: trabajador del dpto)
                 u_dept = u.get('departamento_id')
                 u_rol = u.get('nivel_acceso')
                 
                 # NOTA: u_dept puede ser string o int, asegurar comparacion
                 if str(u_dept) == str(dept_id) and u_rol == 'trabajador':
                      combo_l.addItem(f"{u['email']}", u['id'])

        combo_d.currentIndexChanged.connect(actualizar_lideres)
        # Llamada inicial
        actualizar_lideres()

        layout.addRow("Nombre:", nombre)
        layout.addRow("Descripción:", desc)
        layout.addRow("Departamento:", combo_d)
        layout.addRow("Líder Inicial:", combo_l)
        
        if rol_actual == 'admin':
            layout.addRow("Manager Responsable:", combo_m)
        
        btn = QPushButton("Crear")
        btn.clicked.connect(dialog.accept)
        layout.addRow(btn)
        
        if dialog.exec_():
            if not nombre.text(): return
            d_id = combo_d.currentData()
            l_id = combo_l.currentData()
            
            m_id = None
            if rol_actual == 'admin':
                m_id = combo_m.currentData()
            elif rol_actual == 'manager':
                # Autoasignar self.usuario.id
                if self.usuario and hasattr(self.usuario, 'id'):
                     m_id = self.usuario.id
            
            if self.task_manager.crear_equipo(nombre.text(), d_id, l_id, desc.text(), m_id):
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

    def abrir_detalle_equipo(self, item):
        row = item.row()
        id_eq = self.table_teams.item(row, 0).text()
        try:
            res = db.client.table('equipos').select('*').eq('id', id_eq).single().execute()
            eq_data = res.data
        except:
             QMessageBox.critical(self, "Error", "No se pudo cargar info del equipo")
             return

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Editar Equipo: {eq_data['nombre']}")
        dialog.setFixedWidth(400)
        layout = QFormLayout(dialog)
        
        nombre = QLineEdit(eq_data['nombre'])
        desc = QLineEdit(eq_data.get('descripcion', ''))
        
        combo_d = QComboBox()
        depts = self.task_manager.obtener_departamentos()
        idx_d = 0
        current_dept_id = eq_data.get('departamento_id')
        for i, d in enumerate(depts):
            combo_d.addItem(d['nombre'], d['id'])
            if str(d['id']) == str(current_dept_id):
                idx_d = i
        combo_d.setCurrentIndex(idx_d)

        # Lider
        combo_l = QComboBox()
        
        # Manager
        combo_m = QComboBox()
        
        users = self.task_manager.obtener_todos_usuarios()
        current_lider_id = eq_data.get('lider_id')
        current_manager_id = eq_data.get('manager_id')

        # Rol actual admin?
        rol_actual = 'trabajador'
        if self.parent_window and hasattr(self.parent_window, 'rol'):
            rol_actual = self.parent_window.rol
        elif self.usuario and hasattr(self.usuario, 'nivel_acceso'):
            rol_actual = self.usuario.nivel_acceso

        if rol_actual == 'admin':
             combo_m.addItem("Sin Manager", None)
             idx_m = 0
             count_m = 1
             for u in users:
                 if u['nivel_acceso'] in ['manager', 'admin']: 
                     combo_m.addItem(f"{u['email']} ({u['nivel_acceso']})", u['id'])
                     if str(u['id']) == str(current_manager_id):
                         idx_m = count_m
                     count_m += 1
             combo_m.setCurrentIndex(idx_m)
        
        def actualizar_lideres_edit():
             # Guardar seleccion actual si es posible preservarla? 
             # Es dificil pq la lista cambia. Solo preseleccionamos si coincide con el lider actual del equipo (si no ha cambiado dept)
             # O si estamos editando, el lider actual DEBE salir aunque ya no cumpla las condiciones?
             # Vamos a permitir que salga el lider actual + trabajadores del dpto seleccionado.
             selected_dept = combo_d.currentData()
             
             combo_l.clear()
             combo_l.addItem("Sin Líder", None)
             
             idx_l = 0
             count_l = 1
             
             for u in users:
                 u_id = u['id']
                 u_dept = u.get('departamento_id')
                 u_rol = u.get('nivel_acceso')
                 
                 es_lider_actual = (str(u_id) == str(current_lider_id))
                 es_trabajador_del_dept = (str(u_dept) == str(selected_dept) and u_rol == 'trabajador')
                 
                 if es_lider_actual or es_trabajador_del_dept:
                      combo_l.addItem(f"{u['email']}", u_id)
                      if es_lider_actual:
                          idx_l = count_l
                      count_l += 1
             
             combo_l.setCurrentIndex(idx_l)

        combo_d.currentIndexChanged.connect(actualizar_lideres_edit)
        actualizar_lideres_edit() # Init
        
        layout.addRow("Nombre:", nombre)
        layout.addRow("Descripción:", desc)
        layout.addRow("Departamento:", combo_d)
        layout.addRow("Líder:", combo_l)
        
        if rol_actual == 'admin':
            layout.addRow("Manager:", combo_m)
        
        btn = QPushButton("Guardar Cambios")
        btn.clicked.connect(dialog.accept)
        layout.addRow(btn)
        
        if dialog.exec_():
            new_lider_id = combo_l.currentData()
            
            # Conflicto Lider en Edicion
            # Si cambiamos de lider y habia uno anterior
            if new_lider_id and current_lider_id and new_lider_id != current_lider_id:
                   msg = "Has cambiado el líder del equipo.\n¿Deseas cambiar el rol del líder ANTERIOR a 'trabajador'?"
                   reply = QMessageBox.question(self, "Líder anterior", msg, QMessageBox.Yes | QMessageBox.No)
                   if reply == QMessageBox.Yes:
                       try:
                           # REFACTOR: Usar TaskManager
                           if hasattr(self, 'task_manager'):
                               self.task_manager._mover_usuario_de_tabla(current_lider_id, 'trabajador')
                       except Exception as e:
                           print(f"Error al democionar lider anterior: {e}")
            
            # Determinar manager_id final
            m_id_final = current_manager_id
            if rol_actual == 'admin':
                m_id_final = combo_m.currentData()

            if self.task_manager.editar_equipo(id_eq, nombre.text(), 
                                               combo_d.currentData(), 
                                               new_lider_id,
                                               m_id_final, 
                                               desc.text()):
                QMessageBox.information(self, "Éxito", "Equipo actualizado")
                self.cargar_equipos()
            else:
                QMessageBox.critical(self, "Error", "Fallo al actualizar")