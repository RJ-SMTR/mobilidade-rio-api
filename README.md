# mobilidade-rio-api

API estática do aplicativo de pontos.mobilidade.rio da Prefeitura.

## Requerimentos

- Docker
- Python >=3.9
- Kubernetes (produção), ver [como configurar local](todo-add-link-library)

## Como rodar a API

### Desenvolvimento

[Adicionar instruções]

### Produção

Para acessar o terminal do `pod` localmente, rode:

```sh
kubectl exec -it -n mobilidade-v2 deploy/mobilidade-api -- /bin/bash
```

#### Atualização de dados

1. Copiar novo fixture para o Kubernetes (veja `<pod-em-prod>` [aqui](todo-add-link-library)):

`kubectl cp <seu>/<caminho>/<local> mobilidade-v2/<pod-em-prod>:/app/fixtures/<seu-fixture>.json`

> Você pode também copiar o fixture do Kubernetes para seu local trocando a
> ordem dos parâmetros.

2. Uma vez no terminal do `pod` em questão, rode:

`python3 manage.py loaddata fixtures/<seu-fixture>.json`