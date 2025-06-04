import fitz
import io
import re

def quebra_linha(text, max_width, fontsize, fontname="helv"):
    """
        Função que permite a quebra de linhas com base na largura máxima no pdf

        Argumentos:
            text(string): Texto do comentario que contem muito texto
            max_width(int): Maximo do comprimento do texto
            fontsize(int): Tamanho da letra do texto

        Return:
            Quebra de linha para cada texto selecionado com esta função
    """
    #Utiliza o argumento fontname
    font = fitz.Font(fontname=fontname)
    #Utiliza o argumento fontsize
    space_width = font.text_length(" ", fontsize=fontsize)
    #Separa as palavras no texto
    words = text.split()
    lines = []
    current_line = ""
    current_width = 0

    #Percorre as palavras separadas no texto
    for word in words:
        word_width = font.text_length(word, fontsize=fontsize)
        #Se a palavra cabe na linha atual, adiciona
        if current_width + word_width <= max_width:
            current_line += (word + " ")
            current_width += word_width + space_width
        else:
            #Se não couber, inicia uma nova linha
            lines.append(current_line.strip())
            current_line = word + " "
            current_width = word_width + space_width
    if current_line:
        lines.append(current_line.strip())
    return lines

#Gera um PDF com todas as informações de um evento
def gerarPDFs(evento):
    """
        Gera o PDF consuante a informação do argumento, mas sempre com a mesma estrutura de dados

        Argumentos:
            evento(dicionario): Contem toda informação sobre o evento escolhido pelo utilizador

        Return:
            Devolve o PDF gerado em portugues de portugal
    """
    #Cria um novo documento PDF
    pdf = fitz.open()
    #Adiciona uma página ao PDF
    page = pdf.new_page()
    #Posição vertical inicial do conteúdo
    y = 50

    #Cabeçalho do evento
    page.insert_text((50, y), f"Relatório de Evento: {evento.get('Nome', '')}", fontsize=22, fontname="helv")
    y += 40

    #Informações principais do evento
    page.insert_text((50, y), f"Descrição do Evento: {evento.get('Descrição', '')}", fontsize=14)
    y += 20
    page.insert_text((70, y), f"Data de Início: {evento.get('Data de Inicio do Evento', '')}", fontsize=14)
    y += 20
    page.insert_text((70, y), f"Data do Fim: {evento.get('Data do Fim do Evento', '')}", fontsize=14)
    y += 20
    page.insert_text((70, y), f"Organizador: {evento.get('Organizador', '')}", fontsize=14)
    y += 20
    page.insert_text((70, y), f"Tipo de Evento: {evento.get('Tipo de Evento', '')}", fontsize=14)
    y += 20
    page.insert_text((70, y), f"Capacidade de Participantes: {evento.get('Capacidade de Participantes', '')}", fontsize=14)
    y += 20
    page.insert_text((70, y), f"Condição da Idade de Participação: {evento.get('Condição da Idade de Participação', '')}", fontsize=14)
    y += 30

    #Informação sobre as atividades
    atividades = evento.get("Atividades", [])
    #Cabeçalho das atividades
    page.insert_text((50, y), "Atividades neste evento:", fontsize=18)
    y += 20

    #Se não conter atividades
    if not atividades:
        #Aparece este texto
        page.insert_text((70, y), "Nenhuma atividade cadastrada", fontsize=12)
        y += 20
    else:
        #Se sim percorre toda a informação das atividades e coloca aqui essas informação
        for j in atividades:
            page.insert_text((70, y), f"Hora de Início: {j.get('Hora de Inicio', '')}", fontsize=14)
            y += 20
            page.insert_text((70, y), f"Hora do Fim: {j.get('Hora do Fim', '')}", fontsize=14)
            y += 20
            page.insert_text((70, y), f"Local da Atividade: {j.get('Local da Atividade', '')}", fontsize=14)
            y += 20
            page.insert_text((70, y), f"Capacidade da Atividade: {j.get('Capacidade da Atividade', '')}", fontsize=14)
            y += 20
            page.insert_text((70, y), f"Tipo de Atividade: {j.get('Tipo de Atividade', '')}", fontsize=14)
            y += 20

            #Informação sobre a lista de inscritos
            lista_inscritos = j.get("Lista de Inscritos", [])
            #Se não conter nenhum inscrito para atividade
            if not lista_inscritos:
                #Aparece esse texto
                page.insert_text((90, y), "Nenhum participante inscrito", fontsize=11)
                y += 20
            else:
                #Se sim percorre todas as informações dos inscritos e coloca aqui as informações
                for inscrito in lista_inscritos:
                    page.insert_text((90, y), f"- {inscrito.get('Nome', 'Anônimo')}", fontsize=12)
                    y += 15

            y += 10
            #Quebra de página se necessário
            if y > 750:
                page = pdf.new_page()
                y = 50

    #Informação dos participantes do evento
    participantes_eventos = evento.get("Participantes", [])
    #Cabeçalho dos participantes
    page.insert_text((50, y), "Participantes neste evento:", fontsize=16)
    y += 20
    #Se não conter nenhum participante do evento
    if not participantes_eventos:
        #Aparece esse texto
        page.insert_text((70, y), "Nenhum participante cadastrado", fontsize=11)
        y += 20
    else:
        #Se sim vai percorrer toda a informação e coloca aqui as informações
        for p in participantes_eventos:
            page.insert_text((70, y), f"Nome: {p.get('Nome', '')}", fontsize=14)
            y += 20
            page.insert_text((70, y), f"Idade: {p.get('Idade', '')}", fontsize=14)
            y += 20
            page.insert_text((70, y), f"NIF: {p.get('NIF', '')}", fontsize=14)
            y += 20
            page.insert_text((70, y), f"Telefone: {p.get('Telefone', '')}", fontsize=14)
            y += 30
            #Quebra de pagina se necessario
            if y > 750:
                page = pdf.new_page()
                y = 50

    #Informação das entradas no evento
    Lista_Entradas = evento.get("Entradas de Participantes", [])
    #Cabeçalho das entradas dos participantes
    page.insert_text((50, y), "Entradas de Participantes:", fontsize=16)
    y += 20
    #Se não conter nenhuma entrada do participante
    if not Lista_Entradas:
        #Mostra este texto
        page.insert_text((70, y), "Nenhum participante entrou no evento", fontsize=11)
        y += 20
    else:
        #Se sim vai percorrer toda a informação e coloca aqui as informações
        for e in Lista_Entradas:
            page.insert_text((70, y), f"Nome: {e.get('Nome', '')}", fontsize=14)
            y += 20
            page.insert_text((70, y), f"Idade: {e.get('Idade', '')}", fontsize=14)
            y += 20
            page.insert_text((70, y), f"NIF: {e.get('NIF', '')}", fontsize=14)
            y += 20
            page.insert_text((70, y), f"Telefone: {e.get('Telefone', '')}", fontsize=14)
            y += 20
            page.insert_text((70, y), f"Comentário: {e.get('Comentario', '')}", fontsize=14)
            y += 20

            comentario_bot = f"Comentário_BOT: {e.get('Comentario_BOT', '')}"
            linhas = quebra_linha(comentario_bot, max_width=450, fontsize=14)

            for linha in linhas:
                page.insert_text((70, y), linha, fontsize=14)
                y += 18

            y += 10
            #Quebra de pagina se for necessario
            if y > 750:
                page = pdf.new_page()
                y = 50

    #Finaliza o PDF e retorna como buffer
    buffer = io.BytesIO()
    pdf.save(buffer)
    pdf.close()
    buffer.seek(0)
    return buffer


