# Recommendation API

Este serviço é uma API desenvolvida com FastAPI para disponibilizar recomendações de produtos personalizadas para clientes em canais digitais. Navegue rapidamente pelos tópicos:


- [Arquitetura](#arquitetura)
- [Como rodar o projeto](#como-rodar-o-projeto)
- [Observabilidade](#observabilidade)
- [Melhorias para o futuro](#melhorias-para-o-futuro)

## Arquitetura
Alguns requisitos do projeto estão definidos no arquivo README.md, eles guiaram todo o desenvolvimento do serviço. 
Com o objetivo principal definido (uma API de baixa latência para retornar recomendações), todo o processo que envolve tratamento de dados e geração de features foi estruturado para ser executado durante o startup. Além da construção das features derivadas, o serviço realiza as inferências para todos os usuários conhecidos e mantém em memória a relação usuário → produtos recomendados. Dessa forma, as requisições de runtime tornam-se operações de consulta de baixa latência.



## Rotas
#### Health
```http
GET /health  
```
Temos uma rota básica de health para consulta de status da API.
output:
```json
{
  "status": "OK",
  "version": "1.0.0"
}
```

#### Recommendations
```http
GET /recommendations/{user_id}
```
Endpoint principal responsável por retornar os produtos mais recomendados para um determinado user_id (str).
output:
```json
{
  "user_id": "u_0000",
  "cold_start": false,
  "products": [
    {
      "product_id": "p_056",
      "score": 0.13037174583570496
    },
    {
      "product_id": "p_046",
      "score": 0.12796467191705582
    }
  ]
}
```

Para usuários "desconhecidos", ou seja, usuários que não temos registro de interações na base de dados, a requisição continuará sendo atendida normalmente, porém a recomendação será padronizada com a listagem dos produtos mais populares da base, e também uma flag de "cold_start"
output:
```json
{
  "user_id": "u_teste",
  "cold_start": true,
  "products": [
    {
      "product_id": "p_030",
      "score": 0
    },
    {
      "product_id": "p_000",
      "score": 0
    }
  ]
}
```

### Decisões de projeto
Algumas decisões do case ficam abertas para definição pelo desenvolvedor. Abaixo temos suas justificativas.

#### user_affinity_match
Para a definição do user_affinity_match, foi utilizada a regra padrão de atribuir ao usuário a categoria com o maior número de interações (somatório de todos os tipos). Como critério de desempate foi definido o maior número de interações pelos tipos de eventos com a seguinte prioridade: purchase > add_to_cart > click > view. Se após essa ordem ainda existir empate nas categorias o desempate será ordem alfabética das categorias.

#### Cold Start - Usuários fora da base
Para requisições relacionadas a "usuários" que não constam na relação de eventos/interações, foi definido o retorno com os produtos mais populares da base.

#### Análise de logs, métricas e traces
A opção de instrumentação foi aplicar automaticamente o opentelemetry como produtor de telemetria e utilizar a imagem otel-lgtm como backend de observabilidade.

#### Quantidade de produtos retornada
A quantidade de produtos está parametrizada através da variavel de ambiente "RECOMMENDATION_TOP_K"

#### Teste de integração 
O teste de integração está identificado (marker "integration") e, por padrão, não é executado ao rodar apenas "pytest". Para execução dele utilize:
uv run pytest -m integration

executar todos os testes: 
```bash 
uv run pytest -m ""
```  
com analise de cobertura: 
```bash
uv run pytest -m "" --cov=src
```

## Como rodar o projeto

Foram escolhidas como ferramentas de apoio para gestão de ambiente python e dependências o conjunto PYENV e UV.

A API foi construída a partir da versão 3.12 do Python, você pode administrar diversas versões de Python através do [pyenv](https://github.com/pyenv/pyenv)!

### Guia rápido pyenv
#### Instalação:
```bash
curl -fsSL https://pyenv.run | bash
```

Siga as orientações de configuração do PATH

#### Instalar nova versão do python
```bash 
pyenv install --list | grep "3.12"  #  Para listar as versões disponíveis
```

```bash
pyenv install 3.12.13  #  Instalar versão 3.12.13
```


Com a versão de python ajustada (o arquivo ".python-version" faz essa garantia) você pode instalar todas as dependências através do [uv](https://github.com/astral-sh/uv?tab=readme-ov-file)

### Guia rápido uv
#### Instalação:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
ou
```bash
pip install uv | pipx install uv
```

#### Resolver dependências do projeto
```bash
uv sync --frozen --all-extras
```

### Configurações da API
#### .env file
Crie na raiz um arquivo ".env" e copie o conteúdo de ".env.example". Nela podemos configurar variáveis de ambiente e mudar o comportamento da aplicação.
```bash
[ -f .env ] || cp .env.example .env
```

#### entrypoint.sh
Para facilitar o start do serviço temos o arquivo "entrypoint.sh" que aplica a condição de instrumentar ou não o serviço. Certifique de permitir a execução do arquivo:
```bash
chmod +x entrypoint.sh
```

### Startup da API
#### Startup local (sem Docker e Instrumentação)
Ative o ambiente python:
```bash
source .venv/bin/activate
```

dica: confira o .env para que ele esteja de acordo com seu objetivo

Execute o entrypoint.sh:
```bash
./entrypoint.sh
```
>[Atenção: ]
>A API possui um processamento de dados durante o startup, nos testes locais o tempo médio de start foi próximo de 30s. Você pode acompanhar pelos logs.

A API estará disponível no localhost na porta definida no .env.


### Startup local with Docker (sem instrumentação)
Como temos um "compose.yaml" no projeto, podemos apenas executar o up para que a imagem docker seja buildada. Repare que temos outro serviço no compose além da API, veremos na próxima seção mais detalhes sobre.

Para o start execute:
```bash
docker compose up --build
```

Após o build o container iniciará a aplicação e ficará disponível no localhost porta 8080.

### Startup local with Docker + Otel
Para atender o requisito de métricas e traces foi adicionado uma instrumentação automatica ao serviço, configurada para ser opcional de acordo com o ambiente de execução. No compose.yaml temos o serviço "otel" que utiliza a imagem "otel-lgtm" que disponibiliza de forma fácil e integrada as ferramentas Prometheus, Loki, Grafana, Mimi, coletor OpenTelemetry e Tempo.

Execute(lembre-se de configurar corretamente as envs relacionadas ao OTEL):
```bash
docker compose --profile otel up --build
```

Após o build/pull o container iniciará a API e ficará disponível no localhost porta 8080. Também podemos acessar as outras ferramentas:
- Grafana: localhost:3000

Atenção: Use o acesso admin/admin caso solicitado.
 

## Observabilidade
Foi realizada configuração de log estruturado de forma básica, contemplando todo o processo de inicialização, desde o processamento dos dados, até as inferências e construções das informações de consulta, além de realizar a instrumentação automática do serviço para coleta de métricas.

Essa instrumentação foi uma descoberta durante o desenvolvimento! e oferece muitas possibilidades de monitoramento e até debugging do serviço, com mais tempo seria possível construir as queries e templates para criar dashboards aproveitando todas as features que os aplicativos da imagem otel-lgtm oferece.

Com a separação de responsabilidades também poderíamos aplicar monitoramento dedicado para os processos de tratamento de dados, uso e performance do modelo, construção das features e também controles de uso de recursos computacionais.

## Melhorias para o futuro
Algumas features e evolução podem ser destacadas para a evolução do serviço.

### Separação de responsabilidades
Esse talvez seja o ponto mais necessário em um ambiente produtivo. O processamento de dados e geração de features foge do escopo principal da API, com a estruturação de um workflow de tratamentos de dados, feature store, registro de inferências em lote, a API poderia ser apenas consultiva a esses dados, desacoplando essa camada do seu escopo.

### Async
Certamente esse serviço se enquadra em uma estrutura assíncrona, onde diversas requisições devem chegar ao mesmo tempo e melhor utilização dos recursos computacionais aumenta a capacidade de processamento simultâneo.

### Teste de carga
Importante para monitorar a performance da API e identificar degradação antes mesmo de disponibilizar em ambiente produtivo.

### Filtro de compra
Uma feature relacionada a regra de negócio, poderia ser aplicado um filtro no output para os produtos que já foram comprados pelo cliente e que não sejam produtos de recompra recorrente deixem de ser recomendados, melhorando a oferta, experiência do usuário e margens.

### Inferência em lote
Apesar de ter sido implementado o método predict_scores() para inferência em lote, hoje o serviço está utilizando o predict simples. 