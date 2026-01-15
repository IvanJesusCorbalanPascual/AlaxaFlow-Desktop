import os
from supabase import create_client, Client

# URL y clave de Supabase
URL = "https://gveyougusrpzvpfhmznd.supabase.co"
KEY = "sb_secret_uvD94PvuOBXf0wXEKexozg_THzKlkDV"

class ConexionBD:
    def __init__(self):
        self.client = None
        try:
            self.client = create_client(URL, KEY)
            print("Base de datos conectada.")
        except Exception as e:
            print(f"Error de conexión: {e}")

# Instancia global para usar en el resto la app
db = ConexionBD()