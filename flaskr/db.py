# flask-tiny-app/flaskr/db.py
import sqlite3
from datetime import datetime
import click
from flask import current_app, g
from werkzeug.security import generate_password_hash  # Thêm dòng này

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

# flask-tiny-app/flaskr/db.py
def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

    # Tạo tài khoản admin mặc định nếu chưa có
    admin_user = db.execute('SELECT * FROM user WHERE username = ?', ('admin',)).fetchone()
    if admin_user is None:
        db.execute(
            "INSERT INTO user (username, password, is_admin) VALUES (?, ?, ?)",
            ('admin', generate_password_hash('trungtada123'), 1)  # Mật khẩu mặc định là trungtada123123
        )
        db.commit()

@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

sqlite3.register_converter(
    "timestamp", lambda v: datetime.fromisoformat(v.decode())
)

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)