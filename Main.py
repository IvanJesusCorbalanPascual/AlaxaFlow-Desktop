import sys
from PyQt5.QtWidgets import QApplication
# Importamos la ventana principal desde nuestra estructura de carpetas
from src.views.ventanas import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())