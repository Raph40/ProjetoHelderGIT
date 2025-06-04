from bson import ObjectId
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from EventosOOP import Evento
from AtividadesOOP import Atividades
from ParticipanteOOP import Participante
from Connects import Conexao
import csv
from transformers import pipeline
import threading
from CriarPDF import *
from googletrans import Translator

#Modelo para a emoção da mensagem
classificacao_emocional = pipeline('sentiment-analysis', model='nlptown/bert-base-multilingual-uncased-sentiment')
#Estabelecer ligação á base de dados
Conexao.estabelecer()

#Dicionário com frases motivacionais por emoção em relação ao comentario do participante
textos = {
    "1 star": "Sentimos que este evento não correspondeu às expectativas. Agradecemos o seu feedback para melhorar.",
    "2 stars": "Percebemos que houve pontos negativos. A sua opinião é importante para evoluirmos.",
    "3 stars": "Obrigado pela sua participação. Continuaremos a trabalhar para oferecer melhores experiências.",
    "4 stars": "Ficamos felizes que tenha gostado! Esperamos vê-lo(a) novamente em futuros eventos.",
    "5 stars": "Que bom que adorou o evento! A sua satisfação é o que nos motiva a continuar a organizar momentos inesquecíveis."
}

def ThreadEntrarEvento(_id, nif, codigo):
    """
        Thread para possibilitar a entrada de varias pessoas no evento

        Argumentos:
            _id(ObjectID): id do evento escolhido para entrar
            nif(int): Numero de Identificação Fiscal do utilizador
            codigo(int): Codigo de acesso ao evento

        Returns:
            Mensagens de erros e sucessos do codigo(Não funcional)
    """
    #Cria um dicionario com toda a informação conrespondente ao evento com esse id
    evento_entrada = Conexao.collection_Eventos.find_one({"_id": ObjectId(_id)})

    #Verifica se o bilhete já deu entrada no evento com o nif
    for i in evento_entrada["Entradas de Participantes"]:
        #Verifica se o nif fui utilizado para entrar no evento
        if i["NIF"] == nif:
            #Mensagem de erro(Não funcional)
            return ({"status": "error", "message": "Já entrou no evento"})

    #Vai percorrer a lista de participantes deste evento
    for participante in evento_entrada["Participantes"]:
        #Vai verificar o nif introduzido pelo utilizador está contido na lista de participantes desse evento
        if participante["NIF"] == nif:
            #Vai verificar se o codigo de acesso está contido na lista de participantes e com conrespondencia ao nif introduzido pelo utilizador
            if participante["Codigo de Acesso"] == codigo:
                #Cria o objeto para utilizar a estrutura de dados para o controlo da informação
                entrada = Participante(participante["Nome"],participante["Idade"],nif,participante["Telefone"])
                #Cria um dicionario com a informação para inserir na base de dados
                json_entrada = {
                    "Nome": entrada.get_nome(),
                    "Idade": entrada.get_idade(),
                    "Telefone": entrada.get_telefone(),
                    "NIF": entrada.get_nif(),
                }
                #Como a coluna já foi criada, faz-se push para colocar a informação dentro da lista conrespondente ao evento com esse id
                Conexao.collection_Eventos.update_one(
                    {"_id": ObjectId(_id)},
                    {"$push": {"Entradas de Participantes": json_entrada}}
                )
                #Mensagem de sucesso(Não funcional)
                return ({"status": "success", "message": "Entrou com sucesso no evento!"})
            else:
                #Mensagem de erro(Não funcional)
                return ({"status": "danger", "message": "Código de acesso incorreto."})

    #Se não encontrou o NIF em nenhum participante
    return ({"status": "danger", "message": "NIF não encontrado."})


#Inicializa o serviço flask
app = Flask(__name__)
#Chave criada para utilizar as mensagens flash
app.secret_key = 'uma_chave_secreta_qualquer_muito_segura'

