from django.db import models

class Conteudo(models.Model):
    nome = models.CharField(max_length=100)
    pai = models.ForeignKey('self', null=True, blank=True, on_delete=models.PROTECT, related_name='subconteudos')
    
    TIPO_CHOICES = [
        ('area', 'Área'),
        ('unidade', 'Unidade'),
        ('topico', 'Tópico'),
        ('subtopico', 'Subtópico'),
        ('categoria', 'Categoria'),
    ]
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)

    def __str__(self):
        if self.pai:
            return f"{self.nome} ({self.get_tipo_display()})"
        return f"{self.nome} ({self.get_tipo_display()})"

class Questao(models.Model):
    area = models.ForeignKey('Conteudo', on_delete=models.PROTECT, related_name='q_area')
    unidade = models.ForeignKey('Conteudo', on_delete=models.PROTECT, related_name='q_unidade')
    topico = models.ForeignKey('Conteudo', on_delete=models.PROTECT, related_name='q_topico')
    subtopico = models.ForeignKey('Conteudo', on_delete=models.PROTECT, related_name='q_subtopico')
    categoria = models.ForeignKey('Conteudo', on_delete=models.PROTECT, related_name='q_categoria')

    ano = models.IntegerField()
    banca = models.CharField(max_length=100)
    tipo_questao = models.CharField(max_length=50)
    dificuldade = models.CharField(max_length=20)

