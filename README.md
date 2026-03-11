# Automatizador de Finanzas Personales (Local Edition)

Una aplicación de finanzas *Enterprise-Grade* diseñada bajo el [Engineering Playbook V5.0](./AGENTS.md).
Esta versión está optimizada para ser 100% portable y offline, utilizando un motor SQLite con arquitectura multicapa (Clean Architecture) y soporte preciso de múltiples divisas.

## Instalación y Arranque Rápido

1. **Instalar dependencias:**
   Asegúrate de tener Python 3.12+ e instala el proyecto en modo editable:
   ```bash
   pip install -e .
   ```

2. **Crear la Base de Datos:**
   Inicializa el archivo SQLite local (`mis_finanzas.db`):
   ```bash
   python run_migrations.py
   ```

3. **Encender la API:**
   Levanta el servidor con Uvicorn:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

4. **Uso:**
   Abre tu navegador en `http://127.0.0.1:8000/docs` para interactuar con la aplicación.