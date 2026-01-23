from src.bd.conexion import db, URL, KEY
from supabase import create_client

"""
Clase que maneja la gestión de tareas (obtener, mover, crear) conectandose con la base de datos de Supabase
para guardar los cambios de las tareas y columnas
"""
class TaskManager:
    def _get_admin_client(self):
        """
        Crea un cliente Supabase fresco usando la KEY definida.
        Esto evita usar la sesion del usuario actual (que puede tener restricciones RLS para updates),
        permitiendo que el Admin realice cambios privilegiados (si la KEY tiene permisos/service role).
        """
        try:
             return create_client(URL, KEY)
        except Exception as e:
            print(f"Error creando admin client: {e}")
            return None

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

            usuarios = []

            # Pre-fetch equipos para mapear departamento_id para trabajadores y líderes
            # ya que ellos tienen equipo_id pero no necesariamente departamento_id directo en su tabla
            equipo_to_dept = {}
            try:
                res_eq = db.client.table('equipos').select('id, departamento_id').execute()
                for eq in res_eq.data:
                    equipo_to_dept[eq['id']] = eq['departamento_id']
            except Exception: pass

            # 1. Admins
            try:
                res = db.client.table('admins').select('*').execute()
                for u in res.data:
                    u['nivel_acceso'] = 'admin'
                    u['departamento_id'] = None
                    u['equipo_id'] = None
                    usuarios.append(u)
            except Exception as e: print(f"Error fetching admins: {e}")

            # 2. Managers
            try:
                res = db.client.table('managers').select('*').execute()
                for u in res.data:
                    u['nivel_acceso'] = 'manager'
                    u['equipo_id'] = None
                    # Managers deberian tener departamento_id directo
                    usuarios.append(u)
            except Exception as e: print(f"Error fetching managers: {e}")

            # 3. Lideres
            try:
                res = db.client.table('lideres_equipo').select('*').execute()
                for u in res.data:
                    u['nivel_acceso'] = 'lider_equipo'
                    # Resolver departamento desde el equipo
                    eq_id = u.get('equipo_id')
                    u['departamento_id'] = equipo_to_dept.get(eq_id)
                    usuarios.append(u)
            except Exception as e: print(f"Error fetching leaders: {e}")

            # 4. Trabajadores
            try:
                res = db.client.table('trabajadores').select('*').execute()
                for u in res.data:
                    u['nivel_acceso'] = 'trabajador'
                    # Resolver departamento desde el equipo
                    eq_id = u.get('equipo_id')
                    u['departamento_id'] = equipo_to_dept.get(eq_id)
                    usuarios.append(u)
            except Exception as e: print(f"Error fetching workers: {e}")

            return usuarios
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
                # "descripcion": descripcion, 
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

    # --- GESTIÓN DE DEPARTAMENTOS ---
    def obtener_departamentos(self):
        try:
            if not db.client: return []
            res = db.client.table('departamentos').select('*').order('nombre').execute()
            return res.data if res.data else []
        except Exception as e:
            print(f"Error obteniendo departamentos: {e}")
            return []

    def crear_departamento(self, nombre, descripcion):
        try:
            if not db.client: return False
            db.client.table('departamentos').insert({
                'nombre': nombre,
                'descripcion': descripcion
            }).execute()
            return True
        except Exception as e:
            print(f"Error creando departamento: {e}")
            return False

    def eliminar_departamento(self, dept_id):
        # OJO: Referencias cascada o restricción podrían fallar si hay usuarios o equipos
        try:
            if not db.client: return False
            db.client.table('departamentos').delete().eq('id', dept_id).execute()
            return True
        except Exception as e:
            print(f"Error borrando departamento: {e}")
            return False

    # --- GESTIÓN DE EQUIPOS ---
    def obtener_equipos(self):
        try:
            if not db.client: return []
            # Traer equipo junto con nombre de departamento (si Supabase join lo permite sencillo, 
            # sino toca hacer 2 queries o join manual). Haremos select plano y luego cruzamos en UI.
            res = db.client.table('equipos').select('*').order('nombre').execute()
            return res.data if res.data else []
        except Exception as e:
            print(f"Error obteniendo equipos: {e}")
            return []

    def crear_equipo(self, nombre, departamento_id, lider_id, descripcion, manager_id=None):
        try:
            if not db.client: return False
            
            # 1. Insertar equipo SIN lider/manager para romper dependencia circular
            data_init = {
                'nombre': nombre,
                'departamento_id': departamento_id,
                'descripcion': descripcion,
                'lider_id': None,
                'manager_id': None 
            }
            res = db.client.table('equipos').insert(data_init).execute()
            if not res.data: return False
            
            new_equipo_id = res.data[0]['id']
            
            # 2. Promover Usuarios
            if manager_id:
                self._mover_usuario_de_tabla(manager_id, 'manager', equipo_id=None, dept_id=departamento_id)
            
            if lider_id:
                self._mover_usuario_de_tabla(lider_id, 'lider_equipo', equipo_id=new_equipo_id, dept_id=departamento_id)
                
            # 3. Actualizar Equipo
            data_update = {}
            if lider_id: data_update['lider_id'] = lider_id
            if manager_id: data_update['manager_id'] = manager_id
            
            if data_update:
                db.client.table('equipos').update(data_update).eq('id', new_equipo_id).execute()

            return True
        except Exception as e:
            print(f"Error creando equipo: {e}")
            return False

    def eliminar_equipo(self, equipo_id):
        try:
            if not db.client: return False
            db.client.table('equipos').delete().eq('id', equipo_id).execute()
            return True
        except Exception as e:
            print(f"Error borrando equipo: {e}")
            return False

    def editar_equipo(self, equipo_id, nombre, dept_id, lider_id, manager_id, descripcion):
        try:
            if not db.client: return False
            
            # 1. Asegurar roles correctos (Manager primero, luego Lider)
            if manager_id:
                self._mover_usuario_de_tabla(manager_id, 'manager', equipo_id=None, dept_id=dept_id)
                
            if lider_id: 
                self._mover_usuario_de_tabla(lider_id, 'lider_equipo', equipo_id=equipo_id, dept_id=dept_id)

            # 2. Actualizar datos equipo
            data = {
                'nombre': nombre,
                'departamento_id': dept_id,
                'descripcion': descripcion,
                'lider_id': lider_id,    
                'manager_id': manager_id 
            }
            db.client.table('equipos').update(data).eq('id', equipo_id).execute()
            return True
        except Exception as e:
            print(f"Error editando equipo: {e}")
            return False

    def _mover_usuario_de_tabla(self, user_id, nuevo_rol_objetivo, equipo_id=None, dept_id=None):
        """
        Mueve al usuario de su tabla actual a la tabla correspondiente al nuevo rol.
        Simula una 'promocion' cambiando la tabla donde reside el registro.
        USA CLIENTE ADMIN.
        """
        try:
            admin_client = self._get_admin_client()
            if not admin_client: return

            print(f"[DEBUG] _mover_usuario_de_tabla: User {user_id} -> {nuevo_rol_objetivo}")
            
            # 1. Determinar rol actual (tabla origen) y obtener datos básicos
            user_data = None
            tabla_origen = None
            
            # Intento Trabajador
            res = admin_client.table('trabajadores').select('*').eq('id', user_id).execute()
            if res.data:
                user_data = res.data[0]
                tabla_origen = 'trabajadores'
            else:
                 # Intento Lider
                 res = admin_client.table('lideres_equipo').select('*').eq('id', user_id).execute()
                 if res.data:
                     user_data = res.data[0]
                     tabla_origen = 'lideres_equipo'
                 else:
                     # Intento Manager
                     res = admin_client.table('managers').select('*').eq('id', user_id).execute()
                     if res.data:
                        user_data = res.data[0]
                        tabla_origen = 'managers'
            
            # Si no esta en tablas publicas, quizas es nuevo? Asumimos que debe existir.
            if not user_data:
                print(f"[DEBUG] User {user_id} not found in any known public table.")
                return

            nombre = user_data.get('nombre')
            email = user_data.get('email')
            
            # 2. DELETE de tabla origen (Para evitar unique constraint en posibles triggers o logica global)
            print(f"[DEBUG] Deleting from {tabla_origen}")
            admin_client.table(tabla_origen).delete().eq('id', user_id).execute()
            
            # 3. INSERT en tabla destino
            try:
                new_data = {
                    'id': user_id,
                    'nombre': nombre,
                    'email': email
                }

                if nuevo_rol_objetivo == 'lider_equipo':
                    # Lider requires equipe_id and manager_id
                    manager_del_equipo = None
                    if equipo_id:
                        eq_data = admin_client.table('equipos').select('*').eq('id', equipo_id).single().execute()
                        if eq_data.data:
                             manager_del_equipo = eq_data.data.get('manager_id')
                             # Fallback: buscar manager del departamento
                             if not manager_del_equipo:
                                 dept_id_eq = eq_data.data.get('departamento_id')
                                 if dept_id_eq:
                                     man_res = admin_client.table('managers').select('id').eq('departamento_id', dept_id_eq).limit(1).execute()
                                     if man_res.data: manager_del_equipo = man_res.data[0]['id']

                    # Si aun asi no hay manager... usamos UUID default o esperamos fallo.
                    new_data['equipo_id'] = equipo_id
                    new_data['manager_id'] = manager_del_equipo
                    
                    admin_client.table('lideres_equipo').insert(new_data).execute()

                elif nuevo_rol_objetivo == 'manager':
                    if not dept_id and user_data.get('equipo_id'):
                         eq_res = admin_client.table('equipos').select('departamento_id').eq('id', user_data['equipo_id']).single().execute()
                         if eq_res.data: dept_id = eq_res.data['departamento_id']
                    
                    new_data['departamento_id'] = dept_id
                    admin_client.table('managers').insert(new_data).execute()

                elif nuevo_rol_objetivo == 'trabajador':
                    # Requiere equipo_id
                    # Si no pasamos equipo_id, intentamos mantener el anterior si venia de Lider
                    if not equipo_id and user_data.get('equipo_id'):
                        equipo_id = user_data.get('equipo_id')
                    
                    if equipo_id:
                         new_data['equipo_id'] = equipo_id
                         admin_client.table('trabajadores').insert(new_data).execute()
                    else:
                        print("ERROR: Trabajador requiere equipo_id")

                print(f"[DEBUG] Moved user to {nuevo_rol_objetivo}")

            except Exception as insert_err:
                print(f"CRITICAL ERROR moving user (Insert failed): {insert_err}")
                # INTENTO DE ROLLBACK (Opcional, manual)

        except Exception as e:
            print(f"Error _mover_usuario_de_tabla ({user_id}): {e}")

    def editar_departamento(self, dept_id, nombre, descripcion):
        try:
            if not db.client: return False
            data = {
                'nombre': nombre,
                'descripcion': descripcion
            }
            res = db.client.table('departamentos').update(data).eq('id', dept_id).execute()
            return True if res.data else False
        except Exception as e:
            print(f"Error editando departamento: {e}")
            return False

    def promover_a_manager(self, user_id, dept_id):
        try:
            # Reimplementado usando mover_tabla
            self._mover_usuario_de_tabla(user_id, 'manager', dept_id=dept_id)
            return True
        except Exception as e:
            print(f"Error promoviendo manager: {e}")
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
