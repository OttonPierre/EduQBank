from django.contrib import admin
from .models import Conteudo, Questao

@admin.register(Conteudo)
class ConteudoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'pai', 'tipo')
    search_fields = ('nome',)

@admin.register(Questao)
class QuestaoAdmin(admin.ModelAdmin):
    list_display = ('area', 'unidade', 'topico', 'subtopico', 'categoria', 'ano', 'banca', 'tipo_questao', 'dificuldade')
    search_fields = ('area', 'unidade', 'topico', 'subtopico', 'categoria',)