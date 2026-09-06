# Casos de uso

## CU01 Registrar cuenta

Actor: Cliente. El usuario completa nombre, correo y contraseña; el sistema valida, guarda el hash y crea rol cliente. Un correo duplicado se rechaza.

## CU02 Autenticar usuario

Actor: Cliente o administrador. El sistema verifica el hash, crea una sesión y muestra las funciones del rol. Credenciales inválidas devuelven un mensaje genérico.

## CU03 Registrar solicitud

Actor: Cliente autenticado. Completa asunto, categoría y descripción. El servidor usa el usuario de la sesión, guarda la fecha y devuelve el radicado.

## CU04 Consultar solicitud

Actor: Cliente. El servidor comprueba que el radicado pertenece a la sesión y muestra descripción, estado y respuestas. Un caso ajeno se oculta con 404.

## CU05 Gestionar bandeja

Actor: Administrador. Consulta todos los casos, filtra por estado y abre un detalle. Un filtro inválido se rechaza.

## CU06 Responder solicitud

Actor: Administrador. Escribe respuesta, elige estado y guarda ambas operaciones en una transacción. Casos resueltos quedan cerrados.

## CU07 Generar reporte

Actor: Administrador. Selecciona `AAAA-MM`, consulta total, estados, categorías, porcentaje resuelto y promedio de horas. Mes vacío informa ausencia de datos.

## CU08 Exportar reporte

Actor: Administrador. Descarga los mismos agregados en CSV. No incluye nombres, correos ni descripciones.
