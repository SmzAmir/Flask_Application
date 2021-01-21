from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)  # database configuration
migrate = Migrate(app, db)  # migration instance
login = LoginManager(app)
login.login_view = 'login'  # 'login' is the name of the function that handles the user login

from app import routes, models