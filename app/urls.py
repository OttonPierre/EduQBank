from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter
from .views import QuestaoViewSet

router = DefaultRouter()
router.register(r'questoes', QuestaoViewSet)

urlpatterns =[
    path("signup/", views.signup),
    path("login/", views.login_view),
    path("cadastro_questao/", views.cadastro_questao, name="cadastro_questao"),
    path('buscar-conteudos/', views.buscar_conteudos_filho, name="buscar_conteudos"),
    path('questoes/', views.list_questoes, name='list_questoes'),
    path('questoes/<int:pk>/', views.questao_detail),
]