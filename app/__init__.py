from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy # Importa a extensão para usar banco relacional
import os, json, random, logging, boto3, uuid       # Para lidar com variáveis de ambiente
from dotenv import load_dotenv          # Para carregar as variáveis do .env automaticamente
from functools import wraps
from werkzeug.utils import secure_filename
from PIL import Image
from app.models import User, db, Track
from datetime import timedelta
from app.s3_client import upload_arquivo_s3, deletar_arquivo_s3

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#   <<  SOBRE O BANCO DE DADOS  >>
#db = SQLAlchemy()   # (1) Só cria

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Inicializa a aplicação Flask
app = Flask(__name__)

# Configurando a Secret Key da sessão
app.secret_key = os.getenv("SECRET_KEY")

# Configura o endereço de conexão com o banco, vindo do .env
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")

# Desativa o sistema de track modificado (apenas otimização)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)    # (2) Agora vai vincular ao app


@app.route("/health")
def health():
    return "OK", 200

#   <<  SOBRE AS ROTAS  >>
@app.route("/")
def home():
    musicas = Track.query.order_by(Track.id).all()
    nomes = [m.nome_arquivo for m in musicas]

    # Se não tiver fila salva na sessão, gera nova
    # if "fila" not in session or not session["fila"]:
    #     shuffled = nomes.copy()
    #     random.shuffle(shuffled)
    #     session["fila"] = shuffled
    #     session["indice_atual"] = 0
    # 🔐 Se a session estiver ausente ou defasada, reembaralha
    if "fila" not in session or set(session["fila"]) != set(nomes):
        logger.info("🛡️ Resetando session['fila'] por diferença entre banco e session")
        shuffled = nomes.copy()
        random.shuffle(shuffled)
        session["fila"] = shuffled
        session["indice_atual"] = 0
    else:
        shuffled = session["fila"]

    playlist = [
        f"https://radioimportante-uploads.s3.us-west-2.amazonaws.com/static/musicas/otimizadas/{m}"
        for m in session["fila"]
    ]

    logger.info("Session Fila: %s", session.get("fila"))
    logger.info("Playlist gerada para o frontend: %s", playlist)
    # logger.info("Tracks carregadas do banco: %s", [t.nome_arquivo for t in musicas])
    logger.info("Tracks carregadas do banco: %s", nomes)

    return render_template(
        "home.html",
        nome="Rádio Importante",
        musicas=musicas,
        fila=shuffled,
        playlist=playlist
        )

@app.route("/user-login")
def login_page():
    return render_template("user-login.html")

@app.route("/admin-login")
def admin_login_page():
    return render_template("admin-login.html")

# Nova rota de API
@app.route("/api/status")
def api_status():
    return jsonify({
        "status": "online",
        "mensagem": "A API está funcionando perfeitamente! 🚀"
    })

@app.context_processor
def contexto_geral():
    # Carrega imagem de fundo do config.json
    imagem_fundo = "background.jpg"
    # config_path = "config.json"

    # caminho absoluto e seguro
    caminho_config = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config.json"))

    if os.path.exists(caminho_config):
        try:
            with open(caminho_config, "r") as f:
                config = json.load(f)
                imagem_fundo = config.get("background_image", imagem_fundo)
        except Exception as e:
            logger.info(f"[ERRO] config.json: {e}")
    
    # 🔹 Conecta ao S3 e lista miniaturas
    galeria = []
    bucket_name = "radioimportante-uploads"
    prefix = "static/img/galeria"

    try:
        # 🔁 NOVO: lista os arquivos no S3
        s3 = boto3.client("s3")
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

        # Gera a lista de imagens da galeria (miniatura)
        for obj in response.get("Contents", []):
            key = obj["Key"]
            nome_arquivo = key.split("/")[-1]  # Define antes de usar

            if "thumb_" in nome_arquivo and nome_arquivo.lower().endswith((".jpg", ".jpeg", ".png")):
                galeria.append({
                    "nome": nome_arquivo,
                    "url": f"https://{bucket_name}.s3.amazonaws.com/{key}"
                })
    except Exception as e:
        logger.info(f"[ERRO] Falha ao acessar o S3: {e}")

    return {
        "imagem_fundo": imagem_fundo,
        "galeria_imagens": galeria
    }

