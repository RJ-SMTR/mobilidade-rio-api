
# mobilidade-rio-api

API estática do aplicativo de [pontos.mobilidade.rio](http://pontos.mobilidade.rio) da Prefeitura da cidade do Rio de Janeiro.

## Requerimentos

* [Docker](https://www.docker.com/) (local), Kubernetes (produção)
* Python >=3.9

## Desenvolvimento

### Iniciando o ambiente

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
```

### Criando a aplicação

```sh
docker-compose -f ./mobilidade_rio/docker-compose.yml up --build
```

Os containers `django_hd` (API) e e`postgres_hd` (banco) são criados a
partir desse comando. Você pode acessar a API em:
`http://localhost:8010`

> Para resetar a aplicação do zero, remova os containers e volumes
> associados:
>
> ```sh
> docker-compose -f ./mobilidade_rio/docker-compose.yml down -v && docker image prune -f
> ```

Para acessar o banco via linha de comando (ainda está vazio!), basta rodar:

```sh
docker exec -it postgres_hd psql -U postgres
```

> Veja mais sobre os comandos do psql [aqui](https://www.postgresql.org/docs/9.1/app-psql.html).

### Populando o banco

1. Salve os arquivos do GTFS na pasta
   [`scripts/populate_db/csv_files/pontos`](/scripts/populate_db/csv_files/pontos).
   A estrutura deve seguir:

  ```
  csv_files
  ├── pontos
  │   ├── agency.csv
  │   ├── calendar_dates.csv
  │   ├── calendar.csv
  │   ├── routes.csv
  │   ├── shapes.csv
  │   ├── stop_times.csv
  │   ├── stops.csv
  │   ├── transfers.csv
  │   └── trips.csv
  ```

2. Execute o upload dos dados:

```sh
python scripts/populate_db/populate_db.py --empty_table
```

O arquivo `settings.jsonc` contém as configurações para popular o banco
(nomes das tabelas, ordem, parâmetros para o upload).
  
  > **Os dados subiram?**
  > Você pode listar as tabelas [pelo shell do
  > Postgres](#acessando-o-banco-local) com o comando `\d`. Elas estarão nomeadas como `pontos_[model]` (ex: `pontos_agency`).

### Alterando os modelos

<!-- TODO: Caso haja mudança em outros arquivos (urls, views, serializers, admin.py), essas tambem sao registradas via migrations? -->

Os modelos estão definidos em `mobilidade_rio/models.py`. Para registrar mudanças feitas nesse arquivo (migrações), rode:

```sh
python mobilidade_rio/manage.py makemigrations
python mobilidade_rio/manage.py migrate
```

> Esses comando são executados automaticamente quando o container é criado.

Pronto! Basta acessar a API e ver os dados (ex: <http://localhost:8010/stops/?stop_code=7KKY>).

## Produção (ATUALIZAR)

### Acessar o ambiente

Para acessar o ambiente de Staging localmente, rode:

```sh
kubectl exec -it -n mobilidade-v2-staging deploy/smtr-stag-mobilidade-api -- /bin/bash
```

### Como subir dados

No seu local, copie o novo `fixture` para o Kubernetes (veja
   `<pod-em-prod>` [aqui](todo-add-link-library)) rodando:

```sh
kubectl cp mobilidade_rio/fixtures/<seu-fixture>.json mobilidade-v2/<pod-em-prod>:/app/fixtures/<seu-fixture>.json
```

> Você pode também copiar um `fixture` do Kubernetes para seu local trocando a
> ordem dos parâmetros.

Agora seu `fixture` está armazenado em produção! Para subir os dados
no banco, acesse o ambiente de produção e rode:

```sh
python manage.py loaddata fixtures/<seu-fixture>.json
```

### Como deletar dados

Acesse o ambiente de produção e rode:

```sh
python3 manage.py shell
```

Esse comando vai abrir um `shell` do Django. Em seguida, importe o
respectivo modelo e delete os dados com:

```python
# ex: importa dados de Sequência das linhas
from mobilidade_rio.pontos.models import Sequence
# exclui uma linha passando seu `trip_id`
Sequence.objects.filter(trip=<trip_id>).delete()
```

> Para deletar todos os dados de um modelo, use `.all()` ao invés de
`.filter(...)`.

Todos os modelos existentes na API correespondem a [estas classes](/mobilidade_rio/pontos/models.py).
