from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from .configuracao import Configuracao
from flask_cors import CORS, cross_origin
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

db = SQLAlchemy()

from .autenticacao import auth_bp

def criar_app():
    app = Flask(__name__)

    # Configuração global do CORS
    CORS(app, 
         resources={r"/*": {"origins": "*"}}, 
         supports_credentials=True, 
         allow_headers=['Content-Type', 'Authorization'], 
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

    app.config.from_object(Configuracao)

    db.init_app(app)
    jwt = JWTManager(app)

    # Registrar Blueprints
    app.register_blueprint(auth_bp)

    with app.app_context():
        from . import rotas
        db.create_all()

    return app

