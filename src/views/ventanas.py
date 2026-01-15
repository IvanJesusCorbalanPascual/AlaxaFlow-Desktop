import os
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic
from .widgets import KanbanCard # Importamos nuestro widget personalizado
from src.managers.task_manager import TaskManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Cargar interfaz
        ui_path = os.path.join(os.path.dirname(__file__), "..", "ui", "interface.ui")
        uic.loadUi(ui_path, self)

        # Conectar señales (Botones)
        self.btnLogout.clicked.connect(self.close)

        # Inicializar el gestor de tareas
        self.task_manager = TaskManager()

        # Cargar tareas de la base de datos
        self.cargar_tareas_desde_bd()

    def cargar_tareas_desde_bd(self):
        print("Cargando tareas desde Supabase...")
        
        # 1. Pedimos los datos al manager
        tareas = self.task_manager.obtener_tareas()
        
        # 2. Limpiamos las columnas (por si recargamos)
        self.limpiar_columnas()

        # 3. Diccionario para mapear ID de base de datos -> Nombre del Layout en UI
        # Asumiendo que en BD: 1=Pendiente, 2=Proceso, 3=Revisión, 4=Finalizado
        mapa_layouts = {
            1: "layout_pendiente",
            2: "layout_proceso",
            3: "layout_revision",
            4: "layout_finalizado"
        }

        # 4. Crear tarjetas visuales
        for tarea in tareas:
            texto_tarea = tarea.get('titulo', 'Sin título')
            id_columna = tarea.get('columna_id')
            
            nombre_layout = mapa_layouts.get(id_columna)
            
            if nombre_layout:
                self.add_task(nombre_layout, texto_tarea)

        # 5. Añadir espaciadores al final para estética
        self.layout_pendiente.addStretch()
        self.layout_proceso.addStretch()
        self.layout_revision.addStretch()
        self.layout_finalizado.addStretch()

    def add_task(self, layout_name, text):
        # Obtener el layout dinámicamente por nombre
        if hasattr(self, layout_name):
            target_layout = getattr(self, layout_name)
            card = KanbanCard(text)
            target_layout.addWidget(card)

    def limpiar_columnas(self):
        # Función auxiliar para borrar lo que haya antes de cargar
        layouts = [self.layout_pendiente, self.layout_proceso, 
                   self.layout_revision, self.layout_finalizado]
        
        for layout in layouts:
            # Borrar items en bucle inverso
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()