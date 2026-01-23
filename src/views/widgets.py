import os
from PyQt5.QtWidgets import (QPushButton, QFrame, QVBoxLayout, QLabel, 
                             QScrollArea, QWidget, QGraphicsDropShadowEffect, 
                             QInputDialog, QMessageBox, QMenu, QAction, 
                             QDialog, QLineEdit, QHBoxLayout, QSizePolicy, QTextEdit, QComboBox) # <--- Importantes para el diálogo
from PyQt5.QtCore import Qt, QMimeData, pyqtSignal, QSize, QPoint
from PyQt5.QtGui import QDrag, QColor, QPixmap, QCursor, QIcon

ESTILO_CARD_NORMAL = """
    QFrame[class="tarjeta"] {
        background-color: #FFFFFF; color: #3E2723;
        border: 1px solid #E0E0E0; border-radius: 6px;
        padding: 12px; text-align: left; font-size: 14px; margin-bottom: 8px;
    }
    QFrame[class="tarjeta"] QLabel { background: transparent; }
    QFrame[class="tarjeta"]:hover { background-color: #FFF8E1; border: 1px solid #FFB74D; }
"""

ESTILO_CARD_CONTRASTE = """
    QFrame[class="tarjeta"] {
        background-color: #000000; color: #FFFF00;
        border: 2px solid #FFFFFF; border-radius: 0px;
        padding: 12px; text-align: left; font-size: 16px; font-weight: bold; margin-bottom: 10px;
    }
    QFrame[class="tarjeta"] QLabel { background: transparent; }
    QFrame[class="tarjeta"]:hover { background-color: #333333; border: 2px dashed #FFFF00; }
"""

