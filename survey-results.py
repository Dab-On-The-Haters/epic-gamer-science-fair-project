import flaskr.db as db
import csv

db.cur.execute('DESC survey;')
fieldnames = [field['Field'] for field in db.cur.fetchall()]

with open('/home/thomas/Documents/survey-results.csv', 'w', newline='') as f:
    csvf = csv.DictWriter(f, fieldnames=fieldnames)
    csvf.writeheader()

    db.cur.execute('SELECT * FROM survey;')
    csvf.writerows(db.cur.fetchall())

db.cur.close()
db.conn.close()
