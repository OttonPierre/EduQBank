from django import forms
from .models import Questao
from ckeditor_uploader.widgets import CKEditorUploadingWidget

class QuestaoForm(forms.ModelForm):
    enunciado = forms.CharField(widget=CKEditorUploadingWidget())
    resposta = forms.CharField(widget=CKEditorUploadingWidget())
    resposta_gabarito = forms.CharField(widget=CKEditorUploadingWidget(), required=False)
    class Meta:
        model = Questao
        fields = '__all__'