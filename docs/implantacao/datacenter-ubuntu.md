# Implantação em VM Ubuntu no datacenter institucional

Guia para um administrador de infraestrutura que recebeu **uma VM Ubuntu recém-instalada,
acesso SSH e um nome DNS** chegar a uma instância funcional do Trajetória Ifes.

- **Escopo:** uma única VM com Nginx, Gunicorn, a aplicação Django e o PostgreSQL. Sem
  contêineres, sem orquestração, sem serviços de nuvem.
- **Operação do dia a dia:** [operacao-producao.md](operacao-producao.md).
- **Ambiente de desenvolvimento:** [../desenvolvimento/ambiente-local.md](../desenvolvimento/ambiente-local.md).
- **Revisão:** 2026-10-05, sobre `main` em `04efabd` (inclui a Feature 022).

Convenções deste documento:

- **Estado atual do projeto** descreve o que existe no repositório.
- **Recomendação** descreve uma escolha deste guia, ainda não decidida nem implementada no
  projeto.
- `<ASSIM>` é um valor que depende do seu ambiente: `<DOMAIN>`, `<REPOSITORY_URL>`,
  `<TAG_DE_RELEASE>`, `<DB_PASSWORD>`, `<DB_HOST>`, `<REDE_INSTITUCIONAL_CIDR>`,
  `<REDE_ADMIN_CIDR>`.
- Comandos com `sudo` rodam como um administrador da VM.

---

## 0. Leia antes: o que esta instalação entrega hoje

> **Estado atual do projeto.** O Trajetória Ifes **ainda não tem modo produtivo**. Todas as
> telas existem só no **modo de demonstração**, com dados fictícios. Isso é uma decisão
> registrada nas specs, não um defeito de configuração.

A variável `TRAJETORIA_DEMONSTRACAO` define o comportamento inteiro da aplicação
(`trajetoria/demonstracao/middleware.py`):

| Modo | Valor | Comportamento | Uso possível nesta VM |
|---|---|---|---|
| **Fechado** (padrão) | vazio ou diferente de `1` | **Toda requisição devolve 404**, antes de qualquer view | Infraestrutura pronta e validada, aguardando o modo produtivo. Seguro com qualquer exposição de rede |
| **Demonstração** | `1` | Jornada do egresso, editor, acompanhamento, Minha trajetória — **só com dados fictícios**, operadores fictícios e sem autenticação de operador | Homologação ou demonstração institucional **com acesso restrito à rede interna** e **banco exclusivamente fictício** |

Consequências diretas:

1. **Não implante esta versão para egressos reais nem carregue dados reais.** Não existe
   fonte acadêmica real (só a simulada), não existe identificação produtiva de operadores
   (DP-1001), a comunicação real por e-mail não existe (só Mailpit local) e o próprio
   código avisa que o modo de demonstração não deve rodar "em ambiente acessível a
   egressos nem sobre banco com dados reais" (`.env.example`).
