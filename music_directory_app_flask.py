import os
from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
import sqlite3
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt

app = Flask(__name__)


# Config SQLite
def connect_db():
    conn  = sqlite3.connect(os.path.join(app.root_path, 'db.sqlite'))


@app.route('/')
def index():
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
        # user = User(form.username.data, form.email.data,
        #             form.password.data)
        # db_session.add(user)
        # flash('Thanks for registering')
        # return redirect(url_for('login'))
        return render_template('register.html')
    return render_template('register.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
