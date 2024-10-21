from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .modelos import Doacao, Usuario, db, Instituicao
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from flask_cors import CORS

# Criando o blueprint para Instituição e Autenticação
instituicao_bp = Blueprint('instituicao', __name__)
auth_bp = Blueprint('autenticacao', __name__)

CORS(instituicao_bp, resources={r"/instituicoes/*": {"origins": "*"}})

# Criar instituição
@instituicao_bp.route('/instituicoes', methods=['POST'])
def criar_instituicao():
    dados = request.get_json()
    nome = dados.get('nome')
    endereco = dados.get('endereco')
    telefone = dados.get('telefone')
    cnpj = dados.get('cnpj')
    id_usuario = dados.get('id_usuario')

    nova_instituicao = Instituicao(nome=nome, endereco=endereco, telefone=telefone,id_usuario=id_usuario)
    db.session.add(nova_instituicao)
    db.session.commit()

    return jsonify({"mensagem": "Instituição criada com sucesso"}), 201

# Listar todas as instituições
@instituicao_bp.route('/instituicoes', methods=['GET'])
def listar_instituicoes():
    instituicoes = Instituicao.query.all()
    return jsonify([{
        'id': inst.id,
        'nome': inst.nome,
        'endereco': inst.endereco,
        'telefone': inst.telefone,
        'cnpj': inst.cnpj
    } for inst in instituicoes]), 200

# Atualizar instituição
@instituicao_bp.route('/instituicoes/<int:id>', methods=['PUT'])
def atualizar_instituicao(id):
    instituicao = Instituicao.query.get_or_404(id)
    dados = request.get_json()
    
    instituicao.nome = dados.get('nome', instituicao.nome)
    instituicao.endereco = dados.get('endereco', instituicao.endereco)
    instituicao.telefone = dados.get('telefone', instituicao.telefone)
    instituicao.cnpj = dados.get('cnpj', instituicao.cnpj)

    db.session.commit()
    return jsonify({"mensagem": "Instituição atualizada com sucesso"}), 200

# Deletar instituição
@instituicao_bp.route('/instituicoes/<int:id>', methods=['DELETE'])
def deletar_instituicao(id):
    instituicao = Instituicao.query.get_or_404(id)
    db.session.delete(instituicao)
    db.session.commit()
    return jsonify({"mensagem": "Instituição deletada com sucesso"}), 200

# Rotas de Autenticação
@auth_bp.route('/registro', methods=['POST'])
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
def login():
    dados = request.get_json()
    email = dados.get('email')
    usuario = Usuario.query.filter_by(email=email).first()

    if usuario and check_password_hash(usuario.senha, dados.get('senha')):
        access_token = create_access_token(identity=usuario.id)
        return jsonify(access_token=access_token), 200

    return jsonify({"mensagem": "Credenciais inválidas"}), 401
