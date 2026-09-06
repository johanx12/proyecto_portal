# Arquitectura y secuencias

La arquitectura conserva la separación por capas de NEXORA, simplificada a un monolito para la entrega.

```mermaid
flowchart LR
 C[Cliente] --> UI[Navegador HTML/CSS]
 A[Administrador] --> UI
 UI --> F[Flask: sesión, permisos y reglas]
 F --> D[(SQLite)]
 F --> J[Plantillas Jinja]
 J --> UI
```

## Registrar solicitud

```mermaid
sequenceDiagram
 actor C as Cliente
 participant F as Flask
 participant D as SQLite
 C->>F: POST con sesión y CSRF
 F->>F: Validar propietario y campos
 F->>D: INSERT solicitud
 D-->>F: Radicado
 F-->>C: Detalle y confirmación
```

## Responder

```mermaid
sequenceDiagram
 actor A as Administrador
 participant F as Flask
 participant D as SQLite
 A->>F: Respuesta y estado
 F->>F: Validar rol y caso abierto
 F->>D: INSERT respuesta + UPDATE estado
 D-->>F: Commit
 F-->>A: Historial actualizado
```

## Estados

```mermaid
stateDiagram-v2
 [*] --> Pendiente
 Pendiente --> EnProceso: Respuesta
 EnProceso --> Pendiente: Revisión
 Pendiente --> Resuelta: Solución
 EnProceso --> Resuelta: Solución
 Resuelta --> [*]
```

Las rutas, reglas y campos se detallan en `app.py`, `schema.sql` y `modelo de datos.md`.
