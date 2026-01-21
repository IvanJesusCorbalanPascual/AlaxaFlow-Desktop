import sys, os
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtGui import QIcon
from src.views.main_window import MainWindow
from src.views.login_window import LoginDialog

STYLESHEET = """
/* --- GENERAL --- */
QMainWindow, QDialog {
    background-color: #FAFAFA; 
}
QWidget { 
    font-family: 'Segoe UI', sans-serif; 
    font-size: 14px; 
    color: #3E2723; /* Texto Marrón Oscuro */
}

/* --- CAMPOS DE TEXTO (Para que no sean negros) --- */
QLineEdit {
    background-color: #FFFFFF;
    border: 2px solid #D7CCC8;
    border-radius: 4px;
    padding: 4px;
    color: #3E2723;
}

/* --- HEADER --- */
QFrame#TopBar { background-color: #4E342E; border-bottom: 3px solid #FFB74D; }
QLabel#HeaderTitle { color: #FFFFFF; font-weight: bold; font-size: 20px; }

/* --- BOTONES HEADER --- */
QPushButton#btn_logout, QPushButton#btn_add_user {
    background-color: transparent;
    color: #FFB74D;
    border: 1px solid #FFB74D;
    border-radius: 4px;
    padding: 5px 15px;
}
QPushButton#btn_logout:hover, QPushButton#btn_add_user:hover {
    background-color: #5D4037;
    color: #FFFFFF;
}

/* --- COLUMNAS --- */
QFrame#Columna {
    background-color: #EFF1F3; 
    border-radius: 8px;
    border: 1px solid #D7CCC8;
    min-width: 260px; 
    margin: 5px;      
}

/* --- TARJETAS --- */
QPushButton.tarjeta {
    background-color: #FFFFFF;
    color: #3E2723;
    border: 1px solid #E0E0E0;
    border-left: 4px solid #4E342E; 
    border-radius: 6px;
    padding: 12px;
    text-align: left;
}
QPushButton.tarjeta:hover {
    background-color: #FFF8E1; 
    border: 1px solid #FFB74D;
    border-left: 4px solid #FFB74D;
}

/* --- BOTÓN AÑADIR (ABAJO) --- */
QPushButton {
    text-align: left;
    padding-left: 10px;
    padding: 5px 15px;
}
"""

class UsuarioDummy:
    def __init__(self, id, email):
        self.id = id
        self.email = email
        
if __name__ == "__main__":
    ruta_base = os.path.dirname(os.path.abspath(__file__))
    ruta_icono = os.path.join(ruta_base, "assets", "logoAlaxa.png")

    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    app.setWindowIcon(QIcon(ruta_icono))
   
    # --- CONFIGURACIÓN MANUAL para probar la aplicacion sin tener que logearse todo el rato (Bypasseando el Login) ---
    
    # Tu ID real de Supabase (Cópialo de la web si quieres ver tus tareas)
    # Si pones uno inventado, el tablero saldrá vacío (pero funcionará).
    MI_ID_SUPABASE = "85eb2c66-b364-4c74-a70c-1d4b3e27dccb" 
    
    # El rol con el que queremos probar la aplicacion
    MI_ROL = "admin"  # Cambia a "empleado" para probar la vista restringida
    
    # Creamos el usuario falso
    usuario_falso = UsuarioDummy(MI_ID_SUPABASE, "yo@prueba.com")

    # Arrancamos DIRECTAMENTE el tablero inyectándole los datos
    window = MainWindow(usuario=usuario_falso, rol=MI_ROL)
    window.showMaximized()
    
    sys.exit(app.exec_())