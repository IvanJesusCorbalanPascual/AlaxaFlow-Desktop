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

ESTILO_ADMIN_NORMAL = """
    QMainWindow, QDialog, QWidget { background-color: #FAFAFA; color: #3E2723; font-family: 'Segoe UI'; }
    QLabel { color: #3E2723; font-weight: bold; font-size: 14px; }
    
    /* [AÑADIDO] Estilos de cabecera que antes estaban en el .ui */
    #frame_header { background-color: #FFFFFF; border-bottom: 2px solid #D7CCC8; }
    #label_title { color: #3E2723; font-weight: bold; font-size: 20px; }

    QLineEdit, QComboBox { 
        background-color: #FFFFFF; color: #3E2723; 
        border: 2px solid #D7CCC8; border-radius: 4px; padding: 5px; 
    }
    QComboBox QAbstractItemView { 
        background-color: #FFFFFF; color: #3E2723; 
        selection-background-color: #FFB74D; selection-color: #3E2723; 
    }
    
    /* Estilos de Pestañas y Tablas del .ui original */
    QTabWidget::pane { border: 1px solid #D7CCC8; } 
    QTabBar::tab { background: #EFEBE9; padding: 10px 20px; color: #5D4037; border-top-left-radius: 4px; border-top-right-radius: 4px; margin-right: 2px; }
    QTabBar::tab:selected { background: #FFFFFF; font-weight: bold; border-top: 3px solid #FF9800; border-bottom: 1px solid #FFFFFF; }

    QTableWidget { background-color: white; border: 1px solid #ddd; color: #333; gridline-color: #eee; }
    QHeaderView::section { background-color: #f0f0f0; padding: 4px; border: 1px solid #ddd; }
    
    QPushButton { 
        background-color: #EFEBE9; color: #3E2723; 
        border: 1px solid #D7CCC8; padding: 6px 15px; border-radius: 4px; 
    }
    QPushButton:hover { background-color: #D7CCC8; }

    /* Restauración de colores de botones (Verde, Naranja, etc.) */
    QPushButton#btn_add_user, QPushButton#btn_registrar, QPushButton#btn_save_dept { 
        background-color: #4CAF50; color: white; font-weight: bold; border: none;
    }
    QPushButton#btn_add_board, QPushButton#btn_crear_tablero { 
        background-color: #FF9800; color: white; font-weight: bold; border: none;
    }
    QPushButton#btn_add_dept { background-color: #009688; color: white; font-weight: bold; border: none; }
    QPushButton#btn_add_team { background-color: #673AB7; color: white; font-weight: bold; border: none; }
    QPushButton#btn_promover { background-color: #2196F3; color: white; border: none; }
    
    QPushButton#btn_back { 
        background-color: #795548; color: white; font-weight: bold; border-radius: 4px; 
    }
    
    QPushButton#btn_refresh, QPushButton#btn_refresh_users, QPushButton#btn_refresh_boards { 
         background-color: transparent; color: #00BCD4; font-weight: bold; border: 2px solid #00BCD4;
    }
    QPushButton#btn_refresh:hover, QPushButton#btn_refresh_users:hover, QPushButton#btn_refresh_boards:hover {
         background-color: #E0F7FA;
    }
"""

