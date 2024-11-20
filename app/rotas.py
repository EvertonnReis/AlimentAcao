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
    rua = dados.get('rua')
    numero = dados.get('numero')
    bairro = dados.get('bairro')
    cep = dados.get('cep')
    telefone = dados.get('telefone')
    cnpj = dados.get('cnpj')
    id_usuario = dados.get('id_usuario')

    nova_instituicao = Instituicao(
        nome=nome, 
        rua=rua, 
        numero=numero, 
        bairro=bairro, 
        cep=cep, 
        telefone=telefone, 
        id_usuario=id_usuario,
        cnpj=cnpj
    )
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
        'rua': inst.rua,
        'numero': inst.numero,
        'bairro': inst.bairro,
        'cep': inst.cep,
        'telefone': inst.telefone,
        'cnpj': inst.cnpj
    } for inst in instituicoes]), 200

# Listar instituições de acordo com o id do usuário
@instituicao_bp.route('/instituicoes/<int:id_usuario>', methods=['GET'])
def listar_instituicoes_por_usuario(id_usuario):
    instituicoes = Instituicao.query.filter_by(id_usuario=id_usuario).all()
    return jsonify([{
        'id': inst.id,
        'nome': inst.nome,
        'rua': inst.rua,
        'numero': inst.numero,
        'bairro': inst.bairro,
        'cep': inst.cep,
        'telefone': inst.telefone,
        'cnpj': inst.cnpj
    } for inst in instituicoes]), 200

# Atualizar instituição
@instituicao_bp.route('/instituicoes/<int:id>', methods=['PUT'])
def atualizar_instituicao(id):
    instituicao = Instituicao.query.get_or_404(id)
    dados = request.get_json()
    
    instituicao.nome = dados.get('nome', instituicao.nome)
    instituicao.rua = dados.get('rua', instituicao.rua)
    instituicao.numero = dados.get('numero', instituicao.numero)
    instituicao.bairro = dados.get('bairro', instituicao.bairro)
    instituicao.cep = dados.get('cep', instituicao.cep)
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
            quantidade=quantidade,
            unidade=alimento['unidade']
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
        'alimentos': [{'nome': alimento.nome, 'quantidade': alimento.quantidade, 'validade': alimento.validade.isoformat(), 'unidade': alimento.unidade} for alimento in doacao.alimentos]
    } for doacao in doacoes])

# Listar todas as doações do usuario desejado
@doacao_bp.route('/doacoes/<int:id>', methods=['GET'])
def listar_doacoes_usuario(id):
    doacoes = Doacao.query.filter_by(id_doador=id).all()
    return jsonify([{
        'id': doacao.id,
        'id_doador': doacao.id_doador,
        'doador': doacao.doador.nome_usuario,
        'id_instituicao': doacao.id_instituicao,
        'instituicao': doacao.instituicao.nome,
        'data': doacao.data.isoformat(),
        'alimentos': [{'nome': alimento.nome, 'quantidade': alimento.quantidade, 'validade': alimento.validade.isoformat(), 'unidade': alimento.unidade} for alimento in doacao.alimentos]
    } for doacao in doacoes])

# Listar todas as doações do usuario desejado
@doacao_bp.route('/doacoesInstituicoes/<int:id_instituicao>', methods=['GET'])
def listar_doacoes_instituicoes(id_instituicao):
    doacoes = Doacao.query.filter_by(id_instituicao=id_instituicao).all()
    return jsonify([{
        'id': doacao.id,
        'id_doador': doacao.id_doador,
        'doador': doacao.doador.nome_usuario,
        'id_instituicao': doacao.id_instituicao,
        'instituicao': doacao.instituicao.nome,
        'data': doacao.data.isoformat(),
        'alimentos': [
            {
                'nome': alimento.nome,
                'quantidade': alimento.quantidade,
                'validade': alimento.validade.isoformat(),
                'unidade': alimento.unidade
            } for alimento in doacao.alimentos
        ]
    } for doacao in doacoes])

