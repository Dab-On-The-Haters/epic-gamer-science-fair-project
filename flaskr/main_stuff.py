#!/usr/bin/python3.7
"""
Hi fellow epic gamers,
this will be the main WEB server script. it handles all the requests from the site.
It isn't the WSGI though, that'll be in a separate file, probs one located wherever on the machine
we choose to host the file on.

For the long term, please don't use this to host static files
(but it's fine temporarily)
we can do that on Apache2 more efficiently.

FLASK DOCUMENTATION IS AT https://flask.palletsprojects.com/en/1.1.x/ YOU'LL WANT IT
"""


# import all the flask stuff we'll be needing
from flask import Flask, escape, request, redirect, render_template, send_file, send_from_directory, flash # etc...
# initialize flask as "app". this matters not just for literally everything but for the WSGI as well
app = Flask(__name__)

# login tracking stuff, I both hate and love Todd Birchard
from flask_login import LoginManager login_required, current_user, login_user, logout_user, UserMixin
login_manager = LoginManager()

#import super secure stuff (passwords stored in json)
import json
with open('/home/yeem/private_stuff.json') as f:
    passwords = json.load(f)


#import mail stuff (pip3 install flask-mail)
from flask_mail import Mail, Message
mail = Mail(app)
# configure it to work with thse
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'joethernn@gmail.com'
app.config['MAIL_PASSWORD'] = passwords['JOE_MAIL_PASSWORD']
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

# import MySQL (pip3 install flask-mysql)
from flaskext.mysql import MySQL
mariadb = MySQL()
# configure it to work with the database
app.config['MYSQL_DATABASE_USER'] = 'FAIRY' # lol cuz it's a science fair get it
app.config['MYSQL_DATABASE_PASSWORD'] = passwords['FAIRY_PASSWORD'] # todo: make sure fairy has proper permissions
app.config['MYSQL_DATABASE_DB'] = 'SCIENCE_FAIR'
app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
mariadb.init_app(app)

connDB = mariadb.connect()
curDB = connDB.cursor()

# start login manager
login_manager.init_app(app)

# dumb classes just for flask-login
class User():
    username = str()
    name = str()
    ID = int()
    email = str()
    is_anonymous = False # duh
    is_authenticated = True
    is_active = True

    def setValues(self, fieldName, fieldRequest):
        if not curDB.execute('SELECT verified, ID, username, email, name, self_description FROM users WHERE '+fieldName+'=%s LIMIT 1;', fieldRequest)
            self.ID = 0 # wow i'm such a good person
            self.is_anonymous = True
            self.is_authenticated = False
            self.is_active = False
            self.username = ''
            self.name = 'Anonymous User'
        
        else:
            self.is_anonymous = False
            
            QA = curDB.fetchone()
            self.is_active = QA['verified']
            self.is_authenticated = QA['verified']
            self.ID = QA['ID']
            self.username = QA['username']
            self.email = QA['email']
            self.name = QA['name']
            self.description = QA['self_description']


    def get_id()
        return unicode(ID)

#WTForm stuff
from flask_wtf import FlaskForm
from wtforms import ValidationError
import wtforms.fields as f
import wtforms.fields.html5 as f5
import wtforms.validators as v
import string

urlValidChars = string.ascii_letters + string.digits + '._-+'

# message for InputRequired
r = lambda fieldValue : 'Please enter your ' + fieldValue

class registerForm(FlaskForm):
    # for checking if password is varied enough
    def PasswordCheck(form, field):
        pswSet = set(field.data)
        if not (pswSet.intersection(set(string.digits)) and pswSet.intersection(set(string.ascii_uppercase)) and pswSet.intersection(set(string.ascii_lowercase))):
            raise ValidationError('Password is not varied enough. Try mixing cases and adding numbers.')
    # for checking if email is taken
    def emailTakenCheck(form, field):
        curDB.execute('SELECT verified FROM users WHERE email_addr=%s;', (field.data))
        for verification in curDB.fetchall():
            if verification['verified']:
                raise ValidationError('An account with that email address is already verified')
    # for checking if username is taken
    def usernameTakenCheck(form, field):
        curDB.execute('SELECT verified FROM users WHERE username=%s;', (field.data))
        for verification in curDB.fetchall():
            if verification['verified']:
                raise ValidationError('The username "'+field.data+'" is taken')
    # for checking if username is wack
    def usernameStuffCheck(form, field):
        for char in field.data:
            if char not in urlValidChars:
                raise ValidationError('Usernames can only contain letters, numbers, and the symbols . _ - +')


    email = f5.EmailField('Email address', [v.InputRequired(message=r('email address')), v.Email(message='Must be a valid email address'), v.Length(min=5, max=250, message='Must be a complete email address'), emailTakenCheck])
    name = f.StringField('Name', [v.InputRequired(message=r('name')), v.Length(min=2, max=250, message=r('name'))])
    username = f.StringField('Username', [v.InputRequired(message=r('username')), v.Length(min=5, max=250, message='Username must be between 5 and 250 characters long'), usernameTakenCheck, usernameStuffCheck])
    password = f.PasswordField('Password', [v.InputRequired(message=r('password')), v.Length(min=8, max=250, message='Password must be at least 8 characters long'), PasswordCheck])
    confirm = f.PasswordField('Confirm password', [v.InputRequired(message=r('password confirmation')), v.EqualTo('password', message='Confirmation password does not match')])

