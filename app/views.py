from django.shortcuts import render, redirect
from .models import Conteudo
from .forms import QuestaoForm
from django.http import JsonResponse
from django.contrib import messages

def index(request):
    if request.method == 'POST':
        data = request.POST.copy()
        for campo in ['unidade', 'topico', 'subtopico', 'categoria']:
            if not data.get(campo):
                data[campo] = None

        form = QuestaoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Questão cadastrada com sucesso!")
            return redirect('index')
        else:
            messages.error(request, "Erro ao cadastrar questão.")
    else:   
        form = QuestaoForm()
        
    areas = Conteudo.objects.filter(tipo='area')
    return render(request, 'app/index.html', {'form':form, 'areas': areas})

def buscar_conteudos_filho(request):
    pai_id = request.GET.get('pai_id')
    if not pai_id:
        return JsonResponse({'error': 'pai_id ausente'}, status=400)

    filhos = Conteudo.objects.filter(pai_id=pai_id).values('id', 'nome')
    return JsonResponse(list(filhos), safe=False)

def inicio(request):
    return render(request, 'app/inicio.html')