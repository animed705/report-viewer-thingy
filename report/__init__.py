
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect



app = Flask(__name__)

app.secret_key  = "key_whatever"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
app.config["WTF_CSRF_ENABLED"] = True
db = SQLAlchemy(app)

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
from report import routes