@app.route('/', methods=["GET"])
def index():
    """
        Processa toda informação contida na base de dados

        Return:
            Vai renderizar a pagina index com variaveis que contem informação da base de dados
    """
    #Guarda a informação toda a informação da base de dados dentro de uma lista de dicionarios
    inf = list(Conexao.collection_Eventos.find({}))
    #Vai retornar o template com a informação da base de dados
    return render_template('index.html', inf=inf)

@app.route('/PaginaPDFs/<string:_id>', methods=['GET'])
def PaginaPDFs(_id):
    """
        Processa toda a informação relacionada com o id do evento escolhido pelo utilizador

        Argumentos:
            _id(ObjectID): id do evento escolhido para adquirir informação da mesma

        Return:
            Vai renderizar a pagina PaginaPDFs com variaveis que contem informação do evento na base de dados
    """
    #Guarda a informação num dicionario conrespondente ao id do evento escolhido pelo utilizador
    evento_pdf = Conexao.collection_Eventos.find_one({"_id": ObjectId(_id)})
    #Vai retornar o template com a informação deste evento da base de dados
    return render_template("PaginaPDFs.html", evento_inf=evento_pdf)

@app.route('/PaginaPDFs/downloadAnonimizado/<string:_id>', methods=['GET'])
def downloadAnonimizado(_id):
    """
        Permite realizar o download do ficheiro PDF anonimizado escolhido pelo utilizador

        Argumentos:
            _id(ObjectID): id do evento escolhido para adquirir informação da mesma

        Return:
            Permite realizar download do PDF anonimizado
    """
    #Guarda toda a informação num dicionario conrespondente ao evento selecionado
    evento_pdf = Conexao.collection_Eventos.find_one({"_id": ObjectId(_id)})
    #Chama a função para criar o PDF com a informação do evento escolhida pelo utilizador
    pdf_normal = gerarPDFs(evento_pdf)
    #Chama a função que vai utilizar a informação do pdf e anonimizar a informação sensivel
    pdf_anonimizado = anonimizar_pdf(pdf_normal)
    #Retorna com o ficheiro para o utilizador poder realizar o download
    return send_file(pdf_anonimizado, as_attachment=True, download_name=f"relatorio_{evento_pdf.get('Nome')}_anonimizado.pdf", mimetype="application/pdf")

@app.route('/PaginaPDFs/downloadPDFidioma/<string:_id>', methods=["POST"])
def downloadPDFidioma(_id):
    """
        Permite realizar o download do PDF com os idiomas pt(Portugues), it(Italiano) e en(Ingles)

        Argumentos:
           _id(ObjectID): id do evento escolhido para adquirir informação da mesma

        Returns:
            Permite realizar download dos PDFs com os idiomas selecionados
    """
    #Guarda toda a informação num dicionario conrespondente ao evento selecionado
    evento_pdf = Conexao.collection_Eventos.find_one({"_id": ObjectId(_id)})
    #Guarda o idioma escolhido pelo utilizador
    idioma = request.form["idioma"]
    #Se o idioma escolhido pelo utilizador for pt(Portugues)
    if idioma == "pt":
        #Gera o PDF original, realizado com o idioma portugues
        pdf_pt = gerarPDFs(evento_pdf)
        #Returna o ficheiro PDF original
        return send_file(pdf_pt, as_attachment=True, download_name="relatorio_evento_pt.pdf", mimetype="application/pdf")

    #Para os outros idiomas, vai gerar o pdf na mesma com o idioma original que é portugues
    pdf_normal = gerarPDFs(evento_pdf)
    #Vai extrair o texto desse pdf gerado
    texto_original = extrair_texto_pdf(pdf_normal)
    #É utilizado a biblioteca googleTranslator para fazer a tradução do texto extraido do pdf
    translator = Translator()
    #Vai agarrar no texto e vai traduzir com o idioma que o utilizador escolheu
    texto_traduzido = translator.translate(texto_original, src="pt", dest=idioma).text
    #Cria um pdf simples com as informações traduzidas
    pdf = criar_pdf(texto_traduzido)
    #Returna o ficheiro PDF com o idioma escolhido e com a referencia de idioma no nome do ficheiro
    return send_file(pdf, as_attachment=True, download_name=f"pdf_traduzido_{idioma}.pdf", mimetype="application/pdf")

