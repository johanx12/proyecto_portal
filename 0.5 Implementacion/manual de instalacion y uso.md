# Manual de instalación y uso

## Preparar

En `0.3 Desarrollo`, crear el entorno virtual, instalar `requirements.txt`, crear el administrador por consola y ejecutar `app.py`. Abrir `http://127.0.0.1:5000`.

## Cliente

Crear cuenta, ingresar, pulsar Nueva solicitud, llenar asunto/categoría/descripción y guardar el radicado. En Solicitudes se consulta estado e historial.

## Administrador

Ingresar con la cuenta creada en consola, abrir Solicitudes, filtrar pendientes, entrar a un caso, escribir respuesta y elegir estado. En Reporte mensual seleccionar `AAAA-MM` y descargar CSV.

## Datos y respaldo

La base está en `0.3 Desarrollo/instance/portal.sqlite3`. Para crear copia:

```powershell
& ".\\0.3 Desarrollo\\.venv\\Scripts\\python.exe" ".\\0.5 Implementacion\\respaldo.py"
```

La copia se crea en `backups/`. Detén la aplicación antes de restaurar, conserva el archivo actual y prueba ingreso, radicado e historial después de copiar el respaldo.

El servidor de desarrollo local no es un servicio productivo. Para atención 24/7 real hacen falta proceso supervisado, HTTPS, clave persistente, monitoreo y respaldos programados.
