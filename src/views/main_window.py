import os
from PyQt5.QtWidgets import (QMainWindow, QPushButton, QMessageBox, QInputDialog, QScrollArea, QWidget, QHBoxLayout, QVBoxLayout, QDialog)
from PyQt5 import uic
from PyQt5.QtCore import Qt
from src.managers.task_manager import TaskManager
from src.managers.auth_manager import AuthManager
from src.views.widgets import KanbanColumn, KanbanCard
from src.views.admin_panel import AdminWindow

# Estilo "Alaxa Brown"
ESTILO_NORMAL = """
QMainWindow, QDialog { 
    background-color: #FAFAFA; 
    color: #3E2723;
}

QWidget { 
    font-family: 'Segoe UI', sans-serif; 
    font-size: 14px; 
    color: #3E2723; 
}

QLineEdit { 
    background-color: #FFFFFF; 
    border: 2px solid #D7CCC8; 
    border-radius: 4px; 
    padding: 5px; 
    color: #3E2723; 
}
QLabel {
    color: #3E2723;
    background: transparent;
}

QFrame#TopBar { background-color: #4E342E; border-bottom: 3px solid #FFB74D; }
QLabel#HeaderTitle { color: #FFFFFF; font-weight: bold; font-size: 20px; }
QFrame#Columna { 
    background-color: #EFF1F3; 
    border: 1px solid #D7CCC8; 
}
QLabel#TituloColumna { font-weight: bold; font-size: 16px; color: #4E342E; padding: 5px; }

QFrame[class="tarjeta"] { background-color: #FFFFFF; color: #3E2723; border: 1px solid #E0E0E0; border-radius: 6px; }
QFrame[class="tarjeta"]:hover { background-color: #FFF8E1; border: 1px solid #FFB74D; }

QPushButton { border-radius: 4px; padding: 6px 15px; }
QPushButton:hover { background-color: #D7CCC8; }

QPushButton#btn_logout { background-color: transparent; border: 2px solid #FFB74D; color: #FFB74D; font-weight: bold; }
QPushButton#btn_logout:hover { background-color: #FFB74D; color: #4E342E; }

QPushButton#btn_accesibilidad { background-color: #FFB74D; color: #3E2723; font-weight: bold; border: none; padding: 8px 15px; min-height: 20px; margin-right: 5px; }

QPushButton#btn_add_card { background-color: transparent; border: none; color: #5D4037; text-align: left; padding: 8px; }
QPushButton#btn_add_card:hover { background-color: #D7CCC8; color: #3E2723; }
"""

ESTILO_CONTRASTE = """
QMainWindow, QDialog { 
    background-color: #000000; 
    color: #FFFF00; 
}
QWidget { 
    font-family: 'Verdana'; 
    font-weight: bold; 
    font-size: 14px;
    color: #FFFF00;
}

QFrame#TopBar { background-color: #000000; border-bottom: 4px solid #FFFF00; }
QLabel#HeaderTitle { color: #FFFF00; font-size: 22px; text-decoration: underline; }
QLabel#TituloColumna { color: #FFFFFF; font-size: 18px; border-bottom: 2px solid #333; }
QPushButton#btn_accesibilidad, QPushButton#btn_add_column, QPushButton#btn_admin_panel {
    background-color: #000000; 
    color: #FFFF00; 
    border: 2px solid #FFFF00; 
    font-weight: bold;
    padding: 6px 12px;
    border-radius: 0px;
}
QPushButton#btn_accesibilidad:hover, QPushButton#btn_add_column:hover, QPushButton#btn_admin_panel:hover {
    background-color: #333333;
}

QFrame[class="tarjeta"] { background-color: #000000; color: #FFFF00; border: 2px solid #FFFF00; border-radius: 0px; margin-bottom: 10px; }
QFrame[class="tarjeta"]:hover { border: 2px dashed #FFFFFF; }

QLineEdit { background-color: #000000; color: #FFFF00; border: 2px solid #FFFF00; padding: 5px; }
QPushButton { background-color: #000000; color: #FFFF00; border: 2px solid #FFFF00; padding: 8px 15px; border-radius: 0px; }
QPushButton:hover { background-color: #333333; color: #FFFFFF; border-color: #FFFFFF; }

QPushButton#btn_accesibilidad { background-color: #FFFF00; color: #000000; border: 2px solid #FFFFFF; min-height: 20px; padding: 8px 15px; margin-right: 5px; }
QPushButton#btn_add_card { color: #FFFF00; border: 2px dashed #FFFF00; text-align: center; margin-top: 5px; }

QScrollArea, QScrollArea > QWidget > QWidget {
    background-color: black;
    border: none;
}

QWidget#ContenedorColumnas {
    background-color: transparent;
}
QScrollBar:horizontal { height: 0px; background: transparent; }
QScrollBar:vertical { border: 1px solid #FFFF00; background: #000000; width: 12px; margin: 0px; }
QScrollBar::handle:vertical { background: #FFFF00; min-height: 20px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { background: none; height: 0px; }
"""

