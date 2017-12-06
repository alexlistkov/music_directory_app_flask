import sqlite3

import os
from functools import wraps

from flask import Flask, render_template, flash, redirect, url_for, session, logging, request, g, abort
import forms
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
    db = get_db()
    cursor = db.execute('SELECT * FROM music WHERE user_id = ?', (session['id'],))
    musics = cursor.fetchall()
    music_form = forms.MusicForm(request.form)
    return render_template('index.html', musics=musics, music_form=music_form)


@app.route('/post_music', methods=['POST'])
@is_logged_in
def post_music():
    music_form = forms.MusicForm(request.form)
    if music_form.validate():
        title = music_form.title.data
        artist = music_form.artist.data
        genre = music_form.genre.data
        album = music_form.album.data
        year = music_form.year.data
        cover = music_form.cover.data
        user = session['id']

        with get_db() as db:
            db.execute('INSERT INTO music(title, artist, genre, album, year, cover, user_id)'
                       'VALUES (?, ?, ?, ?, ?, ?, ?)', (title, artist, genre, album, year, cover, user))

        flash('Music created!', 'success')

    else:
        flash('Enter form correctly!', 'error')
    return redirect(url_for('index'))


@app.route('/<int:id>/', methods=['GET', 'POST'])
@is_logged_in
def details(id):
    db = get_db()
    cursor = db.execute('SELECT * FROM music WHERE id = ?', (id,))
    music = cursor.fetchone()

    music_form = forms.MusicForm(request.form)
    music_form.title.data = music['title']
    music_form.album.data = music['album']
    music_form.genre.data = music['genre']
    music_form.artist.data = music['artist']
    music_form.year.data = music['year']
    music_form.cover.data = music['cover']

    music_additional_form = forms.MusicAdditionalForm(request.form)
    music_additional_form.lyrics.data = music['lyrics']
    music_additional_form.video.data = music['video']

    if session['id'] == music['user_id']:
        if request.method == 'POST':
            if music_form.validate():
                title = request.form['title']
                artist = request.form['artist']
                genre = request.form['genre']
                album = request.form['album']
                year = request.form['year']
                cover = request.form['cover']
                with get_db() as db:
                    db.execute('UPDATE music SET title = ?, artist = ?, genre = ?, album = ?, year = ?, cover = ?'
                               'WHERE id = ?', (title, artist, genre, album, year, cover, id))

            elif music_additional_form.validate():
                lyrics = request.form['lyrics']
                video = request.form['video'].replace("watch?v=", "embed/")
                with get_db() as db:
                    db.execute('UPDATE music SET lyrics = ?, video = ? WHERE id =?', (lyrics, video, id))

            return redirect(url_for('details', id=id))

    else:
        abort(404)

    return render_template('details.html', music=music, music_additional_form=music_additional_form,
                           music_form=music_form)


# @app.route('/delete/int:id/', me)
# def delete_music(id):
#     pass


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = forms.RegistrationForm(request.form)
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
                id = data['id']

                if sha256_crypt.verify(password_candidate, password):
                    session['logged_in'] = True
                    session['email'] = email
                    session['username'] = username
                    session['id'] = id
                    flash('You are successfully logged in!', 'success')
                    return redirect(url_for('index'))
                else:
                    error = 'Invalid password or login!'
                    return render_template('login.html', error=error)
            else:
                error = 'Email not found!'
                return render_template('login.html', error=error)

    return render_template('login.html')


@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out!', 'success')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.secret_key = '\x1c\x10d\xad\xb5\xc2\xa1\xce\xdb1.\xefF\x1f\xdbMv\xea1\xe8 m\x10{'
    app.run(debug=True)
