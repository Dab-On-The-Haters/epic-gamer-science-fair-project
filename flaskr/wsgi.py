from main_stuff import app
import json

app.secret_key = json.loads('/home/thomas/.private-stuff.json')['SECRET_KEY']
if __name__ == "__main__":
    app.run()