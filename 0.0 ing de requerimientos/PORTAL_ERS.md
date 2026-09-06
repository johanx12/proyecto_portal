# Especificación de requisitos del Portal

Versión 1.0 · 6 de septiembre de 2026. Adaptación académica de la estructura ERS usada en NEXORA.

## 1. Descripción general

La aplicación es un monolito Flask con HTML/Jinja y CSS en la presentación, reglas y permisos en el servidor y SQLite como base relacional. El cliente registra y consulta casos; el administrador responde y genera el reporte.

## 2. Actores

**Cliente:** crea y consulta sus solicitudes. **Administrador:** ve todos los casos, responde y consulta reportes. **Estudiante:** desarrolla y prueba el MVP. **Docente:** revisa el trabajo.

## 3. Requisitos funcionales

| ID | Requisito | Prioridad |
|---|---|---|
| RF01 | Crear cuenta de cliente | Must |
| RF02 | Iniciar y cerrar sesión | Must |
| RF03 | Registrar una solicitud y generar radicado | Must |
| RF04 | Consultar solicitudes propias | Must |
| RF05 | Administrar bandeja y filtrar por estado | Must |
| RF06 | Responder una solicitud y cambiar estado | Must |
| RF07 | Consultar indicadores del mes de recepción | Must |
| RF08 | Descargar el reporte en CSV | Should |

## 4. Reglas de negocio

- El registro público siempre crea el rol `cliente`; el administrador se crea desde consola.
- El cliente solo consulta solicitudes cuyo propietario coincide con su sesión.
- Asunto: 3–120 caracteres. Descripción: 10–3000 caracteres.
- Categorías: Consulta, Reclamo, Soporte y Sugerencia.
- Toda respuesta administrativa guarda texto, autor, fecha y estado en una transacción.
- Una solicitud `Resuelta` queda cerrada en esta versión.
- El reporte agrupa por mes de creación y usa el estado vigente al consultarlo.
- Si el mes no tiene casos, el porcentaje es 0 y el promedio aparece como `Sin datos`.

## 5. Requisitos de calidad

Las contraseñas se guardan con hash y sal; se valida sesión, rol, propiedad y CSRF en el servidor; se usan consultas SQL parametrizadas; la interfaz es adaptable a móvil; y los datos se conservan en SQLite. HTTPS, bloqueo de intentos, disponibilidad 24/7 real, respaldo programado y prueba de carga quedan para producción.

## 6. Evolución

Notificaciones, recuperación de acceso, archivos adjuntos, agentes, cierre mensual inmutable, PostgreSQL y monitoreo continuo pueden implementarse por fases.
