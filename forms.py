from wtforms import Form, StringField, IntegerField, TextAreaField, PasswordField, validators


class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')


class MusicForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=100)])
    artist = StringField('Artist', [validators.Length(min=1,max=100)])
    genre = StringField('Genre', [validators.Length(min=1,max=100)])
    album = StringField('Album', [validators.Length(min=1,max=100)])
    year = IntegerField('Year', default=0)
    cover = StringField('Cover', [validators.Length(max=100)])
    lyrics = TextAreaField('Lyrics', [validators.Length(max=10000)])
    video = StringField('Video', [validators.Length(max=100)])


# class MusicAdditionalForm(Form):
#     lyrics = TextAreaField('Lyrics', [validators.Length(max=1000)])
#     video = StringField('Video', [validators.Length(max=100)])