"""
Clase para el diálogo de edición de tareas, contiene la logica para editar y borrar tareas
"""
# --- 1. CLASE DIÁLOGO PARA EDITAR/BORRAR ---
class TareaDialog(QDialog):
    def __init__(self, tarea_id, titulo_actual, rol_usuario, manager_instance, parent=None):
        super().__init__(parent)
        self.tarea_id = tarea_id
        self.manager = manager_instance
        self.accion_realizada = None
        self.nuevo_titulo = titulo_actual
    
        self.setWindowTitle("AlaxaFlow - Detalle")
        self.setFixedWidth(650)
        # Color del fondo,
        self.setStyleSheet("""
            QDialog {
                background-color: #FAFAFA; /* ALTERADO: Fondo Crema suave (antes #FFFFFF) */
                border: 2px solid #D7CCC8; /* AÑADIDO: Borde marrón suave */
                border-radius: 8px;
            }
            
            /* TÍTULO EDITABLE */
            QLineEdit#InputTitulo {
                font-family: 'Segoe UI', sans-serif;
                font-size: 22px;
                font-weight: bold;
                color: #3E2723;   /* ALTERADO: Marrón Oscuro */
                background: transparent;
                border: 2px solid transparent;
                padding: 4px 8px; /* AÑADIDO: Padding extra para evitar cortes */
                border-radius: 5px;
                selection-background-color: #FFB74D; /* AÑADIDO: Color selección */
                selection-color: #3E2723;
            }
            QLineEdit#InputTitulo:hover {
                background-color: #FFFFFF; /* ALTERADO: Blanco al pasar el ratón */
                border: 2px dashed #D7CCC8; 
            }
            QLineEdit#InputTitulo:focus {
                background-color: #FFFFFF;
                border: 2px solid #FFB74D; /* ALTERADO: Foco naranja Alaxa */
            }
            
            /* ETIQUETAS */
            QLabel { color: #5D4037; font-weight: bold; font-size: 14px; }
            
            /* ÁREA DE DESCRIPCIÓN */
            QTextEdit {
                background-color: #FFFFFF; /* ALTERADO: Blanco limpio (antes gris #F4F5F7) */
                border: 2px solid #D7CCC8; /* ALTERADO: Borde marrón */
                border-radius: 6px;
                padding: 12px;
                font-size: 14px;
                color: #3E2723; /* ALTERADO: Texto marrón */
            }
            QTextEdit:focus {
                border: 2px solid #FFB74D; /* ALTERADO: Foco Naranja */
            }

            /* BOTÓN GUARDAR (Estilo Principal Alaxa) */
            QPushButton#btn_guardar {
                background-color: #4E342E; /* ALTERADO: Marrón Oscuro (antes verde) */
                color: #FFB74D; /* ALTERADO: Texto Naranja (antes blanco) */
                font-weight: bold; 
                padding: 10px 20px; 
                border-radius: 5px; 
                border: 1px solid #4E342E;
                font-size: 14px;
            }
            QPushButton#btn_guardar:hover { 
                background-color: #5D4037; 
                border: 1px solid #FFB74D;
                color: #FFFFFF;
            }

            /* BOTÓN BORRAR (Estilo Alerta) */
            QPushButton#btn_borrar {
                background-color: transparent; 
                color: #D32F2F; 
                font-weight: bold;
                padding: 8px 15px; 
                border: 2px solid #D32F2F; /* ALTERADO: Borde más grueso (antes 1px) */
                border-radius: 5px;
            }
            QPushButton#btn_borrar:hover { 
                background-color: #FFEBEE; 
            }
            QComboBox {
                background-color: #FFFFFF;
                border: 2px solid #D7CCC8;
                border-radius: 4px;
                padding: 5px;
                font-size: 13px;
                color: #3E2723;
                min-width: 200px;
            }
            QComboBox:hover { border: 2px solid #FFB74D; }
            QComboBox::drop-down { border: none; }          
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;  /* Fondo de la lista BLANCO */
                color: #3E2723;             /* Texto MARRÓN */
                selection-background-color: #FFB74D; /* Color al pasar el ratón (Naranja) */
                selection-color: #3E2723;   /* Texto al pasar el ratón */
                border: 1px solid #D7CCC8;
                outline: none;
            }

        """)
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Cabecera visual marrón
        header_frame = QFrame()
        header_frame.setObjectName("HeaderFrame")
        header_frame.setFixedHeight(50) 
        header_frame.setStyleSheet("background-color: #4E342E; border-bottom: 3px solid #FFB74D;")
        
        header_layout = QHBoxLayout(header_frame)
        # Margen interno del header
        header_layout.setContentsMargins(20, 0, 20, 0)

        lbl_text_header = QLabel("DETALLES DE LA TARJETA")
        lbl_text_header.setObjectName("HeaderTitle")
        lbl_text_header.setStyleSheet("color: white; font-weight: bold; font-family: 'Segoe UI'; letter-spacing: 1px; border: none;")

        header_layout.addWidget(lbl_text_header)
        header_layout.addStretch()

        main_layout.addWidget(header_frame)

        # Contenedor para dar margenes internos
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 20, 30, 20) 
        content_layout.setSpacing(15)

        self.input_titulo = QLineEdit(titulo_actual)
        self.input_titulo.setObjectName("InputTitulo")
        self.input_titulo.setPlaceholderText("Escribe el título...")

        # Si el título es muy largo, no aparece acortado
        self.input_titulo.setCursorPosition(0)

        content_layout.addWidget(self.input_titulo)

        # Sección de asignación de usuario
        assign_layout = QHBoxLayout()

        lbl_assign_icon = QLabel("👤")
        lbl_assign_icon.setStyleSheet("font-size: 18px; border: none;")
        lbl_assign = QLabel("Asignado a:")
        lbl_assign.setStyleSheet("font-weight: bold; color: #5D4037; border: none;")

        self.combo_usuarios = QComboBox()
        self.combo_usuarios.setCursor(Qt.PointingHandCursor)
        self.combo_usuarios.addItem("Sin asignar", None)

        self.cargar_usuarios_combo()

        assign_layout.addWidget(lbl_assign_icon)
        assign_layout.addWidget(lbl_assign)
        assign_layout.addWidget(self.combo_usuarios)
        assign_layout.addStretch()

        # Añade el layout de contenido
        content_layout.addLayout(assign_layout)

        # Descripción
        lbl_desc_layout = QHBoxLayout()
        lbl_desc_icon = QLabel("📝")
        lbl_desc_icon.setStyleSheet("font-size: 18px; border:none;")

        lbl_desc = QLabel("Descripción")
        lbl_desc.setStyleSheet("margin-left: 5px; color: #4E342E;")
        
        lbl_desc_layout.addWidget(lbl_desc_icon)
        lbl_desc_layout.addWidget(lbl_desc)
        # Empuja el label a la izquierda
        lbl_desc_layout.addStretch()

        content_layout.addLayout(lbl_desc_layout)

        self.input_desc = QTextEdit()
        self.input_desc.setPlaceholderText("Añade una descripción más detallada sobre esta tarea...")
        self.input_desc.setMinimumHeight(150)

        content_layout.addWidget(self.input_desc)

        # Carga la descripción desde la BD
        self.cargar_datos()

        # Espacio antes de los botones
        main_layout.addSpacing(10)

        # Botones
        btn_layout = QHBoxLayout()
        
        # Botón borrar (Solo si tienes permisos)
        if rol_usuario in ['admin', 'manager']:
            self.btn_borrar = QPushButton("🗑️ Eliminar Tarea")
            
            # ID para CSS
            self.btn_borrar.setObjectName("btn_borrar")
            self.btn_borrar.setCursor(Qt.PointingHandCursor)

            self.btn_borrar.clicked.connect(self.borrar)
            btn_layout.addWidget(self.btn_borrar)

        # Botón guardar cambios a la derecha
        self.btn_guardar = QPushButton("💾 Guardar cambios")
        self.btn_guardar.setCursor(Qt.PointingHandCursor)
        self.btn_guardar.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50; color: white; font-weight: bold; 
                padding: 10px 20px; border-radius: 5px; border: none; font-size: 14px;
            }
            QPushButton:hover { background-color: #43A047; }
        """)

        self.btn_guardar.clicked.connect(self.guardar)
        btn_layout.addWidget(self.btn_guardar)

        content_layout.addLayout(btn_layout)
        main_layout.addWidget(content_widget)
        self.setLayout(main_layout)

    # Carga los usuarios para el comboBox
    def cargar_usuarios_combo(self): 
        try:
            usuarios = self.manager.obtener_todos_usuarios()
            for u in usuarios:
                texto = f"{u.get('nombre', 'Usuario')} ({u.get('email')})"
                uid = u.get('id')
                self.combo_usuarios.addItem(texto, uid)
        except Exception as e:
            print(f"Error cargando usuarios: {e}")

    def cargar_datos(self):
        datos = self.manager.obtener_tarea_por_id(self.tarea_id) 
        if datos and 'descripcion' in datos:
            self.input_desc.setText(datos['descripcion'] or "") 

            # Selecciona el usuario asignado en el comboBox si existe
            asignado_id = datos.get('asignado_a')
            if asignado_id:
                index = self.combo_usuarios.findData(asignado_id)
                if index >= 0:
                    self.combo_usuarios.setCurrentIndex(index)

    def guardar(self):
        self.nuevo_titulo = self.input_titulo.text()
        nueva_desc = self.input_desc.toPlainText()

        # ID del usuario asignado
        id_usuario = self.combo_usuarios.currentData()

        # Guarda el título y la descripción en la BD
        self.manager.editar_tarea(self.tarea_id, self.nuevo_titulo)
        self.manager.editar_descripcion_tarea(self.tarea_id, nueva_desc)

        if hasattr(self.manager, 'editar_asignacion_tarea'):
            self.manager.editar_asignacion_tarea(self.tarea_id, id_usuario)

        self.accion_realizada = "editar"
        self.accept()

    def borrar(self):
        confirmacion = QMessageBox.question(self, "Confirmar", "¿Borrar esta tarea definitivamente?", 
                                            QMessageBox.Yes | QMessageBox.No)
        if confirmacion == QMessageBox.Yes:
            self.accion_realizada = "borrar"
            self.accept()

# --- TARJETA ARRASTRABLE ---
class KanbanCard(QFrame):
    # Señales para comunicarse con la ventana principal
    request_delete = pyqtSignal(str) # Señal para pedir borrar la tarea
    request_refresh = pyqtSignal() # Señal para pedir guardar cambios

    def __init__(self, id_tarea, text, rol_usuario, manager): 
        super().__init__()
        self.id_tarea = id_tarea 
        self.rol_usuario = rol_usuario 
        self.manager = manager
        self.texto_actual = text # Guardamos el texto original

        self.setProperty("class", "tarjeta")
        self.setFrameShape(QFrame.StyledPanel)
        self.setLineWidth(1)
        self.setCursor(Qt.PointingHandCursor)

        # Layout interno con etiqueta que soporta wrap
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(12, 8, 12, 8)
        self.layout.setSpacing(0)

        self.label = QLabel(text)
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label.setStyleSheet("background: transparent;")
        self.layout.addWidget(self.label)

        # Estilo general (similar al anterior QPushButton)
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
        dialogo = TareaDialog(self.id_tarea, self.text(), self.rol_usuario, self.manager, self)
        
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

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Simula el comportamiento de "clicked" del QPushButton
            self.abrir_detalle()
        super().mouseReleaseEvent(event)

    # Menú Contextual (Clic Derecho)
    def contextMenuEvent(self, event):
        if self.rol_usuario in ['admin', 'manager']:
            menu = QMenu(self)
            action_delete = QAction("🗑️ Eliminar Tarea", self)
            action_delete.triggered.connect(lambda: self.request_delete.emit(str(self.id_tarea)))
            menu.addAction(action_delete)
            menu.exec_(QCursor.pos())

    # Compatibilidad con la API previa (MainWindow usa card.text() y card.setText(...))
    def text(self):
        return self.label.text()

    def setText(self, nuevo):
        self.label.setText(nuevo)

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
        # Márgenes simétricos: mismo espacio a izquierda y derecha
        self.layout.setContentsMargins(12, 10, 12, 10)
        
        # Header con título y botón eliminar
        self.titulo = titulo
        header_layout = QHBoxLayout()
        header_layout.setAlignment(Qt.AlignVCenter)
        self.header_label = QLabel()
        # Permitimos wrap y forzamos ruptura de palabras largas usando HTML/CSS
        self.header_label.setWordWrap(True)
        self.header_label.setTextFormat(Qt.RichText)
        safe = titulo.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        self.header_label.setText(f'<div style="word-break:break-all; white-space:normal;">{safe}</div>')
        # Permitir que el label ocupe el espacio disponible para mostrar el título completo
        self.header_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.header_label.setObjectName("TituloColumna")
        self.header_label.setStyleSheet("")

        # Quitar stretch: colocamos los botones justo al lado del título (a la izquierda)
        header_layout.setSpacing(2)
        # Márgenes simétricos para header: mismo espacio a izquierda y derecha
        header_layout.setContentsMargins(12, 0, 12, 0)

        # (no stretch aquí; añadiremos el label y el contenedor después de crear los botones)

        # Botón editar columna (usa assets/lapiz.png si existe)
        edit_icon_path = os.path.join(os.path.dirname(__file__), "../../assets/lapiz.png")
        edit_btn = QPushButton()
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.setToolTip("Editar título de columna")
        edit_btn.setFixedSize(44, 38)
        edit_btn.setFlat(True)
        edit_btn.setStyleSheet("background:transparent; border:none; padding:2px; margin:0px;")
        if os.path.exists(edit_icon_path):
            edit_btn.setIcon(QIcon(edit_icon_path))
            edit_btn.setIconSize(QSize(28, 28))
        else:
            edit_btn.setText("✏️")
            edit_btn.setStyleSheet("background:transparent; border:none; padding:2px; margin:0px; font-size:18px;")
        edit_btn.setContentsMargins(0, 0, 0, 0)
        edit_btn.clicked.connect(self.pedir_editar_columna)
        self.btn_edit_col = edit_btn

        # Botón eliminar columna (usa assets/papelera.png si existe)
        icon_path = os.path.join(os.path.dirname(__file__), "../../assets/papelera.png")
        btn = QPushButton()
        btn.setFlat(True)
        btn.setStyleSheet("background:transparent; border:none; padding:2px; margin:0px;")
        btn.setContentsMargins(0, 0, 0, 0)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setToolTip("Eliminar columna")
        # Aumentamos el tamaño del botón eliminar para igualar al de editar
        btn.setFixedSize(88, 76)
        if os.path.exists(icon_path):
            btn.setIcon(QIcon(icon_path))
            btn.setIconSize(QSize(56, 56))
        else:
            btn.setText("🗑️")
            btn.setStyleSheet("background:transparent; border:none; padding:2px; margin:0px; font-size:18px;")
        btn.setContentsMargins(0, 0, 0, 0)

        btn.clicked.connect(self.pedir_eliminar_columna)
        self.btn_delete_col = btn

        # Agrupar los botones en un contenedor con ancho fijo para reservar espacio
        button_container = QWidget()
        bc_layout = QHBoxLayout(button_container)
        bc_layout.setContentsMargins(0, 0, 0, 0)
        bc_layout.setSpacing(6)
        bc_layout.addWidget(self.btn_edit_col)
        bc_layout.addWidget(self.btn_delete_col)

        # Calcular ancho del área de botones usando sizeHints reales
        edit_w = self.btn_edit_col.sizeHint().width()
        del_w = self.btn_delete_col.sizeHint().width()
        spacing = bc_layout.spacing() or 6
        button_area_width = edit_w + del_w + spacing
        button_container.setFixedWidth(button_area_width)
        button_container.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

        # Añadir el label y el contenedor de botones al header usando espaciadores
        self.header_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.header_label.setContentsMargins(0, 0, 0, 0)
        header_layout.addSpacing(12)                 # margen izquierdo
        header_layout.addWidget(self.header_label)
        header_layout.addStretch()
        header_layout.addWidget(button_container)
        header_layout.addSpacing(12)                 # margen derecho igual al izquierdo
        self.layout.addLayout(header_layout)

        # Calcular anchura mínima de la columna basada en el título y los botones
        # Usamos las medidas de los botones calculadas arriba y el ancho del texto
        fm = self.header_label.fontMetrics()
        text_width = fm.horizontalAdvance(titulo)
        # Espacio extra: botones + márgenes interiores (usamos 12px de margen lateral)
        extra = (edit_w if 'edit_w' in locals() else 44) + (del_w if 'del_w' in locals() else 88) + 12 * 2 + 20
        desired_width = max(260, text_width + extra)
        self.setMinimumWidth(desired_width)
        # Evitar que el layout padre reduzca la columna: preferimos mantener el ancho mínimo
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        
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
        titulo_columna = self.titulo

        text, ok = QInputDialog.getText(self, "Nueva Tarea", f"Añadir a {titulo_columna}:")
        if ok and text:
            if hasattr(self.main_window, 'usuario') and self.main_window.usuario:
                usuario_id = self.main_window.usuario.id

                # Llama al manager para crear la tarea
                if self.manager.crear_tarea(text, self.id_columna, usuario_id):
                    self.main_window.distribuir_tareas()
            else:
                QMessageBox.critical(self, "Error", "No se ha identificado el usuario actual")

    def add_card_widget(self, card_widget):
        # Asegurar que la tarjeta no estire la columna: limitar su ancho al de la columna
        max_w = max(100, self.minimumWidth() - 20)
        card_widget.setMaximumWidth(max_w)
        card_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.scroll_layout.addWidget(card_widget)

    def resizeEvent(self, event):
        # Al redimensionar la columna, actualizar el ancho máximo de las tarjetas
        max_w = max(100, self.width() - 20)
        for i in range(self.scroll_layout.count()):
            w = self.scroll_layout.itemAt(i).widget()
            if w:
                w.setMaximumWidth(max_w)
        super().resizeEvent(event)

    def pedir_editar_columna(self):
        # Mostrar diálogo para editar el título de la columna
        nuevo, ok = QInputDialog.getText(self, "Editar columna", "Nuevo título:", text=self.titulo)
        if not ok:
            return
        nuevo = nuevo.strip()
        if not nuevo:
            QMessageBox.warning(self, "Nombre inválido", "El título no puede estar vacío.")
            return

        if nuevo == self.titulo:
            return

        # Intentar actualizar en la BD
        if self.manager.editar_columna(self.id_columna, nuevo):
            # Actualizar visualmente
            self.titulo = nuevo
            safe = nuevo.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            self.header_label.setText(f'<div style="word-break:break-all; white-space:normal;">{safe}</div>')
            # Recalcular anchura mínima en caso de cambio de título
            fm = self.header_label.fontMetrics()
            text_width = fm.horizontalAdvance(nuevo)
            extra = self.btn_edit_col.width() or 44
            extra += self.btn_delete_col.width() or 88
            extra += 14 * 2 + 20
            desired_width = max(260, text_width + extra)
            self.setMinimumWidth(desired_width)
            self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
            # Notificar ventana principal para recargar si es necesario
            if hasattr(self.main_window, 'recargar_tablero_completo'):
                self.main_window.recargar_tablero_completo()
        else:
            QMessageBox.critical(self, "Error", "No se pudo actualizar el título en la base de datos.")

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