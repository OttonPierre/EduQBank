import io
from bs4 import BeautifulSoup
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from docx import Document
from datetime import datetime
from app.models import Questao
from app.utils import html_render_math_to_img
from .helpers import (
    _generate_with_pypandoc,
    _generate_with_pandoc,
    _docx_add_if_header,
    _get_image_bytes_from_html,
)


@api_view(["POST"]) 
def generate_test_docx(request):
    ids = request.data.get('question_ids', [])
    if not isinstance(ids, list) or not ids:
        return Response({"detail": "question_ids deve ser uma lista não vazia"}, status=400)
    questions = list(Questao.objects.filter(id__in=ids))
    if not questions:
        return Response({"detail": "Nenhuma questão encontrada"}, status=404)
    
    # Try pypandoc first (preferred)
    pp_bytes = _generate_with_pypandoc(questions, 'docx')
    if pp_bytes:
        resp = HttpResponse(pp_bytes, content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        resp["Content-Disposition"] = f'attachment; filename="prova_{datetime.now().strftime("%Y%m%d_%H%M%S")}.docx"'
        return resp
    
    # Fallback to pandoc CLI
    pandoc_bytes = _generate_with_pandoc(questions, 'docx')
    if pandoc_bytes:
        resp = HttpResponse(pandoc_bytes, content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        resp["Content-Disposition"] = f'attachment; filename="prova_{datetime.now().strftime("%Y%m%d_%H%M%S")}.docx"'
        return resp

    # Fallback to python-docx
    document = Document()
    _docx_add_if_header(document, "PROVA", "Banco de Questões")
    for idx, q in enumerate(questions, start=1):
        document.add_paragraph(f"Questão {idx}")
        html = html_render_math_to_img(q.enunciado or "")
        soup = BeautifulSoup(html, 'lxml')
        accum_text = []
        for element in soup.recursiveChildGenerator():
            if getattr(element, 'name', None) == 'img':
                src = element.get('src','')
                if accum_text:
                    document.add_paragraph(''.join(accum_text))
                    accum_text = []
                img_bytes = _get_image_bytes_from_html(src)
                if img_bytes:
                    stream = io.BytesIO(img_bytes)
                    document.add_picture(stream)
            elif isinstance(element, str):
                accum_text.append(element)
        if accum_text:
            document.add_paragraph(''.join(accum_text))
        if getattr(q, 'resposta', None):
            document.add_paragraph("Resposta:")
            html_r = html_render_math_to_img(q.resposta or "")
            soup_r = BeautifulSoup(html_r, 'lxml')
            accum_text_r = []
            for element in soup_r.recursiveChildGenerator():
                if getattr(element, 'name', None) == 'img':
                    src = element.get('src','')
                    if accum_text_r:
                        document.add_paragraph(''.join(accum_text_r))
                        accum_text_r = []
                    img_bytes = _get_image_bytes_from_html(src)
                    if img_bytes:
                        stream = io.BytesIO(img_bytes)
                        document.add_picture(stream)
                elif isinstance(element, str):
                    accum_text_r.append(element)
            if accum_text_r:
                document.add_paragraph(''.join(accum_text_r))
        document.add_paragraph("")
    
    buffer = io.BytesIO()
    document.save(buffer)
    buffer.seek(0)
    resp = HttpResponse(buffer.getvalue(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    resp["Content-Disposition"] = f'attachment; filename="prova_{datetime.now().strftime("%Y%m%d_%H%M%S")}.docx"'
    return resp

