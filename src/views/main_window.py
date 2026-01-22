import os
from PyQt5.QtWidgets import QMainWindow, QPushButton, QMessageBox, QInputDialog
from PyQt5 import uic
from PyQt5.QtCore import Qt
from src.managers.task_manager import TaskManager
from src.managers.auth_manager import AuthManager
from src.views.widgets import KanbanColumn, KanbanCard
from src.views.admin_panel import AdminWindow

# Estilo "Alaxa Brown"
ESTILO_NORMAL = """
QMainWindow { background-color: #FAFAFA; }
QWidget { font-family: 'Segoe UI', sans-serif; font-size: 14px; color: #3E2723; }
QFrame#TopBar { background-color: #4E342E; border-bottom: 3px solid #FFB74D; }
QLabel#HeaderTitle { color: #FFFFFF; font-weight: bold; font-size: 20px; }
QPushButton { border-radius: 4px; padding: 5px 15px; }

/* --- COLUMNAS --- */
/* Fondo gris claro y bordes suaves */
QFrame#Columna {
    background-color: #EFF1F3; 
    border: 1px solid #D7CCC8; 
    border-radius: 8px;
    margin: 5px;
}
/* TÍTULO DE COLUMNA (Marrón Alaxa) */
QLabel#TituloColumna {
    font-weight: bold; 
    font-size: 16px; 
    color: #4E342E; 
    padding: 5px;
}

/* Tarjetas (KanbanCard) */
QPushButton[class="tarjeta"] {
    background-color: #FFFFFF; color: #3E2723; border: 1px solid #E0E0E0;
}
QPushButton[class="tarjeta"]:hover { background-color: #FFF8E1; border: 1px solid #FFB74D; }

/* BOTÓN AÑADIR TARJETA (Modo Normal) */
QPushButton#btn_add_card {
    background-color: transparent; 
    color: #5D4037;
    border-radius: 4px; 
    padding: 8px; 
    text-align: left;
    border: none;
}

QPushButton#btn_add_card:hover { 
    background-color: #D7CCC8; 
    color: #3E2723; 
}
"""

