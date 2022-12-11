from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@localhost:5432/flasksql'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = 'a325eecd6eef2e537373f5b0a1ca7ed97f55c235a297060b'
app.config['SECRET_KEY'] = 'secret!'
app.config['CACHE_TYPE'] = 'SimpleCache'
app.config['CACHE_DEFAULT_TIMEOUT'] = 10000000000


db = SQLAlchemy(app, )
CORS(app)
cache = Cache(app)
socketio = SocketIO(app, cors_allowed_origins="*")

from app import routes, models