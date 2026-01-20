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

    def registro(self, email, password, nombre_completo, nivel='trabajador'):
        try:
            response = db.client.auth.sign_up({ # Clase nativa de las librerias de Supabase
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "full_name": nombre_completo,
                        "rol": nivel # Lo enviamos como 'rol' para que el trigger lo pille
                    }
                }
            })
            return response.user # Devuelve el usuario creado
        except Exception as e:
            print(f"Error Registro: {e}")
            return None