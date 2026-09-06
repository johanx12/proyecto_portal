"""Pruebas pequeñas y repetibles, con SQLite temporal y datos ficticios."""
import csv
import io
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '0.3 Desarrollo'))
from app import create_app, get_db, monthly_report
from werkzeug.security import generate_password_hash

class PortalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = str(Path(self.tmp.name)/'test.sqlite3')
        self.app = create_app({'TESTING':True,'DATABASE':self.db_path,'SECRET_KEY':'solo-pruebas'})
        self.client = self.app.test_client()
        with self.app.app_context():
            db=get_db()
            for name,role in [('Ana','cliente'),('Luis','cliente'),('Admin','admin')]:
                db.execute('INSERT INTO users(name,email,password_hash,role) VALUES(?,?,?,?)',(name,name.lower()+'@example.test',generate_password_hash('Prueba123!'),role))
            db.commit()
    def tearDown(self):
        with self.app.app_context():
            db = get_db()
            db.close()
            from flask import g
            g.pop('db', None)
        self.tmp.cleanup()
    def post(self,url,data=None):
        self.client.get('/')
        with self.client.session_transaction() as s: token=s['csrf']
        return self.client.post(url,data={**(data or {}),'csrf':token})
    def login(self,email='ana@example.test'):
        return self.post('/ingresar',{'email':email,'password':'Prueba123!'})
    def ticket(self):
        return self.post('/solicitudes/nueva',{'subject':'No puedo ingresar','category':'Soporte','description':'Necesito ayuda para entrar a mi cuenta.'})
    def test_01_registro_y_duplicado(self):
        data={'name':'Eva','email':'eva@example.test','password':'Ejemplo123!','role':'admin'}
        self.assertEqual(self.post('/registro',data).status_code,302)
        self.assertEqual(self.post('/registro',data).status_code,400)
        with self.app.app_context():
            user=get_db().execute('SELECT * FROM users WHERE email=?',(data['email'],)).fetchone()
            self.assertEqual(user['role'],'cliente')
            self.assertNotEqual(user['password_hash'],data['password'])
    def test_02_login_logout(self):
        self.assertEqual(self.post('/ingresar',{'email':'ana@example.test','password':'incorrecta'}).status_code,400)
        self.assertEqual(self.login().status_code,302)
        self.assertEqual(self.client.get('/solicitudes').status_code,200)
        self.post('/salir')
        self.assertEqual(self.client.get('/solicitudes').status_code,302)
    def test_03_crear_y_persistir(self):
        self.login(); response=self.ticket()
        self.assertEqual(response.status_code,302)
        other=create_app({'TESTING':True,'DATABASE':self.db_path,'SECRET_KEY':'otro'})
        with other.app_context():
            ticket=get_db().execute('SELECT * FROM tickets').fetchone()
            self.assertEqual(ticket['status'],'Pendiente')
            self.assertEqual(ticket['user_id'],1)
    def test_04_validacion(self):
        self.login()
        self.assertEqual(self.post('/solicitudes/nueva',{'subject':'','category':'Otra','description':'a'}).status_code,400)
        with self.app.app_context(): self.assertEqual(get_db().execute('SELECT count(*) FROM tickets').fetchone()[0],0)
    def test_05_aislamiento(self):
        self.login(); self.ticket(); self.post('/salir'); self.login('luis@example.test')
        self.assertEqual(self.client.get('/solicitudes/1').status_code,404)
        self.assertNotIn(b'No puedo ingresar',self.client.get('/solicitudes').data)
        self.assertEqual(self.client.get('/reportes').status_code,403)
        self.assertEqual(self.client.get('/reportes?formato=csv').status_code,403)
    def test_06_responder_y_resolver(self):
        self.login(); self.ticket()
        self.assertEqual(self.post('/solicitudes/1',{'body':'Cambio','status':'Resuelta'}).status_code,403)
        self.login('admin@example.test')
        self.assertEqual(self.post('/solicitudes/1',{'body':'Estamos revisando','status':'En proceso'}).status_code,302)
        self.assertEqual(self.post('/solicitudes/1',{'body':'Solución entregada','status':'Resuelta'}).status_code,302)
        with self.app.app_context():
            ticket=get_db().execute('SELECT * FROM tickets').fetchone()
            self.assertEqual(ticket['status'],'Resuelta'); self.assertIsNotNone(ticket['resolved_at'])
            self.assertEqual(get_db().execute('SELECT count(*) FROM responses').fetchone()[0],2)
        self.login()
        self.assertIn('Solución entregada'.encode(),self.client.get('/solicitudes/1').data)
    def test_07_respuesta_invalida_y_cierre(self):
        self.login();self.ticket();self.login('admin@example.test')
        self.assertEqual(self.post('/solicitudes/1',{'body':'','status':'Resuelta'}).status_code,400)
        self.assertEqual(self.post('/solicitudes/1',{'body':'Listo','status':'Inventado'}).status_code,400)
        self.post('/solicitudes/1',{'body':'Resuelto','status':'Resuelta'})
        self.assertEqual(self.post('/solicitudes/1',{'body':'Reabrir','status':'Pendiente'}).status_code,400)
    def test_08_reporte_limites_y_totales(self):
        with self.app.app_context():
            db=get_db()
            for created,closed,state,cat in [('2026-08-01T00:00:00-05:00','2026-08-01T02:00:00-05:00','Resuelta','Soporte'),('2026-08-31T23:59:59-05:00',None,'Pendiente','Consulta'),('2026-09-01T00:00:00-05:00',None,'Pendiente','Reclamo')]:
                db.execute('INSERT INTO tickets(user_id,subject,category,description,status,created_at,resolved_at) VALUES(1,?,?,?,?,?,?)',('Caso',cat,'Descripción ficticia',state,created,closed))
            db.commit(); r=monthly_report(db,'2026-08')
            self.assertEqual(r['total'],2);self.assertEqual(r['percentage'],50)
            self.assertEqual(r['average'],2);self.assertEqual(sum(r['categories'].values()),2)
            self.assertEqual(sum(r['counts'].values()),2)
    def test_09_reporte_vacio(self):
        self.login('admin@example.test')
        self.assertIn(b'No hay solicitudes',self.client.get('/reportes?mes=2025-01').data)
        with self.app.app_context():
            r=monthly_report(get_db(),'2025-01');self.assertEqual(r['percentage'],0);self.assertIsNone(r['average'])
    def test_10_mes_invalido_y_csv(self):
        self.login('admin@example.test')
        for month in ['2026-13','2026-00','0000-01','otro']:
            self.assertEqual(self.client.get('/reportes?mes='+month).status_code,400)
        response=self.client.get('/reportes?mes=2026-08&formato=csv')
        rows=list(csv.reader(io.StringIO(response.data.decode('utf-8-sig'))))
        self.assertEqual(rows[1],['2026-08','Total recibidas','0'])
        self.assertIn('reporte-2026-08.csv',response.headers['Content-Disposition'])
    def test_11_csrf(self):
        self.client.get('/')
        self.assertEqual(self.client.post('/registro',data={'name':'Sin token'}).status_code,400)
    def test_12_escape_html_y_sql(self):
        self.login()
        self.post('/solicitudes/nueva',{'subject':"<script>alert(1)</script>",'category':'Consulta','description':"Prueba '); DROP TABLE users; --"})
        page=self.client.get('/solicitudes/1').data
        self.assertNotIn(b'<script>alert',page);self.assertIn(b'&lt;script&gt;',page)
        with self.app.app_context():self.assertEqual(get_db().execute('SELECT count(*) FROM users').fetchone()[0],3)
    def test_13_filtro_estado(self):
        self.login();self.ticket()
        self.assertIn(b'No puedo ingresar',self.client.get('/solicitudes?estado=Pendiente').data)
        self.assertNotIn(b'No puedo ingresar',self.client.get('/solicitudes?estado=Resuelta').data)
        self.assertEqual(self.client.get('/solicitudes?estado=otro').status_code,400)
    def test_14_paginas_basicas(self):
        for path in ['/','/registro','/ingresar']:
            self.assertEqual(self.client.get(path).status_code,200)
        self.login()
        self.assertEqual(self.client.get('/solicitudes/nueva').status_code,200)
        self.assertEqual(self.client.get('/solicitudes/9999').status_code,404)
    def test_15_respaldo_restaurable(self):
        import sqlite3
        self.login();self.ticket()
        with self.app.app_context():
            target=sqlite3.connect(str(Path(self.tmp.name)/'backup.sqlite3'))
            get_db().backup(target)
            self.assertEqual(target.execute('PRAGMA integrity_check').fetchone()[0],'ok')
            self.assertEqual(target.execute('SELECT count(*) FROM tickets').fetchone()[0],1)
            target.close()

if __name__=='__main__': unittest.main(verbosity=2)
