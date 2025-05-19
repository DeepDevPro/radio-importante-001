import boto3
import uuid
from botocore.exceptions import NoCredentialsError

BUCKET_NAME = "radioimportante-uploads"

def upload_arquivo_s3(arquivo, nome_arquivo, pasta="imagens"):
    s3 = boto3.client("s3")

    try:
        chave = f"{pasta}/{uuid.uuid4().hex}_{nome_arquivo}"
        content_type = arquivo.content_type  # 💡 Corrige erro de variável não definida

        print(f"[S3] Enviando para: {BUCKET_NAME}/{chave} – ContentType: {content_type}")
        print(f"[S3] Tamanho do buffer: {arquivo.getbuffer().nbytes} bytes")

        s3.upload_fileobj(
            arquivo,
            BUCKET_NAME,
            chave,
            ExtraArgs={"ACL": "public-read", "ContentType": content_type}
        )

        url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{chave}"
        print(f"[S3] Upload bem-sucedido! URL: {url}")
        return url

    except NoCredentialsError:
        raise RuntimeError("Credenciais AWS não configuradas corretamente.")

    except Exception as e:
        print(f"[ERRO] Falha ao fazer upload para o S3: {str(e)}")
        raise
