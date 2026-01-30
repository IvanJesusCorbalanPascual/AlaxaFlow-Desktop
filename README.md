# 🚀 AlaxaFlow Desktop

> **Gestión corporativa de tareas eficiente, segura y escalable.**

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![PyQt5](https://img.shields.io/badge/GUI-PyQt5-green?logo=qt&logoColor=white)
![Supabase](https://img.shields.io/badge/Backend-Supabase-emerald?logo=supabase&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?logo=windows)

**AlaxaFlow Desktop** es una aplicación de escritorio diseñada para optimizar el flujo de trabajo en empresas con estructura jerárquica. Permite la gestión de tareas tipo **Kanban** (Tableros, Columnas, Tarjetas) con un robusto sistema de permisos basado en roles, autenticación segura en la nube y funcionalidades de accesibilidad.

---

## 📸 Capturas de Pantalla

*(Aquí puedes añadir capturas de tu aplicación funcionando)*
| Login | Tablero Kanban | Panel Admin |
| *Vista del Login* |
| <img width="395" height="619" alt="image" src="https://github.com/user-attachments/assets/d97102a8-9cd3-4652-936a-13d575766474" />
|:---:|
| *Vista del Tablero* |
| <img width="1919" height="1018" alt="image" src="https://github.com/user-attachments/assets/529c1c59-34f1-49cd-9da3-804fec596135" />
|:---:|
| *Vista del Panel de Control* |
| <img width="995" height="730" alt="image" src="https://github.com/user-attachments/assets/acd1f7ca-0d7e-40f0-b367-e6dec3b2ec79" />


---

## 🌟 Características Principales

### 📋 Gestión de Tareas (Kanban)
* **Drag & Drop:** Mueve tareas entre columnas (Pendiente, En Proceso, Finalizado) arrastrando y soltando.
* **Edición en tiempo real:** Doble clic para editar título, descripción y asignar empleados.
* **Sincronización:** Todo se guarda instantáneamente en la nube (Supabase).

### 🔐 Sistema de Roles Jerárquico (RBAC)
La aplicación adapta su interfaz y permisos según quién inicie sesión:

| Rol | Permisos | Visibilidad |
| :--- | :--- | :--- |
| 👑 **Admin** | Control Total. Crear/Borrar Usuarios, Equipos, Depts. y Tableros. | Global (Ve toda la empresa). |
| 👔 **Manager** | Gestión de su Departamento. Crea usuarios/equipos en su área. | Limitada a su **Departamento**. |
| 🧢 **Líder** | Gestión de Tareas avanzada. Puede **eliminar tareas**. | Limitada a su **Equipo**. |
| 👷 **Trabajador** | Crear y Mover tareas. No puede borrar ni gestionar usuarios. | Limitada a su **Equipo**. |

### 🛠️ Panel de Administración
* Gestión CRUD completa de **Empleados, Departamentos y Equipos**.
* Filtrado automático inteligente: Los Managers solo ven y gestionan a su personal.
* Protección de integridad: Avisos al intentar borrar líderes de equipo activos.

### 👁️ Accesibilidad y UX
* **Modo Alto Contraste:** Tema visual optimizado para visibilidad (Negro/Amarillo) activable con un clic.
* **Persistencia de Sesión:** Login automático mediante tokens seguros.

---

## 🔧 Tecnologías Utilizadas

* **Lenguaje:** Python 3.10
* **Interfaz Gráfica (GUI):** PyQt5 + Qt Designer (`.ui` files).
* **Backend / Base de Datos:** Supabase (PostgreSQL + Auth).
* **Conexión HTTP:** Librerías `supabase` y `httpx`.
* **Empaquetado:** PyInstaller (Generación de `.exe` portable).

---

## 🚀 Instalación y Ejecución (Entorno de Desarrollo)

1.  **Clonar el repositorio:**
    ```bash
    git clone [https://github.com/tu-usuario/AlaxaFlow-Desktop.git](https://github.com/tu-usuario/AlaxaFlow-Desktop.git)
    cd AlaxaFlow-Desktop
    ```

2.  **Crear entorno virtual:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Asegúrate de tener instalados: `PyQt5`, `supabase`, `httpx`, `Pillow`)*

4.  **Configurar Base de Datos:**
    * Asegúrate de tener el archivo `src/bd/conexion.py` con tu `URL` y `KEY` de Supabase.

5.  **Ejecutar:**
    ```bash
    python Main.py
    ```

---

## 📦 Compilación a .EXE

Para generar un ejecutable `AlaxaFlow.exe` independiente que funcione en cualquier Windows (incluso sin Python instalado), utiliza el siguiente comando optimizado:

```powershell
pyinstaller --noconfirm --onefile --windowed --name "AlaxaFlow" --icon "assets/logoAlaxa.ico" --add-data "assets;assets" --add-data "src;src" --hidden-import "PyQt5.uic" --hidden-import "httpx" --hidden-import "supabase" Main.py
