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


# def upload_arquivo_s3(arquivo, nome_arquivo, pasta="imagens", content_type="application/octet-stream"):
#     try:
#         logger.info("[S3] Inicializando cliente")
#         s3 = boto3.client("s3")

#         chave = f"{pasta}/{nome_arquivo}"  # ← importante!
#         # content_type = arquivo.content_type  # 💡 Corrige erro de variável não definida

#         logger.info(f"[S3] Pronto para enviar: {chave}")
#         logger.info(f"[S3] Content-Type detectado: {content_type}")
#         logger.info(f"[S3] Tamanho do arquivo: {len(arquivo)} bytes")

#         s3.upload_fileobj(
#             arquivo,
#             BUCKET_NAME,
#             chave,
#             ExtraArgs={"ContentType": content_type}

#         )

#         url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{chave}"
#         logger.info(f"[S3] Upload bem-sucedido! URL: {url}")
#         return url

#     except NoCredentialsError as e:
#         logger.info(f"[S3] [ERRO] Sem credenciais: {str(e)}")
#         raise RuntimeError("Credenciais AWS não configuradas corretamente.")

#     except Exception as e:
#         logger.info(f"[ERRO] Falha geral no upload: {str(e)}")
#         raise

