import os
from PyQt5.QtWidgets import (QPushButton, QFrame, QVBoxLayout, QLabel, 
                             QScrollArea, QWidget, QGraphicsDropShadowEffect, 
                             QInputDialog, QMessageBox, QMenu, QAction, 
                             QDialog, QLineEdit, QHBoxLayout) # <--- Importantes para el diálogo
from PyQt5.QtCore import Qt, QMimeData, pyqtSignal, QSize, QPoint
from PyQt5.QtGui import QDrag, QColor, QPixmap, QCursor, QIcon

ESTILO_CARD_NORMAL = """
    QPushButton {
        background-color: #FFFFFF; color: #3E2723;
        border: 1px solid #E0E0E0; border-radius: 6px;
        padding: 15px; text-align: left; font-size: 14px; margin-bottom: 5px;
    }
    QPushButton:hover { background-color: #FFF8E1; border: 1px solid #FFB74D; }
"""

ESTILO_CARD_CONTRASTE = """
    QPushButton {
        background-color: #000000; color: #FFFF00;
        border: 2px solid #FFFFFF; border-radius: 0px;
        padding: 15px; text-align: left; font-size: 16px; font-weight: bold; margin-bottom: 10px;
    }
    QPushButton:hover { background-color: #333333; border: 2px dashed #FFFF00; }
"""

