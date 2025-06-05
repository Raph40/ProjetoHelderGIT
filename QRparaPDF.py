from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io

def gerar_pdf_certificado(evento, nome_aluno="Aluno Participante"):
    buffer = io.BytesIO()

    # Define a página com tamanho A4
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Título
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, height - 100, "Certificado de Participação")

    # Corpo
    c.setFont("Helvetica", 12)
    texto = f"Certificamos que {nome_aluno} participou no evento:"
    c.drawCentredString(width / 2, height - 150, texto)

    # Nome do Evento
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2, height - 180, evento.get("Nome", "Nome do Evento"))

    # Datas
    c.setFont("Helvetica", 12)
    data_inicio = evento.get("Data de Inicio do Evento", "N/A")
    data_fim = evento.get("Data do Fim do Evento", "N/A")
    datas = f"Realizado entre {data_inicio} e {data_fim}."
    c.drawCentredString(width / 2, height - 210, datas)

    # Rodapé
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(50, 50, "Câmara Municipal de Abrantes")

    # Finaliza o PDF
    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer