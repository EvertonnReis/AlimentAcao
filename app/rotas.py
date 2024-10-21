from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .modelos import Doacao, Usuario, db, Instituicao, Alimento , doacao_alimento
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from flask_cors import CORS

# Criando o blueprint para Instituição e Autenticação
instituicao_bp = Blueprint('instituicao', __name__)
auth_bp = Blueprint('autenticacao', __name__)
doacao_bp = Blueprint('doacao', __name__)

CORS(instituicao_bp, resources={r"/instituicoes/*": {"origins": "*"}})
CORS(doacao_bp, resources={r"/doacoes/*": {"origins": "*"}})

# Criar instituição
@instituicao_bp.route('/instituicoes', methods=['POST'])
def criar_instituicao():
    dados = request.get_json()
    nome = dados.get('nome')
    endereco = dados.get('endereco')
    telefone = dados.get('telefone')
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
        'telefone': inst.telefone
    } for inst in instituicoes]), 200

# Atualizar instituição
@instituicao_bp.route('/instituicoes/<int:id>', methods=['PUT'])
def atualizar_instituicao(id):
    instituicao = Instituicao.query.get_or_404(id)
    dados = request.get_json()
    
    instituicao.nome = dados.get('nome', instituicao.nome)
    instituicao.endereco = dados.get('endereco', instituicao.endereco)
    instituicao.telefone = dados.get('telefone', instituicao.telefone)

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

# Criar doação
@doacao_bp.route('/doacoes', methods=['POST'])
def criar_doacao():
    data = request.json
    instituicao = Instituicao.query.get(data['id_instituicao'])
    if not instituicao:
        return jsonify({'error': 'Instituição não encontrada'}), 400

    # Criar a doação
    nova_doacao = Doacao(
        id_doador=int(data['id_doador']),
        id_instituicao=int(data['id_instituicao']),
        data=datetime.now()
    )
    db.session.add(nova_doacao)
    db.session.commit()

    # Agora, inserir os alimentos associados
    for alimento in data['alimentos']:
        # Verifique se as chaves necessárias estão presentes
        if 'validade' not in alimento or 'quantidade' not in alimento:
            return jsonify({'error': 'Dados do alimento inválidos'}), 400

        # Convertendo a quantidade para inteiro
        try:
            quantidade = int(alimento['quantidade'])
        except ValueError:
            return jsonify({'error': 'Quantidade deve ser um número inteiro válido'}), 400

        # Criar um novo alimento sem verificar se já existe
        novo_alimento = Alimento(
            nome=alimento['nome'],
            validade=alimento['validade'],
            quantidade=quantidade
        )
        db.session.add(novo_alimento)
        db.session.commit()  # Commit para gerar o ID do alimento
        alimento_id = novo_alimento.id

        # Usar o método `execute` da sessão para criar o relacionamento
        db.session.execute(
            doacao_alimento.insert().values(
                doacao_id=nova_doacao.id,
                alimento_id=alimento_id,
                quantidade=quantidade,
                validade=alimento['validade']
            )
        )

    db.session.commit()  # Commit para salvar os alimentos associados
    return jsonify({'id': nova_doacao.id}), 201


# Listar todas as doações
@doacao_bp.route('/doacoes', methods=['GET'])
def listar_doacoes():
    doacoes = Doacao.query.all()
    return jsonify([{
        'id': doacao.id,
        'id_doador': doacao.id_doador,
        'doador': doacao.doador.nome_usuario,
        'id_instituicao': doacao.id_instituicao,
        'instituicao': doacao.instituicao.nome,
        'data': doacao.data.isoformat(),
        'alimentos': [{'nome': alimento.nome, 'quantidade': alimento.quantidade, 'validade': alimento.validade.isoformat()} for alimento in doacao.alimentos]
    } for doacao in doacoes])


# Atualizar doação
@doacao_bp.route('/doacoes/<int:id>', methods=['PUT'])
def atualizar_doacao(id):
    doacao = Doacao.query.get_or_404(id)
    dados = request.get_json()
    
    doacao.doador = dados.get('doador', doacao.doador)
    doacao.beneficiario = dados.get('beneficiario', doacao.beneficiario)
    doacao.alimentos = dados.get('alimentos', doacao.alimentos)
    doacao.date = dados.get('date', doacao.date)

    db.session.commit()
    return jsonify({"mensagem": "Doação atualizada com sucesso"}), 200

# Deletar doação
@doacao_bp.route('/doacoes/<int:id>', methods=['DELETE'])
def deletar_doacao(id):
    doacao = Doacao.query.get_or_404(id)
    db.session.delete(doacao)
    db.session.commit()
    return jsonify({"mensagem": "Doação deletada com sucesso"}), 200