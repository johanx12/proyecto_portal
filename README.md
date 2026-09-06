# Proyecto Portal

Portal web universitario para recibir requerimientos de clientes, guardarlos en SQLite y generar reportes mensuales para los administradores.

## Entregables

- `0.0 ing de requerimientos`: visión, ERS, historias y casos de uso.
- `0.1 Analisis`: análisis del problema, permisos, trazabilidad y casos.
- `0.2 Diseño`: arquitectura, secuencias, modelo de datos y pantallas.
- `0.3 Desarrollo`: Flask, SQLite, HTML, CSS y guía de ejecución.
- `0.4 Pruebas`: pruebas automatizadas y plan de verificación.
- `0.5 Implementacion`: manual, respaldo y plan de mejora.

La aplicación recibe solicitudes a cualquier hora mientras el servidor esté disponible; la respuesta humana depende del administrador. Esta entrega es un prototipo local, no una promesa de disponibilidad productiva 24/7.

## Ejecución rápida

Desde `0.3 Desarrollo` en Windows:

```powershell
python -m venv .venv
.\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt
.\\.venv\\Scripts\\python.exe -m flask --app app:create_app crear-admin
.\\.venv\\Scripts\\python.exe app.py
```

Abre `http://127.0.0.1:5000`. Crea el cliente en la pantalla de registro. La contraseña del administrador se solicita en consola.

## Demostración

1. Registrar un cliente y crear una solicitud.
2. Ingresar como administrador, responder y actualizar el estado.
3. Volver al cliente para consultar el historial.
4. Consultar el reporte mensual y descargar su CSV.
5. Ejecutar las pruebas desde `0.3 Desarrollo`:

```powershell
.\\.venv\\Scripts\\python.exe "../0.4 Pruebas/test_portal.py"
```

La estructura documental se adaptó de [PROYECTO_NEXORA](https://github.com/johanx12/PROYECTO_NEXORA). El dominio Portal no incluye nómina ni inteligencia artificial.