def anonimizar_pdf(pdf_buffer):
    """
        Permite anonimizar dados sensiveis sobre os eventos

        Argumentos:
            pdf_buffer(file): Recebe o pdf gerado para anonimização dessa informação

        Return:
            PDF devidamente anonimizado
    """
    #Abre o pdf gerado
    pdf_document = fitz.open(stream=pdf_buffer.read(), filetype="pdf")

    #Expressões regulares para detectar informações pessoais
    patterns = {
        "Data de Início": r"Data de Início:\s*(.+)",
        "Data do Fim": r"Data do Fim:\s*(.+)",
        "Nome:": r"Nome:\s*(.+)",
        "NIF:": r"NIF:\s*(\d+)",
        "Telefone:": r"Telefone:\s*(\d{9})",
        "Idade:": r"Idade:\s*(\d+)",
        "Hora de Início": r"Hora de Início:\s*(.+)",
        "hora do Fim": r"Hora do Fim:\s*(.+)",
        "Local da Atividade:": r"Local da Atividade:\s*(.+)",
        "Tipo de Atividade:": r"Tipo de Atividade:\s*(.+)"
    }

    #Percorre todas as páginas do documento
    for page_num in range(len(pdf_document)):
        #Carrega a página atual
        page = pdf_document.load_page(page_num)
        #Extrai o texto da página
        text = page.get_text("text")

        #Para cada rótulo e sua expressão regular associada
        for label, regex in patterns.items():
            #Busca todos os valores que correspondem à expressão
            matches = re.finditer(regex, text, re.IGNORECASE)
            for match in matches:
                #Extrai apenas o valor parte a ser anonimizada
                value_to_anonymize = match.group(1)

                #Localiza no PDF as áreas onde o valor aparece
                areas = page.search_for(value_to_anonymize)
                for area in areas:
                    #Desenha um retângulo preto sobre o valor para ocultá-lo
                    page.draw_rect(area, color=(0, 0, 0), fill=(0, 0, 0))

    #Cria um buffer para o PDF anonimizado
    pdf_anonimizado = io.BytesIO()
    #Guarda as alterações feitas no buffer de saída
    pdf_document.save(pdf_anonimizado)
    #Fecha o documento original
    pdf_document.close()
    #Volta o cursor do buffer para o início para leitura posterior
    pdf_anonimizado.seek(0)
    #Retorna o buffer contendo o PDF anonimizado
    return pdf_anonimizado

#Função simples que extrai texto de um PDF
def extrair_texto_pdf(pdf):
    """
        Extrai a informação do PDF para a sua tradução

        Argumentos:
            pdf(file): Recebe o PDF gerado

        Return:
            Vai retornar o texto com a informação do pdf numa variavel
    """
    #String vazia para inserir o texto
    texto = ""
    #Abre o pdf
    doc = fitz.open(stream=pdf, filetype="pdf")
    #vai percorrer a informação dentro do documento (PDF)
    for pagina in doc:
        #Guarda a informação para a variavel
        texto += pagina.get_text()
    #Returna a variavel com toda informação do PDF
    return texto

def criar_pdf(texto):
    """
        Cria um PDF simples que contem toda a informação traduzida

        Argumentos:
            texto(string): Informação para construir um PDF simples

        Return:
            Retorna o PDF simples com a sua tradução
    """
    #Abre o documento
    doc = fitz.open()
    #Cria uma nova pagina
    pagina = doc.new_page()
    #Insere o texto recebido
    pagina.insert_text((72, 72), texto)
    #Finaliza o PDF e retorna como buffer
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer
