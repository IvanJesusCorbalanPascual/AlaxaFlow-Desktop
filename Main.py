import sys, os
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtGui import QIcon
from src.views.main_window import MainWindow, ESTILO_NORMAL
from src.views.login_window import LoginDialog
from src.managers.auth_manager import AuthManager
        
if __name__ == "__main__":
    ruta_base = os.path.dirname(os.path.abspath(__file__))
    ruta_icono = os.path.join(ruta_base, "assets", "logoAlaxa.png")

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
        # Si se cierra el login sin entrar, cierra el programa
        sys.exit()