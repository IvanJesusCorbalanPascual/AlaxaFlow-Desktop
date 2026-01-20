import os
from PyQt5.QtWidgets import QMainWindow, QPushButton, QMessageBox, QInputDialog
from PyQt5 import uic
from PyQt5.QtCore import Qt
from src.managers.task_manager import TaskManager
from src.managers.auth_manager import AuthManager
from src.views.widgets import KanbanColumn, KanbanCard

"""
Clase que maneja las pantallas de la interfaz gráfica principal (Ventana principal)
"""
class MainWindow(QMainWindow):
    def __init__(self, usuario=None, rol=None):
        super().__init__()
        ui_path = os.path.join(os.path.dirname(__file__), "../ui/interface.ui")
        uic.loadUi(ui_path, self)
        
        self.usuario = usuario
        self.rol = rol # Contiene 'admin', 'manager', 'trabajador', etc.
        self.task_manager = TaskManager()
        self.tablero_actual = None # Aqui es donde guardaremos el objeto tablero
        
        self.configurar_ui()
        
        # Cargar o crear un tablero
        if self.usuario:
            self.inicializar_datos()

    def configurar_ui(self):
        self.btn_logout.clicked.connect(self.close)
        self.HeaderTitle.setText(f"AlaxaFlow - {self.rol.upper()}")
        
        # Botón Admin (Solo para admin y manager)
        if self.rol in ['admin', 'manager']:
            self.btn_add_user = QPushButton("Crear Usuario ")
            self.btn_add_user.setStyleSheet("background-color: #8D6E63; color: white; font-weight: bold; border: none; padding: 5px; margin-right: 20px;")
            self.btn_add_user.setCursor(Qt.PointingHandCursor)
            self.btn_add_user.clicked.connect(self.abrir_registro_admin)
            self.TopBar.layout().insertWidget(2, self.btn_add_user)

        self.tablero_layout = self.contentArea.layout()

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