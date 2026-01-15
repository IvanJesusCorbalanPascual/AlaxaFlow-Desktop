from src.bd.conexion import db

class TaskManager:
    def __init__(self):
        self.db = db
    
    def obtener_tareas(self):
        response = self.db.client.table("tareas").select("*").execute()
        return response.data