@app.route('/EventosFinalizados', methods=["GET"])
def EventosFinalizados():
    """
        Processa toda informação contida na base de dados, para simular a pagina dos eventos simulados

        Return:
            Vai renderizar a pagina EventosFinalizados com variaveis que contem informação da base de dados
    """
    #Guarda a informação toda a informação da base de dados dentro de uma lista de dicionarios
    inf = list(Conexao.collection_Eventos.find({}))
    #Vai retornar o template com a informação da base de dados
    return render_template('EventosFinalizados.html', inf=inf)

@app.route('/AdicionarComentario/<string:_id>', methods=["POST"])
def AdicionarComentarios(_id):
    """
        No fim do evento permite adicionar um comentario sobre o evento e utilizar o pipeline para verificar a
            emoção desse comentario para verificar se o evento teve uma boa receção ou uma má receção dos participantes

        Argumentos:
            _id(ObjectID): id do evento escolhido para adquirir informação da mesma

        Return:
            Redirecionamento para a pagina especifica depois de ter feito as operações
    """
    #Guarda toda a informação num dicionario conrespondente ao evento selecionado
    evento_id = Conexao.collection_Eventos.find_one({"_id": ObjectId(_id)})
    #Faz request dos dados inseridos na pagina html
    dados = request.form
    #Guarda o valor inserido no html
    comentario = dados.get("comentario")
    nif = int(dados.get("nif"))
    #Vai tratar o comentario inserido pelo utilizador
    tratar_mensagem = classificacao_emocional(comentario)[0]
    #Vai guardar a informaçao tratada para guardar na base de dados
    mensagem = textos.get(tratar_mensagem['label'])

    #Este segmento do codigo serve para verificar se o participante entrou no evento e se já deixou um comentario
    for participantes in evento_id["Entradas de Participantes"]:
        #Verifica se o participante já deu entrada no evento
        if participantes["NIF"] == nif:
            #Se está no evento e não deixou um comentario sobre o evento
            if not participantes.get("Comentario"):
                #Cria o objeto com a informação retirada da lista "Entradas de Participantes", para utilizar a estrutura de dados
                comentario_ojt = Participante(participantes["Nome"],participantes["Idade"],participantes["NIF"],participantes["Telefone"])
                #Adiciona o comentario do utilizador ao objeto criado
                comentario_ojt.adicionar_comentario(comentario)
                #Adiciona o comentario tratado pelo pipeline ao objeto criado
                comentario_ojt.adicionar_comentario_emocao(mensagem)
                #Cria o dicionario com a nova informação para guardar na base de dados
                json_comentario = {
                    "Nome": comentario_ojt.get_nome(),
                    "Idade": comentario_ojt.get_idade(),
                    "Telefone": comentario_ojt.get_telefone(),
                    "NIF": comentario_ojt.get_nif(),
                    "Comentario": comentario_ojt.get_comentario(),
                    "Comentario_BOT": comentario_ojt.get_comentario_emocao()
                }
                #Remove a informação antiga pelo nif do participante
                Conexao.collection_Eventos.update_one(
                    {"_id": ObjectId(_id)},
                    {"$pull": {"Entradas de Participantes": {"NIF": nif}}}
                )
                #Adiciona a nova informação com os comentarios do participante
                Conexao.collection_Eventos.update_one(
                    {"_id": ObjectId(_id)},
                    {"$push": {"Entradas de Participantes": json_comentario}}
                )
                #Mostra esta mensagem de sucesso
                flash("Comentário adicionado com sucesso!", "success")
                #Redireciona para a pagina html Eventos finalizados
                return redirect(url_for("EventosFinalizados"))
            else:
                #Se o participante já deixou o seu comentario, aparece esta mensagem de erro
                flash("Participante já deixou o seu comentário ou não entrou no evento!", "error")
                #Redireciona para a pagina html Eventos finalizados
                return redirect(url_for("EventosFinalizados"))
    #Caso o NIF não é encontrado na lista "Entradas de Participantes", mostra esta mensagem de erro
    flash("Participante não encontrado no evento.", "error")
    return redirect(url_for("EventosFinalizados"))


