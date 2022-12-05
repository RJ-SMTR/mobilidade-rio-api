
# mobilidade-rio-api

API estática do aplicativo de [pontos.mobilidade.rio](http://pontos.mobilidade.rio) da Prefeitura da cidade do Rio de Janeiro.

## Estágios de desenvolvimento

* **Nativo**
  * _Desenvolvimento Local em servidor Nativo_
  * Para desenvolver com rapidez os recursos do servidor, ele é executado localmente na sua máquina, sem utilizar o Docker.
  * Se este não é o seu caso, use o `Local`.
* **Local**
  * _Desenvolvimento Local_
  * Utiliza localmente o Docker.
* **Dev**
  * _Desenvolvimento em servidor Remoto_
  * Desenvolver remotamente usando orquestrador Kubernetes (K8s) com o Docker.
* **Staging**
  * _Teste em servidor Remoto_
  * Testar remotamente usando orquestrador Kubernetes (K8s) com o Docker.
* **Prod**
  * _Produção em servidor oficial_
  * Executar as mesmas configurações do ambiente de desenvolvimento, porém com o Docker configurado para produção.

Resumindo o que cada estágio faz:

| Nome | Descrição | Recursos |
|---|---|---|
| native | Desenv. nativo | 🖥️ |
| local | Desenv. local | 🐋 |
| dev | Desenv. Remoto | 🐋☸️ |
| stag | Staging | 🐋☸️ |
| prod | Produção | 🐋☸️ |

## Requerimentos

* [Docker](https://www.docker.com/)(local, desenvolvimento)
* [Kubernetes](https://kubernetes.io/) (produção)
* [Postgres](https://www.postgresql.org/) (nativo)
* Python >=3.9

## Desenvolvimento

### Iniciando o ambiente

```bash
conda activate mobilidade_rio_api
pip install -r mobilidade_rio/requirements-dev.txt
```

### Criando a aplicação

Dev nativo:
```bash
python mobilidade_rio/manage.py makemigrations
python mobilidade_rio/manage.py migrate
python mobilidade_rio/manage.py runserver 8001
```

Dev local:
```bash
docker-compose -f "mobilidade_rio/dev_local/docker-compose_local.yml" up --build
```

Dev remoto:

> _em construção, a saber se será necessário_

### Acessando a aplicação

Para acessar 
* URLs for pontos are in `<site>/gtfs/<entity>` prefix;
  > Example:  
  > Use ✔️ `http://localhost:8010/gtfs/routes`  
  > instead of ❌ `http://localhost:8010/routes`

Os containers `django_hd` (API) e `postgres_hd` (banco) são criados a
partir desse comando. Você pode acessar a API em:
`http://localhost:8010`

Para acessar o banco via linha de comando (ainda está vazio!), basta rodar:

```sh
docker exec -it postgres_hd psql -U postgres
```

> Veja mais sobre os comandos do psql [aqui](https://www.postgresql.org/docs/9.1/app-psql.html).

> Para resetar a aplicação do zero, remova os containers e volumes
> associados:
>
> ```sh
> docker-compose -f ./mobilidade_rio/docker-compose.yml down -v && docker image prune -f
> ```

### Populando o banco

1. Remova os containers e volumes associados:
```sh
docker-compose -f ./mobilidade_rio/dev_local/docker-compose_local.yml down -v
```

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

O arquivo `settings.json` contém as configurações para popular o banco
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

Para esvaziar as tabelas rode:

```sh
scripts\populate_db\populate_db.py --empty_tables --no_insert
```

Para esvaziar todo o banco de dados, rode:
```sh
scripts/populate_db/populate_db.py --empty_db
```

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



O que NÃO pode alterar ali sem quebrar o Kubernetes:

* Dockerfile
* setup.sh

## Problemas comuns

### Erro ao usar manage.py

Possíveis causas:

**Os arquivos `migrations` foram alterados**

Para resolver rode os comandos de acordo com o estágio em que você está trabalhando (veja [aqui](#estágios-de-desenvolvimento)):

Dev nativo:

* Esvaziar banco de dados

  ```sh
  scripts/populate_db/populate_db.py -p 5432 --empty_db
  ```

* Criar tabelas

  ```sh
  python mobilidade_rio/manage.py migrate
  ```

* Subir dados

  ```sh
  scripts/populate_db/populate_db.py
  ```

Dev local:

* Eliminar arquivos do docker, e esvaziar disco virtual

  ```sh
  docker-compose -f ./mobilidade_rio/dev_local/docker-compose_local.yml down -v
  docker image prune -f
  ```

* Rodar o Docker novamente

  ```sh
  docker-compose -f ./mobilidade_rio/dev_local/docker-compose_local.yml up
  ```

* Subir dados

  ```sh
  python scripts/populate_db/populate_db.py
  ```
> Lembre-se que, para usar o `populate_db`, você deve ter os arquivos `.csv` na pasta `csv_files` (veja [aqui](#como-subir-dados))

> **O que é o disco virtual?**
>
> Disco virtual é o disco que o Docker usa para armazenar os dados do banco de dados. Com o passar do tempo, ele pode ficar cheio, ocupando centenas de GBs.
> 
> Para esvaziá-lo, rode o comando `docker system prune -a -f` (ou `docker system prune -a` para ver o que será apagado).