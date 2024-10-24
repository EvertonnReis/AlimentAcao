from . import db
from datetime import datetime

# Tabela Usuario (Doador e Instituição)
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_usuario = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    senha = db.Column(db.String(200), nullable=False)
    e_instituicao = db.Column(db.Boolean, default=False)
    cpf_cnpj = db.Column(db.String(20), unique=True, nullable=True)
    telefone = db.Column(db.String(15), nullable=True)  

    def __repr__(self):
        return f'<Usuario {self.nome_usuario}>'


# Tabela Instituicao (caso separemos de Usuario)
class Instituicao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    endereco = db.Column(db.String(200), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    
    usuario = db.relationship('Usuario', backref=db.backref('instituicoes', lazy=True))

    def __repr__(self):
        return f'<Instituicao {self.nome}>'

# Tabela Alimento
class Alimento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    validade = db.Column(db.DateTime, nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Alimento {self.nome}>'

# Tabela Doacao
class Doacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_alimento = db.Column(db.Integer, db.ForeignKey('alimento.id'), nullable=False)
    id_doador = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)  # Referência correta a Usuario
    id_instituicao = db.Column(db.Integer, db.ForeignKey('instituicao.id'), nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamentos
    instituicao = db.relationship('Instituicao', backref=db.backref('doacoes', lazy=True))
    alimento = db.relationship('Alimento', backref=db.backref('doacoes', lazy=True))
    doador = db.relationship('Usuario', backref=db.backref('doacoes', lazy=True))

    def __repr__(self):
        return f'<Doacao de {self.alimento.nome} para {self.instituicao.nome} por {self.doador.nome_usuario}>'