@doacao_bp.route('/doacoes/<int:id>/alimentos', methods=['GET'])
def listar_alimentos_doacao(id):
    doacao = Doacao.query.get(id)
    if not doacao:
        return jsonify({"error": "Doação não encontrada"}), 404

    alimentos = [{
        'nome': alimento.nome,
        'quantidade': alimento.quantidade,
        'validade': alimento.validade.isoformat(),
        'unidade': alimento.unidade
    } for alimento in doacao.alimentos]

    return jsonify(alimentos)


# Atualizar doação
@doacao_bp.route('/doacoes/<int:id>', methods=['PUT'])
def atualizar_doacao(id):
    doacao = Doacao.query.get_or_404(id)
    data = request.json

    # Obtenha os dados do doador e da instituição
    id_doador = data.get('id_doador')
    id_instituicao = data.get('id_instituicao')
    alimentos = data.get('alimentos')
    date = data.get('date')

    # Validação e atribuição correta das instâncias
    if id_doador:
        doador = Usuario.query.get(id_doador)
        if doador is None:
            return jsonify({"mensagem": "Doador não encontrado"}), 404
        doacao.doador = doador  # Atribui a instância do doador

    if id_instituicao:
        beneficiario = Instituicao.query.get(id_instituicao)
        if beneficiario is None:
            return jsonify({"mensagem": "Beneficiário não encontrado"}), 404
        doacao.instituicao = beneficiario  # Atribui a instância da instituição

    # Atualização dos alimentos
    if alimentos is not None:
        # Limpa os alimentos existentes
        doacao.alimentos.clear()  # Remove todos os alimentos da doação

        # Adiciona os novos alimentos
        for alimento in alimentos:
            # Verifique se as chaves necessárias estão presentes
            if 'validade' not in alimento or 'quantidade' not in alimento or 'nome' not in alimento or 'unidade' not in alimento:
                return jsonify({'error': 'Dados do alimento inválidos'}), 400

            # Convertendo a quantidade para inteiro
            try:
                quantidade = int(alimento['quantidade'])
            except ValueError:
                return jsonify({'error': 'Quantidade deve ser um número inteiro válido'}), 400

            # Criar um novo alimento e adicioná-lo ao banco de dados
            novo_alimento = Alimento(
                nome=alimento['nome'],
                validade=alimento['validade'],
                quantidade=quantidade,
                unidade=alimento['unidade']
            )
            db.session.add(novo_alimento)
            db.session.commit()  # Commit para gerar o ID do alimento
            alimento_id = novo_alimento.id

            # Usar o método `execute` da sessão para criar o relacionamento
            db.session.execute(
                doacao_alimento.insert().values(
                    doacao_id=doacao.id,
                    alimento_id=alimento_id,
                    quantidade=quantidade,
                    validade=alimento['validade']
                )
            )

    if date:
        try:
            doacao.data = datetime.fromisoformat(date)
        except ValueError:
            return jsonify({"mensagem": "Formato de data inválido"}), 400

    db.session.commit()  # Commit para salvar as alterações

    # Prepare a resposta com o ID e o nome do doador
    return jsonify({
        "mensagem": "Doação atualizada com sucesso",
        "doacao": {
            "id": doacao.id,
            "id_doador": doacao.doador.id,
            "nome_doador": doacao.doador.nome_usuario,
            "id_instituicao": doacao.instituicao.id,
            "data": doacao.data.isoformat(),  
            "alimentos": [{"id": alimento.id, "nome": alimento.nome} for alimento in doacao.alimentos]
        }
    }), 200


# Deletar doação
@doacao_bp.route('/doacoes/<int:id>', methods=['DELETE'])
def deletar_doacao(id):
    doacao = Doacao.query.get_or_404(id)
    db.session.delete(doacao)
    db.session.commit()
    return jsonify({"mensagem": "Doação deletada com sucesso"}), 200