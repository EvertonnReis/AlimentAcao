from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .modelos import Doacao, Usuario, db

main_bp = Blueprint('principal', __name__)

@main_bp.route('/doacoes', methods=['POST'])
@jwt_required()
def criar_doacao():
    usuario_atual = get_jwt_identity()
    dados = request.get_json()
    doacao = Doacao(item_comida=dados['item_comida'], quantidade=dados['quantidade'], doador_id=usuario_atual)
    db.session.add(doacao)
    db.session.commit()

    return jsonify({"mensagem": "Doação criada com sucesso"}), 201

@main_bp.route('/doacoes', methods=['GET'])
@jwt_required()
def listar_doacoes():
    doacoes = Doacao.query.all()
    return jsonify([{
        'id': d.id,
        'item_comida': d.item_comida,
        'quantidade': d.quantidade,
        'doador_id': d.doador_id,
        'instituicao_id': d.instituicao_id
    } for d in doacoes]), 200
