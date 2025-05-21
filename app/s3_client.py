import boto3
import uuid
from botocore.exceptions import NoCredentialsError

BUCKET_NAME = "radioimportante-uploads"

def upload_arquivo_s3(arquivo, nome_arquivo, pasta="imagens"):
    try:
        print("[S3] Inicializando cliente")
        s3 = boto3.client("s3")

        chave = f"{pasta}/{uuid.uuid4().hex}_{nome_arquivo}"
        content_type = arquivo.content_type  # 💡 Corrige erro de variável não definida

        print(f"[S3] Pronto para enviar: {chave}")
        print(f"[S3] Content-Type detectado: {content_type}")
        print(f"[S3] Tamanho do arquivo: {arquivo.getbuffer().nbytes} bytes")

        s3.upload_fileobj(
            arquivo,
            BUCKET_NAME,
            chave,
            ExtraArgs={"ACL": "public-read", "ContentType": content_type}
        )

        url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{chave}"
        print(f"[S3] Upload bem-sucedido! URL: {url}")
        return url

    except NoCredentialsError as e:
        print(f"[S3] [ERRO] Sem credenciais: {str(e)}")
        raise RuntimeError("Credenciais AWS não configuradas corretamente.")

    except Exception as e:
        print(f"[ERRO] Falha geral no upload: {str(e)}")
        raise