2. As specs descrevem a demonstração como **local**. Hospedá-la numa VM do datacenter,
   mesmo restrita à rede interna, é uma escolha que precisa ser **decidida pela
   coordenação do projeto** antes de ser feita (ver [seção 22](#22-lacunas-e-decisões-pendentes)).
3. Este guia monta a infraestrutura de forma que **a mudança de modo seja só uma
   variável**. Quando o modo produtivo existir, a mesma VM, os mesmos serviços e o mesmo
   runbook continuam válidos; o que mudará será o conjunto de variáveis e de verificações.

Escolha o modo antes de começar. Os passos são os mesmos; as diferenças estão marcadas
com **[modo fechado]** e **[modo demonstração]**.

---

## 1. Pré-requisitos

### 1.1 Sistema operacional

- **Ubuntu Server 24.04 LTS** (x86_64). É a versão em que o pacote `postgresql` já é o 16
  (o projeto exige PostgreSQL 16+) e em que o `nginx` suporta `proxy_cookie_flags`.
- Instalação mínima, com SSH, NTP e acesso de saída HTTPS durante a implantação.

### 1.2 Capacidade (sizing)

> **Sizing deverá ser definido a partir da carga esperada.** Não há medição de carga do
> sistema; o único dado de capacidade do repositório é o consumo do render de vídeo
> (~0,9 GB por processo Node, ADR 0007).

**Baseline operacional inicial** (a ser monitorada e revista):

| Recurso | Sem vídeo | Com o processador de vídeo (opcional) |
|---|---|---|
| vCPU | 2 | 4 |
| RAM | 4 GB | 8 GB |
| Disco total | 40 GB | 40 GB |
| Banco de dados | < 1 GB no cenário fictício (dump atual: ~120 KB) | idem; os MP4 ficam no banco por até `TRAJETORIA_VIDEO_RETENCAO_MINUTOS` (~1 MB cada) |
| Logs | journald limitado a 1 GB (seção 18) + Nginx com rotação de 14 dias | idem |
| Backups locais | 14 dias de dumps diários | idem |
| Uploads/media | **0** — o sistema não recebe arquivos | 0 |
| Software | Python gerenciado + `.venv`: ~250 MB | + Node (~200 MB) + `video/node_modules` com navegador (~420 MB) |

### 1.3 Rede

| Direção | Porta | Origem/destino | Finalidade |
|---|---|---|---|
| Entrada | 22/tcp | Rede de administração | SSH |
| Entrada | 80/tcp | Usuários (ou o proxy institucional) | Redirecionamento para HTTPS |
| Entrada | 443/tcp | Usuários (ou o proxy institucional) | Aplicação |
| Local | 8000/tcp | `127.0.0.1` apenas | Gunicorn (nunca exposto) |
| Local | 5432/tcp | `localhost`/socket apenas | PostgreSQL (nunca exposto) |
| Saída | 443/tcp | `github.com` (ou o Git institucional), `astral.sh`, `pypi.org`, `files.pythonhosted.org`, `objects.githubusercontent.com` e `release-assets.githubusercontent.com` (Python gerenciado pelo uv) | Implantação e atualização |
| Saída (só com vídeo) | 443/tcp | `nodejs.org`, `registry.npmjs.org`, `remotion.media` e/ou `storage.googleapis.com` | Node, pacotes npm e Chrome Headless Shell |
| Saída | 53, 123 | DNS e NTP institucionais | Resolução de nomes e relógio |

**SMTP: não é necessário.** No estado atual não há envio real de e-mail. A comunicação da
Feature 016 só aceita Mailpit em `127.0.0.1:1025` e destinatários `@example.invalid`
(`trajetoria/comunicacao/seguranca.py`).

### 1.4 DNS e TLS

- Um nome DNS, aqui `<DOMAIN>`, apontando para a VM (ou para o proxy institucional).
- Um certificado TLS para `<DOMAIN>`, fornecido pela infraestrutura do datacenter, pelo
  proxy institucional ou emitido para a VM. Este guia **não** presume Let's Encrypt.

### 1.5 Dependências externas da aplicação em execução

**Nenhuma**, além do PostgreSQL. A aplicação não chama APIs externas, não usa Redis, filas,
Celery, armazenamento de objetos, analytics nem CDN. Fontes, CSS e imagens são embutidos.

---

## 2. Topologia

```text
Usuário (rede institucional)
        │  HTTPS 443
        ▼
[ Proxy institucional ]  ← opcional; se existir, pode terminar o TLS (variante B, seção 14)
        │
        ▼
┌──────────────────────── VM Ubuntu 24.04 ────────────────────────┐
│ Nginx (:80 → 301, :443 TLS)                                     │
│   │ proxy_pass http://127.0.0.1:8000, X-Forwarded-Proto        │
│   ▼                                                             │
│ Gunicorn (systemd: trajetoria.service, usuário trajetoria)      │
│   1 processo × 4 threads — config.wsgi:application              │
│   │ socket Unix local, autenticação peer                        │
│   ▼                                                             │
│ PostgreSQL 16 (somente local)  ◄── processar_videos (opcional,  │
│                                    trajetoria-videos.service)   │
│ journald ← logs da aplicação | /var/log/nginx ← acesso HTTP     │
└─────────────────────────────────────────────────────────────────┘
```

**Fluxo de uma requisição.** O Nginx recebe HTTPS, termina o TLS e repassa para o Gunicorn
em `127.0.0.1:8000`, com `Host` original e `X-Forwarded-Proto: https`. O Gunicorn confia
nesse cabeçalho porque ele vem de `127.0.0.1` (padrão `forwarded_allow_ips`) e marca a
requisição como HTTPS. O Django valida `Host` contra `DJANGO_ALLOWED_HOSTS`, aplica o
middleware do modo (404 em modo fechado) e responde. Páginas, CSS, SVG e o PNG do card são
gerados pela aplicação; **não há arquivos estáticos para o Nginx servir**.

| Pergunta | Resposta |
|---|---|
| Onde a aplicação executa | Gunicorn, como `trajetoria`, código em `/opt/trajetoria/app` |
| Onde ficam os dados persistentes | Só no PostgreSQL local (`/var/lib/postgresql/16/main`) |
| Onde ficam arquivos enviados | Não existem uploads. Os MP4 do vídeo ficam **no banco**, temporariamente |
| Onde ficam os logs | journald (aplicação, Gunicorn, processador) e `/var/log/nginx`, `/var/log/postgresql` |
| Quem termina o TLS | O Nginx da VM (variante A) ou o proxy institucional (variante B) |
| Como o Django é executado | Gunicorn (WSGI) gerenciado pelo systemd |
| O que acontece após reboot | `postgresql`, `nginx` e `trajetoria` estão habilitados no systemd e sobem sozinhos |

**Por que Gunicorn, 1 processo e várias threads.** O projeto expõe só WSGI
(`config/wsgi.py`; não há ASGI nem código assíncrono). O cache é `LocMemCache`, **por
processo**, e guarda os contadores da limitação de tentativas de acesso; o próprio código
diz que "em produção, o cache precisa ser compartilhado entre processos" (DP-1803). Com um
único processo, os limites continuam coerentes; as threads dão concorrência.

**Por que PostgreSQL na mesma VM.** É o arranjo mais simples para o volume atual e evita
senha (autenticação `peer` pelo socket local). Um PostgreSQL institucional separado também
funciona (seção 8.4).

---

## 3. Usuário de serviço

> **Recomendação.** O projeto não define usuário de sistema. Este guia usa `trajetoria`.

| Item | Valor |
|---|---|
| Usuário | `trajetoria` (de sistema, sem senha, sem shell de login) |
| Grupo | `trajetoria` |
| Home | `/var/lib/trajetoria` (o render de vídeo precisa de `HOME` gravável) |
| Pode ler | código, `.venv`, Python gerenciado, `/etc/trajetoria/trajetoria.env` |
| Pode escrever | apenas `/var/lib/trajetoria` e, com vídeo, `/opt/trajetoria/app/video/.bundle` |
| Não pode | alterar o código, o ambiente Python, as configurações nem os backups |

```bash
sudo adduser --system --group --home /var/lib/trajetoria --shell /usr/sbin/nologin trajetoria
```

O código pertence a `root`. Assim, uma falha na aplicação não consegue reescrever o
próprio código nem seu ambiente.

---

## 4. Estrutura de diretórios

> **Recomendação.** O projeto não tem convenção de diretórios de servidor.

| Caminho | Dono:grupo | Modo | Finalidade |
|---|---|---|---|
| `/opt/trajetoria/` | `root:root` | 0755 | Raiz da instalação |
| `/opt/trajetoria/app/` | `root:root` | 0755 | Checkout Git de uma tag de release |
| `/opt/trajetoria/app/.venv/` | `root:root` | 0755 | Ambiente Python criado pelo `uv sync` |
| `/opt/trajetoria/python/` | `root:root` | 0755 | Python 3.13 gerenciado pelo uv |
| `/opt/trajetoria/node/` | `root:root` | 0755 | Node 22 (só com vídeo) |
| `/opt/trajetoria/app/video/.bundle/` | `trajetoria:trajetoria` | 0750 | Bundle do Remotion, gravado no primeiro render (só com vídeo) |
| `/etc/trajetoria/` | `root:trajetoria` | 0750 | Configuração |
| `/etc/trajetoria/trajetoria.env` | `root:trajetoria` | 0640 | Variáveis e **segredos** |
| `/var/lib/trajetoria/` | `trajetoria:trajetoria` | 0750 | `HOME` do serviço; nenhum dado de negócio |
| `/var/cache/trajetoria-uv/` | `root:root` | 0700 | Cache do uv usado na implantação |
| `/var/backups/trajetoria/` | `postgres:postgres` | 0700 | Dumps do banco |
| `/etc/ssl/trajetoria/` | `root:root` | 0750 | Certificado e chave TLS |

Não há `media/` nem `static/` (seção 12). Não há `/var/log/trajetoria/`: a aplicação só
escreve no console, capturado pelo journald (seção 18).

```bash
sudo install -d -o root -g root -m 0755 /opt/trajetoria
```

```bash
sudo install -d -o root -g trajetoria -m 0750 /etc/trajetoria
```

```bash
sudo install -d -o trajetoria -g trajetoria -m 0750 /var/lib/trajetoria
```

```bash
sudo install -d -o root -g root -m 0700 /var/cache/trajetoria-uv
```

```bash
sudo install -d -o root -g root -m 0750 /etc/ssl/trajetoria
```

O diretório de backups é criado na seção 8, depois da instalação do PostgreSQL.

---

## 5. Preparação do sistema operacional

```bash
sudo apt-get update && sudo apt-get -y upgrade
```

```bash
sudo apt-get install -y git curl ca-certificates nginx postgresql postgresql-client ufw unattended-upgrades
```

```bash
sudo timedatectl set-timezone America/Sao_Paulo
```

A aplicação já usa `TIME_ZONE = "America/Sao_Paulo"` com `USE_TZ = True`; o fuso do sistema
afeta só os horários dos logs e dos timers.

Atualizações de segurança automáticas:

```bash
sudo dpkg-reconfigure -plow unattended-upgrades
```

Firewall (SSH só a partir da rede de administração):

```bash
sudo ufw allow from <REDE_ADMIN_CIDR> to any app OpenSSH
```

```bash
sudo ufw allow 'Nginx Full'
```

```bash
sudo ufw enable
```

**[modo demonstração]** restrinja HTTP/HTTPS à rede institucional em vez de liberar para
qualquer origem:

```bash
sudo ufw delete allow 'Nginx Full' && sudo ufw allow from <REDE_INSTITUCIONAL_CIDR> to any app 'Nginx Full'
```

Bibliotecas nativas para Python: **nenhuma**. `psycopg[binary]`, `cryptography` e
`resvg-py` (rasterização do card em PNG) vêm como *wheels* com binários embutidos para
Linux x86_64.

---

## 6. Obtenção do código

> **Estado atual do projeto.** Não existem tags nem processo de release. `main` é protegida
> por CI obrigatório (job `testes`).
>
> **Recomendação.** Implantar sempre por **tag anotada criada sobre um commit de `main`
> com CI verde**, por exemplo `v2026.10.05` ou `v0.1.0`. Nunca implantar uma branch em
> movimento nem rodar `git pull` no servidor.

Criar a tag (na máquina do mantenedor, não no servidor):

```bash
git tag -a <TAG_DE_RELEASE> -m "Release <TAG_DE_RELEASE>" <COMMIT_DE_MAIN_COM_CI_VERDE> && git push origin <TAG_DE_RELEASE>
```

**O que o administrador recebe do mantenedor do projeto** (não é decidido na VM):

- `<REPOSITORY_URL>`: hoje `https://github.com/saymoncastro/ifes-trajetoria-egressos.git`.
  Se o repositório for privado, cadastre na VM uma **deploy key somente leitura** para
  `root` e use a URL SSH correspondente.
- `<TAG_DE_RELEASE>`: o nome da tag a implantar. **Enquanto não houver tags**, o
  mantenedor informa o **SHA completo de um commit de `main` com CI verde**, e esse SHA é
  usado no lugar da tag em todos os comandos deste guia.

Clonar e fixar a release:

```bash
sudo git clone <REPOSITORY_URL> /opt/trajetoria/app
```

```bash
sudo git -C /opt/trajetoria/app checkout --detach <TAG_DE_RELEASE>
```

```bash
sudo git -C /opt/trajetoria/app describe --tags --always
```

A atualização (seção 19) é sempre `git fetch --tags` seguido de `checkout --detach` de
uma tag nova, depois de backup e revisão das migrations.

---

## 7. Python 3.13 e uv

> **Estado atual do projeto.** `requires-python = ">=3.13,<3.14"`; dependências travadas
> em `uv.lock`; o CI usa `uv sync --extra dev --locked`. O Python 3.13 é provisionado pelo
> próprio uv (o Ubuntu 24.04 traz o 3.12, que não serve).

### 7.1 Instalar o uv (versão fixada)

Validado com uv 0.11.21:

```bash
curl -LsSf https://astral.sh/uv/0.11.21/install.sh | sudo env UV_INSTALL_DIR=/usr/local/bin UV_NO_MODIFY_PATH=1 sh
```

```bash
uv --version
```

### 7.2 Dois utilitários de administração

> **Recomendação.** Dois scripts curtos evitam erros de digitação: um roda o uv com o
> Python gerenciado num diretório legível pelo serviço; o outro roda `manage.py` **como
> `trajetoria`** e com o ambiente de produção carregado.

```bash
sudo tee /usr/local/sbin/trajetoria-uv > /dev/null <<'EOF'
#!/bin/sh
# uv da implantação: Python gerenciado em /opt/trajetoria/python, legível pelo serviço.
export UV_PYTHON_INSTALL_DIR=/opt/trajetoria/python
export UV_PYTHON_PREFERENCE=only-managed
export UV_CACHE_DIR=/var/cache/trajetoria-uv
cd /opt/trajetoria/app || exit 1
exec /usr/local/bin/uv "$@"
EOF
```

```bash
sudo tee /usr/local/sbin/trajetoria-manage > /dev/null <<'EOF'
#!/bin/sh
# manage.py como o usuário de serviço, com as variáveis de /etc/trajetoria/trajetoria.env.
set -a
. /etc/trajetoria/trajetoria.env
set +a
cd /opt/trajetoria/app || exit 1
exec runuser -u trajetoria -- /opt/trajetoria/app/.venv/bin/python manage.py "$@"
EOF
```

```bash
sudo chmod 0750 /usr/local/sbin/trajetoria-uv /usr/local/sbin/trajetoria-manage
```

Os dois só funcionam com `sudo` (o segundo lê os segredos e troca de usuário).

### 7.3 Instalar o Python e as dependências

```bash
sudo trajetoria-uv python install 3.13
```

```bash
sudo trajetoria-uv sync --locked
```

- `--locked` falha se o `uv.lock` não corresponder ao `pyproject.toml`: a implantação
  nunca resolve versões novas por conta própria.
- **Sem** `--extra dev`: pytest, ruff etc. não vão para o servidor.
- Use `--locked`, não `pip install -r requirements.txt` (o projeto não tem
  `requirements.txt`).

### 7.4 Servidor de aplicação (Gunicorn)

> **Estado atual do projeto.** Nenhum servidor de produção está declarado; o `runserver`
> é só para desenvolvimento e **nunca** deve ser usado aqui.
>
> **Recomendação.** Gunicorn 23 (WSGI). Enquanto ele não estiver no `pyproject.toml`/
> `uv.lock` (lacuna da seção 22), instale-o com versão exata, **logo depois de cada**
> `uv sync` (o `sync` remove pacotes que não estão no lock):

```bash
sudo trajetoria-uv pip install --python /opt/trajetoria/app/.venv/bin/python "gunicorn==23.0.0"
```

```bash
/opt/trajetoria/app/.venv/bin/gunicorn --version
```

Esperado: `gunicorn (version 23.0.0)`.

---

## 8. PostgreSQL

> **Estado atual do projeto.** PostgreSQL 16+ (ADR 0001; CI com `postgres:16`). A conexão
> vem das variáveis padrão da libpq: `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`,
> `PGDATABASE` (`config/settings.py`). Valores vazios deixam a libpq usar seus padrões
> (socket local e usuário do sistema).

### 8.1 Verificar a instalação

```bash
sudo -u postgres psql -Atc "select version();"
```

Esperado: `PostgreSQL 16.x`. O pacote do Ubuntu 24.04 já escuta só em `localhost` e
autentica conexões locais por `peer`:

```bash
sudo -u postgres psql -Atc "show listen_addresses;"
```

Esperado: `localhost`.

### 8.2 Criar papel e banco

O papel tem o mesmo nome do usuário de sistema. Com `peer`, a aplicação entra pelo socket
**sem senha**: há um segredo a menos para guardar.

```bash
sudo -u postgres createuser --no-superuser --no-createdb --no-createrole trajetoria
```

```bash
sudo -u postgres createdb --owner=trajetoria --encoding=UTF8 --template=template0 --locale=C.UTF-8 --locale-provider=icu --icu-locale=pt-BR trajetoria
```

- **Encoding:** UTF8 (obrigatório: nomes e respostas em português).
- **Ordenação:** não determinada no estado atual do projeto. **Recomendação:** ICU `pt-BR`,
  que ordena nomes acentuados como o leitor espera e não depende dos *locales* instalados
  no sistema operacional.
- **Permissões:** o papel `trajetoria` é dono do banco e, portanto, pode criar as tabelas
  no esquema `public` (necessário para as migrations). Não é superusuário e não cria bancos.

Conferir a conexão como o usuário de serviço:

```bash
sudo -u trajetoria psql -d trajetoria -Atc "select current_user, current_database();"
```

Esperado: `trajetoria|trajetoria`.

### 8.3 Diretório de backups

```bash
sudo install -d -o postgres -g postgres -m 0700 /var/backups/trajetoria
```

### 8.4 Alternativa: PostgreSQL em outro servidor

Se a instituição oferecer um PostgreSQL 16+ gerenciado:

- crie o papel com senha forte (`<DB_PASSWORD>`) e um banco dono desse papel, em UTF8;
- no servidor de banco, libere no `pg_hba.conf` só o IP desta VM, com `scram-sha-256`;
- use TLS na conexão. A libpq lê `PGSSLMODE` e `PGSSLROOTCERT` diretamente do ambiente;
- no arquivo de ambiente (seção 10), defina:

```text
PGHOST=<DB_HOST>
PGPORT=5432
PGUSER=<DB_USER>
PGPASSWORD=<DB_PASSWORD>
PGDATABASE=<DB_NAME>
PGSSLMODE=verify-full
PGSSLROOTCERT=/etc/trajetoria/ca-banco.pem
```

Nesse caso, ignore a seção 8.2 e adapte os comandos de backup (`pg_dump -h <DB_HOST> -U
<DB_USER>`). Nunca exponha a porta 5432 desta VM.

---

## 9. Estrutura da aplicação relevante para a implantação

Fatos confirmados no código, que justificam as escolhas seguintes:

| Item | Valor |
|---|---|
| Módulo de settings | `config.settings` (único; sem `settings/` por ambiente) |
| Entrada WSGI | `config.wsgi:application` |
| ASGI | Não existe |
| Apps Django instaladas | Só `django.contrib.sessions` + apps de domínio. **Sem** admin, auth, contenttypes, messages, staticfiles |
| Sessões | No banco (`django_session`), cookie `trajetoria_sessao_egresso` |
| Cache | `LocMemCache` por processo (`default` e `acesso`) |
| `DEBUG` | **`False` fixo no código**; não há variável para ligá-lo |
| Páginas de erro | `404.html`, `500.html`, `403_csrf.html` próprias, sem traceback |
| Comandos de gestão próprios | `preparar_demonstracao`, `processar_videos` |
| Tarefas periódicas | Nenhuma no projeto; este guia agenda `clearsessions` e o backup (seções 13 e 17) |
| Exportações e dataset analítico (012, 013) | Operações de domínio sem tela nem comando; só via `manage.py shell` |

---

## 10. Variáveis de ambiente e segredos

> **Estado atual do projeto.** Tudo vem do ambiente (`config/settings.py`). **Nada lê
> `.env` automaticamente.** Em produção, o systemd carrega `/etc/trajetoria/trajetoria.env`
> (`EnvironmentFile=`) e o `trajetoria-manage` carrega o mesmo arquivo.

### 10.1 Inventário completo

Lido em `config/settings.py` e no código. "Obrigatória" refere-se a esta VM.

| Variável | Obrigatória | Exemplo seguro | Finalidade | Sensível |
|---|---|---|---|---|
| `DJANGO_SECRET_KEY` | **Sim** | `<gerar: seção 10.2>` | Assinaturas do Django (CSRF, sessão). **Sem ela, o código usa um valor inseguro de desenvolvimento, sem avisar** | **Sim** |
| `DJANGO_ALLOWED_HOSTS` | **Sim** | `<DOMAIN>,127.0.0.1,[::1]` | Hosts aceitos; o resto recebe 400 (no modo fechado, 404 vem antes) | Não |
| `PGDATABASE` | **Sim** | `trajetoria` | Nome do banco | Não |
| `PGHOST` | Não (vazio = socket local) | `<DB_HOST>` | Servidor do banco | Não |
| `PGPORT` | Não | `5432` | Porta | Não |
| `PGUSER` | Não (vazio = usuário do sistema) | `trajetoria` | Papel do banco | Não |
| `PGPASSWORD` | Só com banco remoto | `<DB_PASSWORD>` | Senha | **Sim** |
| `PGSSLMODE`, `PGSSLROOTCERT` | Só com banco remoto | `verify-full` | TLS da conexão; lidas pela libpq, não pelas settings | Não |
| `TRAJETORIA_DEMONSTRACAO` | Define o modo | vazio (fechado) ou `1` | Modo de demonstração. Só `1` ativa | Não |
| `TRAJETORIA_COOKIE_SEGURO` | **Sim** (`1`) | `1` | `SESSION_COOKIE_SECURE` | Não |
| `TRAJETORIA_CHAVE_ACESSO_LOCALIZACAO` | **Sim** [modo demonstração] | `<64 hex>` | HMAC que localiza o CPF sem guardá-lo (018). ≥ 32 caracteres, distinta das demais | **Sim** |
| `TRAJETORIA_CHAVE_ACESSO_VERIFICACAO` | **Sim** [modo demonstração] | `<64 hex>` | HMAC de CPF + nascimento (018). ≥ 32 caracteres, distinta das demais | **Sim** |
| `TRAJETORIA_CHAVE_SELO_DECLARACAO` | **Sim** [modo demonstração] | `<chave Fernet>` | Selos transitórios da declaração de formação (019) | **Sim** |
| `TRAJETORIA_CHAVE_CONSULTA_ACERVO` | **Sim** [modo demonstração] | `<chave Fernet>` | Cifra os dados de consulta ao acervo **persistidos no banco** (019) | **Sim — perda = dados ilegíveis** |
| `TRAJETORIA_CHAVE_PSEUDONIMIZACAO` | Só para exportar | `<64 hex>` | Pseudônimos das exportações (013). Vazia: exportação recusada | **Sim** |
| `TRAJETORIA_SESSAO_INATIVIDADE` | Não | `30` | Minutos de inatividade da sessão do egresso | Não |
| `TRAJETORIA_SESSAO_DURACAO_MAXIMA` | Não | `480` | Duração máxima da sessão, em minutos | Não |
| `TRAJETORIA_SELO_DECLARACAO_VALIDADE` | Não | `30` | Validade dos selos, em minutos | Não |
| `TRAJETORIA_URL_ENTRADA_DEMONSTRACAO` | **Não defina** | — | Link do convite simulado (016). O código só aceita `http://127.0.0.1:8000/acesso/`; outro valor faz a comunicação recusar | Não |
| `EMAIL_BACKEND` | **Deixe vazio** | vazio | Vazio = comunicação desabilitada. O código recusa qualquer SMTP que não seja Mailpit em `127.0.0.1:1025` | Não |
| `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`, `EMAIL_USE_SSL` | Não | — | Idem; não configure SMTP institucional | (senha: Sim) |
| `TRAJETORIA_VIDEO_PROJETO` | Não | `/opt/trajetoria/app/video` | Projeto Node do vídeo (padrão: `video/` do checkout) | Não |
| `TRAJETORIA_VIDEO_NODE` | Só com vídeo | `/opt/trajetoria/node/bin/node` | Executável do Node (padrão: `node` do `PATH`) | Não |
| `TRAJETORIA_VIDEO_NAVEGADOR` | Não | vazio | Chrome do sistema; vazio usa o provisionado em `video/` | Não |
| `TRAJETORIA_VIDEO_TEMPO_MAXIMO` | Não | `120` | Segundos máximos por render | Não |
| `TRAJETORIA_VIDEO_CONCORRENCIA` | Não | `2` | Concorrência interna do Remotion | Não |
| `TRAJETORIA_VIDEO_RETENCAO_MINUTOS` | Não | `120` | Retenção do MP4 no banco. **Fora de 1–1440, a aplicação não inicia** | Não |

**Não configuráveis por ambiente** (fixos no código): `DEBUG=False`,
`CSRF_TRUSTED_ORIGINS`, `SECURE_PROXY_SSL_HEADER`, `CSRF_COOKIE_SECURE`, HSTS,
`SECURE_SSL_REDIRECT`, `LOGGING`, `CACHES`, `TIME_ZONE`, `DEFAULT_FROM_EMAIL`. A seção 14
mostra como o Nginx e o Gunicorn cobrem os itens de HTTPS sem alterar o código.

`CI` e `DJANGO_SETTINGS_MODULE` existem, mas **não** devem ser definidas no servidor.

### 10.2 Gerar os segredos

Gere **cada** valor separadamente, na própria VM. Nunca reutilize valores entre ambientes
nem entre variáveis; o código recusa chaves repetidas.

```bash
python3 -c 'import secrets; print(secrets.token_urlsafe(50))'
```

(use para `DJANGO_SECRET_KEY`)

```bash
python3 -c 'import secrets; print(secrets.token_hex(32))'
```

(rode três vezes: `TRAJETORIA_CHAVE_ACESSO_LOCALIZACAO`, `TRAJETORIA_CHAVE_ACESSO_VERIFICACAO`
e `TRAJETORIA_CHAVE_PSEUDONIMIZACAO`)

```bash
/opt/trajetoria/app/.venv/bin/python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'
```

(rode duas vezes: `TRAJETORIA_CHAVE_SELO_DECLARACAO` e `TRAJETORIA_CHAVE_CONSULTA_ACERVO`)

### 10.3 Criar o arquivo de ambiente

O arquivo é lido pelo systemd **e** pelo `sh` do `trajetoria-manage`. Por isso: uma
variável por linha, `CHAVE=valor`, **sem aspas, sem espaços e sem `$`**. Os geradores acima
só produzem caracteres seguros para esse formato.

```bash
sudo install -o root -g trajetoria -m 0640 /dev/null /etc/trajetoria/trajetoria.env
```

```bash
sudoedit /etc/trajetoria/trajetoria.env
```

Conteúdo (substitua os `<...>`):

```text
# Trajetória Ifes — produção. Formato KEY=valor, sem aspas, sem espaços.
DJANGO_SECRET_KEY=<SECRET_KEY_GERADA>
DJANGO_ALLOWED_HOSTS=<DOMAIN>,127.0.0.1,[::1]
TRAJETORIA_COOKIE_SEGURO=1

# Banco local por socket e autenticação peer (seção 8.2)
PGDATABASE=trajetoria

# Modo: vazio = fechado (tudo 404); 1 = demonstração com dados fictícios
TRAJETORIA_DEMONSTRACAO=

# Chaves (018, 019, 013): cada uma gerada separadamente
TRAJETORIA_CHAVE_ACESSO_LOCALIZACAO=<HEX_64_A>
TRAJETORIA_CHAVE_ACESSO_VERIFICACAO=<HEX_64_B>
TRAJETORIA_CHAVE_SELO_DECLARACAO=<FERNET_A>
TRAJETORIA_CHAVE_CONSULTA_ACERVO=<FERNET_B>
TRAJETORIA_CHAVE_PSEUDONIMIZACAO=<HEX_64_C>

# Comunicação: desabilitada na VM
EMAIL_BACKEND=

# Vídeo (só se a seção 13.3 for aplicada)
# TRAJETORIA_VIDEO_NODE=/opt/trajetoria/node/bin/node
```

Verifique as permissões:

```bash
sudo stat -c '%U:%G %a %n' /etc/trajetoria/trajetoria.env
```

Esperado: `root:trajetoria 640 /etc/trajetoria/trajetoria.env`.

### 10.4 Custódia dos segredos

- O arquivo de ambiente **não** entra no Git, em tickets, em e-mails nem em logs.
- Guarde uma cópia das chaves no cofre de segredos institucional, **separada** dos
  backups do banco.
- Consequências de trocar ou perder uma chave:

| Chave | Efeito da troca ou perda |
|---|---|
| `TRAJETORIA_CHAVE_CONSULTA_ACERVO` | Dados de consulta ao acervo já gravados ficam **ilegíveis para sempre** |
| `TRAJETORIA_CHAVE_ACESSO_*` | Todo material de verificação gravado deixa de conferir; ninguém confirma o acesso até o material ser derivado de novo |
| `TRAJETORIA_CHAVE_PSEUDONIMIZACAO` | Pseudônimos de exportações futuras deixam de bater com os anteriores |
| `TRAJETORIA_CHAVE_SELO_DECLARACAO` | Selos em trânsito expiram (efeito curto) |
| `DJANGO_SECRET_KEY` | Sessões e formulários abertos são invalidados |

Custódia e rotação formais são decisões pendentes do projeto (DP-1301 para a
pseudonimização). Não rotacione chaves sem um procedimento aprovado.

---

## 11. Migrations e dados iniciais

> **Estado atual do projeto.** 13 migrations do projeto, todas aditivas, mais a de
> sessões do Django. Uma delas (`analitico/0002_registro_participacao`) preenche dados em
> lote com `RunPython` reversível e aborta sem alterar nada se encontrar ambiguidade. O
> CI roda `makemigrations --check` e `migrate` a cada mudança.

Sempre como `trajetoria` (pelo `trajetoria-manage`) e **depois** de um backup (exceto na
primeira instalação).

Ver o plano sem aplicar:

```bash
sudo trajetoria-manage migrate --plan
```

Sem pendências, a saída é `No planned migration operations.`

Aplicar:

```bash
sudo trajetoria-manage migrate
```

Verificar que não há pendências (código 0, sem saída):

```bash
sudo trajetoria-manage migrate --check
```

Listar o estado de cada migration:

```bash
sudo trajetoria-manage showmigrations
```

Risco: a Constituição (Princípio XXVII) trata migrations sobre dados reais como operações
de risco. Antes de cada atualização, revise as migrations novas (seção 19, passo 3) e
procure `RemoveField`, `DeleteModel`, `AlterField`, `RunSQL` e `RunPython`.

### 11.1 Dados iniciais

- **[modo fechado]** Nenhum. O banco fica só com as tabelas.
- **[modo demonstração]** Carregue o cenário fictício. O comando exige
  `TRAJETORIA_DEMONSTRACAO=1` e as chaves de acesso, é idempotente e **recusa** banco com
  dados de outra origem:

```bash
sudo trajetoria-manage preparar_demonstracao
```

Esperado: `Cenário de demonstração pronto. Pessoas fictícias:` seguido da lista. As chaves
usadas aqui **precisam ser as mesmas** do serviço.

Não há fixtures, importadores de dados reais nem usuários com senha. Não existe Django
Admin nem `createsuperuser`.

---

## 12. Static e media

> **Estado atual do projeto.** **Não existem.** `django.contrib.staticfiles` não está
> instalado; `STATIC_ROOT`, `STATIC_URL`, `MEDIA_ROOT` e `MEDIA_URL` não estão definidos.
> CSS, SVG e fontes são incluídos inline pelos templates; o PNG do card é gerado a cada
> requisição; o sistema não aceita upload de arquivos.

Consequências:

- **Não rode `collectstatic`**: o comando não existe neste projeto
  (`Unknown command: 'collectstatic'`).
- O Nginx não precisa de `location /static/` nem `/media/`.
- Não há media para backup. Os MP4 do vídeo (Feature 022) ficam no **banco**, numa tabela
  técnica (`video_geracaodevideo`), e são apagados após a retenção configurada.
- Tamanho máximo de requisição: os formulários são pequenos; o padrão do Nginx (1 MB) basta.

---

## 13. systemd

### 13.1 Serviço da aplicação

```bash
sudo tee /etc/systemd/system/trajetoria.service > /dev/null <<'EOF'
[Unit]
Description=Trajetória Ifes (Gunicorn)
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=notify
NotifyAccess=main
User=trajetoria
Group=trajetoria
WorkingDirectory=/opt/trajetoria/app
EnvironmentFile=/etc/trajetoria/trajetoria.env
Environment=HOME=/var/lib/trajetoria
# 1 processo: o cache LocMem (limitação de tentativas) é por processo (DP-1803).
ExecStart=/opt/trajetoria/app/.venv/bin/gunicorn config.wsgi:application \
    --bind 127.0.0.1:8000 \
    --workers 1 \
    --threads 4 \
    --timeout 60 \
    --graceful-timeout 30 \
    --forwarded-allow-ips 127.0.0.1 \
    --error-logfile -
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=35
Restart=on-failure
RestartSec=5
UMask=0027
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/lib/trajetoria
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true
RestrictSUIDSGID=true
LockPersonality=true

[Install]
WantedBy=multi-user.target
EOF
```

Notas:

- `--forwarded-allow-ips 127.0.0.1` (padrão do Gunicorn, aqui explícito) faz o Gunicorn
  aceitar o `X-Forwarded-Proto: https` do Nginx. **Isso é o que faz o CSRF funcionar atrás
  do proxy** (seção 14.4). Não use socket Unix entre Nginx e Gunicorn sem rever esse ponto.
- Sem `--access-logfile`: o Nginx já registra os acessos com o IP real.
- Erros da aplicação (`django.request`, nível ERROR) e avisos (`trajetoria`, WARNING) vão
  para o stderr e, daí, para o journald.

Ativar:

```bash
sudo systemctl daemon-reload
```

```bash
sudo systemctl enable trajetoria
```

```bash
sudo systemctl start trajetoria
```

```bash
sudo systemctl status trajetoria
```

Esperado: `active (running)`. Teste local, antes do Nginx:

```bash
curl -s -o /dev/null -w '%{http_code}\n' -H 'Host: <DOMAIN>' http://127.0.0.1:8000/acesso/
```

Esperado: `404` em [modo fechado]; `200` em [modo demonstração].

### 13.2 Limpeza de sessões expiradas

> **Estado atual do projeto.** As sessões ficam no banco e o Django não apaga as expiradas
> sozinho. **Recomendação:** `clearsessions` diário.

```bash
sudo tee /etc/systemd/system/trajetoria-limpar-sessoes.service > /dev/null <<'EOF'
[Unit]
Description=Trajetória Ifes — remove sessões expiradas
After=postgresql.service

[Service]
Type=oneshot
User=trajetoria
Group=trajetoria
WorkingDirectory=/opt/trajetoria/app
EnvironmentFile=/etc/trajetoria/trajetoria.env
Environment=HOME=/var/lib/trajetoria
ExecStart=/opt/trajetoria/app/.venv/bin/python manage.py clearsessions
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/lib/trajetoria
EOF
```

```bash
sudo tee /etc/systemd/system/trajetoria-limpar-sessoes.timer > /dev/null <<'EOF'
[Unit]
Description=Trajetória Ifes — limpeza diária de sessões

[Timer]
OnCalendar=*-*-* 03:30:00
Persistent=true

[Install]
WantedBy=timers.target
EOF
```

```bash
sudo systemctl daemon-reload && sudo systemctl enable --now trajetoria-limpar-sessoes.timer
```

### 13.3 (Opcional) Processador de vídeos

> **Estado atual do projeto.** A Feature 022 gera o vídeo da Minha trajetória com Node +
> Remotion + Chrome Headless Shell, num processo separado (`manage.py processar_videos`).
> Sem ele, a página funciona igual, só sem a opção de vídeo. Uso permitido **só na
> demonstração**: o aceite das licenças do Remotion e do H.264 (`libx264`, GPL) é a
> **DP-2201**, pendente antes de qualquer produção.

Aplique esta seção **apenas** em [modo demonstração] e se o vídeo for necessário.

**Node 22** (o Ubuntu 24.04 traz uma versão antiga). Use o binário oficial, conferindo o
SHA-256. Escolha a versão 22.x LTS mais recente em `https://nodejs.org/dist/latest-v22.x/`:

```bash
cd /tmp && curl -fsSLO https://nodejs.org/dist/v<NODE_22_VERSAO>/node-v<NODE_22_VERSAO>-linux-x64.tar.xz && curl -fsSLO https://nodejs.org/dist/v<NODE_22_VERSAO>/SHASUMS256.txt
```

```bash
cd /tmp && grep " node-v<NODE_22_VERSAO>-linux-x64.tar.xz\$" SHASUMS256.txt | sha256sum -c -
```

```bash
sudo install -d -o root -g root -m 0755 /opt/trajetoria/node && sudo tar -xJf /tmp/node-v<NODE_22_VERSAO>-linux-x64.tar.xz -C /opt/trajetoria/node --strip-components=1
```

```bash
/opt/trajetoria/node/bin/node --version
```

**Bibliotecas do Chrome Headless Shell** (lista da documentação do Remotion para Ubuntu
24.04; Alpine não é suportado):

```bash
sudo apt-get install -y libnss3 libdbus-1-3 libatk1.0-0 libgbm1 libasound2t64 libxrandr2 libxkbcommon0 libxfixes3 libxcomposite1 libxdamage1 libatk-bridge2.0-0 libpango-1.0-0 libcairo2 libcups2t64
```

**Projeto `video/` e navegador** (como root, a partir do lock versionado):

```bash
sudo env PATH=/opt/trajetoria/node/bin:/usr/bin:/bin npm ci --prefix /opt/trajetoria/app/video
```

```bash
sudo env PATH=/opt/trajetoria/node/bin:/usr/bin:/bin npm --prefix /opt/trajetoria/app/video run garantir-navegador
```

Conferir se o navegador encontra todas as bibliotecas (não deve imprimir nada):

```bash
sudo find /opt/trajetoria/app/video/node_modules/.remotion -name chrome-headless-shell -type f -exec ldd {} \; | grep 'not found'
```

Diretórios gravados pelo serviço no primeiro render: o bundle do template e o cache do
webpack do Remotion (`video/node_modules/.cache/`). Refaça este passo **depois de todo
`npm ci`**, que recria `node_modules`:

```bash
sudo install -d -o trajetoria -g trajetoria -m 0750 /opt/trajetoria/app/video/.bundle /opt/trajetoria/app/video/node_modules/.cache
```

Acrescente ao `/etc/trajetoria/trajetoria.env`:

```text
TRAJETORIA_VIDEO_NODE=/opt/trajetoria/node/bin/node
```

Serviço:

```bash
sudo tee /etc/systemd/system/trajetoria-videos.service > /dev/null <<'EOF'
[Unit]
Description=Trajetória Ifes — processador de vídeos (Feature 022)
After=network.target postgresql.service trajetoria.service
Wants=postgresql.service

[Service]
Type=simple
User=trajetoria
Group=trajetoria
WorkingDirectory=/opt/trajetoria/app
EnvironmentFile=/etc/trajetoria/trajetoria.env
Environment=HOME=/var/lib/trajetoria
Environment=PATH=/opt/trajetoria/node/bin:/usr/bin:/bin
ExecStart=/opt/trajetoria/app/.venv/bin/python manage.py processar_videos
KillSignal=SIGINT
Restart=on-failure
RestartSec=10
UMask=0027
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/lib/trajetoria /opt/trajetoria/app/video/.bundle -/opt/trajetoria/app/video/node_modules/.cache
# O render não precisa de rede (banco por socket Unix; Chrome em localhost).
IPAddressDeny=any
IPAddressAllow=localhost

[Install]
WantedBy=multi-user.target
EOF
```

```bash
sudo systemctl daemon-reload && sudo systemctl enable --now trajetoria-videos && sudo systemctl restart trajetoria
```

O `restart` da aplicação é necessário: ela verifica a disponibilidade do renderizador uma
vez por processo. Segurança: o Remotion abre o Chrome com `--no-sandbox`; o isolamento vem
do usuário sem privilégios e das restrições do systemd acima, inclusive o bloqueio de rede
(`IPAddressDeny`). O Chrome só renderiza a composição gerada pela própria aplicação.

**Não validado em Ubuntu:** esta unidade (em especial `ProtectSystem=strict`, os
`ReadWritePaths` e o bloqueio de rede) foi escrita a partir do código, sem execução numa VM.
Valide na primeira instalação com um ciclo explícito e leia o journal:

```bash
sudo systemctl stop trajetoria-videos && sudo systemd-run --wait --pipe --uid=trajetoria --gid=trajetoria --property=EnvironmentFile=/etc/trajetoria/trajetoria.env --property=Environment=HOME=/var/lib/trajetoria --property=WorkingDirectory=/opt/trajetoria/app --property=ProtectSystem=strict --property=ReadWritePaths="/var/lib/trajetoria /opt/trajetoria/app/video/.bundle /opt/trajetoria/app/video/node_modules/.cache" --property=IPAddressDeny=any --property=IPAddressAllow=localhost /opt/trajetoria/app/.venv/bin/python manage.py processar_videos --uma-vez; sudo systemctl start trajetoria-videos
```

Sem pedido pendente, o comando termina sem fazer nada; para um teste real, peça um vídeo
na página `/minha-trajetoria/` com o processador parado e rode o comando em seguida.

---

## 14. Reverse proxy e HTTPS (Nginx)

### 14.1 Certificado

Coloque o certificado (com a cadeia intermediária) e a chave fornecidos pela instituição:

```bash
sudo install -o root -g root -m 0644 <ARQUIVO_CERTIFICADO_COM_CADEIA> /etc/ssl/trajetoria/fullchain.pem
```

```bash
sudo install -o root -g root -m 0600 <ARQUIVO_CHAVE_PRIVADA> /etc/ssl/trajetoria/privkey.pem
```

### 14.2 Variante A — TLS terminado no Nginx da VM (padrão)

```bash
sudo tee /etc/nginx/sites-available/trajetoria > /dev/null <<'EOF'
# Recusa nomes que não sejam <DOMAIN> (evita ruído de "Invalid HTTP_HOST" no Django).
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    listen 443 ssl http2 default_server;
    listen [::]:443 ssl http2 default_server;
    ssl_certificate     /etc/ssl/trajetoria/fullchain.pem;
    ssl_certificate_key /etc/ssl/trajetoria/privkey.pem;
    return 444;
}

server {
    listen 80;
    listen [::]:80;
    server_name <DOMAIN>;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name <DOMAIN>;

    ssl_certificate     /etc/ssl/trajetoria/fullchain.pem;
    ssl_certificate_key /etc/ssl/trajetoria/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_session_cache shared:TLS:10m;
    ssl_session_timeout 1d;

    # Ative só depois de validar o HTTPS de ponta a ponta (seção 14.5).
    # add_header Strict-Transport-Security "max-age=300" always;

    client_max_body_size 1m;

    # [modo demonstração] acesso só pela rede institucional:
    # allow <REDE_INSTITUCIONAL_CIDR>;
    # deny all;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_redirect off;
        # O código não marca o cookie CSRF como Secure; o Nginx marca todos.
        proxy_cookie_flags ~ secure;
        proxy_connect_timeout 5s;
        proxy_read_timeout 65s;
    }
}
EOF
```

Substitua `<DOMAIN>` no arquivo e, em [modo demonstração], descomente `allow`/`deny`:

```bash
sudo sed -i 's/<DOMAIN>/trajetoria.exemplo.ifes.edu.br/g' /etc/nginx/sites-available/trajetoria
```

(troque `trajetoria.exemplo.ifes.edu.br` pelo seu domínio)

```bash
sudo ln -sf /etc/nginx/sites-available/trajetoria /etc/nginx/sites-enabled/trajetoria && sudo rm -f /etc/nginx/sites-enabled/default
```

```bash
sudo nginx -t && sudo systemctl reload nginx
```

Não há `location /static/` nem `/media/` (seção 12). O tempo de leitura (65 s) acompanha o
`--timeout 60` do Gunicorn.

### 14.3 Variante B — TLS terminado no proxy institucional

Se o proxy do datacenter termina o TLS e fala HTTP com a VM, **pule a seção 14.1** e use
este arquivo no lugar do da variante A. Confirme antes com a equipe do proxy que ele envia
o `Host` original e **sempre** `X-Forwarded-Proto: https`.

```bash
sudo tee /etc/nginx/sites-available/trajetoria > /dev/null <<'EOF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    return 444;
}

server {
    listen 80;
    listen [::]:80;
    server_name <DOMAIN>;

    # Só o proxy institucional fala com esta VM.
    allow <IP_DO_PROXY>;
    deny all;

    client_max_body_size 1m;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        # Repassa o protocolo informado pelo proxy institucional.
        proxy_set_header X-Forwarded-Proto $http_x_forwarded_proto;
        proxy_redirect off;
        proxy_cookie_flags ~ secure;
        proxy_connect_timeout 5s;
        proxy_read_timeout 65s;
    }
}
EOF
```

Firewall: em vez de `Nginx Full`, libere só a porta 80 e só para o proxy:

```bash
sudo ufw delete allow 'Nginx Full'; sudo ufw allow from <IP_DO_PROXY> to any port 80 proto tcp
```

Depois, siga a variante A a partir do `sed` que substitui `<DOMAIN>` (troque também
`<IP_DO_PROXY>`). Redirecionamento HTTP→HTTPS e HSTS ficam a cargo do proxy.

### 14.4 Por que isso importa (CSRF e cookies)

As settings **não** definem `SECURE_PROXY_SSL_HEADER` nem `CSRF_TRUSTED_ORIGINS`. Atrás de
um proxy HTTPS, o Django só reconhece a requisição como HTTPS porque o **Gunicorn** aceita
`X-Forwarded-Proto` vindo de `127.0.0.1`. Validado em 2026-10-05:

| Cenário | POST em `/acesso/` com `Origin: https://<DOMAIN>` |
|---|---|
| `runserver` atrás de proxy HTTPS | **403** (falha de CSRF) |
| Gunicorn 23 com `X-Forwarded-Proto: https` vindo de 127.0.0.1 | **303** (correto) |

Logo: **não substitua o Gunicorn**, não ligue o Nginx ao Gunicorn por socket Unix e não
remova `X-Forwarded-Proto` sem rever esse ponto.

### 14.5 HSTS

Depois que o smoke test (seção 20) passar por HTTPS, ative HSTS de forma gradual: descomente
a linha com `max-age=300`, recarregue o Nginx, observe por alguns dias e só então aumente
para `max-age=31536000`. HSTS longo é difícil de desfazer; não use `includeSubDomains` sem
autorização da equipe responsável pelo domínio institucional.

### 14.6 Avisos esperados de `check --deploy`

```bash
sudo trajetoria-manage check --deploy
```

Com o arquivo de ambiente correto, restam exatamente três avisos, cobertos pelo Nginx:

| Aviso | Por que aparece | Mitigação nesta instalação |
|---|---|---|
| `security.W004` (HSTS) | Não configurável no código | `Strict-Transport-Security` no Nginx (14.5) |
| `security.W008` (`SECURE_SSL_REDIRECT`) | Não configurável no código | Redirecionamento 301 no Nginx |
| `security.W016` (`CSRF_COOKIE_SECURE`) | Não configurável no código | `proxy_cookie_flags ~ secure` no Nginx |

Qualquer outro aviso (por exemplo `W009` sobre `SECRET_KEY`, `W012` sobre cookie de
sessão) indica erro no arquivo de ambiente.

---

## 15. Primeira subida — ordem completa

Resumo do caminho de uma VM limpa até o serviço no ar:

1. Seção 5 — pacotes, fuso, firewall.
1. Seção 18.2 — limite do journald.
2. Seção 3 — usuário `trajetoria`.
3. Seção 4 — diretórios.
4. Seção 6 — clone e `checkout --detach <TAG_DE_RELEASE>`.
5. Seção 7 — uv, utilitários, Python, `sync --locked`, Gunicorn.
6. Seção 8 — papel, banco, diretório de backups.
7. Seção 10 — segredos e `/etc/trajetoria/trajetoria.env`.
8. `sudo trajetoria-manage check --deploy` (só os três avisos da seção 14.6).
9. Seção 11 — `migrate` e, em [modo demonstração], `preparar_demonstracao`.
10. Seção 13 — serviços e timer.
11. Seção 14 — Nginx e TLS.
12. Seção 17 — timer de backup e primeiro backup.
13. Seção 20 — smoke test.

---

## 16. Segurança

### 16.1 Checklist de hardening

| Item | Como verificar |
|---|---|
| `DEBUG` desligado | Fixo `False` no código. `sudo trajetoria-manage shell -c "from django.conf import settings; print(settings.DEBUG)"` → `False` |
| `SECRET_KEY` própria | `sudo trajetoria-manage shell -c "from django.conf import settings; print(settings.SECRET_KEY.startswith('insegura'))"` → `False` |
| Segredos fora do repositório | Só em `/etc/trajetoria/trajetoria.env` (`root:trajetoria 0640`) |
| Hosts permitidos | `DJANGO_ALLOWED_HOSTS` só com `<DOMAIN>` e loopback; Host estranho → 400 [demonstração] (404 [fechado], porque o middleware do modo responde antes) |
| Cookies seguros | `TRAJETORIA_COOKIE_SEGURO=1` + `proxy_cookie_flags ~ secure` |
| CSRF | Ativo (middleware). Funciona atrás do proxy pelo Gunicorn (14.4) |
| TLS | TLS 1.2+; HTTP redireciona para HTTPS |
| Banco não exposto | `sudo ss -ltnp \| grep 5432` só em `127.0.0.1`/`::1` |
| Gunicorn não exposto | `sudo ss -ltnp \| grep 8000` só em `127.0.0.1` |
| Aplicação sem root | `ps -o user= -C gunicorn` → `trajetoria` |
| Menor privilégio | Código e venv de `root`; serviço só escreve em `/var/lib/trajetoria` |
| Firewall | `sudo ufw status` → só 22, 80, 443 |
| SSH | Só chave pública; `PasswordAuthentication no` e `PermitRootLogin no` em `/etc/ssh/sshd_config.d/` |
| Sistema atualizado | `unattended-upgrades` ativo |
| Backups protegidos | `/var/backups/trajetoria` `0700 postgres`; cópia externa cifrada (seção 17) |
| Rotação de logs | journald limitado; logrotate do Nginx (seção 18) |
| Modo correto | `grep ^TRAJETORIA_DEMONSTRACAO= /etc/trajetoria/trajetoria.env` |

### 16.2 Cuidados com dados pessoais (LGPD)

Não são conclusões jurídicas; são cuidados técnicos que o código e a Constituição do
projeto (Princípio XVI, NON-NEGOTIABLE) já pressupõem. Base legal, consentimento e
retenção são decisões institucionais pendentes e não devem ser inventadas na operação.

- **[modo demonstração]** Só dados fictícios. O `preparar_demonstracao` recusa banco com
  dados de outra origem. Nunca restaure nesta instância um dump vindo de outro ambiente.
- O CPF não é guardado em claro: o acesso usa HMAC com chaves dedicadas (018). Os dados de
  consulta ao acervo são cifrados (019). A suíte de testes verifica que CPF e data não
  aparecem em logs nem no banco.
- Os logs da aplicação registram só fatos técnicos. Os logs de acesso do Nginx registram
  **IP e URL**: trate-os como dado pessoal, com retenção limitada (seção 18).
- Exportações (013) saem pseudonimizadas e só por operação explícita. Arquivos exportados
  não devem ficar na VM.
- Backups contêm todo o banco: cifre a cópia externa e restrinja quem a acessa.
- Acesso administrativo à VM (SSH, `sudo`) deve ser nominal e restrito.

---

## 17. Backup e restauração

> **Estado atual do projeto.** Não há política de backup definida. O que precisa de
> backup é **só o banco** (não há media) e, **separadamente**, o arquivo de segredos.
> Validado em 2026-10-05: dump `custom` e restauração em banco novo, com contagens iguais.

### 17.1 Backup do banco

Manual:

```bash
sudo -u postgres pg_dump --format=custom --file=/var/backups/trajetoria/trajetoria-$(date +%Y%m%d-%H%M%S).dump trajetoria
```

Conferir o arquivo (lista o conteúdo; deve mostrar `TABLE DATA`):

```bash
sudo -u postgres sh -c 'pg_restore --list "$(ls -1t /var/backups/trajetoria/*.dump | head -1)" | grep -c "TABLE DATA"'
```

Automático, diário, com retenção local de 14 dias (**recomendação**):

```bash
sudo tee /etc/systemd/system/trajetoria-backup.service > /dev/null <<'EOF'
[Unit]
Description=Trajetória Ifes — backup do banco
After=postgresql.service

[Service]
Type=oneshot
User=postgres
Group=postgres
UMask=0077
ExecStart=/bin/sh -c 'pg_dump --format=custom --file=/var/backups/trajetoria/trajetoria-$$(date +%%Y%%m%%d-%%H%%M%%S).dump trajetoria'
ExecStartPost=/usr/bin/find /var/backups/trajetoria -name 'trajetoria-*.dump' -mtime +14 -delete
EOF
```

```bash
sudo tee /etc/systemd/system/trajetoria-backup.timer > /dev/null <<'EOF'
[Unit]
Description=Trajetória Ifes — backup diário

[Timer]
OnCalendar=*-*-* 02:30:00
Persistent=true

[Install]
WantedBy=timers.target
EOF
```

```bash
sudo systemctl daemon-reload && sudo systemctl enable --now trajetoria-backup.timer
```

```bash
sudo systemctl start trajetoria-backup.service && sudo ls -lh /var/backups/trajetoria
```

### 17.2 Cópia externa, retenção e cifragem

Backup que fica só na VM não protege contra perda da VM.

- **Cópia externa:** envie `/var/backups/trajetoria/` diariamente para o sistema de backup
  do datacenter. A ferramenta é **não determinada no estado atual do projeto**; use a
  institucional.
- **Retenção recomendada (mínima, a validar institucionalmente):** 14 diários locais;
  externamente, 4 semanais e 6 mensais.
- **Cifragem:** cifre a cópia externa (ela contém dados pessoais em uso real).
- **Segredos:** guarde `/etc/trajetoria/trajetoria.env` no cofre institucional,
  **separado** dos dumps. Um dump sem a `TRAJETORIA_CHAVE_CONSULTA_ACERVO` correspondente
  tem colunas cifradas irrecuperáveis.

### 17.3 Backup de media

Não se aplica: não há `MEDIA_ROOT` nem uploads. Os MP4 transitórios ficam no banco e não
precisam ser preservados.

### 17.4 Restauração

Restaurar substitui o banco inteiro: há perda de tudo o que foi gravado depois do dump.

1. Pare quem escreve no banco:

```bash
sudo systemctl stop trajetoria
```

Com o processador de vídeo (seção 13.3):

```bash
sudo systemctl stop trajetoria-videos
```

2. Restaure num banco **novo**, sem tocar no atual:

```bash
sudo -u postgres createdb --owner=trajetoria --encoding=UTF8 --template=template0 --locale=C.UTF-8 --locale-provider=icu --icu-locale=pt-BR trajetoria_restaurado
```

```bash
sudo -u postgres pg_restore --dbname=trajetoria_restaurado --no-owner --role=trajetoria --exit-on-error /var/backups/trajetoria/<ARQUIVO>.dump
```

3. Valide o banco restaurado:

```bash
sudo -u trajetoria psql -d trajetoria_restaurado -Atc "select count(*) from django_migrations;"
```

4. Troque os bancos (o antigo é preservado com outro nome). A troca falha se houver
   conexões abertas: pare os timers e confira que nada está conectado.

```bash
sudo systemctl stop trajetoria-backup.timer trajetoria-limpar-sessoes.timer
```

```bash
sudo -u postgres psql -Atc "select count(*) from pg_stat_activity where datname in ('trajetoria', 'trajetoria_restaurado');"
```

Esperado: `0`. Então:

```bash
sudo -u postgres psql -c "alter database trajetoria rename to trajetoria_antes_restauracao;" -c "alter database trajetoria_restaurado rename to trajetoria;"
```

5. Confira as migrations e suba o serviço:

```bash
sudo trajetoria-manage migrate --check && sudo systemctl start trajetoria
```

```bash
sudo systemctl start trajetoria-backup.timer trajetoria-limpar-sessoes.timer
```

6. Faça o smoke test (seção 20). Remova `trajetoria_antes_restauracao` só depois de
   confirmar que a restauração está correta:

```bash
sudo -u postgres dropdb trajetoria_antes_restauracao
```

Se o dump for de uma versão anterior do código, restaure também a tag correspondente
(seção 19.3) ou rode `migrate` depois da restauração, conforme o caso.

### 17.5 Teste periódico de restauração

**Um backup nunca restaurado não é um backup validado.** Mensalmente (recomendação):

```bash
sudo -u postgres createdb --owner=trajetoria --encoding=UTF8 --template=template0 --locale=C.UTF-8 --locale-provider=icu --icu-locale=pt-BR trajetoria_teste_restauracao
```

```bash
sudo -u postgres sh -c 'pg_restore --dbname=trajetoria_teste_restauracao --no-owner --role=trajetoria --exit-on-error "$(ls -1t /var/backups/trajetoria/*.dump | head -1)"'
```

```bash
sudo -u trajetoria psql -d trajetoria_teste_restauracao -Atc "select count(*) from django_migrations;"
```

```bash
sudo -u postgres dropdb trajetoria_teste_restauracao
```

Registre data, arquivo testado e resultado.

---

## 18. Logs e observabilidade

### 18.1 Onde estão os logs

| Fonte | Destino | Conteúdo |
|---|---|---|
| Aplicação (`trajetoria.*`, WARNING+) | journald, unidade `trajetoria` | Fatos técnicos: falha de rasterização, chaves não configuradas. A limitação de tentativas é registrada em INFO e **não** chega ao journal; veja os 429 no `access.log` do Nginx |
| `django.request` (ERROR) | journald, unidade `trajetoria` | Tracebacks de erros 500 (nunca exibidos ao usuário) |
| Gunicorn | journald, unidade `trajetoria` | Início, parada, workers, timeouts |
| Processador de vídeos | journald, unidade `trajetoria-videos` | `video: falha na geração (<motivo>)` |
| Timers | journald, `trajetoria-backup`, `trajetoria-limpar-sessoes` | Resultado das execuções |
| Nginx | `/var/log/nginx/access.log`, `error.log` | Acessos (IP real, URL, status), 502/504 |
| PostgreSQL | `/var/log/postgresql/postgresql-16-main.log` | Erros e conexões recusadas |

Consultas:

```bash
sudo journalctl -u trajetoria -f
```

```bash
sudo journalctl -u trajetoria --since "1 hour ago" -p warning
```

```bash
sudo tail -n 100 /var/log/nginx/error.log
```

```bash
sudo awk '$9 ~ /^5/' /var/log/nginx/access.log | tail -n 20
```

```bash
sudo awk '$9 == 429' /var/log/nginx/access.log | tail -n 20
```

### 18.2 Retenção e espaço

Limite o journald (recomendação: 1 GB, 30 dias):

```bash
sudo install -d /etc/systemd/journald.conf.d && printf '[Journal]\nSystemMaxUse=1G\nMaxRetentionSec=30day\n' | sudo tee /etc/systemd/journald.conf.d/trajetoria.conf > /dev/null && sudo systemctl restart systemd-journald
```

O Nginx do Ubuntu já rotaciona diariamente e guarda 14 arquivos
(`/etc/logrotate.d/nginx`). Como esses logs têm IP, não aumente a retenção sem
justificativa.

### 18.3 Health check e monitoramento mínimo

> **Estado atual do projeto.** Não existe endpoint de health check. Em modo fechado, toda
> URL responde 404 — inclusive um eventual `/saude/`.

**Recomendação** de verificações (no monitoramento institucional ou por cron externo):

| O que | Como | Alerta quando |
|---|---|---|
| Disponibilidade | `curl -s -o /dev/null -w '%{http_code}' https://<DOMAIN>/acesso/` | ≠ `200` [demonstração] ou ≠ `404` [fechado]; `502`/`504` = aplicação fora |
| Serviço | `systemctl is-active trajetoria` | ≠ `active` |
| Erros 5xx | contagem no `access.log` | crescimento |
| CPU / memória | `top`, `free -m` ou agente institucional | uso sustentado > 80% |
| Disco | `df -h / /var` | > 80% |
| Banco ativo | `sudo -u postgres pg_isready` | ≠ `accepting connections` |
| Tamanho do banco | `sudo -u postgres psql -Atc "select pg_size_pretty(pg_database_size('trajetoria'));"` | crescimento inesperado |
| Backup | `sudo ls -lt /var/backups/trajetoria \| head -2` | arquivo mais recente com mais de 26 h |
| Certificado | `openssl x509 -enddate -noout -in /etc/ssl/trajetoria/fullchain.pem` | < 30 dias para expirar |

Distinga um 404 do Django de uma falha do proxy: o 404 do Django tem o título
"Página não encontrada — Trajetória Ifes".

---

## 19. Procedimento de deploy e atualização

Sempre por tag (seção 6). Duração típica: poucos minutos, com o serviço parado entre os
passos 5 e 10.

### 19.1 Runbook

1. **Anote a versão atual** (para o rollback):

```bash
sudo git -C /opt/trajetoria/app describe --tags --always | sudo tee /opt/trajetoria/release-anterior
```

2. **Obtenha a nova release** e confirme que o commit da tag passou no CI de `main`:

```bash
sudo git -C /opt/trajetoria/app fetch --tags origin
```

```bash
sudo git -C /opt/trajetoria/app rev-list -n 1 <NOVA_TAG>
```

3. **Revise as mudanças sensíveis** entre a versão atual e a nova:

```bash
sudo git -C /opt/trajetoria/app diff --stat HEAD <NOVA_TAG> -- '*/migrations/*' pyproject.toml uv.lock config/ video/package-lock.json
```

Leia cada migration nova. Procure `RemoveField`, `DeleteModel`, `AlterField`, `RunSQL`,
`RunPython`. Leia também as novas variáveis em `config/settings.py` e o `.env.example`.

4. **Faça o backup** e confira o arquivo:

```bash
sudo systemctl start trajetoria-backup.service && sudo ls -lt /var/backups/trajetoria | head -3
```

5. **Pare os serviços:**

```bash
sudo systemctl stop trajetoria
```

Com o processador de vídeo (seção 13.3):

```bash
sudo systemctl stop trajetoria-videos
```


6. **Troque o código:**

```bash
sudo git -C /opt/trajetoria/app checkout --detach <NOVA_TAG>
```

7. **Sincronize as dependências** (e reinstale o Gunicorn, removido pelo `sync`):

```bash
sudo trajetoria-uv sync --locked
```

```bash
sudo trajetoria-uv pip install --python /opt/trajetoria/app/.venv/bin/python "gunicorn==23.0.0"
```

Com vídeo, também:

```bash
sudo env PATH=/opt/trajetoria/node/bin:/usr/bin:/bin npm ci --prefix /opt/trajetoria/app/video && sudo env PATH=/opt/trajetoria/node/bin:/usr/bin:/bin npm --prefix /opt/trajetoria/app/video run garantir-navegador && sudo install -d -o trajetoria -g trajetoria -m 0750 /opt/trajetoria/app/video/.bundle /opt/trajetoria/app/video/node_modules/.cache
```

8. **Verifique a configuração:**

```bash
sudo trajetoria-manage check --deploy
```

9. **Aplique as migrations:**

```bash
sudo trajetoria-manage migrate --plan && sudo trajetoria-manage migrate && sudo trajetoria-manage migrate --check
```

`collectstatic`: **não se aplica** (seção 12).

10. **Suba os serviços:**

```bash
sudo systemctl start trajetoria
```

Com o processador de vídeo (seção 13.3):

```bash
sudo systemctl start trajetoria-videos
```

11. **Smoke test** (seção 20).
12. **Logs dos primeiros minutos:**

```bash
sudo journalctl -u trajetoria --since "10 min ago" -p warning
```

13. **Registre a versão implantada:**

```bash
sudo git -C /opt/trajetoria/app describe --tags --always
```

### 19.2 Quando a release trouxer variáveis novas

Se o passo 3 mostrar novas variáveis em `config/settings.py`, atualize
`/etc/trajetoria/trajetoria.env` **antes** do passo 10. Uma variável com validação na
carga (como `TRAJETORIA_VIDEO_RETENCAO_MINUTOS`) impede o serviço de iniciar se estiver
errada.

### 19.3 Rollback

**Rollback de código** (sem migrations novas, ou com migrations compatíveis com o código
anterior):

```bash
sudo systemctl stop trajetoria
```

Com o processador de vídeo (seção 13.3):

```bash
sudo systemctl stop trajetoria-videos
```

```bash
sudo git -C /opt/trajetoria/app checkout --detach "$(sudo cat /opt/trajetoria/release-anterior)"
```

```bash
sudo trajetoria-uv sync --locked && sudo trajetoria-uv pip install --python /opt/trajetoria/app/.venv/bin/python "gunicorn==23.0.0"
```

Com vídeo, também (seção 13.3):

```bash
sudo env PATH=/opt/trajetoria/node/bin:/usr/bin:/bin npm ci --prefix /opt/trajetoria/app/video && sudo env PATH=/opt/trajetoria/node/bin:/usr/bin:/bin npm --prefix /opt/trajetoria/app/video run garantir-navegador && sudo install -d -o trajetoria -g trajetoria -m 0750 /opt/trajetoria/app/video/.bundle /opt/trajetoria/app/video/node_modules/.cache
```

```bash
sudo systemctl start trajetoria
```

Com o processador de vídeo (seção 13.3):

```bash
sudo systemctl start trajetoria-videos
```

**Rollback com migrations aplicadas.** Não há rollback automático de migrations e não se
deve presumir que ele é seguro. Duas opções, por ordem de preferência:

1. **Restaurar o backup do passo 4** (seção 17.4) e voltar o código. Perde-se o que foi
   gravado depois do backup; por isso o intervalo entre o passo 4 e a decisão de rollback
   deve ser curto.
2. **Reverter migrations** com `sudo trajetoria-manage migrate <app> <migration_anterior>`,
   **somente** se cada migration revertida tiver operação inversa conhecida e tiver sido
   revisada. Reverter uma migration que remove ou transforma dados pode perder informação.

---

## 20. Smoke test pós-deploy

Execute na própria VM, depois de cada implantação. Troque `<DOMAIN>`.

| # | Verificação | Comando | Esperado |
|---|---|---|---|
| 1 | Serviço ativo | `systemctl is-active trajetoria` | `active` |
| 2 | Gunicorn só em loopback | `sudo ss -ltnp \| grep ':8000'` | `127.0.0.1:8000` |
| 3 | Banco e migrations | `sudo trajetoria-manage migrate --check` | código 0, sem saída |
| 4 | Configuração | `sudo trajetoria-manage check --deploy` | só W004, W008, W016 |
| 5 | Modo em vigor | `sudo trajetoria-manage shell -c "from django.conf import settings as s; print(s.DEBUG, s.TRAJETORIA_DEMONSTRACAO)"` | `False False` [fechado] ou `False True` [demonstração] |
| 6 | HTTP → HTTPS | `curl -s -o /dev/null -w '%{http_code} %{redirect_url}\n' http://<DOMAIN>/acesso/` | `301 https://<DOMAIN>/acesso/` |
| 7 | Página principal | `curl -s -o /dev/null -w '%{http_code}\n' https://<DOMAIN>/acesso/` | `404` [fechado] ou `200` [demonstração] |
| 8 | É o Django que responde | `curl -s https://<DOMAIN>/acesso/ \| grep -o '<title>[^<]*'` | título contendo "Trajetória Ifes" |
| 9 | Host inválido recusado | `curl -s -o /dev/null -w '%{http_code}\n' -H 'Host: invalido.example' http://127.0.0.1:8000/acesso/` | `400` [demonstração] ou `404` [fechado] |
| 10 | Raiz | `curl -s -o /dev/null -w '%{http_code} %{redirect_url}\n' https://<DOMAIN>/` | `404` [fechado] ou `302 …/acesso/` [demonstração] |
| 11 | Sem erros novos | `sudo journalctl -u trajetoria --since "10 min ago" -p err` | vazio |

Só em [modo demonstração], no navegador:

| # | Verificação | Esperado |
|---|---|---|
| 12 | Abrir `https://<DOMAIN>/acesso/` | Formulário com o painel "Dados fictícios para demonstração"; estilos aplicados (CSS é inline) |
| 13 | Entrar com Ana Exemplo (`000.000.001-91`, `12/04/1998`) | Vai para `/formacoes/`; prova CSRF, sessão e chaves corretas |
| 14 | Entrar com dados errados | "Não foi possível confirmar os dados informados." (status 200), nunca 403 ou 500 |
| 15 | `/demonstracao/operador/` → operador A → `/acompanhamento/` | Lista de Campanhas de demonstração |
| 16 | Sair | Volta para `/acesso/` |

Static e media: não há o que verificar além do item 12 (seção 12).

Nos comandos com `manage.py shell -c`, o Django 5.2 imprime antes uma linha
`N objects imported automatically`; ela é esperada e pode ser ignorada.

---

## 21. Troubleshooting

Formato: **sintoma → diagnóstico (comando) → causa provável → correção.**

**502 Bad Gateway**
- Diagnóstico: `systemctl status trajetoria`; `sudo journalctl -u trajetoria -n 50`;
  `sudo ss -ltnp | grep 8000`.
- Causa: Gunicorn parado, falhou ao iniciar ou escuta em outro endereço.
- Correção: corrija o erro do journal (geralmente arquivo de ambiente ou venv sem
  Gunicorn: rode o `pip install` da seção 7.4) e `sudo systemctl restart trajetoria`.

**504 Gateway Timeout**
- Diagnóstico: `grep -i timeout` no journal da unidade `trajetoria`.
- Causa: requisição > 60 s (worker reiniciado pelo Gunicorn) ou banco travado.
- Correção: verifique o banco (`pg_stat_activity`); não aumente o timeout sem entender a causa.

**500 Internal Server Error**
- Diagnóstico: `sudo journalctl -u trajetoria -p err --since "15 min ago"` (o traceback
  está lá; a página nunca o mostra porque `DEBUG=False`).
- Causa: exceção da aplicação, tabela ausente (migration pendente), chave inválida.
- Correção: conforme o traceback. Não ative `DEBUG` (não é possível e não é desejável).

**Migration pendente**
- Diagnóstico: `sudo trajetoria-manage migrate --check` (código ≠ 0) e
  `sudo trajetoria-manage showmigrations | grep '\[ \]'`.
- Causa: deploy sem o passo 9.
- Correção: backup e `sudo trajetoria-manage migrate`.

**Erro de conexão com o PostgreSQL**
- Diagnóstico: `sudo -u postgres pg_isready`; `sudo -u trajetoria psql -d trajetoria -c 'select 1'`;
  `sudo tail -n 50 /var/log/postgresql/postgresql-16-main.log`.
- Causas: PostgreSQL parado; `role "trajetoria" does not exist`; `Peer authentication
  failed` (processo rodando com outro usuário de sistema ou `PGUSER` diferente);
  `PGDATABASE` errado.
- Correção: `sudo systemctl start postgresql`; seção 8.2; rode sempre como `trajetoria`.

**Permission denied**
- Diagnóstico: `sudo journalctl -u trajetoria -n 30`; `namei -l <caminho>`.
- Causas: arquivo de ambiente com dono/modo errado; venv criado por outro usuário com
  umask restritiva; `video/.bundle` sem dono `trajetoria`; tentativa de escrever fora de
  `ReadWritePaths`.
- Correção: refaça as permissões da seção 4; `sudo chmod -R a+rX /opt/trajetoria/app /opt/trajetoria/python`.

**Static não encontrado**
- Diagnóstico: o projeto não tem static.
- Causa: alguém configurou `location /static/` ou espera `collectstatic`.
- Correção: nada a fazer; se a página aparece sem estilo, o problema é o template ou o
  proxy alterando a resposta, não arquivos estáticos.

**Media não acessível**
- Não se aplica: não há media. Vídeo "não foi possível preparar": veja o journal de
  `trajetoria-videos`.

**Bad Request (400) / host não permitido** (só em modo de demonstração; no modo fechado tudo é 404)
- Diagnóstico: `sudo awk '$9 == 400' /var/log/nginx/access.log | tail` e
  `curl -s -o /dev/null -w '%{http_code}\n' -H 'Host: <DOMAIN>' http://127.0.0.1:8000/acesso/`.
  O Django **não** registra `DisallowedHost` no journal: o logger `django.security` não
  está configurado em `LOGGING`.
- Causa: `<DOMAIN>` ausente de `DJANGO_ALLOWED_HOSTS` ou o proxy não repassa `Host`.
- Correção: ajuste a variável e `sudo systemctl restart trajetoria`; confira
  `proxy_set_header Host $host`.

**CSRF failure (403 com a página "Não foi possível confirmar o envio.")**
- Diagnóstico: o POST vem por HTTPS? `curl -sI https://<DOMAIN>/acesso/`; confira o
  `X-Forwarded-Proto` no Nginx e o `--forwarded-allow-ips` no serviço.
- Causas: Nginx sem `X-Forwarded-Proto https`; Gunicorn não confia no proxy (socket Unix,
  proxy em outro IP); uso de `runserver`; cookies bloqueados pelo navegador.
- Correção: seção 14.2/14.4. Em proxy externo (variante B), o cabeçalho tem de chegar até
  o Gunicorn vindo de `127.0.0.1`.

**Toda página responde 404**
- Diagnóstico: `grep ^TRAJETORIA_DEMONSTRACAO= /etc/trajetoria/trajetoria.env`.
- Causa: modo fechado. **É o comportamento esperado** sem `TRAJETORIA_DEMONSTRACAO=1`.
- Correção: nenhuma, salvo se esta instância for de demonstração.

**Envio do `/acesso/` (POST) responde 503 "Não foi possível verificar agora"**
- Observação: o GET da página continua 200; só o envio revela o problema.
- Causa: chaves de acesso ausentes, curtas (< 32), repetidas ou iguais à `SECRET_KEY`.
- Correção: seção 10.2 e restart.

**Todo acesso dá "Não foi possível confirmar os dados"**
- Causa: chaves do serviço diferentes das usadas no `preparar_demonstracao`.
- Correção: num banco fictício, recrie o banco e rode o preparo com as chaves atuais.

**"Aguarde alguns instantes…" (429) para todos ao mesmo tempo**
- Causa: a limitação por origem usa `REMOTE_ADDR`, que atrás do Nginx é sempre
  `127.0.0.1`; 30 tentativas em 15 min, somadas de todos os usuários, bloqueiam todos
  (lacuna da seção 22).
- Correção imediata: `sudo systemctl restart trajetoria` (zera o cache em memória).

**Serviço não inicia**
- Diagnóstico: `sudo systemctl status trajetoria`; `sudo journalctl -u trajetoria -b -n 80`;
  `sudo systemd-analyze verify /etc/systemd/system/trajetoria.service`.
- Causas: `ValueError` de `TRAJETORIA_VIDEO_RETENCAO_MINUTOS`; variável numérica inválida
  (`TRAJETORIA_SESSAO_*`); arquivo de ambiente com aspas ou espaços; Gunicorn ausente do
  venv; porta 8000 ocupada.
- Correção: conforme a mensagem; teste a configuração com `sudo trajetoria-manage check`.

**Disco cheio**
- Diagnóstico: `df -h`; `sudo du -xh --max-depth=2 /var | sort -h | tail`;
  `journalctl --disk-usage`; `sudo du -sh /var/backups/trajetoria`.
- Causas: backups locais acumulados (timer de retenção desativado), journal sem limite,
  logs do Nginx, banco crescendo.
- Correção: seção 18.2; confirme a cópia externa antes de apagar qualquer backup;
  `sudo journalctl --vacuum-size=500M`. O PostgreSQL para de aceitar escrita com o disco
  cheio: libere espaço antes de reiniciar serviços.

**Vídeo sempre "Não foi possível preparar o vídeo agora"**
- Diagnóstico: `systemctl is-active trajetoria-videos`;
  `sudo journalctl -u trajetoria-videos -n 50` (motivos: `navegador_ausente`,
  `tempo_esgotado`, `codigo_1`…); o comando `ldd` da seção 13.3.
- Causas: processador parado (após 10 min o pedido vira `sem_processador`); navegador não
  provisionado; biblioteca do Chrome faltando; `.bundle` sem permissão de escrita.
- Correção: seção 13.3; teste um ciclo com
  `sudo trajetoria-manage processar_videos --uma-vez`.

---

## 22. Lacunas e decisões pendentes

Classificação: **BLOQUEANTE** impede uma implantação real com egressos; **IMPORTANTE**
afeta segurança, operação ou reprodutibilidade; **MELHORIA** reduz atrito.

| # | Lacuna | Classe | Situação |
|---|---|---|---|
| L1 | **Não existe modo produtivo**: sem demonstração tudo é 404; com demonstração, só dados fictícios, fonte acadêmica simulada e operadores fictícios sem autenticação (DP-1001) | **BLOQUEANTE** | Depende de features futuras |
| L2 | Hospedar o **modo de demonstração** numa VM do datacenter não está previsto nas specs (descrito como "local") | **BLOQUEANTE** para a instância de demonstração | Decisão da coordenação do projeto, com restrição de rede |
| L3 | Limitação de tentativas usa `REMOTE_ADDR`; atrás do Nginx, todos compartilham a mesma origem | **BLOQUEANTE** para exposição a egressos; IMPORTANTE na demonstração restrita | Requer mudança de código (ler o IP real de um proxy confiável) |
| L4 | Cache `LocMemCache` por processo (DP-1803): obriga 1 processo Gunicorn | IMPORTANTE | Contornado com `--workers 1 --threads 4` |
| L5 | Servidor de aplicação (Gunicorn) fora do `pyproject.toml`/`uv.lock` | IMPORTANTE | Contornado com `uv pip install gunicorn==23.0.0` a cada deploy; recomendação: extra `producao` travado no lock |
| L6 | `SECURE_PROXY_SSL_HEADER`, `CSRF_TRUSTED_ORIGINS`, `CSRF_COOKIE_SECURE`, HSTS e `SECURE_SSL_REDIRECT` não configuráveis | IMPORTANTE | Coberto por Gunicorn + Nginx (seção 14); frágil se a topologia mudar |
| L7 | `DJANGO_SECRET_KEY` tem padrão inseguro silencioso | IMPORTANTE | Verificação manual na seção 16.1 |
| L8 | Sem tags nem processo de release | IMPORTANTE | Recomendação da seção 6 |
| L9 | Política de backup, retenção, cifragem e custódia/rotação de chaves (DP-1301) não definidas | IMPORTANTE | Recomendações das seções 10.4 e 17 |
| L10 | Licenças Remotion e H.264 (DP-2201) | **BLOQUEANTE** para o vídeo fora da demonstração | Vídeo opcional e só em demonstração |
| L11 | Exportações (013) e dataset analítico (012) sem comando nem tela | IMPORTANTE (operação futura) | Só via `manage.py shell` |
| L12 | Sem endpoint de health check | MELHORIA | Monitorar `/acesso/` (seção 18.3) |
| L13 | `TRAJETORIA_CHAVE_PSEUDONIMIZACAO` e as variáveis do vídeo estavam ausentes do `.env.example` | MELHORIA | Corrigido junto com este guia |
| L14 | Comunicação simulada (016) inutilizável fora de `127.0.0.1:8000` + Mailpit | MELHORIA (esperado) | Deixar `EMAIL_BACKEND` vazio |
| L15 | Procedimento validado em macOS, não numa VM Ubuntu 24.04 real (utilitários, unidades systemd, Nginx, bibliotecas do Chrome) | IMPORTANTE | Validar na primeira instalação e corrigir este guia |

---

## 23. Registro de validação deste guia

Validado em 2026-10-05, em macOS arm64 (uv 0.11.21, Python 3.13.14, Django 5.2.17,
PostgreSQL 16.14), sobre `main` em `04efabd`:

- instalação "estilo produção" numa cópia limpa do repositório (`git archive`):
  `uv python install 3.13` com `UV_PYTHON_INSTALL_DIR` próprio, `uv sync --locked` sem
  extras (sem pytest no ambiente), Gunicorn 23.0.0 instalado depois do `sync`;
- arquivo de ambiente no formato `KEY=valor` carregado por `sh` (`set -a`), `check --deploy`
  com exatamente W004, W008 e W016, `migrate --check`;
- modo fechado servido pelo Gunicorn: `/`, `/acesso/`, `/minha-trajetoria/` → 404;
- modo de demonstração pelo Gunicorn com `X-Forwarded-Proto: https`: login → 303; o mesmo
  POST pelo `runserver` → 403 (CSRF); Host não permitido → 400;
- `pg_dump --format=custom` e `pg_restore --no-owner --role=<papel>` num banco novo
  criado com `--locale-provider=icu --icu-locale=pt-BR`: 25 tabelas, contagens iguais;
- suíte completa (2797 passed, 3 skipped sem renderizador, 2 deselected de volume) e
  testes de vídeo com o renderizador real (`CI=true`, 169 passed).

**Não validado** (motivo: nenhuma VM Ubuntu disponível nesta revisão; como validar: na
primeira instalação, seguindo a seção 15 e registrando aqui as correções):

- os comandos específicos do Ubuntu 24.04: `adduser`, `ufw`, `runuser` nos utilitários,
  peer authentication, unidades e timers do systemd com as restrições de sandbox, Nginx
  1.24 (`proxy_cookie_flags`, `return 444`), lista de bibliotecas do Chrome Headless Shell;
- o processador de vídeos sob `ProtectSystem=strict` e `IPAddressDeny` (comando de teste
  na seção 13.3);
- o instalador do uv com `UV_INSTALL_DIR`/`UV_NO_MODIFY_PATH` e o Node por tarball oficial.
