import sqlite3

import os
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


@app.route('/')
def index():
    # db = get_db()
    # cursor = db.execute()
    return render_template('index.html')


@app.route('/<int:id>/')
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
            db.execute('INSERT INTO users(email, username, password) VALUES (?, ?, ?)', (email, username, password))

        # flash('You are now registered and can login!', 'success')

        return redirect(url_for('index'))
    return render_template('register.html', form=form)


if __name__ == '__main__':
    app.secret_key = 'SECRET_KEY123321'
    app.run(debug=True)