# Estilo alto contraste para mejor accesibilidad
ESTILO_CONTRASTE = """
/* --- GENERAL --- */
QMainWindow, QDialog { 
    background-color: #000000; 
}
QWidget { 
    font-family: 'Verdana', sans-serif; 
    font-size: 14px; 
    color: #FFFF00; /* Por defecto todo Amarillo */
    font-weight: bold; 
}

/* --- HEADER SUPERIOR --- */
QFrame#TopBar { 
    background-color: #000000; 
    border-bottom: 4px solid #FFFF00; 
}
QLabel#HeaderTitle { 
    color: #FFFF00; 
    font-size: 22px; 
    text-decoration: underline; 
}

/* --- BOTONES DEL HEADER (Cerrar sesión, Panel, etc) --- */
QPushButton { 
    background-color: #000000; 
    color: #FFFF00; 
    border: 2px solid #FFFF00; 
    border-radius: 0px; 
    padding: 8px;
}
QPushButton:hover { 
    background-color: #FFFF00; 
    color: #000000; 
}

/* --- COLUMNAS (Cajas grandes) --- */
QFrame#Columna {
    background-color: #000000; 
    border: 2px solid #FFFFFF; /* Borde BLANCO para separar columnas */
    border-radius: 0px;
    margin: 2px;
}

/* --- TÍTULOS DE LAS COLUMNAS (PENDIENTE, ETC.) --- */
/* ¡AQUÍ ESTABA EL FALLO! Forzamos blanco y quitamos el marrón */
QLabel#TituloColumna {
    color: #FFFFFF; 
    font-size: 18px;
    background-color: #000000;
    padding: 10px;
    border-bottom: 2px solid #333; /* Separador sutil */
}

/* --- ÁREA DE SCROLL (FONDO) --- */
QScrollArea {
    background-color: #000000;
    border: none;
}
QWidget {
    background-color: #000000; 
}

/* --- BOTÓN "+ AÑADIR TARJETA" (Al pie de la columna) --- */
/* Lo hacemos resaltar mucho más */
QFrame#Columna QPushButton {
    background-color: #000000;
    color: #FFFF00; /* Texto Amarillo */
    border: 2px dashed #FFFF00; /* Borde discontinuo "técnico" */
    text-align: center;
    padding: 10px;
    margin-top: 5px;
}
QFrame#Columna QPushButton:hover {
    background-color: #333333; /* Gris oscuro al pasar el ratón */
    color: #FFFFFF;
}

/* --- TARJETAS (KanbanCard) --- */
QPushButton[class="tarjeta"] {
    background-color: #000000; 
    color: #FFFF00; 
    border: 2px solid #FFFF00; 
    margin-bottom: 10px;
    text-align: left;
}

/* BOTÓN AÑADIR TARJETA (Modo Alto Contraste) */
QPushButton#btn_add_card {
    background-color: #000000;
    color: #FFFF00; /* Amarillo */
    border: 2px dashed #FFFF00; /* Borde discontinuo para resaltar */
    text-align: center; /* Centrado se lee mejor aquí */
    padding: 10px;
    margin-top: 5px;
}
QPushButton#btn_add_card:hover {
    background-color: #333333;
    color: #FFFFFF;
}
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
        self.btn_logout.clicked.connect(self.close)
        self.HeaderTitle.setText(f"AlaxaFlow - {self.rol.upper()}")

        # Botón para activar el modo alto contraste
        self.btn_accesibilidad = QPushButton("👁️ Alto Contraste")
        self.btn_accesibilidad.setCursor(Qt.PointingHandCursor)

        # Estilo para que el botón destaque ligeramente
        self.btn_accesibilidad.setStyleSheet("background-color: #FFB74D; color: #3E2723; font-weight: bold; border: none;")
        self.btn_accesibilidad.clicked.connect(self.alternar_tema)

        # Inserta el botón en la parte superior a la izquierda de cerrar sesión
        self.TopBar.layout().insertWidget(5, self.btn_accesibilidad)

        # Botón para añadir columnas al tablero
        self.btn_add_column = QPushButton("➕ Añadir Columna")
        self.btn_add_column.setCursor(Qt.PointingHandCursor)
        self.btn_add_column.setStyleSheet("background-color: transparent; color: #FFFFFF; border: 1px solid #D7CCC8; padding: 6px; border-radius: 4px;")
        self.btn_add_column.clicked.connect(self.agregar_columna)
        # Lo colocamos junto al botón de accesibilidad
        self.TopBar.layout().insertWidget(6, self.btn_add_column)

        # Botón Admin (Solo para admin y manager)
        
        # 2. LOGICA NUEVA: Botón del Panel de Admin
        # Sustituimos el antiguo botón "Crear Usuario" por el botón "Panel Control"
        if self.rol in ['admin', 'manager']:
            self.btn_admin_panel = QPushButton(" 🛠️ Panel Control ")
            self.btn_admin_panel.setCursor(Qt.PointingHandCursor)
            
            # Le damos un estilo oscuro para diferenciarlo
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

        self.tablero_layout = self.contentArea.layout()

    def alternar_tema(self):
        if self.tema_actual == "normal":
            # Cambia al estilo de Alto Contraste
            self.setStyleSheet(ESTILO_CONTRASTE)
            self.tema_actual = "contraste"
            self.btn_accesibilidad.setText("🎨 Estilo Normal")
            self.btn_accesibilidad.setStyleSheet("background-color: #FFFF00; color: #000000; border: 2px solid white;")
        else:
            # Vuelve al estilo normal 
            self.setStyleSheet(ESTILO_NORMAL)
            self.tema_actual = "normal"
            self.btn_accesibilidad.setText("👁️ Alto Contraste")
            self.btn_accesibilidad.setStyleSheet("background-color: #FFB74D; color: #3E2723; font-weight: bold; border: none;")

        # Actualiza el estilo de las tarjetas, recorriendo las columnas y layouts
        if hasattr(self, 'cols_widgets'):
            for col_widget in self.cols_widgets.values():
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
            QMessageBox.critical(self, "Error", "No se pudo cargar ningún tablero.")

    def recargar_tablero_completo(self):
        # Limpia visualmente el tablero
        while self.tablero_layout.count():
            item = self.tablero_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        
        self.cols_widgets = {} # Diccionario ID_UUID -> WidgetColumna

        # Obtiene las columnas de este tablero por su id
        columnas_data = self.task_manager.obtener_columnas(self.tablero_actual['id'])
        
        # Renderiza las columnas
        for col_data in columnas_data:
            col_uuid = col_data['id']
            col_titulo = col_data['titulo']
            
            # Crea el widget pasándole el UUID
            nuevo_widget = KanbanColumn(col_uuid, col_titulo, self.task_manager, self)
            self.tablero_layout.addWidget(nuevo_widget)
            
            # Guardamos referencia
            self.cols_widgets[col_uuid] = nuevo_widget

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
        
        for t in tareas:
            col_id = t['columna_id'] # Esto es un UUID en la bd
            
            # Crea la tarjeta
            card = KanbanCard(t['id'], t['titulo'], self.rol)
            
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
        # Pide el título de la nueva columna y la crea en la BD
        titulo, ok = QInputDialog.getText(self, "Nueva Columna", "Título de la columna:")
        if not ok or not titulo:
            return

        if not self.tablero_actual:
            QMessageBox.critical(self, "Error", "No hay tablero activo.")
            return

        creado = self.task_manager.crear_columna(self.tablero_actual['id'], titulo)
        if creado:
            # Recargamos el tablero para mostrar la nueva columna
            self.recargar_tablero_completo()
        else:
            QMessageBox.critical(self, "Error", "No se pudo crear la columna en la base de datos.")

    def abrir_panel_admin(self):
        self.admin_window = AdminWindow(self.usuario, parent_window=self)
        self.admin_window.show()
        self.hide()