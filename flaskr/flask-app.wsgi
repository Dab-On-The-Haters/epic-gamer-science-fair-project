#!/usr/bin/python3
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/home/yeem/epic-gamer-science-fair-project/')

from main-stuff import app as application
application.secret_key = 'Add your secret key'