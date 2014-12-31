from flask import Flask

app = Flask(__name__)
app.config.from_object('config') #The app's configuration should be imported from the object 'config'
from app import views