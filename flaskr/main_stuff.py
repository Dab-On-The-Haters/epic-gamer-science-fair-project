#/usr/bin/python3.7
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


#import super secure stuff (passwords stored in json)
import json
with open('/home/yeem/private_stuff.json') as f:
    passwords = json.load(f)


#import form stuff
import forms

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

from random import randint # for generating verification codes

@app.route('/')
def showHomepage():
    # todo in future (not this line tho): avoid send_file (use send_from_directory) in most scenarios! Don't do this! Security risks!
    return send_file('static/homepage.html', mimetype='text/html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    return 'boi'
    #form = LoginForm()

# message for verifying email
verifyMsg = Message('Verify your email to talk to Joe!', sender='joethernn@gmail.com')

@app.route('/register', methods=['GET', 'POST'])
def registerUser():
    RF = forms.register()
    if RF.validate_on_submit():
        
        # add the user to DB
        curDB.execute('INSERT INTO users (email_addr, own_password, username, real_name) VALUES (%s, %s, %s, %s);',
            (RF.email.data, RF.password.data, RF.username.data, RF.name.data))
        connDB.commit()

        # get the user's ID
        curDB.execute('SELECT ID FROM users WHERE email_addr=%s LIMIT 1;', (RF.email.data))
        accountID = curDB.fetchone().get('ID')
        
        #add the verification code to DB
        verificationCode = randint(1000,9999)
        curDB.execute('INSERT INTO verification_codes (codeNumber, accountID) VALUES (%i, %i);',
            (verificationCode, accountID))
        connDB.commit()

        # send the verification message
        verifyMsg.recipients = [RF.email.data]
        verifyMsg.body = 'Hi '+RF.name.data+', use the code '+str(verificationCode)+' to verify your email address and get your account with Joe up and running.\nIf you don\'t know about the amazing Joe project, then just ignore this email. Thanks!'
        with app.app_context(): verifyMsg.send()

        return render_template('verify-email.html')

    return render_template('register.html', form=RF)
