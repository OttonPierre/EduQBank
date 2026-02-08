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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView, RedirectView
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('app.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    
    # Favicon (aponta para asset estático)
    re_path(r'^favicon\.ico$', RedirectView.as_view(url='/assets/favicon.ico', permanent=True)),
    
    # Páginas principais
    path('', views.index, name='index'),
    path('questoes/', views.questoes_list, name='questoes_list'),
    path('questao/<int:questao_id>/', views.questao_detail_page, name='questao_detail_page'),
    path('criar-prova/', views.criar_prova, name='criar_prova'),
    path('perfil/', views.perfil, name='perfil'),
    
    # Autenticação
    path('login/', views.login_page, name='login'),
    path('signup/', views.signup_page, name='signup'),
    path('logout/', views.logout_page, name='logout'),
    
    # Cadastro de questão (staff)
    path('cadastro_questao/', views.cadastro_questao, name='cadastro_questao'),
    # CRUD Bancas (staff, AJAX)
    path('bancas/', views.bancas_page, name='bancas_page'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)