import fitz
import io
import re

def quebra_linha(text, max_width, fontsize, fontname="helv"):
    font = fitz.Font(fontname=fontname)
    space_width = font.text_length(" ", fontsize=fontsize)
    words = text.split()
    lines = []
    current_line = ""
    current_width = 0

    for word in words:
        word_width = font.text_length(word, fontsize=fontsize)
        if current_width + word_width <= max_width:
            current_line += (word + " ")
            current_width += word_width + space_width
        else:
            lines.append(current_line.strip())
            current_line = word + " "
            current_width = word_width + space_width
    if current_line:
        lines.append(current_line.strip())
    return lines

def gerarPDFs(evento):
    pdf = fitz.open()
    page = pdf.new_page()
    y = 50

    page.insert_text((50, y), f"Relatório de Evento: {evento.get('Nome', '')}", fontsize=22, fontname="helv")
    y += 40

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

    atividades = evento.get("Atividades", [])
    page.insert_text((50, y), "Atividades neste evento:", fontsize=18)
    y += 20

    if not atividades:
        page.insert_text((70, y), "Nenhuma atividade cadastrada", fontsize=12)
        y += 20
    else:
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

            lista_inscritos = j.get("Lista de Inscritos", [])
            if not lista_inscritos:
                page.insert_text((90, y), "Nenhum participante inscrito", fontsize=11)
                y += 20
            else:
                for inscrito in lista_inscritos:
                    page.insert_text((90, y), f"- {inscrito.get('Nome', 'Anônimo')}", fontsize=12)
                    y += 15

            y += 10
            if y > 750:
                page = pdf.new_page()
                y = 50

    participantes_eventos = evento.get("Participantes", [])
    page.insert_text((50, y), "Participantes neste evento:", fontsize=16)
    y += 20

    if not participantes_eventos:
        page.insert_text((70, y), "Nenhum participante cadastrado", fontsize=11)
        y += 20
    else:
        for p in participantes_eventos:
            page.insert_text((70, y), f"Nome: {p.get('Nome', '')}", fontsize=14)
            y += 20
            page.insert_text((70, y), f"Idade: {p.get('Idade', '')}", fontsize=14)
            y += 20
            page.insert_text((70, y), f"NIF: {p.get('NIF', '')}", fontsize=14)
            y += 20
            page.insert_text((70, y), f"Telefone: {p.get('Telefone', '')}", fontsize=14)
            y += 30
            if y > 750:
                page = pdf.new_page()
                y = 50

    Lista_Entradas = evento.get("Entradas de Participantes", [])
    page.insert_text((50, y), "Entradas de Participantes:", fontsize=16)
    y += 20

    if not Lista_Entradas:
        page.insert_text((70, y), "Nenhum participante entrou no evento", fontsize=11)
        y += 20
    else:
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
            if y > 750:
                page = pdf.new_page()
                y = 50

    buffer = io.BytesIO()
    pdf.save(buffer)
    pdf.close()
    buffer.seek(0)
    return buffer

def anonimizar_pdf(pdf_buffer):
    pdf_buffer.seek(0)
    pdf_document = fitz.open(stream=pdf_buffer.read(), filetype="pdf")

    combined_pattern = re.compile(
        r"Data de Início:\s*(?P<data_inicio>.+)|"
        r"Data do Fim:\s*(?P<data_fim>.+)|"
        r"Nome:\s*(?P<nome>.+)|"
        r"NIF:\s*(?P<nif>\d+)|"
        r"Telefone:\s*(?P<telefone>\d{9})|"
        r"Idade:\s*(?P<idade>\d+)|"
        r"Hora de Início:\s*(?P<hora_inicio>.+)|"
        r"Hora do Fim:\s*(?P<hora_fim>.+)|"
        r"Local da Atividade:\s*(?P<local>.+)|"
        r"Tipo de Atividade:\s*(?P<tipo>.+)",
        re.IGNORECASE
    )

    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text = page.get_text("text")

        values_to_anonymize = set()
        matches = combined_pattern.finditer(text)
        for match in matches:
            for value in match.groupdict().values():
                if value:
                    values_to_anonymize.add(value.strip())

        for value in values_to_anonymize:
            areas = page.search_for(value)
            for area in areas:
                page.draw_rect(area, color=(0, 0, 0), fill=(0, 0, 0))

    pdf_anonimizado = io.BytesIO()
    pdf_document.save(pdf_anonimizado)
    pdf_document.close()
    pdf_anonimizado.seek(0)
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
