# This file makes the app directory a Python package
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
from fastapi import FastAPI

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

app = FastAPI(title="Medicine Price Comparison API")

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'

    from app.routes import main, auth, medication
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(medication.bp)

    with app.app_context():
        db.create_all()

    return app 