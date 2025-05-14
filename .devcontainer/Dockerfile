# Imagem base leve com Python 3.11
FROM python:3.11-slim

# Atualiza o sistema e instala dependências essenciais
RUN apt-get update && apt-get install -y \
  libpq-dev \
  gcc \
  postgresql-client \
  curl \
  && apt-get clean

# Cria e define o diretório de trabalho
WORKDIR /app

# Copia os arquivos do projeto para o container
COPY . /app

# Atualiza o pip
RUN pip install --upgrade pip
