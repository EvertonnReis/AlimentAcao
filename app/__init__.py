from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from .configuracao import Configuracao

db = SQLAlchemy()

def criar_app():
    app = Flask(__name__)
    app.config.from_object(Configuracao)

    db.init_app(app)
    jwt = JWTManager(app)

    with app.app_context():
        from . import rotas, autenticacao
        db.create_all()

    return app
