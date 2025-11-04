from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


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

