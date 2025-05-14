#!/bin/bash

# Detecta o IP atual da máquina (host)
IP=$(ipconfig getifaddr en0)

# Atualiza o .env
sed -i '' "s|^DATABASE_URL=.*$|DATABASE_URL=postgresql://admin:senha123@${IP}:5432/appdb|" .env

echo "✅ IP atualizado no .env: ${IP}"
echo "Agora use o comando 'Rebuild Container' no VSCode (F1) para aplicar as mudanças."