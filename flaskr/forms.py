"""
WTForms:

Amazing for backend,
Annoying for frontend,
Nightmare for sleep.
"""

from flask_wtf import FlaskForm
from wtforms import ValidationError
import wtforms.fields as f
import wtforms.fields.html5 as f5
import wtforms.validators as v
import string

r = lambda d : 'Please enter your ' + d

class register(FlaskForm):
    def PasswordCheck(form, field):
        pswSet = set(field.data)
        if not (pswSet.intersection(set(string.digits)) and pswSet.intersection(set(string.ascii_uppercase)) and pswSet.intersection(set(string.ascii_lowercase))):
            raise ValidationError('Password is not varied enough. Try mixing cases and adding numbers.')
    
    email = f5.EmailField('Email address', [v.InputRequired(message=r('email address')), v.Email(message='Must be a valid email address'), v.Length(min=5, max=250, message='Must be a complete email address')])
    name = f.StringField('Name', [v.InputRequired(message=r('name')), v.Length(min=5, max=250, message=r('name'))])
    username = f.StringField('Username', [v.InputRequired(message=r('username')), v.Length(min=5, max=250, message='Username must be between 5 and 250 characters long')])
    password = f.PasswordField('Password', [v.InputRequired(message=r('password')), v.Length(min=8, max=250, message='Password must be at least 8 characters long'), PasswordCheck])
    confirm = f.PasswordField('Confirm password', [v.InputRequired(message=r('password confirmation')), v.EqualTo('confirm', message='Confirmation password does not match')])

"""
class verify_email(FlaskForm):
    def verification_code_check"""