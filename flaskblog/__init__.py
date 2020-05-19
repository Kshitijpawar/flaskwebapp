from flask import Flask
from flask_mongoengine import MongoEngine
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import os


app = Flask(__name__)
mongodbsrv = os.environ['MYDBCONN']
app.config['SECRET_KEY'] = 'secret stuff'
app.config['MONGODB_SETTINGS'] = {
    'host': mongodbsrv
}
db = MongoEngine(app)


bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # redirect trespassers
login_manager.login_message = 'aye dipshit first log in '
login_manager.login_message_category = 'info'


from flaskblog import routes
