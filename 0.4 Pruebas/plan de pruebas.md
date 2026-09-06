# Plan de pruebas

Las pruebas usan bases SQLite temporales y datos ficticios. Se ejecutan desde `0.3 Desarrollo`:

```powershell
.\\.venv\\Scripts\\python.exe "../0.4 Pruebas/test_portal.py"
```

Se cubren registro, duplicados, hash, login/logout, persistencia, validación, aislamiento entre clientes, permisos de reporte, respuesta y cierre, cálculos de meses y horas, CSV, CSRF, escape HTML/SQL, filtros, páginas básicas y respaldo restaurable.

La ejecución local no mide carga concurrente, disponibilidad mensual, compatibilidad completa de navegadores ni HTTPS. Esas comprobaciones quedan para un servidor de prueba.
