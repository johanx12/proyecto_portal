"""Copia consistente de la base SQLite del prototipo."""
import sqlite3
from datetime import datetime
from pathlib import Path

root = Path(__file__).resolve().parents[1]
source = root / '0.3 Desarrollo' / 'instance' / 'portal.sqlite3'
if not source.exists():
    raise SystemExit('Primero inicia la aplicación para crear la base.')
folder = root / 'backups'
folder.mkdir(exist_ok=True)
target = folder / ('portal-' + datetime.now().strftime('%Y%m%d-%H%M%S-%f') + '.sqlite3')
src = sqlite3.connect(source)
dst = sqlite3.connect(target)
try:
    src.backup(dst)
    if dst.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
        raise SystemExit('La comprobación de integridad falló.')
finally:
    dst.close()
    src.close()
print('Respaldo creado:', target)
