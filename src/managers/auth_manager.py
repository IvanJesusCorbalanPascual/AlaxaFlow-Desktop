import json
import os
from src.bd.conexion import db

# Constante para guardar la sesión
SESSION_FILE = "session.json"
"""
Clase para gestionar la autenticación de usuarios, contiene la logica para login y registro
ademas de la conexion con la base de datos de supabase para guardar los datos de los usuarios
"""
class AuthManager:
    def login(self, email, password, recordar=False):
        try:
            # Login Auth
            response = db.client.auth.sign_in_with_password({ # Clase nativa de las librerias de Supabase
                "email": email, "password": password
            })
            user = response.user
            # Captura la sesión
            session = response.session
            
            if user:
                # Consultar PERFIL (nivel_acceso)
                data = db.client.table('perfiles').select('nivel_acceso').eq('id', user.id).execute()
                
                nivel = 'trabajador'
                if data.data and len(data.data) > 0:
                    nivel = data.data[0]['nivel_acceso']

                if recordar and session:
                    self.guardar_sesion_local(session)
                
                return user, nivel
            return None, None
        except Exception as e:
            print(f"Error Login: {e}")
            return None, None

    def registro(self, email, password, nombre, apellidos, departamento_id, nivel='trabajador'):
        try:
            response = db.client.auth.sign_up({ # Clase nativa de las librerias de Supabase
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "nombre": nombre,
                        "apellidos": apellidos,
                        "departamento_id": departamento_id,
                        "rol": nivel # Lo envia como 'rol' para que el trigger lo pille
                    }
                }
            })
            # Devuelve el usuario creado
            return response.user 
        except Exception as e:
            print(f"Error Registro: {e}")
            return None
        
    # Guarda la sesión localmente en un archivo JSON
    def guardar_sesion_local(self, session):
        try:
            data = {
                "access_token": session.access_token,
                "refresh_token": session.refresh_token
            }
            with open(SESSION_FILE, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error guardando sesión: {e}")

    # Carga la sesión desde el archivo JSON si existe
    def login_automatico(self):
        if not os.path.exists(SESSION_FILE):
            return None, None
        
        try:
            with open(SESSION_FILE, 'r') as f:
                data = json.load(f)

            # Intenta restaurar la sesión en Supabase
            response = db.client.auth.set_session(data['access_token'], data['refresh_token'])

            user = response.user
            if user:
                # Si el token funciona, obtiene el rol igual que en el login
                data = db.client.table('perfiles').select('nivel_acceso').eq('id', user.id).execute()
                nivel = 'trabajador'
                if data.data and len(data.data) > 0:
                    nivel = data.data[0]['nivel_acceso']

                print("Sesión restaurada automáticamente")
                return user, nivel
        except Exception as e:
            print(f"Sesión caducada o inválida: {e}")
            # Si falla, borra el archivo de sesión corrupto
            self.borrar_sesion_local()

        return None, None
    
    # Método para borrar el archivo al hacer logout
    def borrar_sesion_local(self):
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)