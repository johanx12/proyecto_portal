# Desarrollo

Requiere Python 3.11+. Instala Flask y ejecuta:

```powershell
python -m venv .venv
.\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt
.\\.venv\\Scripts\\python.exe -m flask --app app:create_app crear-admin
.\\.venv\\Scripts\\python.exe app.py
```

El comando de consola crea el primer administrador sin exponer esa operación en el registro público. Abre `http://127.0.0.1:5000` y crea clientes desde la pantalla web.

`app.py` contiene fábrica Flask, sesiones, permisos, validaciones, rutas y reporte. `schema.sql` crea tres tablas. `templates` contiene las vistas y `static/style.css` la presentación. La base se genera en `instance/portal.sqlite3`, excluida de Git.

La clave `SECRET_KEY` puede definirse por variable de entorno; si se omite se genera una temporal y habrá que ingresar de nuevo tras reiniciar. `COOKIE_SECURE=1` se reserva para HTTPS.
