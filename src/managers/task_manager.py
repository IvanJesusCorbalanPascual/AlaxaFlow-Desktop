from src.bd.conexion import db
"""
Clase que maneja la gestión de tareas (obtener, mover, crear) conectandose con la base de datos de Supabase
para guardar los cambios de las tareas y columnas
"""
class TaskManager:
    # --- GESTIÓN DE TABLEROS ---
    def obtener_o_crear_tablero_inicial(self, usuario_id):
        # Busca si existe un tablero. Si no, crea uno por defecto con columnas.
        try:
            # Si no hay cliente disponible, no intentamos llamar a la BD
            if not db.client:
                print("Sin conexión a la base de datos: no se pueden obtener tableros.")
                return None

            # Buscar tableros existentes en la bd
            tableros = db.client.table('tableros').select("*").execute()

            if tableros.data and len(tableros.data) > 0:
                return tableros.data[0]
            
            # Si no hay, creamos uno por defecto
            print("Creando tablero inicial...")
            nuevo_tablero = db.client.table('tableros').insert({
                "titulo": "Tablero General",
                "creado_por": usuario_id
            }).execute()
            
            tablero_id = nuevo_tablero.data[0]['id']
            
            # Creando las columnas básicas para el tablero (UUIDs automáticos)
            columnas_defecto = [
                {"titulo": "PENDIENTE", "orden": 1, "tablero_id": tablero_id},
                {"titulo": "EN PROCESO", "orden": 2, "tablero_id": tablero_id},
                {"titulo": "REVISIÓN", "orden": 3, "tablero_id": tablero_id},
                {"titulo": "FINALIZADO", "orden": 4, "tablero_id": tablero_id}
            ]
            db.client.table('columnas').insert(columnas_defecto).execute()
            
            return nuevo_tablero.data[0] # Devolvemos el tablero creado
            
        except Exception as e:
            print(f"Error gestionando tableros: {e}")
            return None

    def obtener_columnas(self, tablero_id):
        # Recupera las columnas de un tablero específico ordenadas
        try:
            if not db.client:
                print("Sin conexión a la base de datos: no se pueden obtener columnas.")
                return []

            return db.client.table('columnas').select("*")\
                .eq('tablero_id', tablero_id)\
                .order('orden').execute().data
        except Exception as e:
            print(f"Error columnas: {e}")
            return []

    def crear_columna(self, tablero_id, titulo):
        # Crea una nueva columna al final del tablero (orden incremental)
        try:
            # Obtener el mayor orden actual
            res = db.client.table('columnas').select('orden')\
                .eq('tablero_id', tablero_id)\
                .order('orden', desc=True).limit(1).execute()

            if res.data and len(res.data) > 0:
                nuevo_orden = res.data[0].get('orden', 0) + 1
            else:
                nuevo_orden = 1

            insercion = db.client.table('columnas').insert({
                'tablero_id': tablero_id,
                'titulo': titulo,
                'orden': nuevo_orden
            }).execute()

            return insercion.data is not None
        except Exception as e:
            print(f"Error crear columna: {e}")
            return False

    # --- GESTIÓN DE TAREAS ---
    def obtener_tareas_por_tablero(self, tablero_id):
        # Traemos todas las tareas donde su columna pertenezca al tablero X 
        try:
            # Primero obtenemos las columnas de este tablero
            cols = self.obtener_columnas(tablero_id)
            ids_cols = [c['id'] for c in cols]
            
            if not ids_cols: return [] # Si no hay columnas, devolvemos una lista vacía

            # Traemos las tareas que estén en esas columnas en el orden de su posición
            return db.client.table('tareas').select("*")\
                .in_('columna_id', ids_cols)\
                .order('posicion').execute().data
        except Exception as e:
            print(f"Error tareas: {e}")
            return []

    def obtener_tareas_por_columna(self, columna_id):
        # Devuelve las tareas que pertenecen a una columna concreta
        try:
            if not db.client:
                print("Sin conexión a la base de datos: no se pueden obtener tareas por columna.")
                return []
            res = db.client.table('tareas').select('*').eq('columna_id', columna_id).execute()
            return res.data if res and res.data else []
        except Exception as e:
            print(f"Error obtener_tareas_por_columna: {e}")
            return []

    def eliminar_columna(self, columna_id):
        # Elimina todas las tareas de la columna y la propia columna
        try:
            if not db.client:
                print("Sin conexión a la base de datos: no se puede eliminar la columna.")
                return False

            # Primero borrar tareas asociadas
            db.client.table('tareas').delete().eq('columna_id', columna_id).execute()

            # Luego borrar la propia columna
            db.client.table('columnas').delete().eq('id', columna_id).execute()
            return True
        except Exception as e:
            print(f"Error eliminar_columna: {e}")
            return False

    def editar_columna(self, columna_id, nuevo_titulo):
        # Edita el título de una columna
        try:
            if not db.client:
                print("Sin conexión a la base de datos: no se puede editar la columna.")
                return False

            db.client.table('columnas').update({
                'titulo': nuevo_titulo
            }).eq('id', columna_id).execute()
            return True
        except Exception as e:
            print(f"Error editar_columna: {e}")
            return False

    def crear_tarea(self, titulo, columna_id, usuario_id):
        # Crea una nueva tarea en la columna X
        try:
            if not db.client:
                print("Sin conexión a la base de datos: no se puede crear la tarea.")
                return False
            db.client.table('tareas').insert({
                "titulo": titulo,
                "columna_id": columna_id,
                "creado_por": usuario_id,
                "posicion": 0 # Por defecto arriba
            }).execute()
            return True
        except Exception as e:
            print(f"Error crear tarea: {e}")
            return False

    def mover_tarea(self, id_tarea, id_nueva_columna):
        # Mueve una tarea con id (id_tarea) a la nueva columna (id_nueva_columna)
        try:
            if not db.client:
                print("Sin conexión a la base de datos: no se puede mover la tarea.")
                return False
            db.client.table('tareas').update({
                "columna_id": id_nueva_columna
            }).eq('id', id_tarea).execute()
            print(f"Tarea {id_tarea} movida a columna {id_nueva_columna}")  
            return True
        except Exception as e:
            print(f"Error mover tarea: {e}")
            return False

    def eliminar_tarea(self, id_tarea, nivel_acceso):
        # Solo Admin o Manager pueden borrar tareas
        if nivel_acceso not in ['admin', 'manager']:
            print("Solo Admin o Manager pueden borrar.")
            return False
        try:
            if not db.client:
                print("Sin conexión a la base de datos: no se puede eliminar la tarea.")
                return False
            db.client.table('tareas').delete().eq('id', id_tarea).execute()
            return True
        except Exception as e:
            print(f"Error eliminar: {e}")
            return False
        
    def editar_tarea(self, id_tarea, nuevo_titulo):
        try:
            if not db.client:
                print("Sin conexión a la base de datos: no se puede editar la tarea.")
                return False
            db.client.table('tareas').update({
                "titulo": nuevo_titulo
            }).eq('id', id_tarea).execute()
            return True
        except Exception as e:
            print(f"Error editar tarea: {e}")
            return False    
        
    def editar_descripcion_tarea(self, id_tarea, nueva_descripcion):
        try:
            if not db.client:
                return False
            
            # Actualiza solo el campo descripcion
            db.client.table('tareas').update({
                "descripcion": nueva_descripcion
            }).eq('id', id_tarea).execute()
            
            return True
        except Exception as e:
            print(f"Error editando descripción: {e}")
            return False
        
    # Para recuperar la descripción actualiza al abrir una tarjeta
    def obtener_tarea_por_id(self, id_tarea):
        try:
            res = db.client.table('tareas').select('*').eq('id', id_tarea).single().execute()
            return res.data
        except Exception:
            return None

    # --- Gestion de usuarios y tableros por Admin ---

    def obtener_todos_usuarios(self):
        try:
            if not db.client:
                print("Sin conexión a la base de datos: no se pueden listar usuarios.")
                return []

            # Traemos todos los perfiles de la base de datos
            response = db.client.table('perfiles').select('*').execute()
            return response.data
        except Exception as e:
            print(f"Error listando usuarios: {e}")
            return []

    def obtener_todos_tableros(self):
        try:
            if not db.client:
                print("Sin conexión a la base de datos: no se pueden listar tableros.")
                return []

            # Traemos todos los tableros
            response = db.client.table('tableros').select('*').execute()
            return response.data
        except Exception as e:
            print(f"Error listando tableros: {e}")
            return []

    def crear_tablero_admin(self, titulo, descripcion, id_owner):
        # Crear tablero asignado a un usuario específico (Lógica de Admin)
        try:
            if not db.client:
                print("Sin conexión a la base de datos: no se puede crear tablero.")
                return False
            data = {
                "titulo": titulo, 
                "descripcion": descripcion, 
                "creado_por": id_owner
            }
            res = db.client.table('tableros').insert(data).execute()
            
            if res.data:
                # Crear columnas por defecto automáticamente
                tid = res.data[0]['id']
                cols = [
                    {"tablero_id": tid, "titulo": "PENDIENTE", "posicion": 1},
                    {"tablero_id": tid, "titulo": "EN PROCESO", "posicion": 2},
                    {"tablero_id": tid, "titulo": "FINALIZADO", "posicion": 3}
                ]
                db.client.table('columnas').insert(cols).execute()
                return True
            return False
        except Exception as e:
            print(f"Error creando tablero admin: {e}")
            return False
        
    def editar_asignacion_tarea(self, id_tarea, id_usuario):
        try:
            if not db.client: return False
            
            # Actualiza el campo asignado_a
            db.client.table('tareas').update({
                "asignado_a": id_usuario
            }).eq('id', id_tarea).execute()
            
            return True
        except Exception as e:
            print(f"Error asignando tarea: {e}")
            return False