@app.route("/admin-dashboard")
def admin_dashboard():
    aba = request.args.get("aba", "musicas")
#    return render_template("admin-dashboard.html", aba=aba)

    # Consulta tods as músicas salvas no banco
    musicas = Track.query.all()

    # Calcula a duração total da playlist
    total_segundos = sum(m.duracao_segundos or 0 for m in musicas)
    total_formatado = str(timedelta(seconds=total_segundos))

    return render_template("admin-dashboard.html",
                           aba=aba,
                           musicas=musicas,
                           total_musicas=len(musicas),
                           duracao_total=total_formatado)

# Criando a rota para inserir um usuário
@app.route("/api/usuarios", methods=["POST"])
def adicionar_usuario():
    from flask import request
    from app.models import User

    dados = request.get_json()

    novo_usuario = User(
        email=dados.get("email"),
        senha=dados.get("senha")
    )

    db.session.add(novo_usuario)
    db.session.commit()

    return jsonify({
        "mensagem": "Usuário criado com sucesso!",
        "usuario": {
            "email": novo_usuario.email
        }
    }), 201

# Criando a rota para listar todos os usuários
@app.route("/api/usuarios", methods=["GET"])
def listar_usuarios():
#    from app.models import User

    usuarios = User.query.all()

    return jsonify([
        {
            "id": u.id,
            "email": u.email
        } for u in usuarios
    ])

# Criando a rota de api/cadastro
@app.route("/api/cadastro", methods=["POST"])
def cadastro():
    from flask import request
    from app.models import User

    dados = request.get_json()

    email = dados.get("email")
    senha = dados.get("senha")

    if not email or not senha:
        return jsonify({"erro": "Email e senha são obrigatórios"}), 400
    
    # Verifica se o e-mail já está cadastrado
    if User.query.filter_by(email=email).first():
        return jsonify({"erro": "Usuário já cadastrado"}), 400
    
    novo_usuario = User(email=email)
    novo_usuario.set_senha(senha)

    db.session.add(novo_usuario)
    db.session.commit()

    return jsonify({
        "mensagem": "Usuário cadastrado com sucesso!",
        "usuario": {
            "id": novo_usuario.id,
            "email": novo_usuario.email
        }
    }), 201

# Criando a rota /api/login
@app.route("/api/login", methods=["POST"])
def login():
    dados = request.get_json()
    email = dados.get("email")
    senha = dados.get("senha")

    if not email or not senha:
        return jsonify({"erro": "Email e senha são obrigatórios"}), 400
    
    usuario = User.query.filter_by(email=email).first()

    if not usuario:
        return jsonify({"erro": "Usuário não encontrado"}), 404

    if usuario.verificar_senha(senha):
        session["usuario_id"] = usuario.id  # Sessão criada com sucesso
        return jsonify({
            "mensagem": "Login realizado com sucesso!",
            "usuario": {
                "id": usuario.id,
                "email": usuario.email
            }
        })
    else:
        return jsonify({"erro": "Senha incorreta"}), 401

