# mobilidade-rio-api

API estática do aplicativo de
[pontos.mobilidade.rio](http://pontos.mobilidade.rio) da Prefeitura da
cidade do Rio de Janeiro.

## Requerimentos

* Windows, Linux ou macOS
* Docker >= 20.10.20
  * https://www.docker.com/

Para desenvolvimento:
* Python >=3.9

Para produção:
* Linux
* Kubernetes
  > instruções a adicionar

## Desenvolvimento

Certifique-se de estar na pasta `mobilidade_rio` para executar os comandos.

Rodando o projeto pela primeira vez  
ou caso altere o `models.py`:

```sh
docker exec -it django_hd bash
python manage.py makemigrations
python manage.py migrate
```

Para rodar projeto localmente

```sh
docker compose up --build -d
```


### Banco de dados

Sempre que fizer alterações no `models.py` é necessário dar:

```
docker exec -it django_hd bash
python manage.py makemigrations
python manage.py migrate
```

> É necessário rodar desta forma pois há perguntas de segurança que não são respondidas automaticamente.

### Populando banco

Para popular o banco use o script `/scripts/populate_db.py`.

O servidor postgres está configurado na porta `5433`, então você deve executar o script com os seguintes parâmetros:

```
python3 scripts/populate_db.py --port 5433 --user postgres
```

As configurações padrão e demais opções podem ser vistas no próprio script ou executando:

```
python3 scripts/populate_db.py --help
```

* O nome das colunas do CSV devem ser iguais aos da tabela.
  * É possível adicionar um prefixo, porém 
* A ordem dos arquivos (que pode ser definida também no script) é importante, pois há dependências entre as tabelas.

TODO:
* Tentar corrigir colunas csv automaticamente
  > O algoritmo nem sempre consegue achar a coluna certa, mas para erros simples como `nome` e `nome_`, por exemplo, é possível corrigir automaticamente.
  
* Ler subpastas e usar como prefixo (módulos django) de cada tabela
  > Ex.: `./scripts/csv_files/pontos/agency.csv` -> `pontos_agency.csv`

## Produção

### Acessar o ambiente

Para acessar o ambiente de Staging localmente, rode:

```sh
kubectl exec -it -n mobilidade-v2-staging deploy/smtr-stag-mobilidade-api -- /bin/bash
```

### Como subir dados

No seu local, copie o novo `fixture` para o Kubernetes (veja
   `<pod-em-prod>` [aqui](todo-add-link-library)) rodando:

```sh
$ kubectl cp mobilidade_rio/fixtures/<seu-fixture>.json mobilidade-v2/<pod-em-prod>:/app/fixtures/<seu-fixture>.json
```

> Você pode também copiar um `fixture` do Kubernetes para seu local trocando a
> ordem dos parâmetros.

Agora seu `fixture` está armazenado em produção! Para subir os dados
no banco, acesse o ambiente de produção e rode:

```sh
$ python manage.py loaddata fixtures/<seu-fixture>.json
```

### Como deletar dados

Acesse o ambiente de produção e rode:

```sh
$ python3 manage.py shell
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