class verifyForm(FlaskForm):
    verifyAccountID = int()
    def verificationCodeCheck(form, field):
        curDB.execute('SELECT codeNumber FROM verification_codes WHERE accountID=%s LIMIT 1;', (field.data))
        codeNumber = curDB.fetchone()
        if codeNumber['codeNumber'] != int(field.data):
            raise ValidationError('Incorrect verification code. Try redoing the register form if you think you might have made a typo over there.')
    verificationCode = f.IntegerField('Verification code', [v.InputRequired(message=r("4-digit verification code. You should have received it via email. If it's been a while and you still haven't gotten it, please fill out the register form again in case you mistyped it.")), verificationCodeCheck]) 

class loginForm(FlaskForm):
    def checkLoginValidity()

@login_manager.user_loader
def load_user(ID)
    user = User()
    user.setValues('ID', int(ID))
    return user

@app.route('/')
def showHomepage():
    # todo in future (not this line tho): avoid send_file (use send_from_directory) in most scenarios! Don't do this! Security risks!
    return send_file('static/homepage.html', mimetype='text/html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(request.args.get('continue', '/'))

    LF = loginForm()
    if LF.validate_on_submit():
        user = User()

        user.setValues('username', LF.username.data)
        user.savetoDB()
        login_user(user, remember=True, force=True)
        
        return redirect(request.args.get('continue', '/'))
    return render_template('login.html', form=LF)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(request.args.get('continue', '/'))

@app.route('/verify/<int:ID>', methods=['GET', 'POST'])
def verifyUser(ID):
    VF = verifyForm()
    VF.verifyAccountID = ID

    if VF.validate_on_submit():
        # verify the user in the DB
        curDB.execute('UPDATE users SET verified=1 WHERE ID=%s;', (ID))
        # delete the verification code, we don't need it anymore
        curDB.execute('DELETE FROM verification_codes WHERE accountID=%s;', (ID))
        connDB.commit()
        return redirect('/')
    return render_template('verify-email.html', form=VF)


# for generating verification codes
from random import randint

# message for verifying email
verifyMsg = Message('Verify your email to talk to Joe!', sender='joethernn@gmail.com')

@app.route('/register', methods=['GET', 'POST'])
def registerUser():
    RF = registerForm()
    if RF.validate_on_submit():
        
        # add the user to DB
        curDB.execute('INSERT INTO users (email_addr, own_password, username, real_name) VALUES (%s, %s, %s, %s);',
            (RF.email.data, RF.password.data, RF.username.data, RF.name.data))
        connDB.commit()

        # get the user's ID
        curDB.execute('SELECT ID FROM users WHERE email_addr=%s LIMIT 1;', (RF.email.data))
        accountID = curDB.fetchone()
        accountID = accountID['ID']

        #add the verification code to DB
        verificationCode = randint(1000,9999)
        curDB.execute('INSERT INTO verification_codes (codeNumber, accountID) VALUES (%s, %s);',
            (verificationCode, accountID))
        connDB.commit()

        # send the verification message
        verifyMsg.recipients = [RF.email.data]
        verifyMsg.body = 'Hi '+RF.name.data+', use the code '+str(verificationCode)+' to verify your email address and get your account with Joe up and running.\nIf you don\'t know about the amazing Joe project, then just ignore this email. Thanks!'
        with app.app_context(): mail.send(verifyMsg)

        return redirect('/verify/'+accountID)

    return render_template('register.html', form=RF)
