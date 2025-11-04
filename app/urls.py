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
    path('conteudos/', views.list_conteudos, name='list_conteudos'),
    path('unique-values/', views.get_unique_values, name='get_unique_values'),
    path('generate-test/docx/', views.generate_test_docx, name='generate_test_docx'),
    path('', include(router.urls)),
]