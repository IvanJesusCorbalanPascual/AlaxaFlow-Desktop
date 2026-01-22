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
        
if __name__ == "__main__":
    ruta_base = os.path.dirname(os.path.abspath(__file__))
    ruta_icono = os.path.join(ruta_base, "assets", "logoAlaxa.png")

    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    app.setWindowIcon(QIcon(ruta_icono))

    # Instancia y muestra el diálogo de login
    login_dialog = LoginDialog()
      
    # Verifica que el usuario se haya logueado correctamente
    if login_dialog.exec_() == QDialog.Accepted:
        # Recupera el usuario y rol de Supabase guardados en el diálogo
        usuario = login_dialog.usuario_actual
        rol = login_dialog.rol_usuario  

        print(f"✅ Login exitoso. Usuario: {usuario.email} | Rol: {rol}")

        # Arranca directamente el tablero inyectándole los datos
        window = MainWindow(usuario=usuario, rol=rol)
        window.showMaximized()
    
        # Ejecuta la app
        sys.exit(app.exec_())

    else:
        # Si se cierra el login sin entrar, cierra el programa
        sys.exit()