"""
Clase que maneja las pantallas de la interfaz gráfica principal (Ventana principal)
"""
class MainWindow(QMainWindow):
    def __init__(self, usuario=None, rol=None):
        super().__init__()
        ui_path = os.path.join(os.path.dirname(__file__), "../ui/interface.ui")
        uic.loadUi(ui_path, self)
        
        self.usuario = usuario
        if rol:
            self.rol = rol # Contiene 'admin', 'manager', 'trabajador', etc.
        else:
            print("AVISO: El usuario no tiene rol asignado en la BD. Usando rol 'trabajador'.")
            self.rol = 'trabajador' # Por defecto si no se pasa nada
            
        self.task_manager = TaskManager()
        self.tablero_actual = None # Aqui es donde guardaremos el objeto tablero

        # Aqui se guarda el estado del tema actual
        self.tema_actual = "normal"
        
        self.configurar_ui()
        
        # Cargar o crear un tablero
        if self.usuario:
            self.inicializar_datos()

    def configurar_ui(self):
        # 1. Configuración básica (Logout y Título)
        self.btn_logout.clicked.connect(self.cerrar_sesion)
        self.HeaderTitle.setText(f"AlaxaFlow - {self.rol.upper()}")

        # Botón para activar el modo alto contraste
        self.btn_accesibilidad = QPushButton("👁️ Alto Contraste")
        self.btn_accesibilidad.setCursor(Qt.PointingHandCursor)

        # Estilo para que el botón destaque ligeramente
        self.btn_accesibilidad.setObjectName("btn_accesibilidad")
        self.btn_accesibilidad.clicked.connect(self.alternar_tema)

        # Inserta el botón en la parte superior a la izquierda de cerrar sesión
        self.TopBar.layout().insertWidget(5, self.btn_accesibilidad)

        # Botón para añadir columnas al tablero
        self.btn_add_column = QPushButton("➕ Añadir Columna")
        self.btn_add_column.setCursor(Qt.PointingHandCursor)
        self.btn_add_column.setObjectName("btn_add_column")
        self.btn_add_column.setStyleSheet("QPushButton#btn_add_column { background-color: transparent; color: #FFFFFF; border: 1px solid #D7CCC8; padding: 6px; border-radius: 4px; }")
        
        # LOGICA NUEVA: Solo permitimos añadir columna si NO es trabajador
        if self.rol != 'trabajador':
            self.btn_add_column.clicked.connect(self.agregar_columna)
            # Lo colocamos junto al botón de accesibilidad (index 6)
            self.TopBar.layout().insertWidget(6, self.btn_add_column)
        else:
            # Si es trabajador, escondemos (o simplemente no lo añadimos) el botón
            self.btn_add_column.hide()

        # Botón Admin (Solo para admin y manager)
        if self.rol in ['admin', 'manager']:
            self.btn_admin_panel = QPushButton(" 🛠️ Panel Control ")
            self.btn_admin_panel.setCursor(Qt.PointingHandCursor)
            
            # Estilo oscuro para diferenciarlo
            self.btn_admin_panel.setStyleSheet("""
                background-color: #263238; 
                color: white; 
                font-weight: bold; 
                border: 1px solid #455A64; 
                border-radius: 4px; 
                padding: 6px 12px; 
                margin-right: 15px;
            """)
            
            # Conectamos con la función que abre la ventana nueva
            self.btn_admin_panel.clicked.connect(self.abrir_panel_admin)
            
            # Lo ponemos a la izquierda del todo (índice 0) o donde estaba el otro
            self.TopBar.layout().insertWidget(0, self.btn_admin_panel)

        
        # -- Lógica de scroll horizontal --
        self.scroll_area = QScrollArea()

        # Permite que el contenido crezca
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background: transparent; border: none;")

        # Crea un contenedor interno
        self.contenedor_interno = QWidget()
        self.contenedor_interno.setObjectName("ContenedorColumnas") 
        self.contenedor_interno.setStyleSheet("background: transparent;")

        # Layout horizontal dentro del scroll
        self.tablero_layout = QHBoxLayout(self.contenedor_interno)
        self.tablero_layout.setSpacing(15)
        self.tablero_layout.setContentsMargins(30, 20, 30, 20)

        # Conecta el contenedor al ScrollArea
        self.scroll_area.setWidget(self.contenedor_interno)

        # Añade el scroll area al layout principal de la ventana
        if not self.contentArea.layout():
            layout_padre = QVBoxLayout(self.contentArea)
        else:
            layout_padre = self.contentArea.layout()

        while layout_padre.count():
            child = layout_padre.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            
        layout_padre.addWidget(self.scroll_area)

    # Método para cerrar sesión
    def cerrar_sesion(self):
        auth = AuthManager()

        # Borra el archivo de la sesión local
        auth.borrar_sesion_local()
        print("Sesión cerrada y archivo local eliminado.")
        self.close()

    def alternar_tema(self):
        if self.tema_actual == "normal":
            # Cambia al estilo de Alto Contraste
            self.setStyleSheet(ESTILO_CONTRASTE)
            self.tema_actual = "contraste"
            self.btn_accesibilidad.setText("🎨 Estilo Normal")   

            self.btn_add_column.setStyleSheet("")
        else:
            # Vuelve al estilo normal 
            self.setStyleSheet(ESTILO_NORMAL)
            self.tema_actual = "normal"
            self.btn_accesibilidad.setText("👁️ Alto Contraste")

            self.btn_add_column.setStyleSheet("QPushButton#btn_add_column { background-color: transparent; color: #FFFFFF; border: 1px solid #D7CCC8; padding: 6px; border-radius: 4px; }")
            
        # Actualiza el estilo de las tarjetas, recorriendo las columnas y layouts
        if hasattr(self, 'cols_widgets'):
            for col_widget in self.cols_widgets.values():
                if hasattr(col_widget, 'set_modo_visual'):
                    col_widget.set_modo_visual(self.tema_actual)

                layout = col_widget.scroll_layout
                for i in range(layout.count()):
                    widget = layout.itemAt(i).widget()
                    # Si el widget es una KanbanCard, le cambia el modo
                    if widget and hasattr(widget, 'set_modo_visual'):
                        widget.set_modo_visual(self.tema_actual)

    def inicializar_datos(self):
        # Obtiene o crea el tablero
        self.tablero_actual = self.task_manager.obtener_o_crear_tablero_inicial(self.usuario.id)
        
        if self.tablero_actual:
            titulo = self.tablero_actual.get('titulo', 'Tablero')
            self.HeaderTitle.setText(f"{titulo} ({self.rol.upper()})")
            self.recargar_tablero_completo()
        else:
            # Si es Admin o Manager, no mostramos error, es normal no tener tablero personal
            if self.rol in ['admin', 'manager']:
                 self.HeaderTitle.setText(f"Vista {self.rol.capitalize()} (Sin Tablero)")
            else:
                QMessageBox.critical(self, "Error", "No se pudo cargar ningún tablero.")

    def recargar_tablero_completo(self):
        if self.tablero_actual:
            titulo = self.tablero_actual.get('titulo', 'Sin Nombre')
            self.lblTableroActual.setText(f"{titulo}")

        # Limpia visualmente el tablero
        while self.tablero_layout.count():
            item = self.tablero_layout.takeAt(0)
            if item.widget(): 
                item.widget().deleteLater()
            elif item.spacerItem():
                del item


        # Espaciado entre columnas
        self.tablero_layout.setSpacing(15)
        
        self.cols_widgets = {} # Diccionario ID_UUID -> WidgetColumna

        # Obtiene las columnas de este tablero por su id
        columnas_data = self.task_manager.obtener_columnas(self.tablero_actual['id'])
        
        # Renderiza las columnas
        for col_data in columnas_data:
            col_uuid = col_data['id']
            col_titulo = col_data['titulo']
            
            # Crea el widget pasándole el UUID
            nuevo_widget = KanbanColumn(col_uuid, col_titulo, self.task_manager, self)
            # Añade la columna al layout
            self.tablero_layout.addWidget(nuevo_widget)

            # Guardamos referencia
            self.cols_widgets[col_uuid] = nuevo_widget

        self.tablero_layout.addStretch()

        # Carga las tareas
        self.distribuir_tareas()

    def distribuir_tareas(self):
        # Limpia solo las cartas
        for col in self.cols_widgets.values():
            while col.scroll_layout.count():
                item = col.scroll_layout.takeAt(0)
                if item.widget(): item.widget().deleteLater()

        # Obtiene las tareas del tablero actual por su id
        tareas = self.task_manager.obtener_tareas_por_tablero(self.tablero_actual['id'])

        # Carga el mapa de usuarios para asignaciones
        usuarios_lista = self.task_manager.obtener_todos_usuarios()
        mapa_usuarios = {}
        if usuarios_lista:
            for u in usuarios_lista:
                # Crea string "Nombre (email)"
                nombre_mostrar = f"{u.get('nombre', 'Usuario')} ({u.get('email')})"
                mapa_usuarios[u['id']] = nombre_mostrar
        
        for t in tareas:
            col_id = t['columna_id'] # Esto es un UUID en la bd

            # Obtiene el nombre del usuario asignado si lo hay
            uuid_asignado = t.get('asignado_a')
            nombre_str = mapa_usuarios.get(uuid_asignado) if uuid_asignado else None

            # Crea la tarjeta
            card = KanbanCard(t['id'], t['titulo'], self.rol, self.task_manager, nombre_asignado=nombre_str)

            # Si el modo actual es contraste, aplica el estilo a la tarjeta recién creada.
            if hasattr(self, 'tema_actual') and self.tema_actual == 'contraste':
                card.set_modo_visual('contraste')
            
            # Conecta las señales
            card.request_delete.connect(self.eliminar_tarea_directa)
            # Usamos lambda para capturar la tarjeta correcta
            card.request_refresh.connect(lambda c=card: self.guardar_edicion_tarea(c))

            if col_id in self.cols_widgets:
                self.cols_widgets[col_id].add_card_widget(card)

    # --- MÉTODOS DE ACCIÓN ---

    def eliminar_tarea_directa(self, id_tarea):
        if self.task_manager.eliminar_tarea(id_tarea, self.rol):
            self.distribuir_tareas() # Recargar visualmente
        else:
            QMessageBox.critical(self, "Error", "No tienes permisos para borrar.")

    def guardar_edicion_tarea(self, card):
        nuevo_titulo = card.text() 
        if self.task_manager.editar_tarea(card.id_tarea, nuevo_titulo):
            # No hace falta recargar todo, visualmente ya cambió en el widget
            print("Cambio guardado en BD")
        else:
            QMessageBox.critical(self, "Error", "Error al guardar cambio.")

    def abrir_registro_admin(self):
        # Implementación del registro de usuarios
        email, ok = QInputDialog.getText(self, "Admin Panel", "Email del nuevo empleado:")
        if not ok or not email: return
        
        pwd, ok = QInputDialog.getText(self, "Admin Panel", "Contraseña temporal:")
        if not ok or not pwd: return
        
        nombre, ok = QInputDialog.getText(self, "Admin Panel", "Nombre completo:")
        if not ok or not nombre: return
        
        # Llamar al AuthManager
        auth = AuthManager()
        # De momento crea con rol 'trabajador' por defecto
        nuevo = auth.registro(email, pwd, nombre, 'trabajador') 
        
        if nuevo:
            QMessageBox.information(self, "Éxito", "Usuario registrado correctamente.")
        else:
            QMessageBox.critical(self, "Error", "Fallo al registrar en Supabase.")

    def agregar_columna(self):
        dlg = QInputDialog(self)
        dlg.setWindowTitle("Nueva Columna")
        dlg.setLabelText("Título de la columna:")
        dlg.setOkButtonText("Crear")
        dlg.setCancelButtonText("Cancelar")

        dlg.setStyleSheet("""
            QInputDialog { background-color: #FAFAFA; border: 2px solid #D7CCC8; border-radius: 8px; }
            QLabel { color: #3E2723; font-weight: bold; font-size: 14px; }
            QLineEdit { background-color: #FFFFFF; color: #3E2723; border: 2px solid #D7CCC8; border-radius: 4px; padding: 5px; }
            QPushButton { background-color: #EFEBE9; color: #3E2723; border: 1px solid #D7CCC8; padding: 5px 15px; border-radius: 4px; }
            QPushButton:hover { background-color: #D7CCC8; }
        """)

        if dlg.exec_() == QDialog.Accepted:
            titulo = dlg.textValue()
            if not titulo: return

            if not self.tablero_actual:
                QMessageBox.critical(self, "Error", "No hay tablero activo.")
                return

            creado = self.task_manager.crear_columna(self.tablero_actual['id'], titulo)
            if creado:
                self.recargar_tablero_completo()
            else:
                QMessageBox.critical(self, "Error", "No se pudo crear la columna en la base de datos.")

    def solicitar_eliminar_columna(self, columna_id, titulo_columna=None):
        # Comprueba si la columna tiene tareas y pide confirmación si es necesario
        tareas = self.task_manager.obtener_tareas_por_columna(columna_id)

        if not tareas:
            # No hay tareas, eliminar directamente
            eliminado = self.task_manager.eliminar_columna(columna_id)
            if eliminado:
                self.recargar_tablero_completo()
            else:
                QMessageBox.critical(self, "Error", "No se pudo eliminar la columna.")
            return

        # Si hay tareas, avisar que se eliminarán
        count = len(tareas)
        msg = f"La columna '{titulo_columna or ''}' contiene {count} tarea(s).\nSi continúas, las tareas también serán eliminadas. ¿Deseas continuar?"
        respuesta = QMessageBox.question(self, "Eliminar columna con tareas", msg, QMessageBox.Yes | QMessageBox.No)
        if respuesta == QMessageBox.Yes:
            eliminado = self.task_manager.eliminar_columna(columna_id)
            if eliminado:
                self.recargar_tablero_completo()
            else:
                QMessageBox.critical(self, "Error", "No se pudo eliminar la columna y/o sus tareas.")

    def abrir_panel_admin(self):
        self.admin_window = AdminWindow(self.usuario, parent_window=self)
        self.admin_window.show()
        self.hide()

    def cargar_tablero_admin_mode(self, id_tablero, titulo_tablero):
        # Permite al administrador forzar la visualización de un tablero específico.
        print(f"Admin entrando al tablero: {titulo_tablero}")
        
        # Cambiamos el 'chip' del tablero actual manualmente
        self.tablero_actual = {
            'id': id_tablero,
            'titulo': titulo_tablero
        }
        self.HeaderTitle.setText(f"{titulo_tablero} (VISTA ADMIN)")
        
        # Forzamos la recarga de columnas y tareas de ESE tablero
        self.recargar_tablero_completo()