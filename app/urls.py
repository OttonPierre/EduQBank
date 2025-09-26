from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("inicio/", views.inicio, name="inicio"),
    path('buscar-conteudos/', views.buscar_conteudos_filho, name="buscar_conteudos")
]