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
    def _determinar_rol(self, user_id):
        try:
            res = db.client.table('perfiles').select('nivel_acceso').eq('id', user_id).single().execute()
                
            if res.data:
                return res.data.get('nivel_acceso', 'trabajador')

            return 'trabajador' # Default
        except Exception as e:
            print(f"Error determinando rol: {e}")
            return 'trabajador'

    def login(self, email, password, recordar=False):
        try:
            # Login Auth Real
            response = db.client.auth.sign_in_with_password({ 
                "email": email, "password": password
            })
            user = response.user
            session = response.session
            
            if user:
                # Guardar sesión si se solicitó
                if recordar and session:
                    self.guardar_sesion_local(session)

                # Determinar rol usando la nueva función
                rol = self._determinar_rol(user.id)
                
                # Inyectamos datos útiles al objeto usuario
                # user.nivel_acceso = rol

                return user, rol
                
            return None, None
        except Exception as e:
            print(f"Error Login: {e}")
            return None, None

    def registro(self, email, password, nombre, apellidos="", nivel='trabajador', departamento_id=None, equipo_id=None):
        try:
            user_metadata = {
                "nombre": nombre,
                "apellidos": apellidos,
                "nivel": nivel,
                "departamento_id": departamento_id,
                "equipo_id": equipo_id
            }
            
            print(f"Registrando: {email} | Rol: {nivel}")

            # Enviamos todo a Supabase Auth
            response = db.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": user_metadata
                }
            })
            
            user = response.user

            # Si se crea el usuario en Auth, el Trigger SQL creará automáticamente el perfil
            if user:
                return response.user

        except Exception as e:
            err_msg = str(e)
            print(f"Error Registro: {err_msg}")
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
                rol = self._determinar_rol(user.id)
                # user.nivel_acceso = rol
                print("Sesión restaurada automáticamente")
                return user, rol
        except Exception as e:
            print(f"Sesión caducada o inválida: {e}")
            # Si falla, borra el archivo de sesión corrupto
            self.borrar_sesion_local()

        return None, None
    
    # Método para borrar el archivo al hacer logout
    def borrar_sesion_local(self):
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)
