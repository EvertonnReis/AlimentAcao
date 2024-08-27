from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from .modelos import Usuario, db

auth_bp = Blueprint('autenticacao', __name__)

@auth_bp.route('/registro', methods=['POST'])
def registro():
    dados = request.get_json()
    nome_usuario = dados.get('nome_usuario')
    senha = generate_password_hash(dados.get('senha'))
    e_instituicao = dados.get('e_instituicao', False)

    usuario = Usuario(nome_usuario=nome_usuario, senha=senha, e_instituicao=e_instituicao)
    db.session.add(usuario)
    db.session.commit()

    return jsonify({"mensagem": "Usuário criado com sucesso"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    dados = request.get_json()
    usuario = Usuario.query.filter_by(nome_usuario=dados.get('nome_usuario')).first()

    if usuario and check_password_hash(usuario.senha, dados.get('senha')):
        access_token = create_access_token(identity=usuario.id)
        return jsonify(access_token=access_token), 200

    return jsonify({"mensagem": "Credenciais inválidas"}), 401
