
# mobilidade-rio-api

![github action status](https://github.com/RJ-SMTR/mobilidade-rio-api/actions/workflows/cd_stag.yml/badge.svg)

API estática do aplicativo [mobilidade.rio](http://mobilidade.rio) da Prefeitura do Rio de Janeiro.

## Documentação

Acesse a [wiki](https://github.com/RJ-SMTR/mobilidade-rio-api/wiki) para saber maiores detalhes do projeto, como:

- Endpoints
- Problemas comuns
- Links úteis
- Arquitetura
- Desenvolvimento local
- Exemplos e tutoriais

## Requisitos

- Python >= 3.9
- Docker
- Powershell - para usar o utilitário `project`

## Modo de execução

Para definir se o projeto deve rodar como native, dev, staging, prod é preciso configurar um .env, e se achar necessário alterar o settings do Django basta criar um arquivo customizado como no exemplo abaixo:

```bash
mobilidade-rio-api/
📂 mobilidade_rio/
  📂 local_dev/
    ⚙️ api-native.env
  📂 settings/
    ...
    📂 local_dev/
      🐍 native.py
      🐍 docker.py
```

## Desenvolvimento local

### Configuração inicial

1. Criar ambiente virtual Python

    Anaconda:

    ```bash
    conda create -n mobilidade_rio_api python=3.9
    conda activate mobilidade_rio_api
    pip install -r mobilidade_rio/requirements.txt  -r requirements-dev.txt
    ```

    Venv Linux e macOS:

    ```bash
    python -m venv venv
    . venv/scripts/activate
    pip install -r mobilidade_rio/requirements.txt  -r dev/requirements-dev.txt
    ```

2. Criar arquivos de desenvolvimento local:

    Bash ou powershell:

    ```bash
    cp dev/mobilidade_rio/local_dev_example mobilidade_rio/local_dev -r
    cp dev/mobilidade_rio/settings/local_dev_example mobilidade_rio/settings/local_dev -r
    ```

Resultado:

```bash
mobilidade-rio-api/
...
📂 mobilidade_rio/  # "src/"
  ...
  📂 local_dev/
    🐋 Dockerfile
    🐋 docker-compose.yml
    ⚙️ api-native.env
    ⚙️ api.env
      ...
  📂 mobilidade_rio/  # app principal
    📂 settings/
      ...
      📂 local_dev/
        🐍 native.py
```

### Executar no Docker

```bash
docker-compose -f "mobilidade_rio/local_dev/docker-compose.yml" up --build
```

### Executar localmente

1. Iniciar o ambiente virtual (recomendado, toda vez que abrir um terminal)

    ```bash
    conda activate mobilidade_rio_api
    ```

2. Carregando o .env na sessão atual do terminal

    Bash

    ```bash
    source mobilidade_rio/local_dev/api-native.env
    ```

    Powershell

    ```powershell
    project env api-native
    ```

      Para mais informações rode `project help`

3. Iniciar servidor:

    Bash

    ```bash
    python mobilidade_rio/manage.py migrate
    python mobilidade_rio/manage.py runserver 8001
    ```

    Powershell

    ```powershell
    project runserver native
    ```

### Ambientes dev, stag e prod

- O deploy e execução das branches de dev, staging e produção são feitos automaticamente via [Github Actions](https://github.com/features/actions).
- Essas branches usam a configuração Django de acordo com seu nome. Exemplo: a branch `dev` usa a configuração dev.

### Acessando a aplicação

URL base para acessar a aplicação:

- native: `localhost:8001` (sugerido)
- docker: `localhost:8010` (sugerido)
- dev: `https://api.dev.mobilidade.rio`
- stag: `https://api.staging.mobilidade.rio`
- prod: `https://api.mobilidade.rio`

### Acessando o banco de dados

Recomenda-se o [pgAdmin](https://www.pgadmin.org/) para gerenciar o banco de dados.

### Populando o banco de dados

1. Carregue os dados no servidor (pgAdmin web)

    - Vá no menu Tools > Storage Manager
    - Crie e entre na pasta chamada `backup` ou similar
    - Na janela do Storage Manager clique no botão `...` > `Upload`
    - Selecione todos os arquivos desejados

    > ⚠️ Não selecione uma pasta inteira, pode causar falha no upload

2. Esvazie todas as tabelas:

    - Em seu database > schema > public, abra o Query Tool.
    - Esvazie as tabelas rodando esta query:

    ```sql
    -- Truncate tables
    TRUNCATE
    pontos_agency,
    pontos_calendar,
    pontos_calendardates,
    pontos_frequencies,
    pontos_routes,
    pontos_shapes,
    pontos_stops,
    pontos_stoptimes,
    pontos_trips
    RESTART IDENTITY CASCADE
    ```

3. Carregue os dados para as tabelas

    - Selecionar tabela por tabela
    - Clicar no menu `Tools` > `Import/Export data`
    - Configurar o Filename e o formato
    - Dentro da janela de Import/Export, selecione o menu Columns e confira se a ordem das colunas é exatamente a mesma
    - Clique em OK

4. Confira se os dados subiram

    Execute esta query para verificar:

    ```sql
    -- Count tables
    SELECT 'pontos_agency' AS table_name, COUNT(*) AS row_count FROM pontos_agency UNION ALL
    SELECT 'pontos_calendar' AS table_name, COUNT(*) AS row_count FROM pontos_calendar UNION ALL
    SELECT 'pontos_calendardates' AS table_name, COUNT(*) AS row_count FROM pontos_calendardates UNION ALL
    SELECT 'pontos_frequencies' AS table_name, COUNT(*) AS row_count FROM pontos_frequencies UNION ALL
    SELECT 'pontos_routes' AS table_name, COUNT(*) AS row_count FROM pontos_routes UNION ALL
    SELECT 'pontos_shapes' AS table_name, COUNT(*) AS row_count FROM pontos_shapes UNION ALL
    SELECT 'pontos_stops' AS table_name, COUNT(*) AS row_count FROM pontos_stops UNION ALL
    SELECT 'pontos_stoptimes' AS table_name, COUNT(*) AS row_count FROM pontos_stoptimes UNION ALL
    SELECT 'pontos_trips' AS table_name, COUNT(*) AS row_count FROM pontos_trips;
    ```
