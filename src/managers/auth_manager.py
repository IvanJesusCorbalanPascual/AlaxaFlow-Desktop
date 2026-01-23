from src.bd.conexion import db
"""
Clase para gestionar la autenticación de usuarios, contiene la logica para login y registro
ademas de la conexion con la base de datos de supabase para guardar los datos de los usuarios
"""
class AuthManager:
    def login(self, email, password):
        try:
            # Login Auth
            response = db.client.auth.sign_in_with_password({ # Clase nativa de las librerias de Supabase
                "email": email, "password": password
            })
            user = response.user
            
            if user:
                # Consultar PERFIL (nivel_acceso)
                data = db.client.table('perfiles').select('nivel_acceso').eq('id', user.id).execute()
                
                nivel = 'trabajador'
                if data.data and len(data.data) > 0:
                    nivel = data.data[0]['nivel_acceso']
                
                return user, nivel
            return None, None
        except Exception as e:
            print(f"Error Login: {e}")
            return None, None

    def registro(self, email, password, nombre, apellidos, departamento_id, nivel='trabajador', equipo_id=None):
        try:
            # Prepara la metadata
            data_meta = {
                "nombre": nombre,
                "apellidos": apellidos,
                "departamento_id": departamento_id,
                "rol": nivel # Lo envia como 'rol' para que el trigger lo pille
            }
            
            # Si se pasa un equipo, se añade a la metadata
            if equipo_id:
                data_meta['equipo_id'] = equipo_id

            response = db.client.auth.sign_up({ # Clase nativa de las librerias de Supabase
                "email": email,
                "password": password,
                "options": {
                    "data": data_meta
                }
            })
            # Devuelve el usuario creado
            return response.user 
        except Exception as e:
            print(f"Error Registro: {e}")
            return None