@app.route('/EventosDecorrer', methods=["GET"])
def EventosDecorrer():
    """
        Processa toda informação contida na base de dados, para simular a pagina dos eventos a decorrer

        Return:
            Vai renderizar a pagina EventosFinalizados com variaveis que contem informação da base de dados
    """
    #Guarda a informação toda a informação da base de dados dentro de uma lista de dicionarios
    inf = list(Conexao.collection_Eventos.find({}))
    #Vai retornar o template com a informação da base de dados
    return render_template('EventosDecorrer.html', inf=inf)

@app.route('/EntrarEvento/<string:_id>', methods=["GET","POST"])
def EntrarEvento(_id):
    """
        Faz a Validadção dos dados inseridos pelo utilizador para entrar no evento pretendido e carrega a informação sobre o evento
            escolhida pelo utilizador a partir do _id do evento

        Argumentos:
            _id(ObjectID): id do evento escolhido para adquirir informação da mesma

        Return:
            Redireciona para a pagina EventosDecorrer quando as operações estiverem realizadas pelos threads
            Vai renderizar a pagina EntrarEvento com variaveis que contem informação da base de dados

    """
    #Guarda toda a informação num dicionario conrespondente ao evento selecionado
    evento_inf = Conexao.collection_Eventos.find_one({"_id": ObjectId(_id)})
    #Se o metodo do request é POST
    if request.method == "POST":
        #Faz request dos dados inseridos na pagina html
        dados = request.form
        #Guarda o valor inserido no html
        nif = int(dados.get("nif"))
        codigo = int(dados.get("codigo"))

        #Para permitir a entrada de varios participantes no evento em simultâneo
        threadEvento = threading.Thread(target=ThreadEntrarEvento, args=(_id, nif, codigo))
        #Aqui inicia-se o thread
        threadEvento.start()

        #Redireciona para a pagina EventosDecorrer, o thread fica a realizar as atividades pedidas, não limitando este return
        return redirect(url_for("EventosDecorrer"))
    else:
        #Se o metodo do request é GET, é renderizada a pagina EntrarEvento com as informações da base de dados
        return render_template("EntrarEvento.html", evento=evento_inf)

