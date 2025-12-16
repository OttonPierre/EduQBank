from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from app.models import Questao
from .helpers import generate_exam_with_pandoc


@api_view(["POST"]) 
def print_test_docx(request):
    """
    Gera um arquivo DOCX de prova a partir de uma lista de questões.

    Parâmetros aceitos em request.data:
      - question_ids: lista de IDs de questões (obrigatório)
      - gabarito_option (opcional, string):
            "apos_cada_questao"
            "final_arquivo"
            "somente_questoes"
            "somente_gabarito"
            "somente_gabarito_com_expectativa"
      - include_gabarito / use_resposta_gabarito:
            mantidos por compatibilidade com versões antigas do frontend.
    """
    ids = request.data.get('question_ids', [])

    # Compatibilidade: valores antigos ainda podem ser enviados
    include_gabarito = bool(request.data.get('include_gabarito', True))
    use_resposta_gabarito = bool(request.data.get('use_resposta_gabarito', False))
    gabarito_option = request.data.get('gabarito_option')

    # Se a opção de gabarito foi explicitamente informada pelo frontend novo,
    # convertemos para os flags internos.
    if gabarito_option:
        if gabarito_option == "somente_questoes":
            include_gabarito = False
            use_resposta_gabarito = False
        elif gabarito_option == "somente_gabarito":
            include_gabarito = True
            use_resposta_gabarito = True  # usar resposta_gabarito (letras, etc.)
        elif gabarito_option == "somente_gabarito_com_expectativa":
            include_gabarito = True
            use_resposta_gabarito = False  # usar expectativa / resposta completa
        elif gabarito_option in ("apos_cada_questao", "final_arquivo"):
            # Provas completas com gabarito em posições diferentes.
            include_gabarito = True
            # Para essas opções seguimos o valor enviado ou o padrão (False).
        else:
            # Valor desconhecido: assumir comportamento padrão atual
            gabarito_option = "final_arquivo"
    else:
        # Frontend antigo: inferir opção a partir dos flags
        if not include_gabarito:
            gabarito_option = "somente_questoes"
        else:
            gabarito_option = "final_arquivo"
    
    if not isinstance(ids, list) or not ids:
        return Response({"detail": "question_ids deve ser uma lista não vazia"}, status=400)
    questions = list(Questao.objects.filter(id__in=ids))
    if not questions:
        return Response({"detail": "Nenhuma questão encontrada"}, status=404)
    
    # Obter nome da prova (se fornecido)
    test_name = request.data.get('test_name', '').strip()
    if not test_name:
        test_name = "prova" if not include_gabarito else "prova_com_gabarito"
    
    try:
        pandoc_bytes = generate_exam_with_pandoc(
            questions,
            out_format='docx',
            include_gabarito=include_gabarito,
            use_resposta_gabarito=use_resposta_gabarito,
            gabarito_option=gabarito_option,
        )
    except RuntimeError as exc:
        return Response({"detail": str(exc)}, status=500)

    resp = HttpResponse(pandoc_bytes, content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    resp["Content-Disposition"] = f'attachment; filename="{test_name}.docx"'
    return resp

