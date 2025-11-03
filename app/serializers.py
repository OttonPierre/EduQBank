# app/serializers.py
from rest_framework import serializers
from .models import Questao, Conteudo
from .utils import render_latex_to_png_bytes, html_render_math_to_img
import base64
import re
from django.contrib.auth.models import User

class ConteudoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conteudo
        fields = ['id', 'nome', 'tipo', 'pai_id']

def _html_render_math_to_img(html: str) -> str:
    if not html:
        return html or ""
    pattern = re.compile(r"(\\\[.*?\\\]|\\\(.*?\\\)|\$.*?\$)", re.DOTALL)
    def repl(m):
        src = m.group(0)
        try:
            png = render_latex_to_png_bytes(src)
            b64 = base64.b64encode(png).decode('ascii')
            return f'<img alt="math" style="vertical-align: middle;" src="data:image/png;base64,{b64}" />'
        except Exception:
            return src
    return pattern.sub(repl, html)


class QuestaoSerializer(serializers.ModelSerializer):
    area = ConteudoSerializer()
    unidade = ConteudoSerializer(required=False, allow_null=True)
    topico = ConteudoSerializer(required=False, allow_null=True)
    subtopico = ConteudoSerializer(required=False, allow_null=True)
    categoria = ConteudoSerializer(required=False, allow_null=True)
    enunciado_rendered = serializers.SerializerMethodField()
    resposta_rendered = serializers.SerializerMethodField()

    class Meta:
        model = Questao
        fields = [
            'id', 'area', 'unidade', 'topico', 'subtopico', 'categoria',
            'ano', 'banca', 'tipo_questao', 'dificuldade',
            'enunciado', 'resposta',
            'enunciado_rendered', 'resposta_rendered',
        ]

    def get_enunciado_rendered(self, obj: Questao):
        return html_render_math_to_img(obj.enunciado or "")

    def get_resposta_rendered(self, obj: Questao):
        return html_render_math_to_img(obj.resposta or "")

class QuestaoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Questao
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
