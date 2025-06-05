from bson import ObjectId
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify, session
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user
from EventosOOP import Evento
from AtividadesOOP import Atividades
from ParticipanteOOP import Participante
from Connects import Conexao
import csv
from transformers import pipeline
from CriarPDF import *
from googletrans import Translator
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import io
import qrcode
import fitz
import base64
import json
import socket
import logging

# Modelo para a emoção da mensagem
classificacao_emocional = pipeline('sentiment-analysis', model='nlptown/bert-base-multilingual-uncased-sentiment')
# Estabelecer ligação á base de dados
Conexao.estabelecer()

# Dicionário com frases motivacionais por emoção em relação ao comentario do participante
textos = {
    "1 star": "Sentimos que este evento não correspondeu às expectativas. Agradecemos o seu feedback para melhorar.",
    "2 stars": "Percebemos que houve pontos negativos. A sua opinião é importante para evoluirmos.",
    "3 stars": "Obrigado pela sua participação. Continuaremos a trabalhar para oferecer melhores experiências.",
    "4 stars": "Ficamos felizes que tenha gostado! Esperamos vê-lo(a) novamente em futuros eventos.",
    "5 stars": "Que bom que adorou o evento! A sua satisfação é o que nos motiva a continuar a organizar momentos inesquecíveis."
}

# Inicializa o serviço flask
app = Flask(__name__)
# Chave criada para utilizar as mensagens flash
app.secret_key = 'uma_chave_secreta_qualquer_muito_segura'

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Classe User para o Flask-Login
class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.username = user_data['username']
        self.role = user_data['role']

    @staticmethod
    def get(user_id):
        user_data = Conexao.TrabalhoHelder_Utilizadores.find_one({"_id": ObjectId(user_id)})
        if not user_data:
            return None
        return User(user_data)

# Configuração do user_loader
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Decorador para proteger rotas e verificar papel
def role_required(role=None):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            if role and current_user.role != role:
                return "Acesso negado", 403
            return f(*args, **kwargs)
        return wrapped
    return decorator

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user_data = Conexao.TrabalhoHelder_Utilizadores.find_one({"username": username})
        if user_data and check_password_hash(user_data['password'], password):
            user = User(user_data)
            login_user(user)

            if user.role == 'organizador':
                return redirect(url_for('index_organizador'))
            else:
                return redirect(url_for('index_Aluno'))
        else:
            flash("Utilizador ou senha inválidos.", "error")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        if role not in ['aluno', 'organizador']:
            flash("Tipo inválido.", "error")
            return render_template('register.html')

        if Conexao.TrabalhoHelder_Utilizadores.find_one({"username": username}):
            flash("O utilizador já existe.", "error")
            return render_template('register.html')

        hashed = generate_password_hash(password)
        Conexao.TrabalhoHelder_Utilizadores.insert_one({
            "username": username,
            "password": hashed,
            "role": role
        })

        flash("Conta criada com sucesso! Pode fazer login agora.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
@role_required()
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/index_organizador', methods=["GET"])
@role_required('organizador')
def index_organizador():
    nome_organizador = current_user.username
    eventos = list(Conexao.TrabalhoHelder_Eventos.find({"Organizador": nome_organizador}))
    return render_template('index_organizador.html', inf=eventos, nome_organizador=nome_organizador)


@app.route('/index_Aluno', methods=["GET"])
@role_required('aluno')
def index_Aluno():
    inf = list(Conexao.TrabalhoHelder_Eventos.find({}))
    nome_aluno = current_user.username
    return render_template('index_Aluno.html', inf=inf, nome_aluno=nome_aluno)

@app.route('/PaginaPDFs/<string:_id>', methods=['GET'])
@role_required('aluno')
def PaginaPDFs(_id):
    evento_pdf = Conexao.TrabalhoHelder_Eventos.find_one({"_id": ObjectId(_id)})
    if not evento_pdf:
        flash("Evento não encontrado!", "error")
        return redirect(url_for("EventosFinalizados"))

    username = current_user.username

    # Verificar se o username está na lista de participantes que entraram
    participou = any(
        p.get('Nome') == username
        for p in evento_pdf.get("Entradas de Participantes", [])
    )

    if not participou:
        flash("Você precisa entrar no evento antes de aceder aos certificados!", "error")
        return redirect(url_for("EventosFinalizados"))

    return render_template("PaginaPDFs.html", evento_inf=evento_pdf)

@app.route('/PaginaPDFs/downloadCertificado/<string:_id>', methods=['GET'])
@role_required('aluno')
def downloadCertificado(_id):
    """Rota otimizada apenas para download do certificado"""
    try:
        evento_pdf = Conexao.TrabalhoHelder_Eventos.find_one({"_id": ObjectId(_id)})
        if not evento_pdf:
            return "Evento não encontrado", 404

        pdf_buffer = gerarPDFs(evento_pdf)
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=f"certificado_{evento_pdf['Nome']}.pdf",
            mimetype="application/pdf"
        )
    except Exception as e:
        app.logger.error(f"Erro ao gerar PDF: {str(e)}")
        return "Erro ao gerar certificado", 500

