from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
app=Flask(__name__) 
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///site.db'
app.config['SECRET_KEY']='a865aa459375b1219bfb7252'
db=SQLAlchemy(app)
bcrypt=Bcrypt(app)
login_manager=LoginManager(app)
login_manager.login_view="login_page"
login_manager.login_message_category="info"
from inizio import routes