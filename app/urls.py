from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import bancas as bancas_views

router = DefaultRouter()
router.register(r'questoes', views.QuestaoViewSet)

urlpatterns = [
    path('bancas/', bancas_views.api_banca_list_or_create, name='api_banca_list'),
    path('bancas/<int:pk>/', bancas_views.api_banca_detail_update_delete, name='api_banca_detail'),
    path('auth/signup/', views.signup, name='signup'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/user-info/', views.user_info, name='user_info'),
    path('auth/update-profile/', views.update_user_profile, name='update_user_profile'),
    path('upload-image/', views.upload_image, name='upload_image'),
    path('buscar-conteudos/', views.buscar_conteudos_filho, name='buscar_conteudos'),
    path('conteudos/', views.list_conteudos, name='list_conteudos'),
    path('unique-values/', views.get_unique_values, name='get_unique_values'),
    path('print-test/docx/', views.print_test_docx, name='print_test_docx'),
    path('', include(router.urls)),
]