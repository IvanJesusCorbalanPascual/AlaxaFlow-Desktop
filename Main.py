import sys, os
import ctypes
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtGui import QIcon
from src.views.main_window import MainWindow, ESTILO_NORMAL
from src.views.login_window import LoginDialog
from src.managers.auth_manager import AuthManager

import sys
import os

# --- Para compilar correctamente el programa ---
def resolver_ruta(ruta_relativa):
    # Obtiene la ruta absoluta al recurso, funciona para dev y para PyInstaller
    try:
        # PyInstaller crea una carpeta temporal y guarda la ruta en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, ruta_relativa)

if __name__ == "__main__":
    # Para que Windows muestre el icono 'Alaxa' en la barra de tareas
    try:
        myappid = 'alaxa.flow.desktop.v1'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except ImportError:
        pass

    ruta_base = os.path.dirname(os.path.abspath(__file__))
    ruta_icono = resolver_ruta(os.path.join("assets", "logoAlaxa.ico"))

    app = QApplication(sys.argv)
    app.setStyleSheet(ESTILO_NORMAL)
    app.setWindowIcon(QIcon(ruta_icono))

    # Comprueba si hay sesión guardada para login automático
    auth = AuthManager()
    print("Comprobando sesión guardada...")
    user_auto, rol_auto = auth.login_automatico()

    if user_auto:
        print(f" Inicio rápido (Sesión recuperada). Usuario: {user_auto.email}")
        window = MainWindow(usuario=user_auto, rol=rol_auto)
        window.showMaximized()
        sys.exit(app.exec_())

    # Si no hay sesión, muestra el diálogo de login normal
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
        sys.exit()