from flask_wtf import FlaskForm
from wtforms import TextField, PasswordField
from wtforms.validators import DataRequired, EqualTo, Length

# Forms are currently not in use

class LoginForm(FlaskForm):
    username = TextField('Username', [DataRequired()])
    password = PasswordField('Password', [DataRequired()])


class LocalData(FlaskForm):
    name = TextField(
        'Username', validators=[DataRequired(), Length(min=6, max=25)]
    )
    email = TextField(
        'Email', validators=[DataRequired(), Length(min=6, max=40)]
    )
    password = PasswordField(
        'Password', validators=[DataRequired(), Length(min=6, max=40)]
    )
    confirm = PasswordField(
        'Repeat Password',
        [DataRequired(),
        EqualTo('password', message='Passwords must match')]
    )