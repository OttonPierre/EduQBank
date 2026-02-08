"""
CRUD de Bancas (bancas organizadoras) com API JSON para uso via AJAX.
"""
import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render

from app.models import Banca


def _staff_required(user):
    return user.is_authenticated and user.is_staff


# ---------- API JSON (AJAX) ----------

def _api_banca_list(request):
    """Lista todas as bancas. Resposta JSON."""
    bancas = Banca.objects.all().order_by('nome')
    data = [{'id': b.id, 'nome': b.nome, 'sigla': b.sigla or ''} for b in bancas]
    return JsonResponse(data, safe=False)


def _api_banca_create(request):
    """Cria uma banca. Body JSON: { "nome": "...", "sigla": "..." }."""
    if not _staff_required(request.user):
        return JsonResponse({'error': 'Acesso negado'}, status=403)
    try:
        body = json.loads(request.body)
        nome = (body.get('nome') or '').strip()
        if not nome:
            return JsonResponse({'error': 'Nome é obrigatório'}, status=400)
        sigla = (body.get('sigla') or '').strip()
        banca = Banca.objects.create(nome=nome, sigla=sigla)
        return JsonResponse({'id': banca.id, 'nome': banca.nome, 'sigla': banca.sigla or ''}, status=201)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)


def _api_banca_detail(request, pk):
    """Retorna uma banca por ID."""
    try:
        banca = Banca.objects.get(pk=pk)
        return JsonResponse({'id': banca.id, 'nome': banca.nome, 'sigla': banca.sigla or ''})
    except Banca.DoesNotExist:
        return JsonResponse({'error': 'Banca não encontrada'}, status=404)


def _api_banca_update(request, pk):
    """Atualiza uma banca. Body JSON: { "nome": "...", "sigla": "..." }."""
    if not _staff_required(request.user):
        return JsonResponse({'error': 'Acesso negado'}, status=403)
    try:
        banca = Banca.objects.get(pk=pk)
    except Banca.DoesNotExist:
        return JsonResponse({'error': 'Banca não encontrada'}, status=404)
    try:
        body = json.loads(request.body)
        if 'nome' in body:
            nome = (body.get('nome') or '').strip()
            if not nome:
                return JsonResponse({'error': 'Nome é obrigatório'}, status=400)
            banca.nome = nome
        if 'sigla' in body:
            banca.sigla = (body.get('sigla') or '').strip()
        banca.save()
        return JsonResponse({'id': banca.id, 'nome': banca.nome, 'sigla': banca.sigla or ''})
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)


def _api_banca_delete(request, pk):
    """Remove uma banca."""
    if not _staff_required(request.user):
        return JsonResponse({'error': 'Acesso negado'}, status=403)
    try:
        banca = Banca.objects.get(pk=pk)
        banca.delete()
        return JsonResponse({'success': True}, status=200)
    except Banca.DoesNotExist:
        return JsonResponse({'error': 'Banca não encontrada'}, status=404)


@require_GET
def api_banca_list(request):
    return _api_banca_list(request)


@require_POST
def api_banca_create(request):
    return _api_banca_create(request)


@require_http_methods(["GET"])
def api_banca_detail(request, pk):
    return _api_banca_detail(request, pk)


@require_http_methods(["PUT", "PATCH"])
def api_banca_update(request, pk):
    return _api_banca_update(request, pk)


@require_http_methods(["DELETE"])
def api_banca_delete(request, pk):
    return _api_banca_delete(request, pk)


def api_banca_list_or_create(request):
    """GET: lista; POST: cria."""
    if request.method == 'GET':
        return _api_banca_list(request)
    if request.method == 'POST':
        return _api_banca_create(request)
    return JsonResponse({'error': 'Método não permitido'}, status=405)


def api_banca_detail_update_delete(request, pk):
    """GET: detalhe; PUT/PATCH: atualiza; DELETE: remove."""
    if request.method == 'GET':
        return _api_banca_detail(request, pk)
    if request.method in ('PUT', 'PATCH'):
        return _api_banca_update(request, pk)
    if request.method == 'DELETE':
        return _api_banca_delete(request, pk)
    return JsonResponse({'error': 'Método não permitido'}, status=405)


# ---------- Página (template + AJAX) ----------

@ensure_csrf_cookie
@login_required
@user_passes_test(_staff_required, login_url='/login/')
def bancas_page(request):
    """Página de gestão de Bancas: lista + modal para criar/editar, tudo via AJAX."""
    return render(request, 'app/bancas.html')