def login_required(f):  # Esta é uma função para proteger as rotas de usuarios não logados (sempre adicionar antes da função da rota que for utiliza-la, como agora)
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "usuario_id" not in session:
            return jsonify({"erro": "Usuário não autenticado"}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route("/api/dashboard")
@login_required
def dashboard():
    return jsonify({
        "mensagem": "Bem-vindo ao painel do usuário!",
        "detalhes": "Esta é uma área restrita acessível apenas para usuários autenticados."
        # return render_template("dashboard.html")
    })

# Diretório de upload de imagens (garanta que exista)
UPLOAD_FOLDER = os.path.join("app", "static", "img", "galeria")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

def extensao_permitida(nome_arquivo):
    return "." in nome_arquivo and \
            nome_arquivo.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def log_mem(tag=""):
    process = psutil.Process(os.getpid())
    logger.info(f"[MEMORIA] {tag} - {process.memory_info().rss / 1024 / 1024:.2f} MB")

@app.route("/upload-musicas", methods=["POST"])
def upload_musicas():
    arquivos = request.files.getlist("musicas")

    duracoes = request.form.getlist("duracoes")

    if not duracoes:
        duracoes = []
        logger.warning("Nenhuma duração enviada via formulário — fallback para 0s.")

    logger.info("🆙 Iniciando upload de músicas")
    logger.info("Arquivos recebidos: %d", len(arquivos))
    for a in arquivos:
        logger.info("Arquivo: %s (%s)", a.filename, a.content_type)

    try:
        # for arquivo in arquivos:
        for i, arquivo in enumerate(arquivos):
            nome_seguro = secure_filename(arquivo.filename)
            nome_base = os.path.splitext(nome_seguro)[0]
    
            # ✅ Protege contra falta de hífen no nome do arquivo
            if "-" in nome_base:
                artista, titulo_versao = nome_base.split("-", 1)
                artista = artista.strip()
                titulo_versao = titulo_versao.strip()
            else:
                artista = "Desconhecido"
                titulo_versao = nome_base.strip()
            
            # ✅ Protege contra ausência de versão entre parênteses
            if "(" in titulo_versao:
                titulo, versao = titulo_versao.split("(", 1)
                titulo = titulo.strip()
                versao = versao.strip(") ")
            else:
                titulo = titulo_versao
                versao = None

            uuid_id = uuid.uuid4().hex[:24]
            nome_final = f"{uuid_id}_{nome_seguro}"
            logger.info("Salvando em: static/musicas/otimizadas/%s", nome_final)

            buffer = arquivo.stream.read()
            upload_arquivo_s3(buffer, nome_final, pasta="static/musicas/otimizadas", content_type="audio/mpeg")
            logger.info("☁️ Após upload para S3")

            nova_musica = Track(
                artista=artista,
                titulo=titulo,
                versao=versao,
                # duracao_segundos=int(duracoes[i]) if i < len(duracoes) else 0,
                duracao_segundos = int(duracoes[i]) if i < len(duracoes) and duracoes[i].isdigit() else 0,
                nome_arquivo=nome_final
            )
            db.session.add(nova_musica)
        
        db.session.commit()
        logger.info("✅ Final da rota /upload-musicas")

        session["fila"] = []
        session["indice_atual"] = 0
        logger.info("🗑️ Session['fila'] reiniciada após upload")

        return redirect("/admin-dashboard?aba=musicas")
    
    except Exception as e:
        logger.exception("🔥 Erro durante upload de músicas")
        return "Erro interno no servidor (upload)", 500


@app.route("/excluir-musicas", methods=["POST"])
def excluir_musicas():
    ids = request.form.getlist("ids")

    if not ids:
        return redirect(url_for("admin_dashboard", aba="musicas"))
    
    musicas = Track.query.filter(Track.id.in_(ids)).all()

    for musica in musicas:
        # Apaga o arquivo de áudio
        deletar_arquivo_s3(musica.nome_arquivo)

        # Remove do banco
        db.session.delete(musica)

    db.session.commit()

    session["fila"] = []
    session["indice_atual"] = 0
    logger.info("Session['fila'] reiniciada após upload")

    return redirect(url_for("admin_dashboard", aba="musicas"))

@app.route("/reset-session")
def reset_session():
    session.clear()
    return "Sessão resetada com sucesso!"


if __name__ == "__main__":
    app.run(debug=True)
