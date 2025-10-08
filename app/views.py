from django.shortcuts import render, redirect
from .models import Conteudo
from .forms import QuestaoForm
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import viewsets
from rest_framework import generics
from .models import Questao
from .serializers import QuestaoSerializer  


@api_view(["POST"])
def signup(request):
    email = request.data.get("email")
    password = request.data.get("password")

    if not email or not password:
        return Response({"detail": "Campos obrigatórios"}, status=400)

    if User.objects.filter(username=email).exists():
        return Response({"detail": "Email já cadastrado"}, status=400)

    user = User.objects.create_user(username=email, email=email, password=password)
    return Response({"message": "Usuário criado com sucesso"}, status=201)


@api_view(["POST"])
def login_view(request):
    email = request.data.get("email")
    password = request.data.get("password")

    user = authenticate(username=email, password=password)
    if user is None:
        return Response({"detail": "Credenciais inválidas"}, status=400)

    refresh = RefreshToken.for_user(user)
    return Response({
        "token": str(refresh.access_token),
        "refresh": str(refresh),
        "user": {"email": user.email}
    })

def cadastro_questao(request):
    if request.method == 'POST':
        data = request.POST.copy()
        for campo in ['unidade', 'topico', 'subtopico', 'categoria']:
            if not data.get(campo):
                data[campo] = None

        form = QuestaoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Questão cadastrada com sucesso!")
            return redirect('cadastro_questao')
        else:
            messages.error(request, "Erro ao cadastrar questão.")
    else:   
        form = QuestaoForm()
        
    areas = Conteudo.objects.filter(tipo='area')
    return render(request, 'app/cadastro_questao.html', {'form':form, 'areas': areas})

def buscar_conteudos_filho(request):
    pai_id = request.GET.get('pai_id')
    if not pai_id:
        return JsonResponse({'error': 'pai_id ausente'}, status=400)

    filhos = Conteudo.objects.filter(pai_id=pai_id).values('id', 'nome')
    return JsonResponse(list(filhos), safe=False)

def inicio(request):
    return render(request, 'app/inicio.html')

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


class QuestaoList(generics.ListAPIView):
    queryset = Questao.objects.all()
    serializer_class = QuestaoSerializer

class QuestaoDetail(generics.RetrieveAPIView):
    queryset = Questao.objects.all()
    serializer_class = QuestaoSerializer

class QuestaoViewSet(viewsets.ModelViewSet):
    queryset = Questao.objects.all()
    serializer_class = QuestaoSerializer