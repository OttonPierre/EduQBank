from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage


@csrf_exempt
def upload_image(request):
    if request.method == 'POST' and request.FILES.get('upload'):
        image = request.FILES['upload']
        path = default_storage.save(f"uploads/{image.name}", image)
        url = default_storage.url(path)
        return JsonResponse({'url': url})
    return JsonResponse({'error': 'Invalid request'}, status=400)

