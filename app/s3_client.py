import boto3
import uuid
from botocore.exceptions import NoCredentialsError
import logging, io

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BUCKET_NAME = "radioimportante-uploads"

def upload_arquivo_s3(arquivo, nome_arquivo, pasta="static/musicas/otimizadas", content_type="audio/mpeg"):
    logger.info(f"[S3] Content-Type detectado: {content_type}")
    logger.info(f"[S3] Tamanho do arquivo: {len(arquivo)} bytes")

    s3 = boto3.client("s3")
    key = f"{pasta}/{nome_arquivo}"
    bucket = "radioimportante-uploads"

    try:
        s3.upload_fileobj(
            io.BytesIO(arquivo),  # ← Converte bytes em objeto de arquivo
            bucket,
            key,
            ExtraArgs={"ContentType": content_type}
        )
        logger.info("✅ Upload concluído para S3: %s", key)
    except Exception as e:
        logger.error("[ERRO] Falha geral no upload: %s", e)
        raise

def deletar_arquivo_s3(nome_arquivo, pasta="static/musicas/otimizadas"):
    s3 = boto3.client("s3")
    key = f"{pasta}/{nome_arquivo}"
    bucket = BUCKET_NAME

    try:
        s3.delete_object(Bucket=bucket, Key=key)
        logger.info("🗑️ Arquivo excluído do S3: %s", key)
    except Exception as e:
        logger.error("[ERRO] Falha ao excluir do S3: %s", e)

