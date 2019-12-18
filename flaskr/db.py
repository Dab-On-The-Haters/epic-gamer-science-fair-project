import mysql.connector as mariadb
import json
with open("/home/thomas/.private-stuff.json") as f:
  psw = json.load(f)["FAIRY_PASSWORD"]

conn = mariadb.connect(host="172.0.0.1", user="FAIRY", password=psw, database="SCIENCE_FAIR")
cur = mariadb.cursor(dictionary=True) # maybe prepared=True in the future?


# to be exec. in files running this module conn.close()
