import os
import httpx
from typing import Any

# URL y clave de Supabase
URL = "https://gveyougusrpzvpfhmznd.supabase.co"
KEY = "sb_secret_uvD94PvuOBXf0wXEKexozg_THzKlkDV"


class ConexionBD:
    def __init__(self, timeout: float = 5.0):
        # No creamos el client en __init__ para evitar que la app se bloquee
        # en el arranque si la red está lenta o no disponible.
        self._client = None
        self._timeout = timeout

    @property
    def client(self):
        # Lazy init: crea el cliente solo al primer uso.
        if self._client is None:
            try:
                # Import supabase lazily to avoid heavy imports at module load
                # (pydantic/postgrest plugin discovery can block on startup).
                from supabase import create_client  # local import

                # create_client no acepta un httpx client en esta versión,
                # se llama de la forma estándar para evitar el error.
                self._client = create_client(URL, KEY)
                print("Base de datos conectada.")
            except Exception as e:
                print(f"Error de conexión (no bloqueante): {e}")
                self._client = None
        return self._client


# Instancia global para usar en el resto la app
db = ConexionBD()