ESTILO_ADMIN_CONTRASTE = """
    QMainWindow, QDialog, QWidget, QFrame { background-color: #000000; color: #FFFF00; }
    QLabel { color: #FFFF00; font-weight: bold; font-size: 14px; background: transparent; }

    /* IDs actualizados para coincidir con el .ui (#frame_header) */
    #frame_header { background-color: #000000; border-bottom: 4px solid #FFFF00; }
    #label_title { color: #FFFF00; font-size: 22px; text-decoration: underline; }
    
    /* Regla para contenedores de pestañas */
    #tab_users, #tab_boards, #tab_dept, #tab_equipos {
        background-color: #000000; border: none;
    }

    QLineEdit, QComboBox { 
        background-color: #000000; color: #FFFF00; 
        border: 2px solid #FFFF00; border-radius: 0px; padding: 5px; 
    }
    QComboBox QAbstractItemView { 
        background-color: #000000; color: #FFFF00; 
        selection-background-color: #FFFF00; selection-color: #000000; 
        border: 1px solid #FFFF00; 
    }
    
    /* Tablas forzadas a negro */
    QTableWidget, QTableView { 
        background-color: #000000; color: #FFFF00; 
        gridline-color: #FFFF00; border: 2px solid #FFFF00; 
        alternate-background-color: #000000; 
    }
    QTableWidget::item:selected { background-color: #333333; color: #FFFF00; }

    QHeaderView { background-color: #000000; border: none; }
    QHeaderView::section { 
        background-color: #000000; color: #FFFF00; 
        padding: 5px; border: 1px solid #FFFF00; font-weight: bold; 
    }
    QTableCornerButton::section { background-color: #000000; border: 1px solid #FFFF00; }

    QTabWidget::pane { border: 2px solid #FFFF00; background-color: #000000; }
    QTabBar::tab { 
        background: #000000; color: #FFFF00; 
        border: 2px solid #FFFF00; padding: 8px 12px; margin-right: 4px; 
    }
    QTabBar::tab:selected { background: #FFFF00; color: #000000; font-weight: bold; }

    QPushButton { 
        background-color: #000000; color: #FFFF00; 
        border: 2px solid #FFFF00; padding: 6px 15px; border-radius: 0px; font-weight: bold; 
    }
    QPushButton:hover { background-color: #333333; color: #FFFFFF; border-color: #FFFFFF; }

    /* Forzar todos los botones a negro */
    QPushButton#btn_add_user, QPushButton#btn_add_board,
    QPushButton#btn_registrar, QPushButton#btn_crear_tablero, 
    QPushButton#btn_add_dept, QPushButton#btn_add_team, 
    QPushButton#btn_promover, QPushButton#btn_save_dept,
    QPushButton#btn_refresh, QPushButton#btn_refresh_users, QPushButton#btn_refresh_boards,
    QPushButton#btn_back {
        background-color: #000000; 
        color: #FFFF00; 
        border: 2px solid #FFFF00;
    }
    QPushButton#btn_back:hover, QPushButton#btn_add_team:hover {
        background-color: #333333; color: white;
    }
"""

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

        if hasattr(self, 'tab_users'): self.tab_users.setObjectName("tab_users")
        if hasattr(self, 'tab_boards'): self.tab_boards.setObjectName("tab_boards")

        self.btn_back.setObjectName("btn_back")
        self.btn_add_user.setObjectName("btn_add_user")
        self.btn_add_board.setObjectName("btn_add_board")

        self.btn_refresh_users.setObjectName("btn_refresh_users")
        self.btn_refresh_boards.setObjectName("btn_refresh_boards")

        self.setup_tables()
        self.conectar_botones()
        
        # Cargar datos iniciales
        self.cargar_usuarios()
        self.cargar_tableros()
        
        # Pestañas extra según rol
        self.setup_extra_tabs()

        self.aplicar_estilo(self)

    # Método para aplicar el estilo adecuado según el tema actual
    def aplicar_estilo(self, widget):
        usar_contraste = False
        # Consulta a MainWindow qué tema está usando
        if self.parent_window and hasattr(self.parent_window, 'tema_actual') and self.parent_window.tema_actual == 'contraste':
            usar_contraste = True
            
        if usar_contraste:
            widget.setStyleSheet(ESTILO_ADMIN_CONTRASTE)
            self.table_users.setAlternatingRowColors(False)
            self.table_boards.setAlternatingRowColors(False)
            if hasattr(self, 'table_depts'): self.table_depts.setAlternatingRowColors(False)
            if hasattr(self, 'table_teams'): self.table_teams.setAlternatingRowColors(False)
        else:
            widget.setStyleSheet(ESTILO_ADMIN_NORMAL)
            self.table_users.setAlternatingRowColors(True)
            self.table_boards.setAlternatingRowColors(True)
            if hasattr(self, 'table_depts'): self.table_depts.setAlternatingRowColors(True)
            if hasattr(self, 'table_teams'): self.table_teams.setAlternatingRowColors(True)

    def setup_tables(self):
        # Ajustar ancho de columnas para que se vean bonitas
        self.table_users.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_users.setColumnHidden(2, True) # Ocultar Apellidos (sobra)
        self.table_boards.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def conectar_botones(self):
        self.btn_back.clicked.connect(self.volver)
        
        # --- USUARIOS ---
        self.btn_add_user.clicked.connect(self.crear_usuario_dialog)
        self.btn_refresh_users.clicked.connect(self.cargar_usuarios)

        # Activar Clic Derecho y Doble Clic en Tabla Usuarios 
        self.table_users.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_users.customContextMenuRequested.connect(self.menu_contextual_usuario)
        self.table_users.itemDoubleClicked.connect(self.abrir_detalle_usuario)

        # --- TABLEROS ---
        self.input_search_board.textChanged.connect(self.filtrar_tableros)
        self.btn_go_board.clicked.connect(self.ir_al_tablero_seleccionado)
        self.btn_add_board.clicked.connect(self.crear_tablero_dialog)
        self.btn_refresh_boards.clicked.connect(self.cargar_tableros)
        
        # Activar Clic Derecho y Doble Clic en Tabla Tableros
        self.table_boards.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_boards.customContextMenuRequested.connect(self.menu_contextual_tablero)
        self.table_boards.itemDoubleClicked.connect(self.abrir_detalle_tablero)

    def volver(self):
        if self.parent_window:
            self.parent_window.show()
        self.close()

    # --- LÓGICA DE CARGA DE DATOS ---
    def cargar_usuarios(self):
        filtro = None
        if self.usuario.nivel_acceso == 'manager':
            filtro = self.usuario.departamento_id
            
        # Pedir usuarios filtrados
        usuarios = self.task_manager.obtener_todos_usuarios(filtro_dept_id=filtro)
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
        filtro = None
        if self.usuario.nivel_acceso == 'manager':
            filtro = self.usuario.departamento_id
            
        tableros = self.task_manager.obtener_todos_tableros(filtro_dept_id=filtro)
        
        # Obtenemos equipos para traducir ID -> Nombre
        equipos = self.task_manager.obtener_equipos()
        equipos_map = {e['id']: e['nombre'] for e in equipos}

        # Cambiamos cabecera de la columna 4 (índice 3)
        self.table_boards.setHorizontalHeaderItem(3, QTableWidgetItem("Equipo Asignado"))

        self.table_boards.setRowCount(0)
        self.table_boards.setRowCount(len(tableros))
        
        for row, t in enumerate(tableros):
            self.table_boards.setItem(row, 0, QTableWidgetItem(str(t.get('id'))))
            self.table_boards.setItem(row, 1, QTableWidgetItem(t.get('titulo', '')))
            self.table_boards.setItem(row, 2, QTableWidgetItem(t.get('descripcion', '')))
            
            # Buscamos el nombre del equipo usando el ID
            eq_id = t.get('equipo_id')
            nombre_equipo = equipos_map.get(eq_id, "---")
            self.table_boards.setItem(row, 3, QTableWidgetItem(nombre_equipo))

    # --- USUARIOS ---

    # Dialogo de creación de usuario
    def crear_usuario_dialog(self): # Dialogo para crear un usuario con su nombre, email, contraseña y rol
        dialog = QDialog(self)
        dialog.setWindowTitle("Registrar Nuevo Usuario")
        dialog.setFixedWidth(400)
        # Usa el helper para el estilo para asegurar que se ve bien
        self.aplicar_estilo(dialog)
        
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

        lbl_dept = QLabel("Departamento:")
        combo_dept = QComboBox()
        lbl_equipo = QLabel("Equipo:")
        combo_equipo = QComboBox()
        combo_equipo.addItem("Seleccionar equipo...", None) 

        # Logica para cargar departamentos desde la BD
        try:
            res = db.client.table('departamentos').select('id, nombre')
            if rol_actual =='manager':
                res = res.eq('id', self.usuario.departamento_id)
            res = res.execute()
            combo_dept.clear()

            if rol_actual != 'manager': # Solo si no es manager
                combo_dept.addItem("Seleccionar departamento...", None)

            if res.data:
                for dep in res.data:
                    combo_dept.addItem(dep['nombre'], dep['id'])
            if rol_actual == 'manager':
                # Seleccionamos el departamento automáticamente
                idx = combo_dept.findData(self.usuario.departamento_id)
                if idx >= 0: combo_dept.setCurrentIndex(idx)
                
                # Oculatmos los widgets de departamento
                lbl_dept.hide()
                combo_dept.hide()
        except Exception: pass

        # Logica cargar equipos sin filtro
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
        btn.setObjectName("btn_registrar")
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
                            if hasattr(self, 'task_manager'):
                                self.task_manager._mover_usuario_de_tabla(lider_actual_id, 'trabajador')
                            else:
                                # Fallback si no tenemos referencia (rara vez)
                                print("Error: No task_manager ref")
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

    # Menu contextual para tabla usuarios (eliminar usuario)
    def menu_contextual_usuario(self, pos):
        menu = QMenu()
        action_del = QAction("Eliminar Usuario", self)
        action_del.triggered.connect(self.borrar_usuario_seleccionado)
        menu.addAction(action_del)
        menu.exec_(self.table_users.viewport().mapToGlobal(pos))

    def borrar_usuario_seleccionado(self):
        row = self.table_users.currentRow()
        if row < 0: return
        id_user = self.table_users.item(row, 0).text()
        email_user = self.table_users.item(row, 3).text()
        # Comprobar si el usuario es lider de algun equipo
        es_lider = False
        nombre_equipo_liderado = ""
        equipos_donde_es_lider = []
        
        try:
            equipos = self.task_manager.obtener_equipos()
            for eq in equipos:
                # Comparar como strings para estar seguros
                if str(eq.get('lider_id')) == str(id_user):
                    es_lider = True
                    nombre_equipo_liderado = eq.get('nombre', 'un equipo')
                    equipos_donde_es_lider.append(eq['id'])
        except Exception as e:
            print(f"Error checking leadership: {e}")

        if es_lider:
             count = len(equipos_donde_es_lider)
             if count > 1:
                 msg = f"El usuario {email_user} es líder de {count} equipos.\nSi sigues, dejarás esos equipos sin líder.\n¿Seguro que quieres eliminarlo?"
             else:
                 msg = f"El usuario {email_user} es líder del equipo '{nombre_equipo_liderado}'.\nSi sigues, vas a dejar ese equipo sin líder.\n¿Seguro que quieres eliminarlo?"
        else:
             msg = f"¿Estás seguro de eliminar a {email_user}?\nEsta acción es irreversible."

        reply = QMessageBox.question(self, "Confirmar Eliminación", msg, QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            if es_lider and equipos_donde_es_lider:
                try:
                    for eq_id in equipos_donde_es_lider:
                        # Lider a None
                        db.client.table('equipos').update({'lider_id': None}).eq('id', eq_id).execute()
                except Exception as e:
                    print(f"Error unlinking leader: {e}")
                    QMessageBox.critical(self, "Error", f"Error al desvincular equipos: {e}")
                    return

            if self.task_manager.eliminar_usuario(id_user):
                self.cargar_usuarios()
                if hasattr(self, 'cargar_equipos'):
                    self.cargar_equipos()
                QMessageBox.information(self, "Eliminado", "Usuario eliminado correctamente.")
            else:
                QMessageBox.critical(self, "Error", "No se pudo eliminar el usuario (posible error de BD).")

    # Doble clic para editar los datos del usuario
    def abrir_detalle_usuario(self, item):
        # Edición de usuario al hacer doble clic
        row = item.row()
        id_user = self.table_users.item(row, 0).text()
        
        # Recuperar datos frescos de la BD
        try:
            res = db.client.table('perfiles').select('*').eq('id', id_user).single().execute()
            data = res.data
        except:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Editar: {data.get('email')}")
        dialog.setFixedWidth(400)
        self.aplicar_estilo(dialog)
        layout = QFormLayout(dialog)
        
        nombre = QLineEdit(data.get('nombre', ''))
        apellidos = QLineEdit(data.get('apellidos', ''))
        
        # Rol
        rol_combo = QComboBox()
        if self.usuario.nivel_acceso == 'admin':
            rol_combo.addItems(["trabajador", "lider_equipo", "manager", "admin"])
        elif self.usuario.nivel_acceso == 'manager':
            rol_combo.addItems(["trabajador", "lider_equipo"])
        rol_combo.setCurrentText(data.get('nivel_acceso', 'trabajador'))
        
        # Departamentos
        lbl_dept = QLabel("Departamento:")
        dept_combo = QComboBox()
        dept_combo.addItem("Sin Departamento", None)
        depts = self.task_manager.obtener_departamentos()

        if self.usuario.nivel_acceso == 'manager':
            # Solo dejo mi propio departamento en la lista
            depts = [d for d in depts if str(d['id']) == str(self.usuario.departamento_id)]

        idx_d = 0
        for i, d in enumerate(depts):
            dept_combo.addItem(d['nombre'], d['id'])
            if str(d['id']) == str(data.get('departamento_id')):
                idx_d = i + 1 # +1 por el item "Sin Dept"
        dept_combo.setCurrentIndex(idx_d)

        # Equipos (Carga simple para edición)
        lbl_equipo = QLabel("Equipo:")
        equipo_combo = QComboBox()
        equipo_combo.addItem("Sin Equipo", None)
        equipos = self.task_manager.obtener_equipos()
        
        # Intentar buscar el equipo actual del usuario (tabla trabajadores)
        equipo_actual_id = data.get('equipo_id')

        idx_e = 0
        for i, e in enumerate(equipos):
            equipo_combo.addItem(e['nombre'], e['id'])
            if str(e['id']) == str(equipo_actual_id):
                idx_e = i + 1
        equipo_combo.setCurrentIndex(idx_e)

        layout.addRow("Nombre:", nombre)
        layout.addRow("Apellidos:", apellidos)
        layout.addRow("Rol:", rol_combo)
        layout.addRow(lbl_dept, dept_combo)
        layout.addRow(lbl_equipo, equipo_combo)

        # --- Lógica de visibilidad dinámica ---
        def update_edit_ui_state():
            r = rol_combo.currentText()
            # Admin: No dept, no team
            # Manager: Dept, no team
            # Lider/Trabajador: Dept, Team
            
            if r == 'admin':
                lbl_dept.hide()
                dept_combo.hide()
                lbl_equipo.hide()
                equipo_combo.hide()
            elif r == 'manager':
                lbl_dept.show()
                dept_combo.show()
                lbl_equipo.hide()
                equipo_combo.hide()
            else:
                lbl_dept.show()
                dept_combo.show()
                lbl_equipo.show()
                equipo_combo.show()
        
        rol_combo.currentIndexChanged.connect(update_edit_ui_state)
        update_edit_ui_state() # Estado inicial
        
        btn_save = QPushButton("Guardar Cambios")
        btn_save.clicked.connect(dialog.accept)
        layout.addRow(btn_save)
        
        if dialog.exec_():
            if self.task_manager.editar_usuario(
                id_user, 
                nombre.text(), 
                apellidos.text(), 
                rol_combo.currentText(),
                dept_combo.currentData(),
                equipo_combo.currentData()
            ):
                QMessageBox.information(self, "Éxito", "Datos de usuario actualizados.")
                self.cargar_usuarios()
            else:
                QMessageBox.critical(self, "Error", "Fallo al actualizar usuario.")

    # --- TABLEROS ---

    # Dialogo para crear un tablero con su nombre y descripcion, y asignarlo a un usuario
    def crear_tablero_dialog(self): 
        equipos = self.task_manager.obtener_equipos()
        
        if self.usuario.nivel_acceso == 'manager':
            equipos = [e for e in equipos if str(e.get('departamento_id')) == str(self.usuario.departamento_id)]

        if not equipos:
            QMessageBox.warning(self, "Aviso", "No hay equipos disponibles. Crea un equipo primero.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Nuevo Tablero de Equipo")
        self.aplicar_estilo(dialog)
        layout = QFormLayout(dialog)
        
        titulo = QLineEdit()
        desc = QLineEdit()
        combo_equipo = QComboBox()
        
        for e in equipos:
            combo_equipo.addItem(e['nombre'], e['id'])
            
        layout.addRow("Título:", titulo)
        layout.addRow("Descripción:", desc)
        layout.addRow("Asignar al Equipo:", combo_equipo)
        
        btn = QPushButton("Crear Tablero")
        btn.clicked.connect(dialog.accept)
        layout.addRow(btn)
        
        if dialog.exec_():
            if not titulo.text(): return
            equipo_id = combo_equipo.currentData()
            
            # Llamamos a crear SIN pasar usuario (ya no existe creado_por)
            if self.task_manager.crear_tablero_admin(titulo.text(), desc.text(), equipo_id):
                 QMessageBox.information(self, "Éxito", "Tablero creado correctamente.")
                 self.cargar_tableros()
            else:
                QMessageBox.critical(self, "Error", "No se pudo crear el tablero.")

    # --- IMPLEMENTACIÓN DE PESTAÑAS EXTRA (Departamentos y Equipos) ---
    def setup_extra_tabs(self):
        # Determinamos rol
        rol_actual = 'trabajador'
        if self.parent_window and hasattr(self.parent_window, 'rol'):
            rol_actual = self.parent_window.rol
        elif self.usuario and hasattr(self.usuario, 'nivel_acceso'):
            rol_actual = self.usuario.nivel_acceso

        # Pestaña DEPARTAMENTOS (Solo Admin)
        if rol_actual == 'admin':
            self.tab_dept = QWidget()
            self.tab_dept.setObjectName("tab_dept")
            self.tabWidget.addTab(self.tab_dept, "🏢 Gestión Departamentos")
            self.construir_tab_departamentos()
        
        # Pestaña EQUIPOS (Admin, Manager, Lider)
        if rol_actual in ['admin', 'manager', 'lider_equipo']:
            self.tab_equipos = QWidget()
            self.tab_equipos.setObjectName("tab_equipos")
            self.tabWidget.addTab(self.tab_equipos, "⚔️ Gestión Equipos")
            self.construir_tab_equipos()

    def construir_tab_departamentos(self):
        layout = QVBoxLayout(self.tab_dept)
        
        # Header botones
        h_layout = QHBoxLayout()
        btn_add = QPushButton("+ Nuevo Dept.")
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.setObjectName("btn_add_dept")
        btn_add.clicked.connect(self.crear_departamento_dialog)
        
        btn_refresh = QPushButton("🔄 Recargar")
        btn_refresh.setCursor(Qt.PointingHandCursor)
        btn_refresh.setObjectName("btn_refresh")
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
        btn_add.setObjectName("btn_add_team")
        btn_add.clicked.connect(self.crear_equipo_dialog)

        btn_refresh = QPushButton("🔄 Recargar")
        btn_refresh.setCursor(Qt.PointingHandCursor)
        btn_refresh.setObjectName("btn_refresh")
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

    # Menu contextual para tabla tableros (eliminar tablero)
    def menu_contextual_tablero(self, pos):
        menu = QMenu()
        action_del = QAction("Eliminar Tablero", self)
        action_del.triggered.connect(self.borrar_tablero_seleccionado)
        menu.addAction(action_del)
        menu.exec_(self.table_boards.viewport().mapToGlobal(pos))

    def borrar_tablero_seleccionado(self):
        row = self.table_boards.currentRow()
        if row < 0: return
        id_tablero = self.table_boards.item(row, 0).text()
        titulo = self.table_boards.item(row, 1).text()
        
        reply = QMessageBox.question(self, "Borrar", f"¿Eliminar tablero '{titulo}' y todas sus tareas?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.task_manager.eliminar_tablero(id_tablero):
                self.cargar_tableros()
            else:
                QMessageBox.critical(self, "Error", "No se pudo borrar el tablero.")

    # Doble clic para editar los datos del tablero
    def abrir_detalle_tablero(self, item):
        row = item.row()
        id_tablero = self.table_boards.item(row, 0).text()
        
        try:
            res = db.client.table('tableros').select('*').eq('id', id_tablero).single().execute()
            data = res.data
        except: return

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Editar: {data.get('titulo')}")
        self.aplicar_estilo(dialog)
        layout = QFormLayout(dialog)
        
        titulo = QLineEdit(data.get('titulo', ''))
        desc = QLineEdit(data.get('descripcion', ''))
        
        combo_equipo = QComboBox()
        equipos = self.task_manager.obtener_equipos()
        
        if self.usuario.nivel_acceso == 'manager':
             equipos = [e for e in equipos if str(e.get('departamento_id')) == str(self.usuario.departamento_id)]

        idx_eq = 0
        current_eq = data.get('equipo_id')
        for i, e in enumerate(equipos):
            combo_equipo.addItem(e['nombre'], e['id'])
            if str(e['id']) == str(current_eq):
                idx_eq = i
        combo_equipo.setCurrentIndex(idx_eq)
        
        layout.addRow("Título:", titulo)
        layout.addRow("Descripción:", desc)
        layout.addRow("Equipo:", combo_equipo)
        
        btn = QPushButton("Guardar Cambios")
        btn.clicked.connect(dialog.accept)
        layout.addRow(btn)
        
        if dialog.exec_():
            if self.task_manager.editar_tablero(id_tablero, titulo.text(), desc.text(), combo_equipo.currentData()):
                self.cargar_tableros()
                QMessageBox.information(self, "Éxito", "Tablero actualizado.")
            else:
                QMessageBox.critical(self, "Error", "Fallo al actualizar.")

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
        self.aplicar_estilo(dialog)
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
        self.aplicar_estilo(dialog)
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
                    # it = QListWidget(f"{m['email']} ({m.get('nombre', '')} {m.get('apellidos', '')})") 
                    # El original tenia error de typo en QListWidget vs QListWidgetItem.
                    from PyQt5.QtWidgets import QListWidgetItem
                    item_obj = QListWidgetItem(f"{m['email']} ({m.get('nombre', '')} {m.get('apellidos', '')})")
                    item_obj.setData(Qt.UserRole, m['id'])
                    list_managers.addItem(item_obj)
        
        refresh_managers_list()
        
        # Guardamos la referencia para el callback
        self.refresh_managers_callback = refresh_managers_list
        
        # Activar menu contextual
        list_managers.setContextMenuPolicy(Qt.CustomContextMenu)
        list_managers.customContextMenuRequested.connect(self.menu_contextual_manager)
        self.list_managers = list_managers # Guardar ref para el metodo menu
        
        layout.addWidget(list_managers)
        
        # Boton Promover Manager
        btn_promover = QPushButton("Añadir Manager al Departamento")
        btn_promover.setObjectName("btn_promover")
        
        def open_promote_dialog():
            self.promover_manager_dialog(id_dept)
            refresh_managers_list()
            
        btn_promover.clicked.connect(open_promote_dialog)
        layout.addWidget(btn_promover)
        
        btn_save = QPushButton("Guardar Cambios")
        btn_save.setObjectName("btn_save_dept")
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
        self.aplicar_estilo(d)
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
            
            # Verificar si es lider de algun equipo, un usuario podria ser lider de varios
            # Simplificamos asumiendo 1.
            equipos = self.task_manager.obtener_equipos() # Seria mejor query filtrada pero vale
            equipos_liderados = [eq for eq in equipos if str(eq.get('lider_id')) == str(user_id)]
            
            for eq in equipos_liderados:
                msg = f"El usuario es actualmente líder del equipo '{eq['nombre']}'.\nEl puesto quedará vacante.\n¿Deseas seleccionar un sustituto ahora?"
                # CHANGE: Usamos WARNING como pedido
                reply = QMessageBox.warning(d, "Vacante de Líder", msg, QMessageBox.Yes | QMessageBox.No)
                
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
        self.aplicar_estilo(sd)
        sl = QVBoxLayout(sd)
        sl.addWidget(QLabel(f"Selecciona nuevo líder para '{equipo['nombre']}':"))
        
        s_combo = QComboBox()
        users = self.task_manager.obtener_todos_usuarios()
        
        count = 0
        for u in users:
            # No puede ser el que estamos promoviendo (old_lider_id)
            # Debe ser un trabajador del departanento
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
                # Update equipo con nuevo lider
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
                # Si no selecciona nadie, el equipo se queda sin lider
                 try:
                    db.client.table('equipos').update({'lider_id': None}).eq('id', equipo['id']).execute()
                 except: pass

    # --- LOGICA EQUIPOS ---
    def cargar_equipos(self):
        data = self.task_manager.obtener_equipos()

        if self.usuario.nivel_acceso == 'manager': # Filtrar por departamento
            data = [eq for eq in data if str(eq.get('departamento_id')) == str(self.usuario.departamento_id)]

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
        self.aplicar_estilo(dialog)
        layout = QFormLayout(dialog)
        
        # Logica: si soy admin, elijo manager. Si soy manager, me asigno yo.
        rol_actual = 'trabajador'
        if self.parent_window and hasattr(self.parent_window, 'rol'):
            rol_actual = self.parent_window.rol
        elif self.usuario and hasattr(self.usuario, 'nivel_acceso'):
            rol_actual = self.usuario.nivel_acceso

        nombre = QLineEdit()
        desc = QLineEdit()
        combo_d = QComboBox()

        depts = self.task_manager.obtener_departamentos()

        if rol_actual == 'manager':
            depts = [d for d in depts if str(d['id']) == str(self.usuario.departamento_id)]

        for d in depts:
            combo_d.addItem(d['nombre'], d['id'])
            
        combo_l = QComboBox()
        # Se cargara dinamicamente al cambiar de departamento
        combo_m = QComboBox()
            
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
                 u_dept = u.get('departamento_id')
                 u_rol = u.get('nivel_acceso')
                 
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
        self.aplicar_estilo(dialog)
        layout = QFormLayout(dialog)
        
        nombre = QLineEdit(eq_data['nombre'])
        desc = QLineEdit(eq_data.get('descripcion', ''))
        
        combo_d = QComboBox()
        depts = self.task_manager.obtener_departamentos()

        if self.usuario.nivel_acceso == 'manager':
            depts = [d for d in depts if str(d['id']) == str(self.usuario.departamento_id)]

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

        # Rol actual
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
                   msg = "Estás a punto de cambiar al líder del equipo.\n\nEl nuevo trabajador seleccionado pasará a ser LÍDER.\nEl antiguo líder pasará a ser TRABAJADOR.\n\n¿Deseas continuar?"
                   
                   # Usamos Warning como icono, y botones OK / Cancel
                   reply = QMessageBox.warning(self, "Cambio de Líder", msg, QMessageBox.Ok | QMessageBox.Cancel)
                   
                   if reply == QMessageBox.Ok:
                       try:
                           if hasattr(self, 'task_manager'):
                               self.task_manager._mover_usuario_de_tabla(current_lider_id, 'trabajador')
                       except Exception as e:
                           print(f"Error al democionar lider anterior: {e}")
                   else:
                       # Si le da a Cancelar (o cierra), abortamos TODO.
                       return
            
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

    # --- LOGICA TABLEROS ---
    def filtrar_tableros(self):
        # Oculta las filas que no coincidan con el texto escrito
        texto_busqueda = self.input_search_board.text().lower()
        
        for fila in range(self.table_boards.rowCount()):
            # Obtenemos el título (Columna 1)
            item_titulo = self.table_boards.item(fila, 1)
            
            if item_titulo:
                texto_titulo = item_titulo.text().lower()
                # Si el texto buscado está dentro del título, mostramos la fila. Si no, la ocultamos.
                if texto_busqueda in texto_titulo:
                    self.table_boards.setRowHidden(fila, False)
                else:
                    self.table_boards.setRowHidden(fila, True)

    def _alert_leader_conflict(self, old_lider_id):
        # Muestra alerta
        
        msg = "Estás a punto de cambiar al líder del equipo.\n\nEl nuevo trabajador seleccionado pasará a ser LÍDER.\nEl antiguo líder pasará a ser TRABAJADOR.\n\n¿Deseas continuar?"
        reply = QMessageBox.warning(self, "Cambio de Líder", msg, QMessageBox.Ok | QMessageBox.Cancel)
        
        if reply == QMessageBox.Ok:
            try:
                # Democionar al antiguo lider
                if hasattr(self, 'task_manager'):
                    self.task_manager._mover_usuario_de_tabla(old_lider_id, 'trabajador')
                return True
            except Exception as e:
                print(f"Error democionando lider anterior: {e}")
                return False
        else:
            return False

    # MENU PARA DESCENDER A LIDER DE EQUIPO
    def menu_contextual_manager(self, pos):
        # Menu click derecho en la lista de managers
        item = self.list_managers.itemAt(pos)
        if not item: return
        user_id = item.data(Qt.UserRole)
        if not user_id: return 
        
        menu = QMenu()
        
        # Descender a Lider de Equipo
        act_lider = QAction("Descender a Líder de Equipo", self)
        act_lider.triggered.connect(lambda: self.procesar_downgrade_manager(user_id, 'lider_equipo'))
        
        # Descender a Trabajador
        act_trabajador = QAction("Descender a Trabajador", self)
        act_trabajador.triggered.connect(lambda: self.procesar_downgrade_manager(user_id, 'trabajador'))
        
        menu.addAction(act_lider)
        menu.addAction(act_trabajador)
        
        menu.exec_(self.list_managers.mapToGlobal(pos))
        
    def procesar_downgrade_manager(self, user_id, target_rol):
        # Obtenemos info del usuario
        try:
            res = db.client.table('perfiles').select('departamento_id, email').eq('id', user_id).single().execute()
            user_data = res.data
            dept_id = user_data['departamento_id']
        except: return 
        
        if not dept_id:
             QMessageBox.warning(self, "Error", "El usuario no tiene departamento asignado.")
             return

        # Buscamos equipos del departamento
        equipos = self.task_manager.obtener_equipos()
        equipos_dept = [e for e in equipos if str(e.get('departamento_id')) == str(dept_id)]
        
        if not equipos_dept:
             QMessageBox.warning(self, "Aviso", "No hay equipos en este departamento para asignar.")
             return
             
        # Dialogo seleccion equipo
        d = QDialog(self)
        d.setWindowTitle(f"Asignar Equipo ({target_rol})")
        self.aplicar_estilo(d)
        l = QVBoxLayout(d)
        l.addWidget(QLabel("Selecciona el equipo de destino:"))
        
        combo = QComboBox()
        for e in equipos_dept:
            combo.addItem(e['nombre'], e['id'])
        l.addWidget(combo)
        
        btn = QPushButton("Confirmar Asignación")
        btn.clicked.connect(d.accept)
        l.addWidget(btn)
        
        if d.exec_():
            equipo_dest_id = combo.currentData()
            if not equipo_dest_id: return
            
            # Solo si el destino es ser LIDER
            if target_rol == 'lider_equipo':
                # Chequear si ese equipo ya tiene lider
                try:
                    eq_data = db.client.table('equipos').select('lider_id').eq('id', equipo_dest_id).single().execute()
                    if eq_data.data and eq_data.data.get('lider_id'):
                         current_lider = eq_data.data['lider_id']
                         # LLAMADA AL HELPER
                         if not self._alert_leader_conflict(current_lider):
                             return # Abortado por usuario
                except Exception as e:
                    print(f"Error check lider: {e}")
            
            # Usamos _mover_usuario_de_tabla para cambiar rol a 'trabajador' o 'lider_equipo'
            
            if self.task_manager._mover_usuario_de_tabla(user_id, target_rol):
                 # Update equipo_id
                 try:
                     db.client.table('perfiles').update({'equipo_id': equipo_dest_id}).eq('id', user_id).execute()
                     if target_rol == 'lider_equipo':
                         # Update tabla equipos set lider_id
                         db.client.table('equipos').update({'lider_id': user_id}).eq('id', equipo_dest_id).execute()
                     
                     QMessageBox.information(self, "Exito", f"Usuario descendido a {target_rol} correctamente.")

                     if hasattr(self, 'refresh_managers_callback') and self.refresh_managers_callback:
                         self.refresh_managers_callback()
                         
                 except Exception as ex:
                     QMessageBox.critical(self, "Error", f"Fallo asignando equipo: {ex}")
            else:
                 QMessageBox.critical(self, "Error", "Fallo al cambiar rol.")

    def ir_al_tablero_seleccionado(self):
        # Detecta qué fila está seleccionada y manda al Main Window a cargar ese tablero
        fila_actual = self.table_boards.currentRow()

        
        # Manejo de errores básico
        if fila_actual < 0:
            QMessageBox.warning(self, "Aviso", "Por favor, selecciona un tablero de la lista primero.")
            return

        # Obtenemos el ID del tablero (Columna 0) y el Título (Columna 1)
        item_id = self.table_boards.item(fila_actual, 0)
        item_titulo = self.table_boards.item(fila_actual, 1)
        
        if item_id and self.parent_window:
            id_tablero = item_id.text()
            titulo_tablero = item_titulo.text()
            
            # Llamamos al método cargar_tablero_admin_mode en MainWindow para forzar la carga de este tablero específico
            self.parent_window.cargar_tablero_admin_mode(id_tablero, titulo_tablero)
            self.volver()