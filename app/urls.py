from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'questoes', views.QuestaoViewSet)

urlpatterns = [
    path('auth/signup/', views.signup, name='signup'),
    path('auth/login/', views.login_view, name='login'),
    path('upload-image/', views.upload_image, name='upload_image'),
    path('buscar-conteudos/', views.buscar_conteudos_filho, name='buscar_conteudos'),
    path('', include(router.urls)),
]