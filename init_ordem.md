# Para inicializar o projeto devo seguir a ordem:

0. Iniciar o Dev Container antes de rodar o ./dev-start.sh por causa do pip freeze.

1. Rodar o comando ./dev-start.sh no terminal do Mac, na pasta raíz do projeto;
2. Acessar com F1 ou clicar na barra de comandos do VSCode (a barra superior) e escolher a opção "Dev Container: Rebuild Container";
3. Inicializar o servidor Flask com os comandos:
```bash
	export FLASK_APP=app		# No terminal do Dev Container dentro do VSCode
	flask run --host=0.0.0.0	# No terminal do Dev Container dentro do VSCode
```

3.1 Depois que o Container estiver rodando, rodar estes dois comandos no termional dele:
pip freeze > requirements.txt - esse comando busca todos os pacotes que precisam ser instalados
pip install -r requirements.txt - esse comando instala os pacotes listados no .txt

4. Verificar se o postgres-local já está rodando na máquina com o comando:
```bash
	docker ps	# No terminal do Mac, em qualquer pasta
```
	Se caso não aparecer na lista, inicialize-o com o seguinte comando:
```bash
	docker start postgres-local		# Em quaquer local
```
- Rodar o comando anterrior para conferir se agora o postgres-local está rodando

Caso eu queira reiniciar o Container do postgres-local é só dar o comando:
```bash
	docker restart postgres-local
```

Pronto, fim.