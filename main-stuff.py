"""
Hi fellow epic gamers,
this will be the main WEB server script. it handles all the requests from the site.
It isn't the WSGI though, that'll be in a separate file, probs one located wherever on the machine
we choose to host the file on.

For the long term, please don't use this to host static files
(but it's fine temporarily)
we can do that on Apache2 more efficiently.

FLASK DOCUMENTATION IS AT https://flask.palletsprojects.com/en/1.1.x/ YOU'LL WANT IT

Oh and Leo, there's some info on configuring git for vscode in the google doc if you want that.
actually never mind you should just go to
https://stackoverflow.com/questions/55671825/how-to-use-%D0%B0-private-repository-with-vscode
you'll find everything you need there

This file was pushed by Thomas btw
"""


#import all the flask stuff we'll be needing
from flask import Flask, escape, request, render_template # etc...


#initialize flask as "app". this matters not just for literally everything but for the WSGI as well
app = Flask(__name__)