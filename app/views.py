from django.shortcuts import render, redirect
from .models import Conteudo
from .forms import QuestaoForm
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import viewsets
from rest_framework import generics
from .models import Questao
from .serializers import QuestaoSerializer, ConteudoSerializer  
import json
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image as ReportLabImage, KeepTogether
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus.tableofcontents import TableOfContents
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from datetime import datetime
import io
import os
import urllib.parse
import requests
from PIL import Image as PILImage

@csrf_exempt
def upload_image(request):
    if request.method == 'POST' and request.FILES.get('upload'):
        image = request.FILES['upload']
        path = default_storage.save(f"uploads/{image.name}", image)
        url = default_storage.url(path)
        return JsonResponse({'url': url})
    return JsonResponse({'error': 'Invalid request'}, status=400)


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



def buscar_conteudos_filho(request):
    pai_id = request.GET.get('pai_id')
    if not pai_id:
        return JsonResponse({'error': 'pai_id ausente'}, status=400)

    filhos = Conteudo.objects.filter(pai_id=pai_id).values('id', 'nome')
    return JsonResponse(list(filhos), safe=False)

@api_view(["GET"])
def list_conteudos(request):
    """List all Conteudos, optionally filtered by tipo and pai_id"""
    conteudos = Conteudo.objects.all()
    
    tipo = request.query_params.get('tipo', None)
    if tipo:
        conteudos = conteudos.filter(tipo=tipo)
    
    pai_id = request.query_params.get('pai_id', None)
    if pai_id:
        conteudos = conteudos.filter(pai_id=pai_id)
    else:
        # If no pai_id, return only root-level (no parent) conteudos
        if tipo:
            conteudos = conteudos.filter(pai__isnull=True)
    
    serializer = ConteudoSerializer(conteudos, many=True)
    return Response(serializer.data)

@api_view(["GET"])
def get_unique_values(request):
    """Get unique values for fields like banca, tipo_questao, dificuldade, ano"""
    field = request.query_params.get('field', None)
    
    if not field:
        return Response({"error": "Field parameter is required"}, status=400)
    
    if field == 'banca':
        values = Questao.objects.values_list('banca', flat=True).distinct().order_by('banca')
    elif field == 'tipo_questao':
        values = Questao.objects.values_list('tipo_questao', flat=True).distinct().order_by('tipo_questao')
    elif field == 'dificuldade':
        values = Questao.objects.values_list('dificuldade', flat=True).distinct().order_by('dificuldade')
    elif field == 'ano':
        values = Questao.objects.values_list('ano', flat=True).distinct().order_by('-ano')
    else:
        return Response({"error": "Invalid field"}, status=400)
    
    return Response(list(values))

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
    
    def get_queryset(self):
        queryset = Questao.objects.all()
        
        # Text search on enunciado
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(enunciado__icontains=search)
        
        # Filter by area (by ID)
        area_id = self.request.query_params.get('area_id', None)
        if area_id:
            try:
                queryset = queryset.filter(area_id=int(area_id))
            except ValueError:
                pass
        
        # Filter by unidade (by ID)
        unidade_id = self.request.query_params.get('unidade_id', None)
        if unidade_id:
            try:
                queryset = queryset.filter(unidade_id=int(unidade_id))
            except ValueError:
                pass
        
        # Filter by topico (by ID)
        topico_id = self.request.query_params.get('topico_id', None)
        if topico_id:
            try:
                queryset = queryset.filter(topico_id=int(topico_id))
            except ValueError:
                pass
        
        # Filter by subtopico (by ID)
        subtopico_id = self.request.query_params.get('subtopico_id', None)
        if subtopico_id:
            try:
                queryset = queryset.filter(subtopico_id=int(subtopico_id))
            except ValueError:
                pass
        
        # Filter by categoria (by ID)
        categoria_id = self.request.query_params.get('categoria_id', None)
        if categoria_id:
            try:
                queryset = queryset.filter(categoria_id=int(categoria_id))
            except ValueError:
                pass
        
        # Filter by ano
        ano = self.request.query_params.get('ano', None)
        if ano:
            try:
                ano_int = int(ano)
                queryset = queryset.filter(ano=ano_int)
            except ValueError:
                pass
        
        # Filter by banca
        banca = self.request.query_params.get('banca', None)
        if banca:
            queryset = queryset.filter(banca__icontains=banca)
        
        # Filter by tipo_questao
        tipo_questao = self.request.query_params.get('tipo_questao', None)
        if tipo_questao:
            queryset = queryset.filter(tipo_questao__icontains=tipo_questao)
        
        # Filter by dificuldade
        dificuldade = self.request.query_params.get('dificuldade', None)
        if dificuldade:
            queryset = queryset.filter(dificuldade__icontains=dificuldade)
        
        return queryset