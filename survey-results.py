#!/usr/bin/python3
import flaskr.db as db
import csv


with open('/home/thomas/Documents/survey-results.csv', 'w', newline='') as f:
    db.cur.execute('DESC survey;')
    csvf = csv.DictWriter(f, fieldnames=[field['Field'] for field in db.cur.fetchall()])
    csvf.writeheader()

    db.cur.execute('SELECT * FROM survey;')
    csvf.writerows(db.cur.fetchall())

db.cur.close()
db.conn.close()
