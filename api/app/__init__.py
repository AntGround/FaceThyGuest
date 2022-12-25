from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from celery import Celery
from os.path import join
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@localhost:5432/flasksql'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = 'a325eecd6eef2e537373f5b0a1ca7ed97f55c235a297060b'
app.config['SECRET_KEY'] = 'secret!'
app.config['CACHE_TYPE'] = 'SimpleCache'
app.config['CACHE_DEFAULT_TIMEOUT'] = 10000000000

app.config['broker_url'] = 'redis://localhost:6379'
app.config['result_backend'] = 'redis://localhost:6379'
app.config['secondary_dataset_path'] = join(app.root_path, "FaceStuff", "DetectionPhase")

celery = Celery(
        app.name,
        broker=app.config['broker_url'],
        backend=app.config['result_backend'],
        include=["app.FaceStuff.face_clustering"]
    )
db = SQLAlchemy(app, )
CORS(app)
cache = Cache(app)
socketio = SocketIO(app, cors_allowed_origins="*")

from app import routes, models