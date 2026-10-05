# Ambiente local de desenvolvimento

Procedimento executável para sair de uma máquina limpa e chegar a: aplicação rodando
localmente, banco configurado, migrations aplicadas e testes passando.

Este documento foi escrito para ser seguido **literalmente**, inclusive por um agente de
IA.

> **Agentes de IA:** cada chamada de ferramenta costuma abrir um shell novo, e variáveis
> carregadas antes se perdem. A partir do passo 2.7, **prefixe todo comando `manage.py`
> com `source .env &&`**, por exemplo
> `source .env && uv run python manage.py preparar_demonstracao`. Servidores devem rodar em
> segundo plano (passo 2.10). Os comandos rodam na raiz do repositório, salvo indicação contrária. Se algo falhar,
siga o [protocolo de diagnóstico](#se-o-ambiente-não-subir) **antes** de alterar qualquer
código.

- **Referência principal:** Ubuntu 24.04 LTS (Linux).
- **Também validado:** macOS (Apple Silicon, Homebrew). As diferenças estão marcadas com
  **macOS:**.
- **Última validação prática:** 2026-10-05, em macOS arm64, com uv 0.11.21,
  Python 3.13.14, Django 5.2.17 e PostgreSQL 16.14. O caminho Ubuntu segue os mesmos
  comandos do CI (`.github/workflows/ci.yml`, `ubuntu-latest`), mas não foi executado numa
  máquina Ubuntu limpa nesta revisão.

---

## 1. O que você precisa saber antes de começar

Fatos do projeto, confirmados no código. Não presuma nada além disto.

| Item | Valor real | Onde está |
|---|---|---|
| Python | `>=3.13,<3.14` | `pyproject.toml` (`requires-python`) |
| Django | `>=5.2,<5.3` (5.2 LTS) | `pyproject.toml` |
| Banco | PostgreSQL 16+ (CI usa `postgres:16`) | `config/settings.py`, ADR 0001, CI |
| Driver | `psycopg[binary]` 3.x (traz a libpq embutida) | `pyproject.toml` |
| Gerenciador | `uv` com `uv.lock` versionado | `uv.lock` |
| Dependências de desenvolvimento | extra opcional `dev` (**não** é `dependency-groups`) | `pyproject.toml` |
| Settings | um único módulo: `config.settings` | `manage.py`, `config/wsgi.py` |
| WSGI | `config.wsgi:application` | `config/wsgi.py` |
| Testes | `pytest` + `pytest-django`, pasta `tests/` | `[tool.pytest.ini_options]` |
| Lint | `ruff check` (regras E, F, I, B, UP; linha 100) | `[tool.ruff]` |
| `.env` | **não é lido automaticamente**; `.env.example` é só referência | `config/settings.py`, `.env.example` |
| `DEBUG` | **sempre `False`**, fixo no código; não há variável para ligá-lo | `config/settings.py` |
| Static / media | **não existem**: CSS, SVG e fontes são embutidos pelos templates; não há upload | `config/settings.py` (sem `staticfiles`) |
| Docker | **não existe** no projeto | — |
| Makefile / scripts | **não existem**; só `manage.py` | — |
| Redis, Celery, filas | **não existem**; cache é `LocMemCache` por processo | `config/settings.py` |
| Processo auxiliar | `manage.py processar_videos` (opcional, Feature 022) | `trajetoria/video/` |
| Dados de desenvolvimento | `manage.py preparar_demonstracao` (dados fictícios) | `trajetoria/demonstracao/` |

### O ponto mais importante: o modo de demonstração

O sistema **só responde páginas** quando a variável `TRAJETORIA_DEMONSTRACAO` vale
exatamente `1`. Sem ela, **toda requisição devolve 404**, de propósito
(`trajetoria/demonstracao/middleware.py`). Isso não é defeito. Se o servidor sobe e tudo
dá 404, a primeira coisa a verificar é essa variável.

O modo de demonstração existe só para dados **fictícios**. Nunca aponte o ambiente local
para um banco com dados reais.

### Duas formas de usar o ambiente local

| Objetivo | Precisa de |
|---|---|
| Rodar testes e lint | Python/uv, PostgreSQL e um usuário PostgreSQL que possa **criar bancos** |
| Navegar na aplicação | Tudo acima, mais o banco local migrado, as 4 chaves exportadas e `preparar_demonstracao` |
| Ver o vídeo da Minha trajetória (opcional) | Tudo acima, mais Node ≥ 22 e o projeto `video/` instalado |

---

## 2. Bootstrap passo a passo

### 2.1 Pacotes do sistema operacional

```bash
sudo apt-get update
```

```bash
sudo apt-get install -y git curl ca-certificates postgresql postgresql-client
```

No Ubuntu 24.04, o pacote `postgresql` é a versão 16. Em versões anteriores do Ubuntu, o
repositório padrão traz uma versão mais antiga; nesse caso, use o repositório oficial do
PostgreSQL (PGDG) e instale `postgresql-16`.

**macOS:**

```bash
brew install git postgresql@16
```

```bash
brew link --force postgresql@16
```

O `postgresql@16` é *keg-only*: sem o `link`, `psql`, `createdb` e `pg_isready` não ficam
no `PATH`. (Alternativa: `export PATH="$(brew --prefix postgresql@16)/bin:$PATH"`.)

```bash
brew services start postgresql@16
```

Não há bibliotecas nativas extras para o Python: `psycopg[binary]`, `cryptography` e
`resvg-py` são distribuídos como *wheels* com binários embutidos.

### 2.2 Clonar o repositório

```bash
git clone <REPOSITORY_URL> trajetoria-ifes
```

```bash
cd trajetoria-ifes
```

`<REPOSITORY_URL>` é a URL do repositório Git que você recebeu. A branch de
desenvolvimento integrada é `main`.

### 2.3 Instalar o uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Abra um novo terminal (ou rode `source $HOME/.local/bin/env`) e confirme:

```bash
uv --version
```

Validado com uv 0.11.21. O CI usa a versão mais recente do `astral-sh/setup-uv@v6`.

**macOS:** o mesmo comando funciona; `brew install uv` também serve.

### 2.4 Instalar o Python 3.13

O uv provisiona o Python. Não use o Python do sistema.

```bash
uv python install 3.13
```

### 2.5 Sincronizar as dependências

```bash
uv sync --extra dev --locked
```

- `--extra dev` instala pytest, pytest-django, ruff, openpyxl, numpy e Pillow.
- `--locked` falha se `uv.lock` estiver desatualizado em relação ao `pyproject.toml`
  (é o que o CI usa). Não rode `uv lock` nem `uv add` para "consertar" uma falha aqui sem
  entender a causa.
- O ambiente fica em `.venv/` (ignorado pelo Git). Sempre execute via `uv run`.

Confirme:

```bash
uv run python --version
```

Esperado: `Python 3.13.x`.

### 2.6 Configurar o PostgreSQL local

As settings usam as variáveis padrão da libpq (`PGHOST`, `PGPORT`, `PGUSER`,
`PGPASSWORD`, `PGDATABASE`). **Sem nenhuma variável**, a aplicação conecta ao banco
`trajetoria`, pelo socket local, com o usuário do sistema operacional. O caminho mais
simples é criar um papel PostgreSQL com o mesmo nome do seu usuário de sistema.

**Ubuntu** — criar o papel com permissão para criar bancos (o pytest cria o banco de
teste `test_<nome>` a cada execução):

```bash
sudo -u postgres createuser --createdb "$USER"
```

**macOS (Homebrew):** o papel com o seu nome de usuário já existe e é superusuário; pule
este passo.

Crie o banco de desenvolvimento:

```bash
createdb trajetoria
```

Confirme a conexão:

```bash
psql -d trajetoria -c "select version();"
```

Esperado: `PostgreSQL 16.x` ou superior.

> **Alternativa: PostgreSQL em outro host ou com senha.** Exporte as variáveis antes de
> qualquer comando `manage.py` ou `pytest`, por exemplo:
> `export PGHOST=localhost PGPORT=5432 PGUSER=trajetoria PGPASSWORD=<DB_PASSWORD> PGDATABASE=trajetoria`.
> O papel continua precisando de `CREATEDB` para os testes.

### 2.7 Variáveis de ambiente

**Nada lê `.env` automaticamente.** `.env.example` só documenta as variáveis. Para
desenvolvimento, crie um arquivo local **fora do controle de versão** e carregue-o com
`source` em cada terminal.

O arquivo `.env` já está no `.gitignore`. Crie-o com chaves novas (os valores são gerados
na hora e nunca devem ser versionados). O `[ -e .env ] ||` impede que uma segunda execução
troque as chaves de um banco já preparado:

```bash
[ -e .env ] || cat > .env <<EOF
export PGDATABASE=trajetoria
export TRAJETORIA_DEMONSTRACAO=1
export TRAJETORIA_CHAVE_ACESSO_LOCALIZACAO=$(uv run python -c 'import secrets; print(secrets.token_hex(32))')
export TRAJETORIA_CHAVE_ACESSO_VERIFICACAO=$(uv run python -c 'import secrets; print(secrets.token_hex(32))')
export TRAJETORIA_CHAVE_SELO_DECLARACAO=$(uv run python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')
export TRAJETORIA_CHAVE_CONSULTA_ACERVO=$(uv run python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')
EOF
```

```bash
source .env
```

Confira que as quatro chaves foram geradas (não deve imprimir nada):

```bash
source .env && for v in TRAJETORIA_CHAVE_ACESSO_LOCALIZACAO TRAJETORIA_CHAVE_ACESSO_VERIFICACAO TRAJETORIA_CHAVE_SELO_DECLARACAO TRAJETORIA_CHAVE_CONSULTA_ACERVO; do eval "test \${#$v} -ge 32" || echo "$v inválida"; done
```

Regras que o código impõe (e que explicam erros comuns):

- As duas chaves de acesso precisam ter **≥ 32 caracteres**, ser **diferentes entre si**
  e diferentes de `DJANGO_SECRET_KEY` e de `TRAJETORIA_CHAVE_PSEUDONIMIZACAO`.
- As duas chaves Fernet precisam ser chaves Fernet válidas, diferentes entre si e das
  demais.
- **As chaves do `preparar_demonstracao` e as do servidor precisam ser as mesmas.** O
  preparo deriva o material de verificação com as chaves vigentes. Trocou as chaves?
  Recrie o banco (passo 2.8) ou todo acesso dará "Não foi possível confirmar".
- Sem as chaves de acesso, o `preparar_demonstracao` recusa e o **envio** do formulário de
  `/acesso/` (POST) responde 503 ("Não foi possível verificar agora"). O GET da página
  continua 200: só o login de teste (passo 2.11) detecta chave ausente.

O inventário completo das variáveis está na
[seção 10 do guia de implantação](../implantacao/datacenter-ubuntu.md#10-variáveis-de-ambiente-e-segredos).
Para desenvolvimento, as variáveis acima bastam; todas as outras têm padrão local.

### 2.8 Aplicar as migrations

```bash
uv run python manage.py migrate
```

Confirme que não há migration pendente nem modelo sem migration:

```bash
uv run python manage.py migrate --check
```

```bash
uv run python manage.py makemigrations --check --dry-run
```

Esperado: o primeiro termina sem saída e com código 0; o segundo imprime
`No changes detected`.

### 2.9 Carregar os dados de desenvolvimento

Não há fixtures, seeds SQL nem usuários de demonstração com senha. O único carregador é o
comando de preparo do cenário fictício:

```bash
uv run python manage.py preparar_demonstracao
```

Ele exige `TRAJETORIA_DEMONSTRACAO=1` e as chaves de acesso (passo 2.7). É idempotente:
rodar de novo não duplica nada. Saída esperada (trecho):

```text
Cenário de demonstração pronto. Pessoas fictícias:
  Ana Exemplo — 1 formação com pesquisa pendente
  Bruno Exemplo — escolha entre formações com pesquisa pendente
  ...
```

Linhas `Material COLISAO em simulada:SIM-P-00xx (campos: —)` também aparecem no stderr
(uma ou mais, inclusive ao reexecutar): são cenários fictícios propositais de colisão de
CPF, não erros nem quebra de idempotência.

O que o preparo cria, só com dados fictícios: Pessoas e Conclusões Acadêmicas da fonte
simulada; a baseline do Formulário Egresso Ifes 2024 em rascunho e uma cópia publicada
localmente; três Campanhas de demonstração; vínculos de governança dos operadores
fictícios A (CPAEG), B (CSAEG Vitória) e C (sem vínculo); o contexto simulado da Minha
trajetória; os contatos de e-mail fictícios (`@example.invalid`) da Feature 020.

**Recomeçar do zero** é recriar o banco (não existe operação para apagar Participações).
Pare o `runserver` antes (ele mantém uma conexão aberta):

```bash
source .env && dropdb --force trajetoria && createdb trajetoria && uv run python manage.py migrate && uv run python manage.py preparar_demonstracao
```

### 2.10 Executar o servidor

Interativo (num terminal próprio):

```bash
source .env && uv run python manage.py runserver 127.0.0.1:8000
```

Em segundo plano (agentes): o `PYTHONUNBUFFERED=1` faz o log aparecer na hora; o `until`
espera o servidor ficar pronto.

```bash
source .env && PYTHONUNBUFFERED=1 nohup uv run python manage.py runserver 127.0.0.1:8000 > /tmp/trajetoria-runserver.log 2>&1 &
```

```bash
until curl -sf -o /dev/null http://127.0.0.1:8000/acesso/; do sleep 0.5; done; echo pronto
```

Para parar: `pkill -f "runserver 127.0.0.1:8000"`.

Use exatamente `127.0.0.1:8000`: o envio por Lote em modo demonstração (Feature 020, que
substituiu a comunicação simulada da 016) só aceita a URL de entrada
`http://127.0.0.1:8000/acesso/`.

### 2.11 Abrir a aplicação

| URL | O que é |
|---|---|
| `http://127.0.0.1:8000/` | Redireciona para `/acesso/` |
| `http://127.0.0.1:8000/acesso/` | Entrada do egresso: CPF e data de nascimento **fictícios**. A própria página mostra o painel "Dados fictícios para demonstração" |
| `http://127.0.0.1:8000/formacoes/` | Formações da Pessoa confirmada (exige acesso) |
| `http://127.0.0.1:8000/minha-trajetoria/` | Devolutiva após a pesquisa concluída (Feature 021) |
| `http://127.0.0.1:8000/demonstracao/operador/` | Escolha do operador fictício A, B ou C |
| `http://127.0.0.1:8000/acompanhamento/` | Acompanhamento da coleta e gestão de Campanha (exige operador) |
| `http://127.0.0.1:8000/editor/` | Editor do instrumento (exige operador) |
| `http://127.0.0.1:8000/validacoes-formacao/` | Fila de validação da formação declarada (exige operador) |

Dados fictícios de entrada (definidos na fonte simulada; ver
[quickstart da 018](../../specs/018-identificacao-acesso-egresso/quickstart.md)):

| Pessoa | CPF | Nascimento | Caso |
|---|---|---|---|
| Ana Exemplo | `000.000.001-91` | `12/04/1998` | Uma formação |
| Diego Exemplo | `000.000.003-53` | `08/02/1994` | Três formações |

Verificação rápida por linha de comando (com o servidor rodando em outro terminal):

```bash
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8000/acesso/
```

Esperado: `200`. Se vier `404`, o servidor foi iniciado sem `TRAJETORIA_DEMONSTRACAO=1`.

Login de teste por linha de comando (prova CSRF, sessão e chaves). A página tem vários
formulários, cada um com seu token; use só o primeiro:

```bash
curl -s -c /tmp/trajetoria-cookies -o /tmp/trajetoria-acesso.html http://127.0.0.1:8000/acesso/ && T=$(grep -o 'name="csrfmiddlewaretoken" value="[^"]*"' /tmp/trajetoria-acesso.html | head -1 | sed 's/.*value="//;s/"//') && curl -s -b /tmp/trajetoria-cookies -o /dev/null -w '%{http_code} %{redirect_url}\n' --data-urlencode "csrfmiddlewaretoken=$T" --data-urlencode cpf=000.000.001-91 --data-urlencode data_nascimento=12/04/1998 http://127.0.0.1:8000/acesso/
```

Esperado: `303 http://127.0.0.1:8000/formacoes/`. Com `503`, as chaves estão ausentes ou
inválidas; com "Não foi possível confirmar" (200), as chaves diferem das do preparo.

Não existe Django Admin nem login de operador com senha: o operador é escolhido entre
fictícios em `/demonstracao/operador/`.

### 2.12 Rodar os testes

Os testes **não** dependem de `.env`, do modo de demonstração nem das chaves: cada teste
configura o que precisa. Eles precisam apenas de PostgreSQL acessível e de permissão para
criar o banco `test_<PGDATABASE>`.

```bash
uv run pytest
```

Duração de referência: ~5 a 6 min em macOS arm64; ~20 min no CI quando os testes de vídeo
rodam com o renderizador.

Recortes úteis:

| Objetivo | Comando |
|---|---|
| Suíte completa (padrão do CI) | `uv run pytest` |
| Um módulo (pasta) | `uv run pytest tests/acesso` |
| Um arquivo | `uv run pytest tests/acesso/test_verificacao.py` |
| Um teste | `uv run pytest tests/test_modelo.py::<nome_do_teste>` |
| Por palavra-chave | `uv run pytest -k vazamento` |
| Parar na primeira falha | `uv run pytest -x` |
| Testes de volume (fora da suíte padrão) | `uv run pytest -m volume` |

Para descobrir o nome exato de um teste:

```bash
uv run pytest --collect-only -q tests/test_modelo.py
```

Não há separação formal entre "unitários" e "integração": todos ficam em `tests/`,
organizados por feature/app, e a maioria usa o banco.

**Marcadores** (declarados no `pyproject.toml`, com `--strict-markers`):

- `volume`: medição de volume, **excluída** por padrão (`-m 'not volume'` em `addopts`).
- `precisa_renderizador`: testes de mídia do vídeo. **Sem** o projeto `video/`
  instalado, são pulados (*skipped*) com o motivo. Com `CI=true`, a ausência do
  renderizador vira falha. Não exporte `CI=true` localmente sem instalar o renderizador.

### 2.13 Qualidade de código

Ferramentas realmente configuradas: só **ruff (lint)** e **pytest**.

```bash
uv run ruff check .
```

Verificações que o CI também roda:

```bash
uv run python manage.py check
```

```bash
uv run python manage.py makemigrations --check --dry-run
```

Não estão configurados no projeto: `ruff format` como verificação obrigatória, mypy,
coverage/pytest-cov, pre-commit, djlint. Não os trate como obrigatórios. `ruff format`
pode ser usado localmente, mas o CI não o verifica.

### 2.14 (Opcional) Vídeo da Minha trajetória — Feature 022

Sem isto, tudo funciona; a página `/minha-trajetoria/` só não mostra o bloco de vídeo.

Requer Node ≥ 22 (o CI usa 22).

**Ubuntu** — o `nodejs` do repositório do Ubuntu 24.04 é antigo demais. Use o binário
oficial ou um gerenciador de versões (nvm, fnm). Confirme:

```bash
node --version
```

**macOS:**

```bash
brew install node
```

Instale o projeto e provisione o navegador (uma vez; ~420 MB medidos em
`video/node_modules`, o `video/README.md` estima ~600 MB):

```bash
npm ci --prefix video
```

```bash
npm --prefix video run garantir-navegador
```

No Linux, o Chrome Headless Shell precisa das bibliotecas de sistema listadas na
[seção 13.3 do guia de implantação](../implantacao/datacenter-ubuntu.md#133-opcional-processador-de-vídeos).

Em outro terminal (com `source .env`), rode o processador junto do servidor:

```bash
uv run python manage.py processar_videos
```

Testes de vídeo com o renderizador real:

```bash
uv run pytest tests/video tests/narrativa
```

---

## 3. Arquivos e diretórios que o ambiente local cria

| Caminho | Criado por | Versionado? |
|---|---|---|
| `.venv/` | `uv sync` | Não |
| `.env` | você (passo 2.7) | Não (`.gitignore`) |
| `video/node_modules/` | `npm ci` | Não |
| `video/.bundle/` | primeiro render de vídeo | Não |
| Bancos `trajetoria` e `test_trajetoria` | `createdb` / pytest | — |

---

## Checklist determinístico para um agente

Pré-requisito: seção 2 executada até o passo 2.9 (inclusive `createdb`, `.env` e
`migrate`). Execute em ordem; cada item tem um comando e um resultado esperado objetivo.
Itens com `manage.py` pressupõem `source .env &&` antes do comando.

```text
[ ] uv instalado ............ uv --version                              → "uv 0.x.y"
[ ] Python 3.13 ............. uv run python --version                   → "Python 3.13.x"
[ ] Dependências ............ uv sync --extra dev --locked              → código 0
[ ] PostgreSQL ativo ........ pg_isready                                → "accepting connections"/"aceitando conexões"
[ ] Banco local existe ...... psql -d trajetoria -c 'select 1'          → 1 linha
[ ] Papel cria bancos ....... psql -d trajetoria -Atc "select rolcreatedb or rolsuper from pg_roles where rolname = current_user" → "t"
[ ] .env criado e carregado . source .env && echo $TRAJETORIA_DEMONSTRACAO → "1"
[ ] Django sem erros ........ uv run python manage.py check             → "System check identified no issues"
[ ] Migrations aplicadas .... uv run python manage.py migrate --check; echo $? → só "0" (1 = pendências)
[ ] Modelos sem migration ... uv run python manage.py makemigrations --check --dry-run → "No changes detected"
[ ] Lint .................... uv run ruff check .                       → "All checks passed!"
[ ] Dados fictícios ......... uv run python manage.py preparar_demonstracao → "Cenário de demonstração pronto."
[ ] Suíte mínima ............ uv run pytest tests/test_modelo.py tests/acesso → "passed", 0 failed
[ ] Suíte completa .......... uv run pytest                             → 0 failed (skips de vídeo são aceitáveis sem Node)
[ ] Aplicação inicia ........ runserver em segundo plano (passo 2.10)   → "pronto" do laço until
[ ] URL local responde ...... curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8000/acesso/ → "200"
[ ] Acesso fictício ......... receita de login do passo 2.11              → "303 http://127.0.0.1:8000/formacoes/"
```

---

## Se o ambiente não subir

**Não altere código da aplicação para fazer o ambiente subir.** Quase todo problema de
ambiente aqui é configuração. Execute nesta ordem e pare no primeiro item que falhar.

1. **Python.** `uv run python --version` deve dar 3.13.x. Se não: `uv python install 3.13`
   e `uv sync --extra dev --locked`.
2. **uv.** `uv --version`. Se o comando não existe, reabra o terminal ou rode
   `source $HOME/.local/bin/env`.
3. **Lockfile.** `uv sync --extra dev --locked`. Se falhar com "lockfile needs to be
   updated", você está numa revisão inconsistente do repositório: confira
   `git status` e `git log -1`; não rode `uv lock` sem decidir isso conscientemente.
4. **Variáveis.** Num terminal novo, você rodou `source .env`? Confira:
   `env | grep -E '^(PG|TRAJETORIA_|DJANGO_)' | sed 's/=.*/=<definida>/'`
   (não imprima os valores das chaves).
5. **PostgreSQL ativo.** `pg_isready`. Ubuntu: `sudo systemctl status postgresql`.
   macOS: `brew services list | grep postgresql`.
6. **Conexão com o banco.** `psql -d "${PGDATABASE:-trajetoria}" -c 'select 1'`.
   - `role "<usuário>" does not exist` → passo 2.6 (`createuser`).
   - `database "trajetoria" does not exist` → `createdb trajetoria`.
   - `permission denied to create database` (no pytest) → o papel precisa de `CREATEDB`:
     `sudo -u postgres psql -c "alter role \"$USER\" createdb"`.
7. **Migrations.** `uv run python manage.py migrate --check`. Se houver pendências:
   `uv run python manage.py migrate`. Se `makemigrations --check` acusar mudanças numa
   revisão limpa de `main`, isso é defeito do repositório: registre e não gere migration
   por conta própria.
8. **Django.** `uv run python manage.py check`.
9. **Traceback.** Leia a última exceção no terminal do `runserver`. Com `DEBUG=False`
   fixo, as páginas nunca mostram traceback; ele só aparece no console (logger
   `django.request`).
10. **Sintomas conhecidos** — consulte a tabela abaixo e, para o servidor, o
    [troubleshooting de implantação](../implantacao/datacenter-ubuntu.md#21-troubleshooting).

| Sintoma | Causa provável | Correção |
|---|---|---|
| Toda página dá 404 | `TRAJETORIA_DEMONSTRACAO` diferente de `1` no processo do servidor | `source .env` e reinicie o `runserver` |
| Envio do `/acesso/` (POST) responde 503 "Não foi possível verificar agora" | Chaves de acesso ausentes ou inválidas | Passo 2.7 |
| Todo acesso dá "Não foi possível confirmar os dados" | Chaves do servidor diferentes das usadas no `preparar_demonstracao`, ou preparo não executado | Recrie o banco e rode o preparo com as mesmas chaves |
| `preparar_demonstracao` recusa a base | Banco com dados de outra origem | Use um banco novo |
| `Bad Request (400)` | Host fora de `DJANGO_ALLOWED_HOSTS` (padrão: `localhost,127.0.0.1,[::1]`) | Acesse por `127.0.0.1` ou ajuste a variável |
| "Aguarde alguns instantes…" (429) | Limitação de tentativas (contadores em memória do processo) | Espere a janela ou reinicie o `runserver` |
| Testes de vídeo *skipped* | Projeto `video/` não instalado | Esperado; ver 2.14 se quiser rodá-los |
| Testes de vídeo falham com "renderizador indisponível" | `CI=true` exportado sem renderizador | `unset CI` ou instale o renderizador |
| `ValueError: TRAJETORIA_VIDEO_RETENCAO_MINUTOS…` ao iniciar | Variável fora de 1–1440 | Corrija ou remova a variável |
