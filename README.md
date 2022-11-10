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

### Populando o banco

Para popular o banco use o script `scripts/populate_db/populate_db.py`.

> Só funciona com o postgres.

Dependências:

```sh
pip install -r scripts/populate_db/requirements.txt
```

**Configurando o script**

O script possui argumentos, para ver a lista de argumentos veja os script ou use:

```
python3 scripts/populate_db/populate_db.py --help
```

As configurações padrão estão no próprio script.

Para editar as configurações use o arquivo `settings.jsonc`, na mesma pasta do script.  
Veja o arquivo `settings.example.jsonc` para ver como configurar.

**Arquivos CSV**

Os arquivos CSV devem estar na pasta `scripts/populate_db/csv_files`.

O script irá popular tabelas Django, que ficam dentro de apps, por exemplo: `my_app.table_1`.

Seguindo este padrão, os arquivos CSV devem estar dentro de pastas com o nome do app, por exemplo:
  
  ```
  csv_files
  ├── my_app
  │   ├── table_1.csv
  │   └── table_2.csv
  └── other_app
      └── table_1.csv
  ```

**Sintaxe dos arquivos CSV**

* O nome das colunas do CSV devem ser iguais aos da tabela.
 
* A ordem dos arquivos e pastas é importante, pois há dependências entre as tabelas. (configurável em `settings.jsonc`)

**Ordem das tabelas e dependências**

> A ordem das tabelas é configurável em `settings.jsonc`.

Se não for configurado, a ordem padrão é a ordem alfabética, padrão do Python.

Com a configuração, é possível evitar erros de dependência:

```jsonc
"table_order": {
    "pontos": ["ponto", "placa"],
    "linhas": ["linha"],
}
```

Resultado:
```
1. pontos_ponto
2. pontos_placa
3. linhas_linha
```

É possível preencher os dados de uma pasta, pular para outra e voltar para a primeira. Isto resolve as dependências entre tabelas, mesmo que não estejam na mesma pasta:

```python
table_order = {
    "pontos": ["ponto", "placa"],
    "linhas": ["linha"],
    "pontos": ["parada"],
}
```

Resultado:
```
1. pontos_ponto
2. pontos_placa
3. linhas_linha
4. pontos_parada
```


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