@app.route('/ComprarBilhete/<string:_id>', methods=["POST", "GET"])
def ComprarBilhete(_id):
    """
        Faz a validação na compra de bilhetes para o evento escolhido pelo utilizador e carrega a informação sobre o evento
            escolhida pelo utilizador a partir do _id do evento

        Argumentos:
            _id(ObjectID): id do evento escolhido para adquirir informação da mesma

        Return:
            Redireciona para a pagina index caso haja erro nas validações das capacidades maxima do evento
            Vai renderizar a pagina ComprarBilhete com variaveis que contem informação da base de dados
    """
    #Guarda toda a informação num dicionario conrespondente ao evento selecionado
    evento = Conexao.collection_Eventos.find_one({"_id": ObjectId(_id)})
    #Vai buscar a capcacidade maxima do evento escolhido
    capacidade_maxima = int(evento["Capacidade de Participantes"])
    #Vai contar contar o numero de participantes inscritos(dicionarios)
    participantes_atuais = len(evento.get("Participantes", []))

    #Verifica se o numero de participantes atuais é maior ao numero de capacidade maxima do evento
    if participantes_atuais >= capacidade_maxima:
        #Mostra esta mensagem de erro
        flash("Evento esgotado! Não há mais bilhetes disponíveis!", "error")
        #Redireciona para a pagina index
        return redirect(url_for("index"))

    #Se o metodo do request é POST
    if request.method == "POST":
        #Faz request dos dados inseridos na pagina html
        dados = request.form
        #Guarda o valor inserido no html
        nome = dados.get("nome")
        idade = int(dados.get("idade"))
        nif = int(dados.get("nif"))
        telefone = int(dados.get("telefone"))

        #Vai percorrer a lista de participantes
        for i in evento["Participantes"]:
            #Verifica se o participante já comprou o bilhete com o nif presente na lista "Participantes"
            if nif == i["NIF"]:
                #Mostra a mensagem de erro caso acha o nif esteja na lista "Participantes"
                flash("Participante com esse NIF já contem bilhete de entrada para este evento", "error")
                #Renderizada a pagina ComprarBilhete com as informações da base de dados
                return render_template("ComprarBilhete.html", evento=evento)

        #Vai percorrer a lista de participantes
        for i in evento["Participantes"]:
            #Verifica se o participante já utilizou o mesmo numero de telefone para aquisição do bilhete presente na lista "Participantes"
            if telefone == i["Telefone"]:
                #Mostra a mensagem de erro caso acha o numero de telefone repetido na lista "Participantes"
                flash("Numero de Telefone já inserido, por favor insira um numero diferente!", "error")
                #Renderizada a pagina ComprarBilhete com as informações da base de dados
                return render_template("ComprarBilhete.html", evento=evento)

        #Verifica se a idade do utilizador a comprar o bilhete cumpre com os requisitos do evento
        if idade <= evento.get("Condição da Idade de Participação"):
            #Mostra a mensagem de erro caso a idade do utilizador não cumpre com os requisitos do evento
            flash("Não contem idade minima para entrar neste evento!", "error")
            #Renderizada a pagina ComprarBilhete com as informações da base de dados
            return render_template("ComprarBilhete.html", evento=evento)

        #Cria o objeto com as informações inseridas pelo utilizador, para verificar a estrutura dos dados
        bilhete = Participante(nome, idade, nif, telefone)

        #Cria o dicionario com a informação do utilizador ao fazer a compra do bilhete
        json_bilhete_inf = {
            "Nome": bilhete.get_nome(),
            "Idade": bilhete.get_idade(),
            "NIF": bilhete.get_nif(),
            "Telefone": bilhete.get_telefone(),
            "Codigo de Acesso": bilhete.codigo_acesso()
        }

        #Como a lista de participantes é criada quando o evento é adicionado,
        #nesta parte vai fazer um push desse dicionario para guardar as informações conrespondentes á compra do bilhete
        Conexao.collection_Eventos.update_one(
            {"_id": ObjectId(_id)},
            {"$push": {"Participantes": json_bilhete_inf}}
        )

        #Renderizada a pagina ComprarBilhete com as informações da base de dados
        return render_template("ComprarBilhete.html", inf=json_bilhete_inf, mostrar_modal=True, evento=evento)
    #Renderizada a pagina ComprarBilhete com as informações da base de dados
    return render_template("ComprarBilhete.html", evento=evento)


