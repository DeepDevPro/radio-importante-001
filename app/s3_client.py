import boto3
import os
from botocore.exceptions import NoCredentialsError
import uuid

# Nome do bucket (coloque o nome EXATO criado no console da AWS)
BUCKET_NAME = "radioimportante-uploads"

# Caminho base das imagens e músicas no bucket
PASTA_IMAGENS = "static/img/galeria"
PASTA_MUSICAS = "static/musicas/otimizadas"

# Cria o cliente S3 (sem chave explícita pois usaremos IAM Role)
s3 = boto3.client("s3")

def listar_buckets():
	"""Função de teste opcional"""
	resposta = s3.list_buckets()
	return [b["Name"] for b in resposta["Buckets"]]

# def upload_para_s3(arquivo, caminho_destino):
# 	""""
# 	Salva o arquivo recebido (objeto FileStorage) no S3.

# 	Exemplo de uso:
# 		upload_para_s3(arquivo, "uploads/imagens/logo.png")
# 	"""
# 	s3.upload_fileobj(
# 		Fileobj=arquivo,
# 		Bucket=BUCKET_NAME,
# 		Key=caminho_destino,
# 		ExtraArgs={"ACL": "public-read", "ContentType": arquivo.content_type}
# 	)

def upload_para_s3(arquivo, nome_arquivo, pasta="imagens"):
	chave = f"{pasta}/{uuid.uuid4().hex}_{nome_arquivo}"

	s3.upload_fileobj(
		arquivo,
		BUCKET_NAME,
		chave,
		ExtraArgs={"ACL": "public-read", "ContentType": arquivo.content_type}
	)

	url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{chave}"
	return url

def gerar_url_publica(nome_arquivo, pasta="imagens"):
	""""
	Gera a URL pública de um arquivo armazenado.
	"""
	pasta_base = PASTA_IMAGENS if pasta == "imagens" else PASTA_MUSICAS
	return f"https://{BUCKET_NAME}.s3.amazonaws.com/{pasta_base}/{nome_arquivo}"
