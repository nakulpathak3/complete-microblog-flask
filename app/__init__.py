from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config') #The app's configuration should be imported from the object 'config'
db = SQLAlchemy(app)

from app import views, models