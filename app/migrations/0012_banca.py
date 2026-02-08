# Generated manually for Banca model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_alter_conteudo_nome_alter_questao_grau_escolaridade_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Banca',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=200)),
                ('sigla', models.CharField(blank=True, max_length=30)),
            ],
            options={
                'verbose_name': 'Banca',
                'verbose_name_plural': 'Bancas',
                'ordering': ['nome'],
            },
        ),
    ]
