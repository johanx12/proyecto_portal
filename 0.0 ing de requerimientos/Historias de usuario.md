# Historias de usuario

Todas son prioridad `Must` en el MVP, salvo exportación que es `Should`.

| ID | Actor | Historia | Criterio de aceptación |
|---|---|---|---|
| HU01 | Cliente | Como cliente, quiero crear una cuenta para registrar solicitudes. | Cuenta válida creada; correo duplicado rechazado. |
| HU02 | Cliente/Administrador | Como usuario, quiero iniciar y cerrar sesión para proteger mi información. | Credencial válida entra; incorrecta no entra; salir retira acceso. |
| HU03 | Cliente | Como cliente, quiero registrar un requerimiento para recibir un radicado. | Datos válidos guardan caso en Pendiente; inválidos no guardan. |
| HU04 | Cliente | Como cliente, quiero ver mis solicitudes y respuestas para conocer su avance. | No puedo ver el radicado de otro cliente. |
| HU05 | Administrador | Como administrador, quiero filtrar la bandeja para priorizar la atención. | El filtro devuelve solo estados permitidos. |
| HU06 | Administrador | Como administrador, quiero responder y cambiar el estado para atender el caso. | Respuesta y estado se guardan juntos; un caso resuelto no se modifica. |
| HU07 | Administrador | Como administrador, quiero consultar el reporte mensual para tomar decisiones. | Totales y promedio coinciden con los registros del mes. |
| HU08 | Administrador | Como administrador, quiero exportar el reporte para presentarlo. | CSV conserva mes y cifras; cliente no puede descargarlo. |
