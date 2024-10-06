from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from .modelos import Usuario, db
from flask_cors import cross_origin

auth_bp = Blueprint('autenticacao', __name__)
instituicao_bp = Blueprint('instituicao', __name__)

@auth_bp.route('/registro', methods=['POST'])
@cross_origin(origins="*", supports_credentials=True, 
              allow_headers=['Content-Type', 'Authorization'], 
              methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def registro():
    dados = request.get_json()
    nome_usuario = dados.get('nome_usuario')
    email = dados.get('email')
    senha = generate_password_hash(dados.get('senha'))
    e_instituicao = dados.get('e_instituicao', False)

    usuario = Usuario(nome_usuario=nome_usuario, email=email, senha=senha, e_instituicao=e_instituicao)
    db.session.add(usuario)
    db.session.commit()

    return jsonify({"mensagem": "Usuário criado com sucesso"}), 201

@auth_bp.route('/login', methods=['POST'])
@cross_origin(origins="*", supports_credentials=True, 
              allow_headers=['Content-Type', 'Authorization'], 
              methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def login():
    dados = request.get_json()
    email = dados.get('email')
    usuario = Usuario.query.filter_by(email=email).first()

    if usuario and check_password_hash(usuario.senha, dados.get('senha')):
        access_token = create_access_token(identity=usuario.id)
        return jsonify(access_token=access_token), 200

    return jsonify({"mensagem": "Credenciais inválidas"}), 401
