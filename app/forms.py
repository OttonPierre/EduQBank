from django import forms
from .models import Questao

class QuestaoForm(forms.ModelForm):
    class Meta:
        model = Questao
        fields = '__all__'