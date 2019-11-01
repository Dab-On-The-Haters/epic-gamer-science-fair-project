#!/usr/bin/python3

"""
This script is only for the machine that actually runs the server. 
go away if you aren't running it
"""
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/home/yeem/epic-gamer-science-fair-project/flaskr/')

from main_stuff import app as application
application.secret_key = 'wow much secret'