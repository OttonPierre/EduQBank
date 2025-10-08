"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from app import views
from app.views import QuestaoViewSet

urlpatterns = [
    path("api/", include("app.urls")),
    path("admin/", admin.site.urls),
    path('', TemplateView.as_view(template_name='index.html')),
    path("api/signup/", views.signup),
    path("api/login/", views.login_view),
    path("cadastro_questao/", views.cadastro_questao, name="cadastro_questao"),
    path('buscar-conteudos/', views.buscar_conteudos_filho, name="buscar_conteudos"),
    path('questoes/', views.list_questoes, name='list_questoes'),
    path('questoes/<int:pk>/', views.questao_detail, name='questao_detail'),
]