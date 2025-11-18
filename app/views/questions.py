from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import viewsets, generics
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from app.models import Questao, Conteudo
from app.forms import QuestaoForm
from app.serializers import QuestaoSerializer


class QuestaoList(generics.ListAPIView):
    queryset = Questao.objects.all()
    serializer_class = QuestaoSerializer


class QuestaoDetail(generics.RetrieveAPIView):
    queryset = Questao.objects.all()
    serializer_class = QuestaoSerializer


class QuestaoViewSet(viewsets.ModelViewSet):
    queryset = Questao.objects.all()
    serializer_class = QuestaoSerializer
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        All actions require authentication.
        """
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        from django.db.models import Q
        queryset = Questao.objects.all()
        
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(enunciado__icontains=search)
        
        area_id = self.request.query_params.get('area_id', None)
        if area_id:
            try:
                queryset = queryset.filter(area_id=int(area_id))
            except ValueError:
                pass
        
        unidade_id = self.request.query_params.get('unidade_id', None)
        if unidade_id:
            try:
                queryset = queryset.filter(unidade_id=int(unidade_id))
            except ValueError:
                pass
        
        topico_id = self.request.query_params.get('topico_id', None)
        if topico_id:
            try:
                queryset = queryset.filter(topico_id=int(topico_id))
            except ValueError:
                pass
        
        subtopico_id = self.request.query_params.get('subtopico_id', None)
        if subtopico_id:
            try:
                queryset = queryset.filter(subtopico_id=int(subtopico_id))
            except ValueError:
                pass
        
        categoria_id = self.request.query_params.get('categoria_id', None)
        if categoria_id:
            try:
                queryset = queryset.filter(categoria_id=int(categoria_id))
            except ValueError:
                pass
        
        ano = self.request.query_params.get('ano', None)
        if ano:
            try:
                ano_int = int(ano)
                queryset = queryset.filter(ano=ano_int)
            except ValueError:
                pass
        
        banca = self.request.query_params.get('banca', None)
        if banca:
            queryset = queryset.filter(banca__icontains=banca)
        
        tipo_questao = self.request.query_params.get('tipo_questao', None)
        if tipo_questao:
            queryset = queryset.filter(tipo_questao__icontains=tipo_questao)
        
        dificuldade = self.request.query_params.get('dificuldade', None)
        if dificuldade:
            queryset = queryset.filter(dificuldade__icontains=dificuldade)
        
        grau_escolaridade = self.request.query_params.get('grau_escolaridade', None)
        if grau_escolaridade:
            queryset = queryset.filter(grau_escolaridade=grau_escolaridade)
        
        tem_imagem = self.request.query_params.get('tem_imagem', None)
        if tem_imagem is not None:
            if tem_imagem.lower() == 'true':
                # Questões que têm imagem no enunciado ou resposta
                queryset = queryset.filter(
                    Q(enunciado__icontains='<img') | Q(resposta__icontains='<img')
                )
            elif tem_imagem.lower() == 'false':
                # Questões que não têm imagem
                queryset = queryset.exclude(
                    Q(enunciado__icontains='<img') | Q(resposta__icontains='<img')
                )
        
        return queryset


@api_view(["GET"])
def list_questoes(request):
    questions = Questao.objects.all()
    serializer = QuestaoSerializer(questions, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def questao_detail(request, pk):
    try:
        question = Questao.objects.get(pk=pk)
    except Questao.DoesNotExist:
        return Response({"detail": "Questão não encontrada"}, status=404)
    serializer = QuestaoSerializer(question)
    return Response(serializer.data)


def is_staff(user):
    return user.is_authenticated and user.is_staff

def authenticate_jwt_request(request):
    """
    Autentica a requisição usando JWT token do header Authorization ou cookie.
    Retorna o usuário se autenticado, None caso contrário.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    jwt_auth = JWTAuthentication()
    token = None
    
    # Tentar obter token do header Authorization primeiro
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        logger.debug("Token obtido do header Authorization")
    else:
        # Tentar obter token do cookie
        token = request.COOKIES.get('jwt_token')
        if token:
            logger.debug("Token obtido do cookie")
        else:
            logger.debug(f"Cookie jwt_token não encontrado. Cookies disponíveis: {list(request.COOKIES.keys())}")
    
    if token:
        try:
            validated_token = jwt_auth.get_validated_token(token)
            user = jwt_auth.get_user(validated_token)
            logger.debug(f"Usuário autenticado: {user.username}, is_staff: {user.is_staff}")
            return user
        except (InvalidToken, TokenError, KeyError, IndexError) as e:
            logger.debug(f"Erro ao validar token: {e}")
            pass
    return None

def cadastro_questao(request):
    import logging
    logger = logging.getLogger(__name__)
    
    # Verificar autenticação via JWT primeiro (para requisições do frontend)
    user = authenticate_jwt_request(request)
    logger.debug(f"Usuário após authenticate_jwt_request: {user}")
    
    # Se não autenticado via JWT, verificar sessão Django (para uso direto no navegador)
    if not user:
        user = request.user if request.user.is_authenticated else None
        logger.debug(f"Usuário após verificar sessão: {user}")
    
    # Verificar se está autenticado e é staff
    # Quando autenticado via JWT, o user existe mas pode não ter is_authenticated=True
    # Então verificamos se user existe e é staff
    if not user:
        logger.debug("Nenhum usuário encontrado")
        messages.error(request, "Você precisa estar autenticado para acessar esta página.")
        return redirect('/')
    
    if not user.is_staff:
        logger.debug(f"Usuário {user.username} não é staff")
        messages.error(request, "Você precisa ser staff para acessar esta página.")
        return redirect('/')
    
    logger.debug(f"Acesso permitido para {user.username} (staff: {user.is_staff})")
    
    # Autenticar o usuário na sessão Django para que o formulário funcione
    from django.contrib.auth import login
    if not request.user.is_authenticated or request.user != user:
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    
    if request.method == 'POST':
        form = QuestaoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Questão cadastrada com sucesso!")
            return redirect('cadastro_questao')
        else:
            messages.error(request, "Erro ao cadastrar questão.")
    else:
        form = QuestaoForm()

    areas = Conteudo.objects.filter(tipo='area')
    return render(request, 'app/cadastro_questao.html', {'form': form, 'areas': areas})


def inicio(request):
    return render(request, 'app/inicio.html')