@app.route('/PaginaPDFs/downloadPDFidioma/<string:_id>', methods=["POST"])
@role_required('aluno')
def downloadPDFidioma(_id):
    evento_pdf = Conexao.TrabalhoHelder_Eventos.find_one({"_id": ObjectId(_id)})
    idioma = request.form["idioma"]

    if idioma == "pt":
        pdf_pt = gerarPDFs(evento_pdf)
        return send_file(pdf_pt, as_attachment=True, download_name="relatorio_evento_pt.pdf", mimetype="application/pdf")

    pdf_normal = gerarPDFs(evento_pdf)
    texto_original = extrair_texto_pdf(pdf_normal)
    translator = Translator()
    texto_traduzido = translator.translate(texto_original, src="pt", dest=idioma).text
    pdf = criar_pdf(texto_traduzido)
    return send_file(pdf, as_attachment=True, download_name=f"pdf_traduzido_{idioma}.pdf", mimetype="application/pdf")

def get_local_ip():
    # Retorna o IP local da máquina na rede (ex: 192.168.1.100)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))  # IP dummy para pegar IP local real
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

@app.route('/PaginaPDFs/downloadPDFQRCcode/<string:_id>')
@role_required('aluno')
def downloadPDFQRCcode(_id):
    try:
        # Verificar se o evento existe
        evento_pdf = Conexao.TrabalhoHelder_Eventos.find_one({"_id": ObjectId(_id)})
        if not evento_pdf:
            return jsonify({"status": "error", "message": "Evento não encontrado"}), 404

        # Criar dados mínimos para o QR Code (sem gerar PDF ainda)
        qr_data = {
            "evento_id": str(evento_pdf['_id']),
            "nome_evento": evento_pdf['Nome'],
            "action": "download_certificado"
        }

        # Gerar QR Code pequeno e rápido
        qr = qrcode.QRCode(
            version=1,  # Versão menor possível
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=6,  # Tamanho reduzido
            border=2
        )
        qr.add_data(json.dumps(qr_data))
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        return jsonify({
            "status": "success",
            "qr_code": base64.b64encode(img_byte_arr.getvalue()).decode('utf-8'),
            "qr_data": {
                "evento_id": str(evento_pdf['_id']),
                "nome_evento": evento_pdf['Nome']
            }
        })

    except Exception as e:
        app.logger.error(f"Erro ao gerar QR Code: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/EventosFinalizados', methods=["GET"])
@role_required('aluno')
def EventosFinalizados():
    nome_aluno = current_user.username
    inf = list(Conexao.TrabalhoHelder_Eventos.find({}))
    return render_template('EventosFinalizados.html', inf=inf, nome_aluno=nome_aluno)

@app.route('/AdicionarComentario/<string:_id>', methods=["POST"])
@role_required('aluno')
def AdicionarComentarios(_id):
    evento_id = Conexao.TrabalhoHelder_Eventos.find_one({"_id": ObjectId(_id)})
    dados = request.form
    comentario = dados.get("comentario")
    nif = int(dados.get("nif"))

    tratar_mensagem = classificacao_emocional(comentario)[0]
    mensagem = textos.get(tratar_mensagem['label'])

    for participantes in evento_id["Entradas de Participantes"]:
        if participantes["NIF"] == nif:
            if not participantes.get("Comentario"):
                comentario_ojt = Participante(participantes["Nome"], participantes["Idade"], participantes["NIF"], participantes["Telefone"])
                comentario_ojt.adicionar_comentario(comentario)
                comentario_ojt.adicionar_comentario_emocao(mensagem)
                json_comentario = {
                    "Nome": comentario_ojt.get_nome(),
                    "Idade": comentario_ojt.get_idade(),
                    "Telefone": comentario_ojt.get_telefone(),
                    "NIF": comentario_ojt.get_nif(),
                    "Comentario": comentario_ojt.get_comentario(),
                    "Comentario_BOT": comentario_ojt.get_comentario_emocao()
                }
                Conexao.TrabalhoHelder_Eventos.update_one(
                    {"_id": ObjectId(_id)},
                    {"$pull": {"Entradas de Participantes": {"NIF": nif}}}
                )
                Conexao.TrabalhoHelder_Eventos.update_one(
                    {"_id": ObjectId(_id)},
                    {"$push": {"Entradas de Participantes": json_comentario}}
                )
                flash("Comentário adicionado com sucesso!", "success")
                return redirect(url_for("EventosFinalizados"))
            else:
                flash("Participante já deixou o seu comentário ou não entrou no evento!", "error")
                return redirect(url_for("EventosFinalizados"))

    flash("Participante não encontrado no evento.", "error")
    return redirect(url_for("EventosFinalizados"))

@app.route('/EventosDecorrer', methods=["GET"])
@role_required('aluno')
def EventosDecorrer():
    nome_aluno = current_user.username
    inf = list(Conexao.TrabalhoHelder_Eventos.find({}))
    return render_template('EventosDecorrer.html', inf=inf, nome_aluno=nome_aluno)

@app.route('/EntrarEvento/<string:_id>', methods=["GET", "POST"])
@role_required('aluno')
def EntrarEvento(_id):
    evento_inf = Conexao.TrabalhoHelder_Eventos.find_one({"_id": ObjectId(_id)})

    if request.method == "POST":
        dados = request.form
        nif = int(dados.get("nif"))
        codigo = int(dados.get("codigo"))

        for i in evento_inf.get("Entradas de Participantes", []):
            if i["NIF"] == nif:
                flash("Já entrou no evento.", "error")
                return redirect(request.url)

        for participante in evento_inf.get("Participantes", []):
            if participante["NIF"] == nif:
                if participante["Codigo de Acesso"] == codigo:
                    entrada = Participante(participante["Nome"], participante["Idade"], nif, participante["Telefone"])
                    json_entrada = {
                        "Nome": entrada.get_nome(),
                        "Idade": entrada.get_idade(),
                        "Telefone": entrada.get_telefone(),
                        "NIF": entrada.get_nif(),
                    }

                    Conexao.TrabalhoHelder_Eventos.update_one(
                        {"_id": ObjectId(_id)},
                        {"$push": {"Entradas de Participantes": json_entrada}}
                    )

                    flash("Entrou com sucesso no evento!", "success")
                    return redirect(url_for("EventosDecorrer"))
                else:
                    flash("Código de acesso incorreto.", "error")
                    return redirect(request.url)

        flash("NIF não encontrado.", "error")
        return redirect(request.url)

    return render_template("EntrarEvento.html", evento=evento_inf)

@app.route('/ComprarBilhete/<string:_id>', methods=["POST", "GET"])
@role_required('aluno')
def ComprarBilhete(_id):
    evento = Conexao.TrabalhoHelder_Eventos.find_one({"_id": ObjectId(_id)})
    capacidade_maxima = int(evento["Capacidade de Participantes"])
    participantes_atuais = len(evento.get("Participantes", []))

    nome_aluno = current_user.username

    if participantes_atuais >= capacidade_maxima:
        flash("Evento esgotado! Não há mais bilhetes disponíveis!", "error")
        return redirect(url_for("index_Aluno"))

    if request.method == "POST":
        dados = request.form
        nome = dados.get("nome")
        idade = int(dados.get("idade"))
        nif = int(dados.get("nif"))
        telefone = int(dados.get("telefone"))

        for i in evento["Participantes"]:
            if nif == i["NIF"]:
                flash("Participante com esse NIF já contem bilhete de entrada para este evento", "error")
                return render_template("ComprarBilhete.html", evento=evento, nome_aluno=nome_aluno)

        for i in evento["Participantes"]:
            if telefone == i["Telefone"]:
                flash("Numero de Telefone já inserido, por favor insira um numero diferente!", "error")
                return render_template("ComprarBilhete.html", evento=evento, nome_aluno=nome_aluno)

        if idade <= evento.get("Condição da Idade de Participação"):
            flash("Não contem idade minima para entrar neste evento!", "error")
            return render_template("ComprarBilhete.html", evento=evento, nome_aluno=nome_aluno)

        bilhete = Participante(nome, idade, nif, telefone)
        json_bilhete_inf = {
            "Nome": bilhete.get_nome(),
            "Idade": bilhete.get_idade(),
            "NIF": bilhete.get_nif(),
            "Telefone": bilhete.get_telefone(),
            "Codigo de Acesso": bilhete.codigo_acesso()
        }

        Conexao.TrabalhoHelder_Eventos.update_one(
            {"_id": ObjectId(_id)},
            {"$push": {"Participantes": json_bilhete_inf}}
        )

        return render_template("ComprarBilhete.html", inf=json_bilhete_inf, mostrar_modal=True, evento=evento, nome_aluno=nome_aluno)

    return render_template("ComprarBilhete.html", evento=evento, nome_aluno=nome_aluno)

@app.route('/AdicionarEventosCSV', methods=["POST"])
@role_required('organizador')
def AdicionarEventosCSV():
    organizador_logado = current_user.username
    csv_file = request.files["filecsv"]
    reader = csv.reader(io.StringIO(csv_file.stream.read().decode("utf-8")))

    csv_inf = []
    next(reader)
    for i in reader:
        # Verificar se o organizador no CSV é o mesmo que está logado
        if i[4] != organizador_logado:
            flash(f"Erro: Você não tem permissão para adicionar eventos do organizador {i[4]}", "error")
            continue

        csv_linha_obj = Evento(i[0], i[1], i[2], i[3], i[4], i[5], int(i[6]), int(i[7]))
        for j in i[8].split(";"):
            nome, hora_inicio, hora_fim, local, capacidade_atividade, tipo_atividade = j.split("|")
            atividade = Atividades(nome, hora_inicio, hora_fim, local, capacidade_atividade, tipo_atividade)
            csv_linha_obj.adicionar_atividades(atividade)

        json_csv = {
            "Nome": csv_linha_obj.get_nome(),
            "Descrição": csv_linha_obj.get_descricao(),
            "Data de Inicio do Evento": csv_linha_obj.get_data_inicio(),
            "Data do Fim do Evento": csv_linha_obj.get_data_fim(),
            "Organizador": csv_linha_obj.get_organizador(),
            "Tipo de Evento": csv_linha_obj.get_tipo(),
            "Capacidade de Participantes": csv_linha_obj.get_capacidade(),
            "Condição da Idade de Participação": csv_linha_obj.get_condicao_idade(),
            "Atividades": [{
                "Atividade": i.get_atividade(),
                "Hora de Inicio": i.get_hora_inicio(),
                "Hora do Fim": i.get_hora_fim(),
                "Local da Atividade": i.get_local_atividade(),
                "Capacidade da Atividade": i.get_capacidade(),
                "Tipo de Atividade": i.get_tipo_atividade(),
                "Lista de Inscritos": [],
            } for i in csv_linha_obj.get_atividades()],
            "Participantes": [],
            "Entradas de Participantes": []
        }
        csv_inf.append(json_csv)

    if csv_inf:
        Conexao.TrabalhoHelder_Eventos.insert_many(csv_inf)
        flash("CSV inserido com sucesso!", "success")
    else:
        flash("Erro ao carregar a informação do ficheiro CSV!", "error")
    return redirect(url_for("index_organizador"))

@app.route('/RemoverEvento/<string:_id>', methods=["DELETE"])
@role_required('organizador')
def RemoverEvento(_id):
    evento = Conexao.TrabalhoHelder_Eventos.find_one({"_id": ObjectId(_id)})

    # Verificar se o organizador do evento é o mesmo que está logado
    if evento["Organizador"] != current_user.username:
        flash("Você não tem permissão para remover este evento", "error")
        return redirect(url_for("index_organizador"))

    Conexao.TrabalhoHelder_Eventos.delete_one({"_id": ObjectId(_id)})
    flash("Evento removido com sucesso!", "success")
    return redirect(url_for("index_organizador"))

@app.route('/EditarEventos/<string:_id>', methods=['GET', 'POST'])
@role_required('organizador')
def AlterarEvento(_id):
    evento_inf = Conexao.TrabalhoHelder_Eventos.find_one({"_id": ObjectId(_id)})

    # Verificar se o organizador do evento é o mesmo que está logado
    if evento_inf["Organizador"] != current_user.username:
        flash("Você não tem permissão para editar este evento", "error")
        return redirect(url_for("index_organizador"))

    if request.method == 'GET':
        return render_template("EditarEventos.html", evento=evento_inf)

    elif request.method == 'POST':
        nome = request.form.get('nome')
        descricao = request.form.get('descricao')
        data_inicio = request.form.get('data_inicio')
        data_fim = request.form.get('data_fim')
        # Manter o organizador original (não permitir alteração)
        organizador = evento_inf["Organizador"]
        tipo = request.form.get('tipo')
        capacidade = int(request.form.get('capacidade'))
        condicao = int(request.form.get('condicao'))
        atividade = request.form.getlist('atividade')
        hora_inicio = request.form.getlist('hora_inicio')
        hora_fim = request.form.getlist('hora_fim')
        local_atividade = request.form.getlist('local_atividade')
        capacidade_atividade = request.form.getlist('capacidade_atividade')
        tipo_atividade = request.form.getlist('tipo_atividade')

        evento = Evento(nome, descricao, data_inicio, data_fim, organizador, tipo, capacidade, condicao)
        atividades = []

        for atividade, inicio, fim, local, capacidade, tipo in zip(atividade, hora_inicio, hora_fim, local_atividade, capacidade_atividade, tipo_atividade):
            atividade_obj = Atividades(atividade, inicio, fim, local, capacidade, tipo)
            atividades.append(atividade_obj)

        for i in atividades:
            evento.adicionar_atividades(i)

        json_update = {
            "Nome": evento.get_nome(),
            "Descrição": evento.get_descricao(),
            "Data de Inicio do Evento": evento.get_data_inicio(),
            "Data do Fim do Evento": evento.get_data_fim(),
            "Organizador": organizador,
            "Tipo de Evento": evento.get_tipo(),
            "Capacidade de Participantes": evento.get_capacidade(),
            "Condição da Idade de Participação": evento.get_condicao_idade(),
            "Atividades": [{
                "_id": ObjectId(),
                "Atividade": i.get_atividade(),
                "Hora de Inicio": i.get_hora_inicio(),
                "Hora do Fim": i.get_hora_fim(),
                "Local da Atividade": i.get_local_atividade(),
                "Capacidade da Atividade": i.get_capacidade(),
                "Tipo da Atividade": i.get_tipo_atividade(),
                "Lista de Inscritos": []
            } for i in evento.get_atividades()],
            "Participantes": evento_inf.get("Participantes", []),
            "Entradas de Participantes": evento_inf.get("Entradas de Participantes", [])
        }

        Conexao.TrabalhoHelder_Eventos.update_one({"_id": ObjectId(_id)}, {"$set": json_update})
        flash("Evento atualizado com sucesso!", "success")
        return redirect(url_for("index_organizador"))

@app.route('/AdicionarEventos', methods=['GET', 'POST'])
@role_required('organizador')
def AdicionarEventos():
    if request.method == 'POST':
        nome = request.form["nome"]
        descricao = request.form["descricao"]
        date_inicio = request.form["data_inicio"]
        date_fim = request.form["data_fim"]
        # Pegar o nome do organizador do usuário logado
        organizador = current_user.username
        tipo = request.form["tipo"]
        capacidade = int(request.form["capacidade_evento"])
        condicao_idade = int(request.form["condicao"])
        atividade = request.form.getlist("atividade")
        hora_inicio = request.form.getlist("hora_inicio")
        hora_fim = request.form.getlist("hora_fim")
        local = request.form.getlist("local_atividade")
        capacidade_atividade = request.form.getlist("capacidade_atividade")
        tipo_atividade = request.form.getlist("tipo_atividade")

        atividades_lista = []
        for a, inicio, fim, l, cap, t in zip(atividade, hora_inicio, hora_fim, local, capacidade_atividade, tipo_atividade):
            atividade_obj = Atividades(a, inicio, fim, l, cap, t)
            atividades_lista.append(atividade_obj)

        evento = Evento(nome, descricao, date_inicio, date_fim, organizador, tipo, capacidade, condicao_idade)

        for i in atividades_lista:
            evento.adicionar_atividades(i)

        json = {
            "Nome": evento.get_nome(),
            "Descrição": evento.get_descricao(),
            "Data de Inicio do Evento": evento.get_data_inicio(),
            "Data do Fim do Evento": evento.get_data_fim(),
            "Organizador": organizador,
            "Tipo de Evento": evento.get_tipo(),
            "Capacidade de Participantes": evento.get_capacidade(),
            "Condição da Idade de Participação": evento.get_condicao_idade(),
            "Atividades": [{
                "Atividade": i.get_atividade(),
                "Hora de Inicio": i.get_hora_inicio(),
                "Hora do Fim": i.get_hora_fim(),
                "Local da Atividade": i.get_local_atividade(),
                "Capacidade da Atividade": i.get_capacidade(),
                "Tipo da Atividade": i.get_tipo_atividade(),
                "Lista de Inscritos": []
            } for i in evento.get_atividades()],
            "Participantes": [],
            "Entradas de Participantes": []
        }

        Conexao.TrabalhoHelder_Eventos.insert_one(json)
        flash("Evento inserido com sucesso!", "success")
        return redirect(url_for("index_organizador"))

    return render_template('AdicionarEventos.html', enviado=False, nome_organizador=current_user.username)

if __name__ == '__main__':
    app.run(debug=True)