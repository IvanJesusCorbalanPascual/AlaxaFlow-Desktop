import json
import os
from types import SimpleNamespace # <--- Herramienta estándar de Python
from src.bd.conexion import db

SESSION_FILE = "session.json"

class AuthManager:
    
    # --- MÉTODO CLAVE: Convierte el usuario 'rígido' en uno 'flexible' ---
    def _convertir_usuario(self, sb_user):
        try:
            # 1. Creamos un objeto vacío estándar de Python
            user_flexible = SimpleNamespace()
            
            # 2. Copiamos los datos obligatorios de Supabase
            user_flexible.id = sb_user.id
            user_flexible.email = sb_user.email
            
            # 3. Buscamos y pegamos los datos extra de la base de datos
            res = db.client.table('perfiles').select('*').eq('id', sb_user.id).single().execute()
            
            if res.data:
                # Pegamos las etiquetas nuevas. Ahora SI dejará hacerlo.
                user_flexible.nivel_acceso = res.data.get('nivel_acceso', 'trabajador')
                user_flexible.departamento_id = res.data.get('departamento_id')
                user_flexible.equipo_id = res.data.get('equipo_id')
                user_flexible.nombre = res.data.get('nombre', '')
                user_flexible.apellidos = res.data.get('apellidos', '')
            else:
                # Valores por defecto si no hay perfil
                user_flexible.nivel_acceso = 'trabajador'
                user_flexible.departamento_id = None
                user_flexible.equipo_id = None
                user_flexible.nombre = ''
                user_flexible.apellidos = ''
                
            return user_flexible
            
        except Exception as e:
            print(f"Error convirtiendo perfil: {e}")
            # Si falla, devolvemos un objeto básico para que no rompa
            fallback = SimpleNamespace()
            fallback.id = sb_user.id
            fallback.email = sb_user.email
            fallback.nivel_acceso = 'trabajador'
            return fallback

    def login(self, email, password, recordar=False):
        try:
            response = db.client.auth.sign_in_with_password({"email": email, "password": password})
            if response.user:
                if recordar and response.session: self.guardar_sesion_local(response.session)
                
                # Devolvemos el usuario convertido
                user = self._convertir_usuario(response.user)
                return user, user.nivel_acceso
            return None, None
        except Exception as e:
            print(f"Error Login: {e}")
            return None, None

    def registro(self, email, password, nombre, apellidos="", nivel='trabajador', departamento_id=None, equipo_id=None):
        try:
            user_metadata = {
                "nombre": nombre, "apellidos": apellidos, "nivel": nivel,
                "departamento_id": departamento_id, "equipo_id": equipo_id
            }
            res = db.client.auth.sign_up({"email": email, "password": password, "options": {"data": user_metadata}})
            
            if res.user:
                # Devolvemos usuario convertido
                return self._convertir_usuario(res.user)
            return None
        except: return None
        
    def login_automatico(self):
        if not os.path.exists(SESSION_FILE): return None, None
        try:
            with open(SESSION_FILE, 'r') as f: data = json.load(f)
            res = db.client.auth.set_session(data['access_token'], data['refresh_token'])
            if res.user:
                user = self._convertir_usuario(res.user)
                print("Sesión recuperada")
                return user, user.nivel_acceso
        except: self.borrar_sesion_local()
        return None, None
    
    def guardar_sesion_local(self, session):
        try:
            data = {"access_token": session.access_token, "refresh_token": session.refresh_token}
            with open(SESSION_FILE, 'w') as f: json.dump(data, f)
        except: pass
    
    def borrar_sesion_local(self):
        if os.path.exists(SESSION_FILE): os.remove(SESSION_FILE)