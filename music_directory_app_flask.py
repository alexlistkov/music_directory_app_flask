import sqlite3

import os
from functools import wraps

from flask import Flask, render_template, flash, redirect, url_for, session, logging, request, g
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt

app = Flask(__name__)


# Config SQLite
def connect_db():
    conn = sqlite3.connect(os.path.join(app.root_path, 'db.sqlite'))
    conn.row_factory = sqlite3.Row
    return conn


def get_db():
    if not hasattr(g, 'db'):
        g.db = connect_db()
    return g.db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Please login!', 'danger')
            return redirect(url_for('login'))
    return wrap

@app.route('/')
@is_logged_in
def index():
    # db = get_db()
    # cursor = db.execute()
    return render_template('index.html')


@app.route('/<int:id>/')
@is_logged_in
def details(id):
    return render_template('details.html', id=id())


class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        with get_db() as db:
            if email in [i['email'] for i in db.execute('SELECT * FROM users')]:
                flash('This email has already registered!', 'error')
                redirect(url_for('register'))
            else:
                db.execute('INSERT INTO users(email, username, password) VALUES (?, ?, ?)', (email, username, password))
                flash('You are now registered and can login!', 'success')
                return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password_candidate = request.form['password']

        with get_db() as db:
            result = db.execute('SELECT * FROM users WHERE email = ?', (email,))
            data = result.fetchone()
            if data:
                password = data['password']
                username = data['username']

                if sha256_crypt.verify(password_candidate, password):
                    session['logged_in'] = True
                    session['email'] = email
                    session['username'] = username
                    flash('You are successfully logged in!', 'success')
                    return redirect(url_for('index'))
                else:
                    error = 'Invalid password or login!'
                    return render_template('login.html', error=error)
            else:
                error = 'Email not found!'
                return render_template('login.html', error = error)

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out!', 'success')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.secret_key = 'SECRET_KEY123321'
    app.run(debug=True)
