"""Portal universitario: solicitudes, respuestas y reporte mensual con SQLite."""
import csv
import io
import os
import re
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from functools import wraps
from pathlib import Path

import click
from flask import Flask, Response, abort, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

BASE = Path(__file__).resolve().parent
CATEGORIES = ('Consulta', 'Reclamo', 'Soporte', 'Sugerencia')
STATES = ('Pendiente', 'En proceso', 'Resuelta')
LOCAL = timezone(timedelta(hours=-5))


def now():
    return datetime.now(LOCAL).isoformat(timespec='seconds')


def get_db():
    if 'db' not in g:
        from flask import current_app
        g.db = sqlite3.connect(current_app.config['DATABASE'], timeout=10)
        g.db.row_factory = sqlite3.Row
        g.db.execute('PRAGMA foreign_keys=ON')
    return g.db


def monthly_report(db, month):
    if not re.fullmatch(r'\d{4}-(0[1-9]|1[0-2])', month) or month[:4] == '0000':
        raise ValueError('El mes debe tener formato AAAA-MM válido.')
    rows = db.execute('SELECT * FROM tickets WHERE substr(created_at,1,7)=?', (month,)).fetchall()
    counts = {state: sum(t['status'] == state for t in rows) for state in STATES}
    categories = {cat: sum(t['category'] == cat for t in rows) for cat in CATEGORIES}
    hours = [(datetime.fromisoformat(t['resolved_at']) - datetime.fromisoformat(t['created_at'])).total_seconds()/3600
             for t in rows if t['status'] == 'Resuelta' and t['resolved_at']]
    total = len(rows)
    return dict(month=month, total=total, counts=counts, categories=categories,
                percentage=round(100*counts['Resuelta']/total, 1) if total else 0,
                average=round(sum(hours)/len(hours), 2) if hours else None, generated=now())


