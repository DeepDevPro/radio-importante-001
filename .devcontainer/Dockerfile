# Imagem base com Python 3.11 slim
FROM python:3.11-slim

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    postgresql-client \
    curl \
 && apt-get clean

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos para o container
COPY . /app

# Atualiza pip e instala dependências do projeto
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expõe a porta 5000 (padrão Flask/Gunicorn)
EXPOSE 5000

# Comando para iniciar o servidor com Gunicorn
# CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "application:application"]
# Diminuí pra "1" pra ver se o uso de memória baixa dos 90% no painel do EB
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:5000", "application:application"]
