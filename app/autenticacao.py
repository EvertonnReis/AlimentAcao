from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from .modelos import Instituicao, Usuario, db
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
    cpf_cnpj = dados.get('cpf_cnpj')  
    telefone = dados.get('telefone') 

    usuario = Usuario(
        nome_usuario=nome_usuario,
        email=email,
        senha=senha,
        e_instituicao=e_instituicao,
        cpf_cnpj=cpf_cnpj,
        telefone=telefone
    )
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

        instituicao = Instituicao.query.filter_by(id_usuario=usuario.id).first()
        id_instituicao = instituicao.id if instituicao else None

        return jsonify(
            access_token=access_token,
            id=usuario.id,
            username=usuario.nome_usuario,
            instituicao=id_instituicao
        ), 200
    
    return jsonify({"mensagem": "Credenciais inválidas"}), 401

# Pegar usuário pelo id
@auth_bp.route('/usuarios/<int:id>', methods=['GET'])
def pegar_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    return jsonify({
        "id": usuario.id,
        "nome_usuario": usuario.nome_usuario,
        "cpf_cnpj": usuario.cpf_cnpj,
        "email": usuario.email,
        "telefone": usuario.telefone,
}), 200

@auth_bp.route('/usuarios/<int:id>', methods=['PUT'])
@cross_origin(origins="*", supports_credentials=True, 
              allow_headers=['Content-Type', 'Authorization'], 
              methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def atualizar_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    dados = request.get_json()

    # Atualizando os campos do usuário
    usuario.nome_usuario = dados.get('nome_usuario', usuario.nome_usuario)
    usuario.email = dados.get('email', usuario.email)
    usuario.cpf_cnpj = dados.get('cpf_cnpj', usuario.cpf_cnpj)
    usuario.telefone = dados.get('telefone', usuario.telefone)

    # Se a senha for fornecida, ela será atualizada
    senha = dados.get('senha')
    if senha:
        usuario.senha = generate_password_hash(senha)

    try:
        # Commitando as alterações no banco de dados
        db.session.commit()
        return jsonify({"mensagem": "Usuário atualizado com sucesso"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"mensagem": "Erro ao atualizar usuário", "erro": str(e)}), 500
