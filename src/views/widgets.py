from PyQt5.QtWidgets import QPushButton, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

class KanbanCard(QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self.setCursor(Qt.PointingHandCursor)
        # Definimos el estilo de la tarjepip
        self.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: #3E2723;
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                padding: 15px;
                text-align: left;
                font-size: 14px;
                margin-bottom: 5px;
            }
            QPushButton:hover {
                background-color: #FFF8E1;
                border: 1px solid #FFB74D;
            }
        """)
        
        # Efecto de sombra
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(shadow)