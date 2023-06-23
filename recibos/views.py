from reportlab.graphics.barcode import createBarcodeDrawing
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from django.template.loader import render_to_string
from django.http import FileResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum
from io import BytesIO
import os
from .models import Recibo
from .forms import ReciboForm
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing, Line
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Image
from reportlab.platypus import Image as RLImage



def recibo_pdf(request, pk):
    recibo = get_object_or_404(Recibo, pk=pk)
    pdf_file = generate_pdf(recibo)
    if pdf_file:
        response = FileResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{recibo.codigo}.pdf"'
        return response
    return redirect('recibo_detail', pk=pk)

def generate_pdf(recibo):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()

    # Estilos personalizados
    custom_styles = {
        'Title': ParagraphStyle(
            'custom_title',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=20,
            textColor='navy',
            alignment=1,
        ),
        'Subtitle': ParagraphStyle(
            'custom_subtitle',
            parent=styles['Heading3'],
            fontSize=14,
            textColor='darkgreen',
            alignment=2,
        ),
        'TableHeader': ParagraphStyle(
            'custom_table_header',
            parent=styles['Normal'],
            fontSize=12,
            textColor='white',
            backgroundColor='steelblue',
            alignment=1,
            leading=20,
            spaceAfter=10,
        ),
        'TableCell': ParagraphStyle(
            'custom_table_cell',
            parent=styles['Normal'],
            fontSize=12,
            textColor='black',
            leading=20,
            spaceAfter=10,
        ),
    }

    # Encabezado del recibo
    logo = Image("static/images/image1.png", width=100, height=100)
    logo.hAlign = "LEFT"
    header = Paragraph("<u>Recibo</u>", custom_styles['Title'])
    sub_header = Paragraph(f"<b>Código:</b> {recibo.codigo}", custom_styles['Subtitle'])

    # Línea horizontal
    line = Drawing(500, 1)
    line.add(Line(0, 0, 500, 0))

    # Contenido del recibo
    data = [
        [Paragraph("<b>Descripción</b>", custom_styles['TableHeader']),
         Paragraph("<b>Monto</b>", custom_styles['TableHeader'])],
        [Paragraph(recibo.descripcion, custom_styles['TableCell']),
         Paragraph(f"${recibo.monto}", custom_styles['TableCell'])],
    ]
    table = Table(data)
    table.setStyle([
        ("BOX", (0, 0), (-1, -1), 1.5, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), custom_styles['TableHeader'].backgroundColor),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
    ])

    # Código QR del recibo
    qr_code_barcode = createBarcodeDrawing('QR', value=recibo.codigo, barWidth=200, barHeight=200)
    qr_image = Image(qr_code_barcode, width=200, height=200)

    # Agregar los elementos al documento PDF
    content = [
        Spacer(1, 50),
        logo,
        Spacer(1, 20),
        header,
        sub_header,
        Spacer(1, 20),
        line,
        Spacer(1, 20),
        table,
        Spacer(1, 20),
        qr_image,
    ]
    doc.build(content)

    buffer.seek(0)
    return buffer

def draw_qr_code(code):
    qr_code = qr.QrCodeWidget(code)
    bounds = qr_code.getBounds()
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    qr_drawing = Drawing(width, height)
    qr_drawing.add(qr_code)
    qr_code_image = qr_drawing.asString('png')

    # Guardar la imagen en un archivo temporal
    temp_file = "temp_qr_code.png"
    with open(temp_file, "wb") as f:
        f.write(qr_code_image)

    return temp_file


def home(request):
    recibo = Recibo.objects.first()
    context = {'recibo': recibo}
    return render(request, 'recibos/home.html', context)

def recibo_list(request):
    codigo = request.GET.get('codigo', '')
    descripcion = request.GET.get('descripcion', '')

    recibos = Recibo.objects.all()

    if codigo:
        recibos = recibos.filter(codigo__icontains=codigo)
    if descripcion:
        recibos = recibos.filter(descripcion__icontains=descripcion)

    total_monto = recibos.aggregate(total_monto=Sum('monto'))['total_monto']

    context = {
        'recibos': recibos,
        'total_monto': total_monto,
        'codigo_filtro': codigo,
        'descripcion_filtro': descripcion
    }

    return render(request, 'recibos/recibo_list.html', context)

def recibo_detail(request, pk):
    recibo = get_object_or_404(Recibo, pk=pk)
    context = {'recibo': recibo}
    return render(request, 'recibos/recibo_detail.html', context)

def recibo_create(request):
    if request.method == 'POST':
        form = ReciboForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('recibo_list')
    else:
        form = ReciboForm()

    return render(request, 'recibos/recibo_form.html', {'form': form})

def recibo_update(request, pk):
    recibo = get_object_or_404(Recibo, pk=pk)

    if request.method == 'POST':
        form = ReciboForm(request.POST, instance=recibo)
        if form.is_valid():
            form.save()
            return redirect('recibo_list')
    else:
        form = ReciboForm(instance=recibo)

    return render(request, 'recibos/recibo_form.html', {'form': form})

def recibo_delete(request, pk):
    recibo = get_object_or_404(Recibo, pk=pk)

    if request.method == 'POST':
        recibo.delete()
        return redirect('recibo_list')

    return render(request, 'recibos/recibo_confirm_delete.html', {'recibo': recibo})
