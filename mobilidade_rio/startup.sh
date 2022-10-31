# Este arquivo susbtituirá o start-server.sh
# Por enquanto está em testes

# TODO: fazer o Docker ler este arquivo e parar de dar erros como:
# ': not found  | /django/startup.sh: 5:'
# Ele lê o arquivo mas o diretório parece conter algum problema.
# De resto tudo funciona.

#!/usr/bin/env bash
# startup.sh
(
    echo 'hello startup.sh';
    cd /app;
    # echo 'files:'; ls -a;
    source .env;
    python manage.py makemigrations;
    python manage.py migrate;
    python manage.py runserver 0.0.0.0:8000;
)