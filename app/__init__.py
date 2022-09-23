from flask import Flask, g
from config import Config
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
import sqlite3
import os

from flask_recaptcha import ReCaptcha

# create and configure app
app = Flask(__name__)
Bootstrap(app)
app.config.from_object(Config)

# TODO: Handle login management better, maybe with flask_login?
login_manager = LoginManager(app)
login_manager.login_message = "Please log in."
# login_manager = LoginManager()
# login_manager.init_app(app)

class User():
    def __init__(self):
        self.id = ""
        self.username = ""
        self.f_name = ""
        self.l_name = ""
        self.password = ""
        self.employment = ""
        self.education = ""
        self.song = ""
        self.movie = ""
        self.nationality = ""
        self.birthday = ""
        self.is_active = True

    def SetUser(self, id):
        sql = query_db('SELECT * FROM Users WHERE id="{}";'.format(id), one=True)
        if sql != None:
            self.id = sql["id"]
            self.username = sql["username"]
            self.f_name = sql["first_name"]
            self.l_name = sql["last_name"]
            self.password = sql["password"] 
            self.employment = sql["employment"]
            self.education = sql["education"]
            self.music = sql["music"]
            self.movie = sql["movie"]
            self.nationality = sql["nationality"]
            self.birthday = sql["birthday"]
            self.is_active = True
    def get_id(self):
        return self.id


#app.config["user"] = User()

@login_manager.user_loader #Denne kaller vi manuelt i route, i tillegg kaller den seg selv med ID som argument automatisk når en side blir lastet på my
def load_user(id):
    user = User()
    user.SetUser(id)
    return user

app.config['RECAPTCHA_PUBLIC_KEY'] = '6Le8iA8iAAAAAPhyntZcF2vaR08uOth1Lw-j6aB6'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6Le8iA8iAAAAAF1DLx6EeX6G4jdZwZ2pbnDfJ9ZJ'
ReCaptcha(app)


# get an instance of the db
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db

# initialize db for the first time
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# perform generic query, not very secure yet
def query_db(query, one=False):
    db = get_db()
    cursor = db.execute(query)
    rv = cursor.fetchall()
    cursor.close()
    db.commit()
    return (rv[0] if rv else None) if one else rv

# TODO: Add more specific queries to simplify code

# automatically called when application is closed, and closes db connection
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# initialize db if it does not exist
if not os.path.exists(app.config['DATABASE']):
    init_db()

if not os.path.exists(app.config['UPLOAD_PATH']):
    os.mkdir(app.config['UPLOAD_PATH'])

from app import routes
