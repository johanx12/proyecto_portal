# Análisis del problema

| Necesidad | Solución | Evidencia |
|---|---|---|
| Atención 24/7 | Formulario y seguimiento sin restricción horaria en código | Registro y consulta local |
| Reporte mensual | Conteos por mes, estado y categoría, porcentaje y promedio | Pantalla y CSV |
| Base de datos | Usuarios, solicitudes y respuestas en SQLite | Persistencia tras reiniciar |

## Flujo

El cliente crea cuenta, registra un caso y recibe radicado. El administrador revisa la bandeja, responde y actualiza el estado. El cliente vuelve al portal para consultar la respuesta. Al cerrar el mes, el administrador selecciona el mes de recepción y revisa pendientes, categorías y tiempos.

## Permisos

| Operación | Cliente | Administrador |
|---|---|---|
| Crear solicitud | Propias | No |
| Ver detalle | Propias | Todas |
| Responder | No | Sí |
| Reporte y CSV | No | Sí |

## Riesgos y decisiones

El servidor local no garantiza disponibilidad continua; se deja alojamiento, HTTPS y monitoreo para 0.5. SQLite sirve para el trabajo académico; se evaluará PostgreSQL si crece la concurrencia. No se incorpora IA porque este problema se resuelve con reglas transparentes.