@app.route('/AdicionarEventosCSV', methods = ["POST"])
def AdicionarEventosCSV():
    """
        Permite adicionar o evento em formato CSV para carregar informações para adicionar o evento (POST)

        Return:
            Redireciona para a pagina index
    """
    #Vai obter o ficheiro csv inserido pelo utilizador
    csv_file = request.files["filecsv"]
    #Lê um arquivo CSV enviado via formulário, converte os dados para texto, e os prepara para serem lidos linha por linha com o módulo csv
    reader = csv.reader(io.StringIO(csv_file.stream.read().decode("utf-8")))

    #Cria uma lista para alocar a informação presente no csv
    csv_inf = []
    #Esta linha de codigo vai ignorar o cabeçalho do csv
    next(reader)
    #Vai percorrer toda informação dentro do csv
    for i in reader:
        #É criado um objeto desses valores para manter a estrutura dos dados a inserir na base de dados
        csv_linha_obj = Evento(i[0], i[1], i[2], i[3], i[4], i[5], int(i[6]), int(i[7]))
        #Percorre todas atividades presentes no ficheiro csv, separados por ponto e virgulas
        for j in i[8].split(";"):
            #Divide cada string da atividade, separando com o simbolo "|"
            nome, hora_inicio, hora_fim, local, capacidade_atividade, tipo_atividade = j.split("|")
            #É criado um objeto com as informações das atividades no csv, para manter a mesma estrutura de dados
            atividade = Atividades(nome, hora_inicio, hora_fim, local, capacidade_atividade, tipo_atividade)
            #Adiciona as atividades dentro da lista nos eventos
            csv_linha_obj.adicionar_atividades(atividade)

        #Cria um dicionario com a informação adquirida no csv
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
            }for i in csv_linha_obj.get_atividades()],
            "Participantes": [],
            "Entradas de Participantes": []
        }
        #Adiciona o dicionario dentro desta lista, repetindo o ciclo para percorrer toda a informação presente no csv
        csv_inf.append(json_csv)

    #Se a lista de dicionarios contem informação
    if csv_inf:
        #Faz insert na base de dados com a nova informção
        Conexao.collection_Eventos.insert_many(csv_inf)
        #Mostra a mensagem de sucesso ao inserir os dados na base de dados
        flash("CSV inserido com sucesso!", "success")
    else:
        #Mostra a mensagem de erro quando a lista de dicionarios estiver vazia
        flash("Erro ao carregar a informação do ficheiro CSV!", "error")
    #Redireciona para a pagina index
    return redirect(url_for("index"))

@app.route('/RemoverEvento/<string:_id>', methods = ["DELETE"])
def RemoverEvento(_id):
    """
        Permite remover o evento atravez do _id desse evento (DELETE)

        Argumentos:
            _id(ObjectID): id do evento escolhido para adquirir informação da mesma

        Return:
            Vai renderizar a pagina index com variaveis que contem informação da base de dados

    """
    #Guarda toda a informação num dicionario conrespondente ao evento selecionado que deseja apagar
    apagar = Conexao.collection_Eventos.delete_one({"_id": ObjectId(_id)})
    #Mensagem de sucesso quando o evento é apagado
    flash("Evento removido com sucesso!", "success")
    #Renderizada a pagina index com as informações da base de dados
    return render_template("index.html", apagar=apagar)

@app.route('/EditarEventos/<string:_id>', methods=['GET', 'POST'])
def AlterarEvento(_id):
    """
        Permite editar a informção do evento escolhido pelo utilizador e tambem permite adicionar mais atividades caso o utilizador desejar

        Argumentos:
            _id(ObjectID): id do evento escolhido para adquirir informação da mesma

        Return:
            Redireciona para a pagina index no final das operações
            Vai renderizar a pagina EditarEventos com variaveis que contem informação da base de dados
    """
    #Guarda toda a informação num dicionario conrespondente ao evento selecionado
    evento_inf = Conexao.collection_Eventos.find_one({"_id": ObjectId(_id)})
    #Se o metodo do request é GET
    if request.method == 'GET':
        #Renderiza a informação na pagina EditarEventos com as informações da base de dados
        return render_template("EditarEventos.html", evento=evento_inf)

    #Se o metodo do request é POST
    elif request.method == 'POST':
        #Faz request dos dados inseridos na pagina html e guarda o valor inserido no html nas variaveis
        nome = request.form.get('nome')
        descricao = request.form.get('descricao')
        data_inicio = request.form.get('data_inicio')
        data_fim = request.form.get('data_fim')
        organizador = request.form.get('organizador')
        tipo = request.form.get('tipo')
        capacidade = int(request.form.get('capacidade'))
        condicao = int(request.form.get('condicao'))
        atividade = request.form.getlist('atividade')
        hora_inicio = request.form.getlist('hora_inicio')
        hora_fim = request.form.getlist('hora_fim')
        local_atividade = request.form.getlist('local_atividade')
        capacidade_atividade = request.form.getlist('capacidade_atividade')
        tipo_atividade = request.form.getlist('tipo_atividade')

        #Cria um objeto para o evento mantendo a estrutura dos dados
        evento = Evento(nome, descricao, data_inicio, data_fim, organizador, tipo, capacidade, condicao)

        #Criada uma lista para colocar os dicionarios da atividades a editar
        atividades = []
        #Percorre todos os campos em formato de tupla para guardar a informação
        for atividade, inicio, fim, local, capacidade, tipo in zip(atividade, hora_inicio, hora_fim, local_atividade, capacidade_atividade, tipo_atividade):
            #Cria um objeto com as informações nas atividades de cada tupla
            atividade_obj = Atividades(atividade, inicio, fim, local, capacidade, tipo)
            #Adiciona o objeto á lista de atividades
            atividades.append(atividade_obj)

        #Percorre a lista atividade
        for i in atividades:
            #Adiciona toda informação presente nessa lista no evento
            evento.adicionar_atividades(i)

        #Cria um dicionario com as informações do evento
        json_update = {
            "Nome": evento.get_nome(),
            "Descrição": evento.get_descricao(),
            "Data de Inicio do Evento": evento.get_data_inicio(),
            "Data do Fim do Evento": evento.get_data_fim(),
            "Organizador": evento.get_organizador(),
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
            "Participantes": evento_inf.get("Participantes", []),
            "Entradas de Participantes": evento_inf.get("Entradas de Participantes", [])
        }
        #Vai atualizar as informações alteradas no dicionario
        Conexao.collection_Eventos.update_one({"_id": ObjectId(_id)}, {"$set": json_update})
        #Mostra esta mensagem de sucesso
        flash("Evento atualizado com sucesso!", "success")
        #Redireciona para a pagina index
        return redirect(url_for("index"))


