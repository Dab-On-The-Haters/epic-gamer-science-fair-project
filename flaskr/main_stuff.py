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
from flask import Flask, escape, request, render_template, send_file, send_from_directory # etc...

"""
# import MySQL stuff (requires installation from PIP)
from flaskext.mysql import MySQL
mariadb = MySQL()
"""

# initialize flask as "app". this matters not just for literally everything but for the WSGI as well
app = Flask(__name__)
"""
# configure it to work with the database
app.config['MYSQL_DATABASE_USER'] = 'FAIRY' # lol cuz it's a science fair get it
app.config['MYSQL_DATABASE_PASSWORD'] = '123456789' # todo: make sure fairy has proper permissions
app.config['MYSQL_DATABASE_DB'] = 'SCIENCE_FAIR'
app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
mariadb.init_app(app)
"""

@app.route('/')
def showHomepage():
    # todo in future (not this line tho): avoid send_file (use send_from_directory) in most scenarios! Don't do this! Security risks!
    return send_file('static/homepage.html', mimetype='text/html')