"""
Clase para el diálogo de edición de tareas, contiene la logica para editar y borrar tareas
"""
# --- 1. CLASE DIÁLOGO PARA EDITAR/BORRAR ---
class TareaDialog(QDialog):
    def __init__(self, tarea_id, titulo_actual, rol_usuario, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Detalle de Tarea")
        self.setFixedWidth(400)
        self.accion_realizada = None # "borrar", "editar" o None
        self.nuevo_titulo = titulo_actual

        layout = QVBoxLayout()

        # Campo para editar
        layout.addWidget(QLabel("Editar título:"))
        self.input_titulo = QLineEdit(titulo_actual)
        layout.addWidget(self.input_titulo)

        # Botones
        btn_layout = QHBoxLayout()
        
        self.btn_guardar = QPushButton("💾 Guardar")
        self.btn_guardar.setStyleSheet("background-color: #4CAF50; color: white; padding: 6px;")
        self.btn_guardar.clicked.connect(self.guardar)
        btn_layout.addWidget(self.btn_guardar)

        # Botón borrar (Solo si tienes permisos)
        if rol_usuario in ['admin', 'manager']:
            self.btn_borrar = QPushButton("🗑️ Borrar")
            self.btn_borrar.setStyleSheet("background-color: #F44336; color: white; padding: 6px;")
            self.btn_borrar.clicked.connect(self.borrar)
            btn_layout.addWidget(self.btn_borrar)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def guardar(self):
        self.nuevo_titulo = self.input_titulo.text()
        self.accion_realizada = "editar"
        self.accept()

    def borrar(self):
        confirmacion = QMessageBox.question(self, "Confirmar", "¿Borrar esta tarea?", 
                                            QMessageBox.Yes | QMessageBox.No)
        if confirmacion == QMessageBox.Yes:
            self.accion_realizada = "borrar"
            self.accept()

# --- TARJETA ARRASTRABLE ---
class KanbanCard(QPushButton):
    # Señales para comunicarse con la ventana principal
    request_delete = pyqtSignal(str) # Señal para pedir borrar la tarea
    request_refresh = pyqtSignal() # Señal para pedir guardar cambios

    def __init__(self, id_tarea, text, rol_usuario): 
        super().__init__(text)
        self.id_tarea = id_tarea 
        self.rol_usuario = rol_usuario 
        self.texto_actual = text # Guardamos el texto original
        
        self.setProperty("class", "tarjeta")
        self.setCursor(Qt.PointingHandCursor)
        
        # CONEXIÓN CLIC IZQUIERDO -> ABRIR EDICIÓN
        self.clicked.connect(self.abrir_detalle)

        # Estilo
        self.setStyleSheet(ESTILO_CARD_NORMAL)
        
        # Sombra
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(shadow)

    # Cambia visualmente la tarjeta
    def set_modo_visual(self, modo):
        if modo == "contraste":
            self.setStyleSheet(ESTILO_CARD_CONTRASTE)
            # Quita la sombra para que sea más legible
            self.setGraphicsEffect(None)
        else:
            # Restaura la sombra
            self.setStyleSheet(ESTILO_CARD_NORMAL)

    # Lógica para abrir el diálogo al hacer clic
    def abrir_detalle(self):
        dialogo = TareaDialog(self.id_tarea, self.text(), self.rol_usuario, self)
        
        if dialogo.exec_() == QDialog.Accepted:
            if dialogo.accion_realizada == "borrar":
                self.request_delete.emit(str(self.id_tarea))
            
            elif dialogo.accion_realizada == "editar":
                # Actualizamos el texto visualmente
                self.setText(dialogo.nuevo_titulo)
                # Avisamos a la ventana principal para que guarde en BD
                self.request_refresh.emit()

    # Drag & Drop
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            mime.setText(str(self.id_tarea))
            drag.setMimeData(mime)

            # Captura fiable del widget (incluye estilo y contenido)
            try:
                pixmap = self.grab()
            except Exception:
                pixmap = QPixmap(self.size())
                self.render(pixmap)

            # Si la captura es válida, ajustar y centrar el hotspot para un preview correcto
            if not pixmap.isNull():
                # Escalado suave si es necesario (mantener tamaño original normalmente)
                scaled = pixmap.scaled(pixmap.width(), pixmap.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                drag.setPixmap(scaled)
                center = scaled.rect().center()
                if isinstance(center, QPoint):
                    drag.setHotSpot(center)

            drag.exec_(Qt.MoveAction)

    # Menú Contextual (Clic Derecho)
    def contextMenuEvent(self, event):
        if self.rol_usuario in ['admin', 'manager']:
            menu = QMenu(self)
            action_delete = QAction("🗑️ Eliminar Tarea", self)
            action_delete.triggered.connect(lambda: self.request_delete.emit(str(self.id_tarea)))
            menu.addAction(action_delete)
            menu.exec_(QCursor.pos())

# --- COLUMNA ---
class KanbanColumn(QFrame):
    def __init__(self, id_columna, titulo, task_manager_instance, parent_window):
        super().__init__()
        self.id_columna = id_columna 
        self.manager = task_manager_instance
        self.main_window = parent_window 
        
        self.setObjectName("Columna")
        self.setAcceptDrops(True) 
        
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(10, 10, 10, 10)
        
        # Header con título y botón eliminar
        self.titulo = titulo
        header_layout = QHBoxLayout()
        header_layout.setAlignment(Qt.AlignVCenter)
        header_label = QLabel(titulo)
        header_label.setObjectName("TituloColumna")
        header_label.setStyleSheet("")
        header_layout.addWidget(header_label)

        # Botón eliminar columna (usa assets/papelera.png si existe)
        icon_path = os.path.join(os.path.dirname(__file__), "../../assets/papelera.png")
        btn = QPushButton()
        # Asegurar contenidos centrados y sin padding extra
        btn.setFlat(True)
        btn.setStyleSheet("background:transparent; border:none; padding:4px; margin:0px;")
        btn.setContentsMargins(0, 0, 0, 0)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setToolTip("Eliminar columna")
        # Hacemos el botón más grande y el icono aún más visible
        btn.setFixedSize(64, 56)
        if os.path.exists(icon_path):
            btn.setIcon(QIcon(icon_path))
            btn.setIconSize(QSize(40, 40))
            btn.setFlat(True)
        else:
            # Fallback a emoji si no existe la imagen
            btn.setText("🗑️")
            btn.setStyleSheet("font-size:28px; line-height:28px;")

        btn.clicked.connect(self.pedir_eliminar_columna)
        self.btn_delete_col = btn
        header_layout.addWidget(self.btn_delete_col)

        # Asegurar que el label ocupe el espacio disponible
        header_layout.setStretch(0, 1)
        self.layout.addLayout(header_layout)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setStyleSheet("background: transparent;")
        
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        self.scroll_layout.setSpacing(10)
        
        self.scroll.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll)

        self.btn_add = QPushButton(" + Añadir tarjeta")
        self.btn_add.setCursor(Qt.PointingHandCursor)
        self.btn_add.setObjectName("btn_add_card")
        self.btn_add.clicked.connect(self.crear_nueva_tarea)
        self.layout.addWidget(self.btn_add)
        self.setLayout(self.layout)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText(): event.accept()
        else: event.ignore()

    def dropEvent(self, event):
        id_tarea = event.mimeData().text()
        if self.manager.mover_tarea(id_tarea, self.id_columna):
            widget_origen = event.source()
            if widget_origen: self.add_card_widget(widget_origen)
            event.accept()
        else: event.ignore()

    def crear_nueva_tarea(self):
        titulo_columna = self.layout.itemAt(0).widget().text()
        text, ok = QInputDialog.getText(self, "Nueva Tarea", f"Añadir a {titulo_columna}:")
        if ok and text:
            if self.main_window.usuario:
                usuario_id = self.main_window.usuario.id
                if self.manager.crear_tarea(text, self.id_columna, usuario_id):
                    self.main_window.distribuir_tareas()
            else:
                print("Error: Sin usuario")

    def add_card_widget(self, card_widget):
        self.scroll_layout.addWidget(card_widget)

    def pedir_eliminar_columna(self):
        # Delegamos la confirmación y la eliminación a la ventana principal
        if hasattr(self.main_window, 'solicitar_eliminar_columna'):
            self.main_window.solicitar_eliminar_columna(self.id_columna, self.titulo)
        else:
            # Fallback: intentar eliminar directamente
            confirm = QMessageBox.question(self, "Eliminar columna", 
                                           "¿Eliminar esta columna y sus tareas?", 
                                           QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                if self.manager.eliminar_columna(self.id_columna):
                    self.main_window.recargar_tablero_completo()