def create_app(config=None):
    app = Flask(__name__, instance_path=str(BASE / 'instance'))
    app.config.update(DATABASE=str(BASE / 'instance' / 'portal.sqlite3'),
                      SECRET_KEY=os.environ.get('SECRET_KEY') or secrets.token_hex(32),
                      MAX_CONTENT_LENGTH=64*1024, SESSION_COOKIE_HTTPONLY=True,
                      SESSION_COOKIE_SAMESITE='Lax', SESSION_COOKIE_SECURE=os.environ.get('COOKIE_SECURE') == '1',
                      PERMANENT_SESSION_LIFETIME=timedelta(minutes=30))
    if config:
        app.config.update(config)
    Path(app.config['DATABASE']).parent.mkdir(parents=True, exist_ok=True)
    with app.app_context():
        get_db().executescript((BASE / 'schema.sql').read_text(encoding='utf-8'))
        g.pop('db').close()

    @app.teardown_appcontext
    def close_db(error=None):
        db = g.pop('db', None)
        if db is not None:
            db.close()

    @app.before_request
    def security():
        g.user = get_db().execute('SELECT * FROM users WHERE id=?', (session.get('uid'),)).fetchone()
        if 'csrf' not in session:
            session['csrf'] = secrets.token_hex(24)
        if request.method == 'POST' and not secrets.compare_digest(session['csrf'], request.form.get('csrf', '')):
            abort(400, 'Formulario vencido. Recarga la página e inténtalo otra vez.')

    @app.after_request
    def headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Cache-Control'] = 'no-store'
        response.headers['Content-Security-Policy'] = "default-src 'self'; style-src 'self'; form-action 'self'; frame-ancestors 'none'"
        return response

    def login_required(admin=False):
        def decorate(fn):
            @wraps(fn)
            def wrapped(*args, **kwargs):
                if not g.user:
                    return redirect(url_for('login'))
                if admin and g.user['role'] != 'admin':
                    abort(403)
                return fn(*args, **kwargs)
            return wrapped
        return decorate

    @app.context_processor
    def context():
        return dict(categories=CATEGORIES, states=STATES)

    @app.route('/')
    def index():
        return render_template('home.html')

    @app.route('/registro', methods=['GET','POST'])
    def register():
        if request.method == 'POST':
            name = request.form.get('name','').strip()
            email = request.form.get('email','').strip().lower()
            password = request.form.get('password','')
            if not (2 <= len(name) <= 80 and len(email) <= 120 and re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email) and 8 <= len(password) <= 128):
                flash('Revisa nombre, correo y contraseña (8 a 128 caracteres).')
                return render_template('auth.html', register=True), 400
            try:
                db = get_db()
                db.execute('INSERT INTO users(name,email,password_hash) VALUES(?,?,?)', (name,email,generate_password_hash(password)))
                db.commit()
            except sqlite3.IntegrityError:
                flash('No se pudo crear la cuenta. Revisa los datos o inicia sesión.')
                return render_template('auth.html', register=True), 400
            flash('Cuenta creada. Ya puedes iniciar sesión.')
            return redirect(url_for('login'))
        return render_template('auth.html', register=True)

    @app.route('/ingresar', methods=['GET','POST'])
    def login():
        if request.method == 'POST':
            user = get_db().execute('SELECT * FROM users WHERE email=?', (request.form.get('email','').strip().lower(),)).fetchone()
            if user and check_password_hash(user['password_hash'], request.form.get('password','')):
                session.clear()
                session['uid'] = user['id']
                session['csrf'] = secrets.token_hex(24)
                session.permanent = True
                return redirect(url_for('tickets'))
            flash('Correo o contraseña incorrectos.')
            return render_template('auth.html', register=False), 400
        return render_template('auth.html', register=False)

    @app.post('/salir')
    def logout():
        session.clear()
        return redirect(url_for('index'))

    @app.get('/solicitudes')
    @login_required()
    def tickets():
        state = request.args.get('estado','')
        if state and state not in STATES:
            abort(400)
        query, params = 'SELECT tickets.*, users.name FROM tickets JOIN users ON users.id=tickets.user_id WHERE 1=1', []
        if g.user['role'] != 'admin':
            query += ' AND user_id=?'
            params.append(g.user['id'])
        if state:
            query += ' AND status=?'
            params.append(state)
        rows = get_db().execute(query+' ORDER BY tickets.id DESC', params).fetchall()
        return render_template('tickets.html', tickets=rows, selected=state)

    @app.route('/solicitudes/nueva', methods=['GET','POST'])
    @login_required()
    def new_ticket():
        if g.user['role'] != 'cliente':
            abort(403)
        if request.method == 'POST':
            subject = request.form.get('subject','').strip()
            category = request.form.get('category','')
            description = request.form.get('description','').strip()
            if not (3 <= len(subject) <= 120 and category in CATEGORIES and 10 <= len(description) <= 3000):
                flash('Revisa asunto (3–120), categoría y descripción (10–3000 caracteres).')
                return render_template('new.html'), 400
            db = get_db()
            cursor = db.execute('INSERT INTO tickets(user_id,subject,category,description,created_at) VALUES(?,?,?,?,?)',
                                (g.user['id'],subject,category,description,now()))
            db.commit()
            flash('Solicitud recibida. Conservamos tu radicado y puedes consultar su estado.')
            return redirect(url_for('detail', ticket_id=cursor.lastrowid))
        return render_template('new.html')

    @app.route('/solicitudes/<int:ticket_id>', methods=['GET','POST'])
    @login_required()
    def detail(ticket_id):
        db = get_db()
        ticket = db.execute('SELECT * FROM tickets WHERE id=?', (ticket_id,)).fetchone()
        if not ticket or (g.user['role'] != 'admin' and ticket['user_id'] != g.user['id']):
            abort(404)
        if request.method == 'POST':
            if g.user['role'] != 'admin':
                abort(403)
            body, status = request.form.get('body','').strip(), request.form.get('status','')
            if not (3 <= len(body) <= 3000 and status in STATES):
                abort(400, 'La respuesta debe tener entre 3 y 3000 caracteres y un estado válido.')
            if ticket['status'] == 'Resuelta':
                abort(400, 'Una solicitud resuelta conserva su historial y no se modifica.')
            stamp = now()
            with db:
                db.execute('INSERT INTO responses(ticket_id,user_id,body,status,created_at) VALUES(?,?,?,?,?)', (ticket_id,g.user['id'],body,status,stamp))
                db.execute('UPDATE tickets SET status=?, resolved_at=? WHERE id=?', (status,stamp if status=='Resuelta' else None,ticket_id))
            flash('Respuesta y estado guardados.')
            return redirect(url_for('detail',ticket_id=ticket_id))
        responses = db.execute('SELECT responses.*, users.name FROM responses JOIN users ON users.id=responses.user_id WHERE ticket_id=? ORDER BY responses.id', (ticket_id,)).fetchall()
        return render_template('detail.html', ticket=ticket, responses=responses)

    @app.get('/reportes')
    @login_required(admin=True)
    def report():
        month = request.args.get('mes',now()[:7])
        try:
            data = monthly_report(get_db(),month)
        except ValueError as error:
            abort(400,str(error))
        if request.args.get('formato') == 'csv':
            output = io.StringIO(newline='')
            writer = csv.writer(output)
            writer.writerow(['Mes','Indicador','Valor'])
            for key, value in [('Total recibidas', data['total']), *data['counts'].items(), *data['categories'].items(),
                               ('Porcentaje resuelto', data['percentage']), ('Promedio horas resolución', data['average'] if data['average'] is not None else 'Sin datos')]:
                writer.writerow([month,key,value])
            return Response('\ufeff'+output.getvalue(), mimetype='text/csv', headers={'Content-Disposition': f'attachment; filename="reporte-{month}.csv"'})
        return render_template('report.html', report=data)

    @app.errorhandler(400)
    @app.errorhandler(403)
    @app.errorhandler(404)
    @app.errorhandler(413)
    def error_page(error):
        return render_template('error.html', error=error), error.code

    @app.cli.command('crear-admin')
    @click.option('--nombre', prompt=True)
    @click.option('--correo', prompt=True)
    @click.password_option(confirmation_prompt=True)
    def create_admin(nombre, correo, password):
        """Crear administrador desde consola; nunca desde el registro público."""
        if len(password) < 8:
            raise click.ClickException('Usa al menos 8 caracteres.')
        try:
            db = get_db()
            db.execute('INSERT INTO users(name,email,password_hash,role) VALUES(?,?,?,?)', (nombre.strip(),correo.strip().lower(),generate_password_hash(password),'admin'))
            db.commit()
        except sqlite3.IntegrityError:
            raise click.ClickException('El correo ya existe.')
        click.echo('Administrador creado.')

    return app


if __name__ == '__main__':
    create_app().run(host='127.0.0.1', port=5000, debug=False)
