from django.urls import path
from . import views


urlpatterns = [
    path("cadastro_questao/", views.cadastro_questao, name="cadastro_questao"),
    path('buscar-conteudos/', views.buscar_conteudos_filho, name="buscar_conteudos")
]