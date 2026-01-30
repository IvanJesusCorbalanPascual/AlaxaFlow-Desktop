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
        try:
            # 1. Buscar equipo del usuario en su perfil
            perfil = db.client.table('perfiles').select('equipo_id').eq('id', usuario_id).single().execute()
            
            if perfil.data and perfil.data.get('equipo_id'):
                eq_id = perfil.data['equipo_id']
                # 2. Buscar si ese equipo tiene tablero asignado
                tabs = db.client.table('tableros').select('*').eq('equipo_id', eq_id).execute()
                if tabs.data: 
                    return tabs.data[0]
            
            return None
        except Exception as e:
            print(f"Error buscando tablero inicial: {e}")
            return None

    def obtener_columnas(self, tablero_id):
        # Recupera las columnas de un tablero específico ordenadas
        try:
            if not db.client:
                print("Sin conexión a la base de datos: no se pueden obtener columnas.")
                return []

            response = db.client.table('columnas')\
                .select('*')\
                .eq('tablero_id', tablero_id)\
                .order('posicion')\
                .execute()
            return response.data
        except Exception as e:
            print(f"Error columnas: {e}")
            return []

    def crear_columna(self, tablero_id, titulo):
        # Crea una nueva columna al final del tablero (posicion incremental)
        try:
            # Obtener la mayor posicion actual
            res = db.client.table('columnas').select('posicion')\
                .eq('tablero_id', tablero_id)\
                .order('posicion', desc=True).limit(1).execute()

            if res.data and len(res.data) > 0:
                nueva_posicion = res.data[0].get('posicion', 0) + 1
            else:
                nueva_posicion = 1

            insercion = db.client.table('columnas').insert({
                'tablero_id': tablero_id,
                'titulo': titulo,
                'posicion': nueva_posicion
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

    def obtener_todos_usuarios(self, filtro_dept_id=None):
        try:
            query = db.client.table('perfiles').select('*')
            
            if filtro_dept_id:
                query = query.eq('departamento_id', filtro_dept_id)
                
            return query.order('nombre').execute().data
        except Exception as e:
            print(f"Error listando usuarios: {e}")
            return []
        
    def obtener_admins(self):
        try:
            return db.client.table('perfiles').select('*').eq('nivel_acceso', 'admin').execute().data
        except: return []
        
        # --- GESTIÓN DE USUARIOS (CRUD) ---
    def editar_usuario(self, user_id, nombre, apellidos, rol, dept_id, equipo_id):
        try:
            data = {
                "nombre": nombre,
                "apellidos": apellidos,
                "nivel_acceso": rol,
                "departamento_id": dept_id if dept_id else None,
                "equipo_id": equipo_id if equipo_id else None
            }
            db.client.table('perfiles').update(data).eq('id', user_id).execute()
            return True
        except Exception as e:
            print(f"Error editando usuario: {e}")
            return False

    def eliminar_usuario(self, user_id):
        try:
            # 1. Desvincular de equipos (Líder o Manager)
            # Esto evita el error de FK en equipos que ya tratamos en UI, pero es mas seguro aqui tambien
            db.client.table('equipos').update({'lider_id': None}).eq('lider_id', user_id).execute()
            db.client.table('equipos').update({'manager_id': None}).eq('manager_id', user_id).execute()
            
            # 2. Desvincular de tareas (Creado por / Asignado a)
            # Intentamos poner a NULL. Si la BD no permite NULL, esto fallara, pero asumimos que si.
            db.client.table('tareas').update({'creado_por': None}).eq('creado_por', user_id).execute()
            db.client.table('tareas').update({'asignado_a': None}).eq('asignado_a', user_id).execute()
            
            # 3. Borrado limpio del perfil
            db.client.table('perfiles').delete().eq('id', user_id).execute()
            return True
        except Exception as e:
            print(f"Error eliminando usuario: {e}")
            return False

    def obtener_managers(self):
        try:
            return db.client.table('perfiles').select('*').eq('nivel_acceso', 'manager').execute().data
        except: return []

    def obtener_lideres(self):
        try:
            return db.client.table('perfiles').select('*').eq('nivel_acceso', 'lider_equipo').execute().data
        except: return []

    def obtener_trabajadores(self):
        try:
            return db.client.table('perfiles').select('*').eq('nivel_acceso', 'trabajador').execute().data
        except: return []

    # --- GESTIÓN DE TABLEROS (CRUD) ---
    def obtener_todos_tableros(self, filtro_dept_id=None):
        try:
            query = db.client.table('tableros').select('*')
            
            # Si nos pasan un departamento (Manager), filtramos
            if filtro_dept_id:
                query = query.eq('departamento_id', filtro_dept_id)
                
            return query.execute().data
        except Exception as e:
            print(f"Error listando tableros: {e}")
            return []

    def crear_tablero_admin(self, titulo, descripcion, equipo_id):
        try:
            # 1. Obtener departamento del equipo seleccionado
            eq_data = db.client.table('equipos').select('departamento_id').eq('id', equipo_id).single().execute()
            dept_id = eq_data.data.get('departamento_id') if eq_data.data else None
            
            # 2. Crear tablero vinculado al equipo (SIN creado_por)
            data = {
                "titulo": titulo, 
                "descripcion": descripcion, 
                "equipo_id": equipo_id,
                "departamento_id": dept_id
            }
            res = db.client.table('tableros').insert(data).execute()
            
            # 3. Crear columnas por defecto
            if res.data:
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
            print(f"Error creando tablero: {e}")
            return False

    def editar_tablero(self, tablero_id, titulo, descripcion, equipo_id):
        try:
            # Si cambiamos el equipo, actualizamos el departamento automáticamente
            dept_id = None
            if equipo_id:
                eq_data = db.client.table('equipos').select('departamento_id').eq('id', equipo_id).single().execute()
                if eq_data.data: dept_id = eq_data.data.get('departamento_id')

            data = {
                "titulo": titulo,
                "descripcion": descripcion,
                "equipo_id": equipo_id,
                "departamento_id": dept_id
            }
            db.client.table('tableros').update(data).eq('id', tablero_id).execute()
            return True
        except Exception as e:
            print(f"Error editando tablero: {e}")
            return False
        
    def eliminar_tablero(self, tablero_id):
        try:
            # Primero borrar columnas y tareas (Cascada manual si no está en BD)
            # Supabase suele tener ON DELETE CASCADE, probamos directo:
            db.client.table('tableros').delete().eq('id', tablero_id).execute()
            return True
        except Exception as e:
            print(f"Error eliminando tablero: {e}")
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

    def crear_equipo(self, nombre, dept_id, lider_id, descripcion, manager_id=None):
        try:
            if not db.client: return False
            
            # 1. Insertar equipo SIN lider/manager para romper dependencia circular
            data_equipo = {
                'nombre': nombre,
                'departamento_id': dept_id,
                'descripcion': descripcion,
                'lider_id': None,
                'manager_id': None 
            }
            res = db.client.table('equipos').insert(data_equipo).execute()
            
            if res.data:
                nuevo_equipo_id = res.data[0]['id']
                
                # 2. Si hay líder asignado, actualizar su perfil
                if lider_id:
                    # Lo ascendemos a 'lider_equipo' y le asignamos este equipo
                    self._mover_usuario_de_tabla(lider_id, 'lider_equipo', dept_id=dept_id, equipo_id=nuevo_equipo_id)
                
                return True
            return False
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

    def _mover_usuario_de_tabla(self, user_id, nuevo_rol, dept_id=None, equipo_id=None):
        """
        Mueve al usuario de su tabla actual a la tabla correspondiente al nuevo rol.
        Simula una 'promocion' cambiando la tabla donde reside el registro.
        USA CLIENTE ADMIN.
        """
        try:
            print(f"[DEBUG] Actualizando rol usuario {user_id} -> {nuevo_rol}")
            
            data = {'nivel_acceso': nuevo_rol}
            
            # Si nos pasan departamento o equipo, también los actualizamos
            if dept_id:
                data['departamento_id'] = dept_id
            if equipo_id is not None: # Permitir None para limpiar equipo
                data['equipo_id'] = equipo_id
                
            db.client.table('perfiles').update(data).eq('id', user_id).execute()
            return True
        except Exception as e:
            print(f"Error actualizando rol: {e}")
            return False

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
