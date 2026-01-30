import os
import httpx
from typing import Any

# URL y clave de Supabase
URL = "https://gveyougusrpzvpfhmznd.supabase.co"
KEY = "sb_secret_uvD94PvuOBXf0wXEKexozg_THzKlkDV"

class ConexionBD:
    def __init__(self, timeout: float = 5.0):
        self._client = None
        self._timeout = timeout

    @property
    def client(self):
        if self._client is None:
            try:
                from supabase import create_client
                self._client = create_client(URL, KEY)
                print("Base de datos conectada.")
            except Exception as e:
                print(f"Error de conexión (no bloqueante): {e}")
                self._client = None
        return self._client

# Instancia global para usar en el resto la app
db = ConexionBD()