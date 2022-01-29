# mobilidade-rio-api

API estática do aplicativo de
[pontos.mobilidade.rio](http://pontos.mobilidade.rio) da Prefeitura da
cidade do Rio de Janeiro.

## Requerimentos

- Docker
- Python >=3.9
- Kubernetes (produção), ver [como configurar local](todo-add-link-library)

## Desenvolvimento

[Adicionar instruções]

## Produção
### Acessando o ambiente

Para acessar o ambiente de produção localmente, rode:

```sh
kubectl exec -it -n mobilidade-v2 deploy/mobilidade-api -- /bin/bash
```

### Como subir dados

No seu local, copie o novo `fixture` para o Kubernetes (veja
   `<pod-em-prod>` [aqui](todo-add-link-library)) rodando:

```sh
$ kubectl cp <seu>/<caminho>/<local> mobilidade-v2/<pod-em-prod>:/app/fixtures/<seu-fixture>.json
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