
# mobilidade-rio-api

API estática do aplicativo de [pontos.mobilidade.rio](http://pontos.mobilidade.rio) da Prefeitura da cidade do Rio de Janeiro.

## Requerimentos

Em parêntesis, o [modo de execução](#modo-de-execução) que utiliza o recurso.

* [Docker](https://www.docker.com/) (local, dev)
* [Kubernetes kubectl](https://kubernetes.io/docs/tasks/tools/) (dev, staging, prod)
* [Kubernetes Lens](https://k8slens.dev/) (dev, staging, prod)
* [Postgres](https://www.postgresql.org/) (nativo)
* Python >=3.9

## Desenvolvimento

### Modo de execução

> Você pode executar a aplicação de várias formas, cada uma tem seu objetivo e suas vantagens. A seguir, é descrito o que cada uma faz.

* **Native**
  * _Desenvolvimento Local em servidor nativo_
  * Para desenvolver com rapidez os recursos do servidor, ele é executado localmente na sua máquina, sem utilizar o Docker.
  * Se este não é o seu caso, use o `Local`.
* **Local**
  * _Desenvolvimento Local_
  * Utiliza localmente o Docker.
* **Dev**
  * _Desenvolvimento em servidor Remoto_
  * Desenvolver num servidor remoto, utilizando o orquestrador Kubernetes (K8s) com o Docker.
* **Staging**
  * _Teste em servidor Remoto_
  * Também chamado de `stag`
  * Funciona semelhante ao `dev`, mas com um banco de dados diferente.
* **Prod**
  * _Produção em servidor oficial_
  * Também chamado de `prod`
  * Funciona semelhante ao `dev`, mas tudo é executado em um servidor oficial.

Resumindo o que cada um faz:

| Nome | Descrição | Recursos |
|---|---|---|
| native | Desenv nativo | 🖥️ |
| local | Desenv. local | 🐋 |
| dev | Desenv. Remoto | 🐋☸️ |
| stag | Remoto como staging | 🐋☸️ |
| prod | Remoto como produção | 🐋☸️ |

### Iniciando o ambiente

```bash
conda activate mobilidade_rio_api
pip install -r mobilidade_rio/requirements-dev.txt
```

### Criando a aplicação

Native:
```bash
python mobilidade_rio/manage.py makemigrations
python mobilidade_rio/manage.py migrate
python mobilidade_rio/manage.py runserver 8001
```

Local:
```bash
docker-compose -f "mobilidade_rio/dev_local/docker-compose_local.yml" up --build
```

Dev, Staging, Prod:

> _em construção_

### Acessando a aplicação

URL base para acessar a aplicação:

* Nativo: `localhost:8001`
* Local: `localhost:8010`
* Dev: `https://api.dev.mobilidade.rio`


Endpoints:

* `<URL base>` - API Root com todos os endpoints disponíveis
* `<URL base>/gtfs` - Endpoints para acessar os dados do GTFS
* `<URL base>/predictor` - Endpoints para acessar os dados do predictor


Acessando containers:

> No Docker ou Kubernetes, são criados os containers `django_hd` (API) e `postgres_hd` (banco).

`local` e `dev`:

```bash
docker exec -it django_hd bash
```

Para acessar o banco via linha de comando (ainda está vazio!), basta rodar:

```sh
docker exec -it postgres_hd psql -U postgres
```

> Veja mais sobre os comandos do psql [aqui](https://www.postgresql.org/docs/9.1/app-psql.html).

Para resetar a aplicação do zero, remova os containers e volumes
associados:

```sh
docker-compose -f ./mobilidade_rio/docker-compose.yml down -v && docker image prune -f
```

### Populando o banco

1. Remova os containers e volumes associados:
```sh
docker-compose -f ./mobilidade_rio/dev_local/docker-compose_local.yml down -v
```

2. Salve os arquivos do GTFS na pasta
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

3. Execute o upload dos dados:

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


## Produção

> TODO: Revisar e atualizar comandos

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

> loaddata é um comando do Django que carrega dados de um `fixture` no banco de dados.

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

## Endpoints

Os diagramas dos endpoints (e ) [here](https://miro.com/app/board/o9J_lqIY7Eg=/).
> Os diagramas estão em português.

### Pontos (gtfs)

Todos os endpoints estão no endereço `/gtfs`.

#### stops

Endereço: `/gtfs/stops`

Parâmetros:

* `stop_code` - Filtra por 1 ou mais stop_code
  * Uso: `stop_code=1,2,3`
  * Exemplo real: <http://localhost:8010/gtfs/stops/?stop_code=1K84,1EBQ>

* `stop_name` - Filtra por 1 ou mais stop_name, não diferencia maiúsculas de minúsculas
  * Uso: `stop_name=AB,cd,Ef`
  * Exemplo real: <http://localhost:8010/gtfs/stops/?stop_name=term,AVen>

* `stop_id` - Filtra por 1 ou mais stop_id
  * Uso: `stop_id=1,2,3`
  * Exemplo real: <http://localhost:8010/gtfs/stops/?stop_id=2028O00023C0,5144O00512C9>

#### stop_times

Endereço: `/gtfs/stop_times`

Parâmetros:

* `trip_id` - Filtra por 1 ou mais trip_id
  * Uso: `trip_id=1,2,3`
  * Exemplo real: <http://localhost:8010/gtfs/stop_times/?trip_id=O0041CAA0AIDU01,O0309AAA0AVDU01>

* `stop_id` - Filtra por 1 ou mais stop_id
  * Uso: `stop_id=1,2,3`
  * Funcionamento:
    * Se o stop não possuir filhos (`location_type`=0), retorna apenas ele mesmo.
      * Exemplo real: <http://localhost:8010/gtfs/stop_times/?stop_id=2028O00023C0,5144O00512C9>
    * Se o stop for `parent_station` de alguém (`location_type`=1), retorna apenas seus filhos.
      * Exemplo real: <http://localhost:8010/gtfs/stop_times/?stop_id=4128O00169P0,5144O00487P9>
    * ⚠️ Por enquanto não é possível pesquisar por `stop_id` e seus filhos ao mesmo tempo. O primeiro item deste parâmetro valerá para os demais.

* `stop_id__all` - Filtra por 1 ou mais stop_id, onde as trips combinam com todos os stops passados.
  > **Por exemplo:**  
  > Se stop_id__all = `1`, `2`, `3` retorna as ips > `a`, `b`.  
  > **O resultado será:**
  > | stop_id | trip_id |
  > | --- | :--|
  > |1|a|
  > |1|b|
  > |2|a|
  > |2|b|
  > |3|a|
  > |3|b|
  * Uso: `stop_id__all=1,2,3`
  * Exemplo real: <http://localhost:8010/gtfs/stop_times/?stop_id__all=2028O00023C0,5144O00512C9>

* É possível combinar todos os parâmetros acima.
  * Exemplo: `trip_id=a,b&stop_id=1,2,3&stop_id__all=2,3,4`
  * Exemplo real: <http://localhost:8010/gtfs/stop_times/?trip_id=O0041CAA0AIDU01,O0309AAA0AVDU01&stop_id=2028O00023C0,5144O00512C9>

## Apps

### Utils

Contém funções úteis usadas em outros apps.

**query_utils**

Funções para separar a lógica de queries do código e facilitar a manutenção em queries complexas.

Sempre que possível evite usar queries cruas, use o ORM do Django. Caso contrário, use ou crie uma função em `query_utils`.

`query_utils.ipynb` é um notebook feito para testar as funções de `query_utils`. Testado na [extensão do VSCode](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter).
## Gerenciando o projeto

### Branches do projeto

* **main**
  * _Produção_
  * Branch principal do projeto, onde o código está em produção.

* **staging**
  * _Testar aplicação para produção, mas em servidor de desenvolvimento_
  * Quando o `dev` estiver funcionando corretamente, o código é enviado para o `staging`.

* **dev**
  * _Desenvolvimento_
  * Branch de desenvolvimento, onde o código está em desenvolvimento.

* ⚠️ **dev-local**
  * _Desenvolvimento local_
  * Criado inicialmente para permitir o desenvolvimento local, sem a necessidade de um servidor remoto.
  * Talvez seja deletado, pois já cumpriu seu objetivo.

* **hotfix/`branch`**
  * _Tudo relacionado a correções de bugs naquela branch_
  * Nomes alternativos:
    * hotfix-outro_titulo/`branch`
  * Apenas uma correção de bug por vez.
  * Ao terminar, deve-se fazer um PR para a respectiva branch, então deletar esta aqui.

* **feat/`branch`**
  * _Tudo relacionado a novas funcionalidades naquela branch_
  * Nomes alternativos:
    * feat-outro_titulo/`branch`
  * Apenas uma nova funcionalidade por vez.
  * Ao terminar, deve-se fazer um PR para a respectiva branch, então deletar esta aqui.

### Github Project

_Vulgo Board, Kanban ou Org._

* [Board deste projeto](https://github.com/orgs/prefeitura-rio/projects/18/views/1)

Aqui ficam todos os problemas, correções, melhorias, e afins, que precisam ser feitos.

Cada card representa um futuro PR a ser feito. Cada PR deve seguir o padrão adotado nas [branches do projeto](#branches-do-projeto).

### Criando um PR

Normalmente um PR é criado da seguinte forma:

1. Baseado no Card do Kanban, crie uma branch a partir da branch que você está trabalhando. (e.g. de  `dev` para `fix/bug1`)

2. Subir os commits com as alterações.

3. Criar um PR da branch nova para a original. (e.g. de `fix/bug1` para `dev`)

No PR, preencha os seguintes campos:

**Reviewers**: Nessa etapa verifique quem irá revisar o PR.

**Assignees** serve para marcar quem está trabalhando no PR. (e.g. você mesmo)

**Projects**: Marque o projeto que o PR está relacionado.

Caso você não tenha acesso ao Project com os cards você pode fazer o seguinte:
* Peça para sua equipe te adicionar como [membro da organização](https://github.com/orgs/RJ-SMTR/people), que é diferente de [membro do projeto](https://github.com/RJ-SMTR/mobilidade-rio-api/graphs/contributors).
* Caso não seja possível, insira o link do card no PR e o link do PR no card:

  PR:
  ```md
  Kanban aberto em: https://github.com/orgs/prefeitura-rio/projects/18/views/1
  Nome: **[BE] Remover rotas noturnas em routes**
  ---
  ### Objetivo
  * Tirar tudo que tiver `SN` em `route_short_name`

  ### O que foi alterado?

  * Uma configuração para filtrar rotas noturnas em settings.json
  * Código para filtrar rotas noturnas na função `validate_col_values()`

  ### Como usar
  ...
  ```

  Card (Kanban):
  ```md
  PR aberto em: https://github.com/RJ-SMTR/mobilidade-rio-api/pull/105
  ---
  ### Objetivo
  * Tirar tudo que tiver `SN` em `route_short_name`

  ### O que foi feito
  - [x] Criar branch para hotfix de `populate_db`
  - [x] Dar commit em `dev-local`
  - [ ] Enviar PR
  ```

4. Aguarde a revisão do PR.
5. Mova o card do Kanban para a coluna `✅ Feito`.

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


### PG Admin: Erro ao conectar ao banco de dados


### PG Admin: must be owner of database

**Causa:**

O seu usuário atual (e.g. `postgres`) não é dono do banco de dados.

**Solução:**

1. Se necessário, peça ajuda ao responsável pelo banco de dados.

2. Entre no banco de dados `postgres`:

Exemplo:
```sh
psql -h localhost -p 5433 -U postgres -W postgres
``` 

3. Altere o dono do banco de dados (ex: `mobilidade_rio`) para o usuário em questão (ex: `meu_usuario`):
```sql
ALTER DATABASE mobilidade_rio OWNER TO meu_usuario;
```