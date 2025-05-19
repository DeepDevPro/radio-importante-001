from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy # Importa a extensão para usar banco relacional
import os, json, random                               # Para lidar com variáveis de ambiente
from dotenv import load_dotenv          # Para carregar as variáveis do .env automaticamente
from functools import wraps
from werkzeug.utils import secure_filename
from PIL import Image
from pydub import AudioSegment
from app.models import User, db, Track
from datetime import timedelta
from app.s3_client import listar_buckets, upload_para_s3, upload_arquivo_s3
from io import BytesIO


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
    if "fila" not in session or not session["fila"]:
        shuffled = nomes.copy()
        random.shuffle(shuffled)
        session["fila"] = shuffled
        session["indice_atual"] = 0
    else:
        shuffled = session["fila"]
    
    return render_template("home.html", nome="Rádio Importante", musicas=musicas, fila=shuffled)

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
    config_path = "config.json"
    imagem_fundo = "background.jpg"

    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config = json.load(f)
            imagem_fundo = config.get("background_image", imagem_fundo)
    
    # # Caminho absoluto CORRETO
    # base_dir = os.path.dirname(__file__)
    # pasta = os.path.join(base_dir, "static", "img", "galeria")

    # Gera a lista de imagens da galeria (miniatura)
    galeria = []
    # pasta = os.path.join("app", "static", "img", "galeria")
    # pasta = os.path.join(app.root_path, "static", "img", "galeria")

    extensoes_validas = [".jpg", ".jpeg", ".png"]

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
    total_segundos = sum(m.duracao_segundos for m in musicas)
    total_formatado = str(timedelta(seconds=total_segundos))

    return render_template("admin-dashboard.html",
                           aba=aba,
                           musicas=musicas,
                           total_musicas=len(musicas),
                           duracao_total=total_formatado)

# Testando o funcionamento do S3
@app.route("/testar-s3")
def testar_s3():
    try:
        buckets = lista_buckets()
        return jsonify({"buckets": buckets})
    except Exception as e:
        return jsonify({"erro": str(e)})

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
# MAX_WIDTH = 1600
# THUMB_SIZE = (200, 200) # Para a galeria

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

def extensao_permitida(nome_arquivo):
    return "." in nome_arquivo and \
            nome_arquivo.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/upload-imagens", methods=["POST"])
def upload_imagens():
    if "imagens" not in request.files:
        return {"erro": "Nenhum arquivo encontrado"}, 400
    
    arquivos = request.files.getlist("imagens")
    salvos = []

    for arquivo in arquivos:
        if arquivo and extensao_permitida(arquivo.filename):
            nome_seguro = secure_filename(arquivo.filename)
            # caminho = os.path.join(app.config["UPLOAD_FOLDER"], nome_seguro)

            # ✅ Garante que a pasta exista antes de salvar
            # os.makedirs(os.path.dirname(caminho), exist_ok=True)

            imagem = Image.open(arquivo)
            imagem = imagem.convert("RGB")

            # Redimensiona imagem original para no máx. 1600x1600
            imagem.thumbnail((1600, 1600))

            buffer = BytesID()
            # caminho = os.path.splitext(caminho) [0] + ".jpg"
            # imagem.save(caminho, format="JPEG", quality=65, optimize=True)
            imagem.save(buffer, format="JPEG", quality=65, optimize=True)
            buffer.seek(0)
            # salvos.append(os.path.basename(caminho))

            # Envia imagem otimizada
            upload_arquivo_s3(buffer, nome_seguro, pasta="static/img/galeria")

            # Miniaturas
            thumb = imagem.copy()
            thumb.thumbnail((300, 300))
            buffer_thumb = BytesIO()
            thumb.save(buffer_thumb, format="JPEG", quality=50, optimize=True)
            buffer_thumb.seek(0)

            nome_thumb = f"thumb_{nome_seguro}"
            upload_arquivo_s3(buffer_thumb, nome_thumb, pasta="static/img/galeria")

            salvos.append(nome_thumb)
    
    if salvos:
        return redirect(url_for("admin_dashboard", aba="imagens"))
    else:
        return {"erro": "Nenhum arquivo válido"}, 400

@app.route("/definir-fundo", methods=["POST"])
def definir_fundo():
    imagem = request.form.get("imagem")

    if not imagem:
        return{"erro": "Imagem não informada"}, 400
    
    # caminho_config = "config.json"
    caminho_config = os.path.join(os.path.dirname(__file__), "..", "config.json")
    caminho_config = os.path.abspath(caminho_config)


    with open(caminho_config, "r") as f:
        config = json.load(f)

    config["background_image"] = imagem

    with open(caminho_config, "w") as f:
        json.dump(config, f, indent=2)
    
    return redirect(url_for("admin_dashboard", aba="imagens"))

@app.route("/upload-musicas", methods=["POST"])
def upload_musicas():
    arquivos = request.files.getlist("musicas")

    for arquivo in arquivos:
        nome_seguro = secure_filename(arquivo.filename)
        nome_base = os.path.splitext(nome_seguro) [0]
        partes = nome_base.split("-")

        artista = partes[0].strip() if len(partes) > 0 else "Desconhecido"
        titulo_versao = partes[1].strip() if len(partes) > 1 else "Sem Título"

        if "(" in titulo_versao:
            titulo, versao = titulo_versao.split("(", 1)
            titulo - titulo.strip()
            versao = versao.strip(") ")
        else:
            titulo = titulo_versao
            versao = None
        
        audio = AudioSegment.from_file(arquivo)
        audio = audio.set_channels(2).set_frame_rate(44100)

        buffer = BytesIO()
        audio.export(buffer, format="mp3", bitrate="128k")
        buffer.seek(0)

        nome_final = f"{nome_base}.mp3"
        upload_arquivo_s3(buffer, nome_final, pasta="static/musicas/otimizadas")

        duracao = len(audio) // 1000

        nova_musica = Track(
            artista=artista,
            titulo=titulo,
            versao=versao,
            duracao_segundos=duracao,
            nome_arquivo=nome_final
        )
        db.session.add(nova_musica)
    
    db.session.commit()
    return redirect("/admin-dashboard?aba=musicas")

@app.route("/excluir-musicas", methods=["POST"])
def excluir_musicas():
    ids = request.form.getlist("ids")

    if not ids:
        return redirect(url_for("admin_dashboard", aba="musicas"))
    
    musicas = Track.query.filter(Track.id.in_(ids)).all()

    for musica in musicas:
        # Apaga o arquivo de áudio
        caminho = os.path.join("app", "static", "musicas", "otimizadas", musica.nome_arquivo)
        if os.path.exists(caminho):
            os.remove(caminho)
        
        # Remove do banco
        db.session.delete(musica)

    db.session.commit()
    return redirect(url_for("admin_dashboard", aba="musicas"))


