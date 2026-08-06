from flask import Flask
from config import Config
from database.models import db

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    print("✅ Connected Successfully!")
    print(db.engine)