@app.route('/AdicionarEventos', methods=['GET', 'POST'])
def AdicionarEventos():
    if request.method == 'POST':
        #Faz request dos dados inseridos na pagina html e guarda o valor inserido no html nas variaveis
        nome = request.form["nome"]
        descricao = request.form["descricao"]
        date_inicio = request.form["data_inicio"]
        date_fim = request.form["data_fim"]
        organizador = request.form["organizador"]
        tipo = request.form["tipo"]
        capacidade = int(request.form["capacidade_evento"])
        condicao_idade = int(request.form["condicao"])
        atividade = request.form.getlist("atividade")
        hora_inicio = request.form.getlist("hora_inicio")
        hora_fim = request.form.getlist("hora_fim")
        local = request.form.getlist("local_atividade")
        capacidade_atividade = request.form.getlist("capacidade_atividade")
        tipo_atividade = request.form.getlist("tipo_atividade")

        #Criada uma lista para colocar os dicionarios da atividades
        atividades_lista = []
        #Percorre todos os campos em formato de tupla para guardar a informação
        for a, inicio, fim, l, cap, t in zip(atividade, hora_inicio, hora_fim, local, capacidade_atividade, tipo_atividade):
            #Cria um objeto com as informações nas atividades de cada tupla
            atividade_obj = Atividades(a, inicio, fim, l, cap, t)
            atividades_lista.append(atividade_obj)

        #Cria um objeto para o evento mantendo a estrutura dos dados
        evento = Evento(nome, descricao, date_inicio, date_fim, organizador, tipo, capacidade, condicao_idade)

        #Percorre a lista atividade
        for i in atividades_lista:
            #Adiciona toda informação presente nessa lista no evento
            evento.adicionar_atividades(i)

        #Cria um dicionario com as informações do evento
        json = {
            "Nome": evento.get_nome(),
            "Descrição": evento.get_descricao(),
            "Data de Inicio do Evento": evento.get_data_inicio(),
            "Data do Fim do Evento": evento.get_data_fim(),
            "Organizador": evento.get_organizador(),
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
        #Faz insert do dicionario para a base de dados
        Conexao.collection_Eventos.insert_one(json)
        #Mostra a mensagem de sucesso
        flash("Evento inserido com sucesso!", "success")
        #Redireciona para a pagina index
        return redirect(url_for("index"))
    #Rederiza a pagina AdicionarEventos
    return render_template('AdicionarEventos.html', enviado=False)

if __name__ == '__main__':
    #Inicializa a aplicação
    app.run(debug=True)