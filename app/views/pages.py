from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse, HttpResponse
from app.models import Questao, Conteudo
from app.utils import html_render_math_to_img
import json


def index(request):
    """Página inicial com lista de áreas"""
    # Buscar áreas e contar questões de forma mais explícita
    # Usar Count com distinct=True para evitar contagens duplicadas
    areas = Conteudo.objects.filter(tipo='area').annotate(
        questao_count=Count('q_area', distinct=True)
    ).order_by('nome')
    
    # Garantir que o contador seja sempre atualizado
    # Forçar avaliação da query e recalcular contadores
    areas_list = []
    for area in areas:
        # Recalcular o contador diretamente do banco para garantir atualização
        area.questao_count = Questao.objects.filter(area=area).count()
        areas_list.append(area)
    
    # Verificar se usuário está autenticado
    is_authenticated = request.user.is_authenticated
    is_staff = request.user.is_staff if is_authenticated else False
    
    context = {
        'areas': areas_list,
        'is_authenticated': is_authenticated,
        'is_staff': is_staff,
        'user': request.user if is_authenticated else None,
    }
    return render(request, 'app/index.html', context)


@login_required
def questoes_list(request):
    """Lista de questões com filtros e busca"""
    questoes = Questao.objects.all().select_related('area', 'unidade', 'topico', 'subtopico', 'categoria')
    
    # Busca por texto
    search = request.GET.get('search', '')
    if search:
        questoes = questoes.filter(enunciado__icontains=search)
    
    # Filtros - filtrar valores vazios e converter IDs para inteiros
    area_ids_raw = request.GET.getlist('area_id')
    area_ids = []
    for a in area_ids_raw:
        a_str = str(a).strip()
        if a_str:
            try:
                area_ids.append(int(a_str))
            except ValueError:
                pass
    if area_ids:
        questoes = questoes.filter(area_id__in=area_ids)
    
    unidade_ids_raw = request.GET.getlist('unidade_id')
    unidade_ids = []
    for u in unidade_ids_raw:
        u_str = str(u).strip()
        if u_str:
            try:
                unidade_ids.append(int(u_str))
            except ValueError:
                pass
    if unidade_ids:
        questoes = questoes.filter(unidade_id__in=unidade_ids)
    
    topico_ids_raw = request.GET.getlist('topico_id')
    topico_ids = []
    for t in topico_ids_raw:
        t_str = str(t).strip()
        if t_str:
            try:
                topico_ids.append(int(t_str))
            except ValueError:
                pass
    if topico_ids:
        questoes = questoes.filter(topico_id__in=topico_ids)
    
    subtopico_ids_raw = request.GET.getlist('subtopico_id')
    subtopico_ids = []
    for s in subtopico_ids_raw:
        s_str = str(s).strip()
        if s_str:
            try:
                subtopico_ids.append(int(s_str))
            except ValueError:
                pass
    if subtopico_ids:
        questoes = questoes.filter(subtopico_id__in=subtopico_ids)
    
    categoria_ids_raw = request.GET.getlist('categoria_id')
    categoria_ids = []
    for c in categoria_ids_raw:
        c_str = str(c).strip()
        if c_str:
            try:
                categoria_ids.append(int(c_str))
            except ValueError:
                pass
    if categoria_ids:
        questoes = questoes.filter(categoria_id__in=categoria_ids)
    
    # Filtro por ano (IntegerField) - ignorar valores vazios
    anos_raw = request.GET.getlist('ano')
    anos = []
    for a in anos_raw:
        a_str = str(a).strip()
        if a_str:
            try:
                anos.append(int(a_str))
            except ValueError:
                pass
    if anos:
        questoes = questoes.filter(ano__in=anos)
    
    bancas_raw = request.GET.getlist('banca')
    bancas = [b for b in bancas_raw if str(b).strip()]
    if bancas:
        questoes = questoes.filter(banca__in=bancas)
    
    tipos_questao_raw = request.GET.getlist('tipo_questao')
    tipos_questao = [t for t in tipos_questao_raw if str(t).strip()]
    if tipos_questao:
        questoes = questoes.filter(tipo_questao__in=tipos_questao)
    
    dificuldades_raw = request.GET.getlist('dificuldade')
    dificuldades = [d for d in dificuldades_raw if str(d).strip()]
    if dificuldades:
        questoes = questoes.filter(dificuldade__in=dificuldades)
    
    graus_escolaridade_raw = request.GET.getlist('grau_escolaridade')
    graus_escolaridade = [g for g in graus_escolaridade_raw if str(g).strip()]
    if graus_escolaridade:
        questoes = questoes.filter(grau_escolaridade__in=graus_escolaridade)
    
    tem_imagem = request.GET.get('tem_imagem')
    if tem_imagem == 'true':
        questoes = questoes.filter(Q(enunciado__icontains='<img') | Q(resposta__icontains='<img'))
    elif tem_imagem == 'false':
        questoes = questoes.exclude(Q(enunciado__icontains='<img') | Q(resposta__icontains='<img'))
    
    # Ordenação
    order_by = request.GET.get('order_by', '-id')
    questoes = questoes.order_by(order_by)
    
    # Paginação
    paginator = Paginator(questoes, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Dados para filtros
    areas = Conteudo.objects.filter(tipo='area').order_by('nome')
    anos_disponiveis = Questao.objects.values_list('ano', flat=True).distinct().order_by('-ano')
    bancas_disponiveis = Questao.objects.values_list('banca', flat=True).distinct().order_by('banca')
    tipos_disponiveis = Questao.objects.values_list('tipo_questao', flat=True).distinct().order_by('tipo_questao')
    dificuldades_disponiveis = Questao.objects.values_list('dificuldade', flat=True).distinct().order_by('dificuldade')
    graus_disponiveis = Questao.objects.values_list('grau_escolaridade', flat=True).distinct().order_by('grau_escolaridade')
    
    # Carregar hierarquia baseada na área selecionada
    unidades = []
    topicos = []
    subtopicos = []
    categorias = []
    
    if area_ids:
        # Carregar unidades das áreas selecionadas
        unidades = Conteudo.objects.filter(tipo='unidade', pai_id__in=area_ids).order_by('nome')
        if unidade_ids:
            # Carregar tópicos das unidades selecionadas
            topicos = Conteudo.objects.filter(tipo='topico', pai_id__in=unidade_ids).order_by('nome')
            if topico_ids:
                # Carregar subtópicos dos tópicos selecionados
                subtopicos = Conteudo.objects.filter(tipo='subtopico', pai_id__in=topico_ids).order_by('nome')
                if subtopico_ids:
                    # Carregar categorias dos subtópicos selecionados
                    categorias = Conteudo.objects.filter(tipo='categoria', pai_id__in=subtopico_ids).order_by('nome')
    
    context = {
        'page_obj': page_obj,
        'questoes': page_obj,
        'search': search,
        'areas': areas,
        'unidades': unidades,
        'topicos': topicos,
        'subtopicos': subtopicos,
        'categorias': categorias,
        'anos_disponiveis': anos_disponiveis,
        'bancas_disponiveis': bancas_disponiveis,
        'tipos_disponiveis': tipos_disponiveis,
        'dificuldades_disponiveis': dificuldades_disponiveis,
        'graus_disponiveis': graus_disponiveis,
        'filtros_ativos': {
            'area_ids': [str(a) for a in area_ids],
            'unidade_ids': [str(u) for u in unidade_ids],
            'topico_ids': [str(t) for t in topico_ids],
            'subtopico_ids': [str(s) for s in subtopico_ids],
            'categoria_ids': [str(c) for c in categoria_ids],
            'anos': [str(a) for a in anos],
            'bancas': bancas,
            'tipos_questao': tipos_questao,
            'dificuldades': dificuldades,
            'graus_escolaridade': graus_escolaridade,
            'tem_imagem': tem_imagem,
        }
    }
    return render(request, 'app/questoes.html', context)


@login_required
def questao_detail(request, questao_id):
    """Detalhe de uma questão"""
    questao = get_object_or_404(Questao, id=questao_id)
    
    # Renderizar HTML com MathJax
    questao.enunciado_rendered = html_render_math_to_img(questao.enunciado or "")
    questao.resposta_rendered = html_render_math_to_img(questao.resposta or "")
    
    context = {
        'questao': questao,
    }
    return render(request, 'app/questao_detail.html', context)


@login_required
def criar_prova(request):
    """Página para criar prova selecionando questões"""
    if request.method == 'POST':
        question_ids = request.POST.getlist('question_ids')
        gabarito_option = request.POST.get('gabarito_option', 'final_arquivo')
        test_name = request.POST.get('test_name', 'prova').strip()
        
        if not question_ids:
            messages.error(request, "Selecione pelo menos uma questão.")
            return redirect('criar_prova')
        
        # Converter para inteiros
        try:
            question_ids_int = [int(qid) for qid in question_ids]
        except ValueError:
            messages.error(request, "IDs de questões inválidos.")
            return redirect('criar_prova')
        
        # Verificar se as questões existem
        questoes = Questao.objects.filter(id__in=question_ids_int)
        if questoes.count() != len(question_ids_int):
            messages.error(request, "Algumas questões não foram encontradas.")
            return redirect('criar_prova')
        
        # Usar a view de exportação diretamente
        from app.views.export import print_test_docx
        from rest_framework.test import APIRequestFactory
        import json
        
        factory = APIRequestFactory()
        api_request = factory.post(
            '/api/print-test/docx/',
            json.dumps({
                'question_ids': question_ids_int,
                'gabarito_option': gabarito_option,
                'test_name': test_name,
            }),
            content_type='application/json'
        )
        api_request.user = request.user

        try:
            response = print_test_docx(api_request)  # api_view espera HttpRequest; ele cria o DRF Request internamente
            # Limpar seleção após gerar
            return response
        except Exception as e:
            messages.error(request, f"Erro ao gerar prova: {str(e)}")
            return redirect('criar_prova')
    
    # GET - mostrar página de seleção
    areas = Conteudo.objects.filter(tipo='area')
    context = {
        'areas': areas,
    }
    return render(request, 'app/criar_prova.html', context)


@login_required
def perfil(request):
    """Página de perfil do usuário"""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        if username:
            if request.user.username != username:
                from django.contrib.auth.models import User
                if User.objects.filter(username=username).exclude(id=request.user.id).exists():
                    messages.error(request, "Este nome de usuário já está em uso.")
                else:
                    request.user.username = username
                    request.user.save()
                    messages.success(request, "Perfil atualizado com sucesso!")
            else:
                messages.info(request, "Nenhuma alteração foi feita.")
        else:
            messages.error(request, "Nome de usuário é obrigatório.")
    
    context = {
        'user': request.user,
    }
    return render(request, 'app/perfil.html', context)

