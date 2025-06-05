import fitz
import io
import re
from io import BytesIO

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

def gerarPDFs(evento, nome_participante, nome_palestrante, nome_diretor):
    pdf_buffer = BytesIO()
    doc = fitz.open()

    pagina = doc.new_page(width=595, height=842)

    # Cores
    cor_titulo = (0, 0, 0.5)  # Azul escuro
    cor_texto = (0, 0, 0)      # Preto

    # Borda
    pagina.draw_rect(fitz.Rect(50, 50, 545, 792), color=cor_titulo, width=1.5)

    # Título
    pagina.insert_textbox(fitz.Rect(50, 100, 545, 150),
                          "Certificado de Participação",
                          fontname="helv", fontsize=24,
                          color=cor_titulo, align=1)  # 1 = CENTER

    # Texto
    pagina.insert_textbox(fitz.Rect(50, 180, 545, 220),
                          "CONCEDEMOS ESTE A",
                          fontname="helv", fontsize=16,
                          color=cor_texto, align=1)

    # Nome do participante
    pagina.insert_textbox(fitz.Rect(50, 220, 545, 280),
                          nome_participante.upper(),
                          fontname="helv", fontsize=28,
                          color=cor_titulo, align=1)

    # Evento
    pagina.insert_textbox(fitz.Rect(50, 300, 545, 350),
                          f'por participar do evento "{evento["Nome"]}" da Audios Soluções.',
                          fontname="helv", fontsize=14,
                          color=cor_texto, align=1)

    # Assinaturas
    y_pos = 450
    pagina.draw_line(fitz.Point(150, y_pos+50), fitz.Point(300, y_pos+50), color=cor_titulo)
    pagina.insert_text(fitz.Point(150, y_pos), "Palestrante", fontname="helv", fontsize=10)
    pagina.insert_text(fitz.Point(150, y_pos+70), nome_palestrante.upper(), fontname="helv", fontsize=12)

    pagina.draw_line(fitz.Point(350, y_pos+50), fitz.Point(500, y_pos+50), color=cor_titulo)
    pagina.insert_text(fitz.Point(350, y_pos), "Diretor de Marketing", fontname="helv", fontsize=10)
    pagina.insert_text(fitz.Point(350, y_pos+70), nome_diretor.upper(), fontname="helv", fontsize=12)

    doc.save(pdf_buffer)
    pdf_buffer.seek(0)
    doc.close()

    return pdf_buffer

# Função auxiliar para extrair texto do PDF (mantida como no seu código original)
def extrair_texto_pdf(pdf_buffer):
    texto = ""
    pdf_buffer.seek(0)  # Garante que estamos lendo desde o início
    with fitz.open(stream=pdf_buffer.read(), filetype="pdf") as doc:
        for pagina in doc:
            texto += pagina.get_text()
    return texto

# Função auxiliar para criar PDF simples (mantida como no seu código original)
def criar_pdf(texto):
    doc = fitz.open()
    pagina = doc.new_page()

    # Configurações de layout para o PDF traduzido
    margin = 50
    linha_atual = margin

    # Divide o texto em linhas e insere no PDF
    for linha in texto.split('\n'):
        if linha.strip():  # Ignora linhas vazias
            pagina.insert_text(
                (margin, linha_atual),
                linha.strip(),
                fontsize=11,
                fontname="helv"
            )
            linha_atual += 14  # Espaçamento entre linhas

    # Salva em buffer
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer
