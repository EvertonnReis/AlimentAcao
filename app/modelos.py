from . import db
from datetime import datetime

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_usuario = db.Column(db.String(80), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)
    e_instituicao = db.Column(db.Boolean, default=False)

# class Doacao(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     item_comida = db.Column(db.String(200), nullable=False)
#     quantidade = db.Column(db.Integer, nullable=False)
#     doador_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
#     instituicao_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)
#     criado_em = db.Column(db.DateTime, default=datetime.utcnow)

class Instituicao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    endereco = db.Column(db.String(200), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)

    def _repr_(self):
        return f'<Instituicao {self.nome}>'

# Tabela Alimentos
class Alimento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    validade = db.Column(db.DateTime, nullable=False)

    def _repr_(self):
        return f'<Alimento {self.nome}>'

# Tabela Doação
class Doacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_instituicao = db.Column(db.Integer, db.ForeignKey('instituicao.id'), nullable=False)
    id_alimento = db.Column(db.Integer, db.ForeignKey('alimento.id'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)

    instituicao = db.relationship('Instituicao', backref=db.backref('doacoes', lazy=True))
    alimento = db.relationship('Alimento', backref=db.backref('doacoes', lazy=True))

    def _repr_(self):
        return f'<Doacao {self.quantidade} de {self.alimento.nome} para {self.instituicao.nome}>'

