from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.shortcuts import render, redirect
from django.contrib import messages


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
        "user": {
            "email": user.email,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser
        }
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_info(request):
    """Retorna informações do usuário autenticado"""
    return Response({
        "id": request.user.id,
        "username": request.user.username,
        "email": request.user.email,
        "is_staff": request.user.is_staff,
        "is_superuser": request.user.is_superuser
    })


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    """Atualiza o perfil do usuário autenticado"""
    username = request.data.get('username')
    
    if not username:
        return Response({"detail": "Nome de usuário é obrigatório"}, status=400)
    
    # Verificar se o username já existe (exceto para o próprio usuário)
    if User.objects.filter(username=username).exclude(id=request.user.id).exists():
        return Response({"detail": "Este nome de usuário já está em uso"}, status=400)
    
    request.user.username = username
    request.user.save()
    
    return Response({
        "message": "Perfil atualizado com sucesso",
        "user": {
            "id": request.user.id,
            "username": request.user.username,
            "email": request.user.email,
            "is_staff": request.user.is_staff,
            "is_superuser": request.user.is_superuser
        }
    })


# Views com templates Django
def login_page(request):
    """Página de login com template"""
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not email or not password:
            messages.error(request, "Preencha todos os campos.")
            return render(request, 'app/pages/auth.html', {'mode': 'login'})
        
        user = authenticate(username=email, password=password)
        if user is None:
            messages.error(request, "Credenciais inválidas.")
            return render(request, 'app/pages/auth.html', {'mode': 'login'})
        
        django_login(request, user)
        messages.success(request, f"Bem-vindo, {user.username}!")
        next_url = request.GET.get('next', 'index')
        return redirect(next_url)
    
    return render(request, 'app/pages/auth.html', {'mode': 'login'})


def signup_page(request):
    """Página de cadastro com template"""
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not email or not password:
            messages.error(request, "Preencha todos os campos.")
            return render(request, 'app/pages/auth.html', {'mode': 'signup'})
        
        if len(password) < 8:
            messages.error(request, "A senha deve ter pelo menos 8 caracteres.")
            return render(request, 'app/pages/auth.html', {'mode': 'signup'})
        
        if User.objects.filter(username=email).exists():
            messages.error(request, "Este email já está cadastrado.")
            return render(request, 'app/pages/auth.html', {'mode': 'signup'})
        
        user = User.objects.create_user(username=email, email=email, password=password)
        django_login(request, user)
        messages.success(request, "Conta criada com sucesso!")
        return redirect('index')
    
    return render(request, 'app/pages/auth.html', {'mode': 'signup'})


def logout_page(request):
    """Logout do usuário"""
    django_logout(request)
    messages.info(request, "Você saiu da sua conta.")
    return redirect('index')

