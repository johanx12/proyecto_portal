# Modelo de datos

```mermaid
erDiagram
 users ||--o{ tickets : registra
 users ||--o{ responses : escribe
 tickets ||--o{ responses : contiene
 users { INTEGER id PK; TEXT name; TEXT email UK; TEXT password_hash; TEXT role }
 tickets { INTEGER id PK; INTEGER user_id FK; TEXT subject; TEXT category; TEXT description; TEXT status; TEXT created_at; TEXT resolved_at }
 responses { INTEGER id PK; INTEGER ticket_id FK; INTEGER user_id FK; TEXT body; TEXT status; TEXT created_at }
```

## Diccionario resumido

`users` identifica cuentas y roles. `tickets` guarda radicado, dueño, asunto, categoría, descripción, estado y fechas. `responses` conserva el historial, su autor y el estado asociado. Las relaciones son `USUARIO 1:N SOLICITUD`, `USUARIO 1:N RESPUESTA` y `SOLICITUD 1:N RESPUESTA`.

Las claves foráneas se activan en cada conexión y los catálogos pequeños usan `CHECK`. La descripción no se concatena en SQL. Las respuestas se separan para no perder historial.

## Indicadores

Total: casos cuyo `created_at` empieza por el mes elegido. Por estado y categoría: conteos de esa cohorte. Porcentaje: `Resuelta / total * 100`; con cero se muestra 0. Promedio: horas entre creación y resolución de casos resueltos; sin casos se muestra `Sin datos`.
