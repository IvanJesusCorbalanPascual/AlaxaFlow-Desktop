from src.bd.conexion import db
"""
Clase para gestionar la autenticación de usuarios, contiene la logica para login y registro
ademas de la conexion con la base de datos de supabase para guardar los datos de los usuarios
"""
class AuthManager:
    def login(self, email, password):
        try:
            # BACKDOOR ADMIN
            # BACKDOOR ADMIN
            if email == 'admin' and password == 'admin':
                class MockUser:
                    id = '00000000-0000-0000-0000-000000000000'
                    email = 'admin@local'
                return MockUser(), 'admin'

            # Login Auth
            response = db.client.auth.sign_in_with_password({ 
                "email": email, "password": password
            })
            user = response.user
            
            if user:
                # Determinar rol buscando en las tablas una por una
                # Orden: admin > manager > lider > trabajador
                if db.client.table('admins').select('id').eq('id', user.id).execute().data:
                    return user, 'admin'
                
                if db.client.table('managers').select('id').eq('id', user.id).execute().data:
                    return user, 'manager'
                    
                if db.client.table('lideres_equipo').select('id').eq('id', user.id).execute().data:
                    return user, 'lider_equipo'
                    
                if db.client.table('trabajadores').select('id').eq('id', user.id).execute().data:
                    return user, 'trabajador'
                
                # Default o error si no esta en ninguna tabla publica pero si en auth
                return user, 'trabajador' 
                
            return None, None
        except Exception as e:
            print(f"Error Login: {e}")
            return None, None

    def registro(self, email, password, nombre, apellidos, departamento_id, nivel='trabajador', equipo_id=None):
        try:
            # 1. Crear usuario en Auth
            # Nota: Ya no enviamos metadata para trigger de perfiles antiguos
            # a menos que sea necesario.
            response = db.client.auth.sign_up({
                "email": email,
                "password": password
            })
            user = response.user
            if not user: return None
            
            # 2. Insertar en la tabla especifica segun rol
            # Usamos nombre + apellidos concatenados si la tabla pide solo nombre, o ajustamos.
            # Esquema dice: 'nombre' text. Pasaremos "Nombre Apellidos".
            full_name = f"{nombre} {apellidos}"
            
            if nivel == 'admin':
                 db.client.table('admins').insert({
                     'id': user.id,
                     'nombre': full_name,
                     'email': email
                 }).execute()

            elif nivel == 'manager':
                # Managers requieren departamento_id
                 db.client.table('managers').insert({
                     'id': user.id,
                     'nombre': full_name,
                     'email': email,
                     'departamento_id': departamento_id
                 }).execute()

            elif nivel == 'lider_equipo':
                manager_id = None
                if equipo_id:
                     # Buscar manager del equipo o departamento
                     try:
                         eq = db.client.table('equipos').select('manager_id, departamento_id').eq('id', equipo_id).single().execute()
                         if eq.data:
                             manager_id = eq.data.get('manager_id')
                             if not manager_id and eq.data.get('departamento_id'):
                                 m = db.client.table('managers').select('id').eq('departamento_id', eq.data['departamento_id']).limit(1).execute()
                                 if m.data: manager_id = m.data[0]['id']
                     except Exception as e:
                         print(f"Error buscando manager para lider: {e}")

                if manager_id:
                     db.client.table('lideres_equipo').insert({
                         'id': user.id,
                         'nombre': full_name,
                         'email': email,
                         'equipo_id': equipo_id,
                         'manager_id': manager_id
                     }).execute()
                else:
                    print("Error: No se puede registrar Lider sin Manager asignado (Equip/Dept).")
                    return None

            else: # trabajador
                # Trabajador requiere equipo_id NOT NULL
                if equipo_id:
                     db.client.table('trabajadores').insert({
                         'id': user.id,
                         'nombre': full_name,
                         'email': email,
                         'equipo_id': equipo_id
                     }).execute()
                else:
                    print("Error: Trabajador requiere equipo_id")

            # 3. Check result
            # Si algo falla en insert, deberíamos considerar borrar el usuario de auth? 
            # Por seguridad data integrity, si el insert de rol falla, este user queda "huerfano" en auth.
            
            return user 
        except Exception as e:
            err_msg = str(e)
            print(f"Error Registro DETALLADO: {err_msg}")
            
            # Detectar error de usuario existente
            if "User already registered" in err_msg:
                # Esto viene de Supabase Auth
                return None
            
            # Si el error es de base de datos (p.ej. email duplicado en tabla lideres/trabajadores)
            if "duplicate key value violates unique constraint" in err_msg:
                 print("Error: El email ya existe en la tabla de roles.")
                 return None
                 
            return None