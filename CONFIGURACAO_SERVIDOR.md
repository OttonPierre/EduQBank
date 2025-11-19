# Configuração do Servidor - EduQBank

Este documento contém as instruções para configurar o servidor AlmaLinux 9 corretamente para que o login seja persistido.

## Problema Resolvido

O problema de login não persistir foi causado por:
1. **ALLOWED_HOSTS vazio** - O Django bloqueia requisições de domínios não autorizados
2. **Configurações de CORS inadequadas** - Conflito entre `CORS_ALLOW_ALL_ORIGINS` e `CORS_ALLOWED_ORIGINS`
3. **Falta de configurações de sessão/cookies** - Cookies não estavam sendo configurados corretamente para produção
4. **Configurações de JWT** - Tokens podem estar expirando muito rápido

## Variáveis de Ambiente Necessárias

Configure as seguintes variáveis de ambiente no seu servidor:

### 1. Configuração Básica

```bash
# Secret Key do Django (gere uma nova para produção!)
export SECRET_KEY='sua-chave-secreta-aqui-muito-longa-e-aleatoria'

# Modo de Debug (False em produção)
export DEBUG='False'

# Domínios permitidos (separados por vírgula, sem espaços extras)
export ALLOWED_HOSTS='seu-dominio.com,www.seu-dominio.com,ip-do-servidor'
```

### 2. Configuração de CORS

```bash
# Origens permitidas para CORS (separadas por vírgula)
# Deve incluir o protocolo (http:// ou https://)
export CORS_ALLOWED_ORIGINS='https://seu-dominio.com,https://www.seu-dominio.com'
```

### 3. Configuração de CSRF (opcional, mas recomendado)

```bash
# Origens confiáveis para CSRF (geralmente as mesmas do CORS)
export CSRF_TRUSTED_ORIGINS='https://seu-dominio.com,https://www.seu-dominio.com'
```

## Exemplo de Configuração Completa

Crie um arquivo `.env` na raiz do projeto (EduQBank/) ou configure as variáveis no seu servidor:

```bash
# .env
SECRET_KEY='django-insecure-mm*t!tsgl5=)f)@hevqnyn_nbiiq71m4@kottj1w3=ju!yzq%g'
DEBUG=False
ALLOWED_HOSTS='meusite.com,www.meusite.com,192.168.1.100'
CORS_ALLOWED_ORIGINS='https://meusite.com,https://www.meusite.com'
CSRF_TRUSTED_ORIGINS='https://meusite.com,https://www.meusite.com'
```

## Como Configurar no Servidor

### Opção 1: Arquivo .env (Recomendado)

1. Crie um arquivo `.env` na raiz do projeto:
```bash
cd /caminho/para/EduQBank
nano .env
```

2. Adicione as variáveis de ambiente (veja exemplo acima)

3. Instale python-dotenv (se ainda não tiver):
```bash
pip install python-dotenv
```

4. Adicione no início do `settings.py` (já está configurado para usar `os.environ.get()`)

### Opção 2: Variáveis de Ambiente do Sistema

1. Edite o arquivo de configuração do seu servidor web (Nginx, Apache, etc.) ou systemd service

2. Para systemd, edite o arquivo de serviço:
```bash
sudo nano /etc/systemd/system/eduqbank.service
```

3. Adicione as variáveis na seção `[Service]`:
```ini
[Service]
Environment="SECRET_KEY=sua-chave-secreta"
Environment="DEBUG=False"
Environment="ALLOWED_HOSTS=seu-dominio.com,www.seu-dominio.com"
Environment="CORS_ALLOWED_ORIGINS=https://seu-dominio.com,https://www.seu-dominio.com"
```

4. Recarregue e reinicie o serviço:
```bash
sudo systemctl daemon-reload
sudo systemctl restart eduqbank
```

### Opção 3: Exportar no Shell

Se estiver rodando manualmente, exporte antes de iniciar:
```bash
export SECRET_KEY='sua-chave'
export DEBUG='False'
export ALLOWED_HOSTS='seu-dominio.com'
export CORS_ALLOWED_ORIGINS='https://seu-dominio.com'
python manage.py runserver
```

## Gerar uma Nova Secret Key

**IMPORTANTE**: Gere uma nova SECRET_KEY para produção:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Configuração do Banco de Dados MariaDB

Se você está usando MariaDB, certifique-se de que o `settings.py` está configurado corretamente:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'nome_do_banco',
        'USER': 'usuario',
        'PASSWORD': 'senha',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}
```

## Verificações Pós-Configuração

1. **Verifique se o servidor está acessível**:
```bash
curl -I https://seu-dominio.com
```

2. **Verifique os logs do Django**:
```bash
tail -f /caminho/para/logs/django.log
```

3. **Teste o login**:
   - Faça login no sistema
   - Verifique se o token está sendo salvo no localStorage (F12 > Application > Local Storage)
   - Navegue para outra página
   - Verifique se ainda está autenticado

## Problemas Comuns

### 1. "DisallowedHost" error
- **Solução**: Adicione o domínio/IP em `ALLOWED_HOSTS`

### 2. CORS errors no navegador
- **Solução**: Verifique se `CORS_ALLOWED_ORIGINS` inclui o domínio correto com o protocolo (http:// ou https://)

### 3. Token expira muito rápido
- **Solução**: As configurações de JWT já estão ajustadas (1 dia para access token, 7 dias para refresh token)

### 4. Cookies não funcionam
- **Solução**: Se estiver usando HTTPS, certifique-se de que `SESSION_COOKIE_SECURE` e `CSRF_COOKIE_SECURE` estão como `True` (já configurado automaticamente quando `DEBUG=False`)

## Suporte

Se ainda tiver problemas após seguir estas instruções, verifique:
- Logs do servidor web (Nginx/Apache)
- Logs do Django
- Console do navegador (F12) para erros JavaScript
- Network tab do navegador para ver as requisições HTTP

