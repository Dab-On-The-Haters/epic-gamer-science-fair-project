"""
WTForms:

Amazing for backend,
Annoying for frontend,
Nightmare for sleep.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField
import wtforms.validators as v

r = lambda d : 'Please enter your ' + d

class register(FlaskForm):
    email = EmailField('Email address', [v.InputRequired(message=r('email address')), v.Email(message='Must be a valid email address')), v.Length(min='5', max='250', message='Must be a complete email address')])
    name = StringField('Name', [v.InputRequired(message=r('name')), v.Length(min='5', max='250', message=r('name'))])
    username = StringField('Username', [v.InputRequired(message=r('username')), v.Length(min='5', max='250', message='Username must be between 5 and 250 characters long')])
    password = PasswordField('Password', [v.InputRequired(message=r('password')), v.Length(min='8', max='250', message='Password must be at least 8 characters long'), v.EqualTo('confirm', message='Confirmation password does not match')])
    confirm = PasswordField('Confirm password')