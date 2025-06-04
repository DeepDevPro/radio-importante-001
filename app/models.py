#from app import db	# nova alteração pra importar o banco do init
from werkzeug.security import generate_password_hash, check_password_hash

# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Cria uma classe User que representa a tabela "user"
class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)	# ID único, chave primária
	email = db.Column(db.String(120), unique=True, nullable=False)	# Campo de e-mail, obrigatório e único
	senha_hash = db.Column(db.String(256), nullable=False)	# Campo senha obrigatório

	def set_senha(self, senha_pura):
		self.senha_hash = generate_password_hash(senha_pura)
	
	def verificar_senha(self, senha_pura):
		return check_password_hash(self.senha_hash, senha_pura)

	def __repr__(self):
		return f"<User {self.email}>"	# Mostra algo útil no terminal quando printar o objeto


class Track(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	artista = db.Column(db.String(100))
	titulo = db.Column(db.String(100))
	versao = db.Column(db.String(100), nullable=True)
	duracao_segundos = db.Column(db.Integer)
	nome_arquivo = db.Column(db.String(200))

class Audicao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    duracao = db.Column(db.Integer, default=60)

