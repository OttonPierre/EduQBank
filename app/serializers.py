# app/serializers.py
from rest_framework import serializers
from .models import Questao, Conteudo
from django.contrib.auth.models import User

class ConteudoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conteudo
        fields = ['id', 'nome', 'tipo', 'pai_id']

class QuestaoSerializer(serializers.ModelSerializer):
    area = ConteudoSerializer()
    unidade = ConteudoSerializer(required=False, allow_null=True)
    topico = ConteudoSerializer(required=False, allow_null=True)
    subtopico = ConteudoSerializer(required=False, allow_null=True)
    categoria = ConteudoSerializer(required=False, allow_null=True)

    class Meta:
        model = Questao
        fields = '__all__'

class QuestaoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Questao
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
