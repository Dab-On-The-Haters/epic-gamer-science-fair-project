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

msg = Message('Joe says hi', sender='joethernn@gmail.com', recipients=['einstein.thomas2@gmail.com', 'leoawesome0201@gmail.com'])
msg.body = 'biggy brain time automated email lol'

with app.app_context():
    mail.send(msg)

@app.route('/')
def showHomepage():
    # todo in future (not this line tho): avoid send_file (use send_from_directory) in most scenarios! Don't do this! Security risks!
    return send_file('static/homepage.html', mimetype='text/html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    return 'boi'
    #form = LoginForm()



@app.route('/register', methods=['GET', 'POST'])
def registerUser():
    if request.method == 'GET':
        return send_file('static/register.html', mimetype='text/html')
    if request.method == 'POST':
        curDB.execute('INSERT INTO users (email_addr, own_password, username, name) VALUES %s %s %s %s',
            (request.form('email'), request.form('pwd'), (request.form('username'), request.form('name')))
        return 'weelll fricc yoo'
