# Operação do Trajetória Ifes na VM

Runbook do administrador para uma VM já instalada conforme
[datacenter-ubuntu.md](datacenter-ubuntu.md). Não repete a instalação; remete a ela quando
necessário.

> **Lembrete.** No estado atual, a aplicação só tem o **modo fechado** (toda página 404) e
> o **modo de demonstração** (dados fictícios). Veja a
> [seção 0 do guia de implantação](datacenter-ubuntu.md#0-leia-antes-o-que-esta-instalação-entrega-hoje).

## Referência rápida

| Item | Valor |
|---|---|
| Código | `/opt/trajetoria/app` (checkout de uma tag) |
| Configuração e segredos | `/etc/trajetoria/trajetoria.env` (`root:trajetoria 0640`) |
| Serviço da aplicação | `trajetoria.service` (Gunicorn em `127.0.0.1:8000`) |
| Processador de vídeos (opcional) | `trajetoria-videos.service` |
| Timers | `trajetoria-backup.timer` (02:30), `trajetoria-limpar-sessoes.timer` (03:30) |
| Banco | PostgreSQL 16 local, banco `trajetoria`, papel `trajetoria` (peer) |
| Backups locais | `/var/backups/trajetoria/` (14 dias) |
| Logs | `journalctl -u trajetoria`, `/var/log/nginx/`, `/var/log/postgresql/` |
| `manage.py` | `sudo trajetoria-manage <comando>` (roda como `trajetoria`, com o ambiente) |
| uv | `sudo trajetoria-uv <comando>` |

Nunca rode `python manage.py runserver` na VM. Nunca rode `manage.py` como `root` sem o
`trajetoria-manage`.

---

## 1. Iniciar, parar, reiniciar, status

```bash
sudo systemctl start trajetoria
```

```bash
sudo systemctl stop trajetoria
```

```bash
sudo systemctl restart trajetoria
```

Recarregar o código sem derrubar conexões em andamento (o Gunicorn troca o worker):

```bash
sudo systemctl reload trajetoria
```

```bash
systemctl status trajetoria --no-pager
```

Todos os componentes de uma vez:

```bash
systemctl is-active postgresql nginx trajetoria trajetoria-videos trajetoria-backup.timer trajetoria-limpar-sessoes.timer
```

(`trajetoria-videos` aparece como `inactive` se a seção 13.3 não foi aplicada.)

Quando reiniciar a aplicação:

- depois de alterar `/etc/trajetoria/trajetoria.env` (o processo só lê o ambiente ao
  iniciar);
- depois de instalar ou remover o renderizador de vídeo;
- para zerar a limitação de tentativas de acesso (cache em memória do processo).

---

## 2. Logs

```bash
sudo journalctl -u trajetoria -f
```

```bash
sudo journalctl -u trajetoria --since today -p warning --no-pager
```

```bash
sudo journalctl -u trajetoria -b --no-pager | tail -n 100
```

```bash
sudo journalctl -u trajetoria-videos --since "1 hour ago" --no-pager
```

```bash
sudo journalctl -u trajetoria-backup -u trajetoria-limpar-sessoes --since "2 days ago" --no-pager
```

```bash
sudo tail -f /var/log/nginx/access.log /var/log/nginx/error.log
```

```bash
sudo tail -n 100 /var/log/postgresql/postgresql-16-main.log
```

Os tracebacks de erro 500 só aparecem no journal (`django.request`). Os logs da aplicação
não contêm CPF, datas de nascimento nem conteúdo do card; se aparecer algo assim, trate
como incidente (seção 15.4).

---

## 3. Versão instalada

```bash
sudo git -C /opt/trajetoria/app describe --tags --always
```

```bash
sudo git -C /opt/trajetoria/app log -1 --format='%H %cI %s'
```

```bash
sudo git -C /opt/trajetoria/app status --short
```

O último comando deve sair vazio: qualquer arquivo modificado no servidor é uma alteração
fora do processo de release.

Versões das dependências em uso:

```bash
/opt/trajetoria/app/.venv/bin/python --version && /opt/trajetoria/app/.venv/bin/python -c "import django; print('Django', django.get_version())" && /opt/trajetoria/app/.venv/bin/gunicorn --version
```

---

## 4. Banco de dados

Disponibilidade:

```bash
sudo -u postgres pg_isready
```

Conexão como a aplicação:

```bash
sudo -u trajetoria psql -d trajetoria -Atc "select current_user, now();"
```

Pela própria aplicação (prova settings + driver + banco):

```bash
sudo trajetoria-manage shell -c "from django.db import connection; connection.ensure_connection(); print('ok', connection.pg_version)"
```

Tamanho:

```bash
sudo -u postgres psql -Atc "select pg_size_pretty(pg_database_size('trajetoria'));"
```

Conexões e consultas longas:

```bash
sudo -u postgres psql -d trajetoria -c "select pid, usename, state, now() - query_start as duracao, left(query, 60) from pg_stat_activity where datname = 'trajetoria' order by duracao desc nulls last;"
```

Tabelas técnicas que crescem e são limpas automaticamente:

```bash
sudo -u trajetoria psql -d trajetoria -Atc "select 'sessoes', count(*) from django_session union all select 'videos', count(*) from video_geracaodevideo;"
```

---

## 5. Migrations

```bash
sudo trajetoria-manage migrate --check
```

Código 0 e nenhuma saída: nada pendente.

```bash
sudo trajetoria-manage showmigrations
```

Aplicar (só dentro do procedimento de atualização, depois do backup):

```bash
sudo trajetoria-manage migrate --plan
```

```bash
sudo trajetoria-manage migrate
```

---

## 6. Backup

Disparar o backup agora (o mesmo do timer):

```bash
sudo systemctl start trajetoria-backup.service
```

```bash
sudo systemctl status trajetoria-backup.service --no-pager
```

Último arquivo e seu conteúdo:

```bash
sudo ls -lht /var/backups/trajetoria | head -5
```

```bash
sudo -u postgres sh -c 'pg_restore --list "$(ls -1t /var/backups/trajetoria/*.dump | head -1)" | grep -c "TABLE DATA"'
```

Próximas execuções dos timers:

```bash
systemctl list-timers 'trajetoria-*' --no-pager
```

Confirme também, no sistema institucional, que a **cópia externa** do dia existe. O
arquivo `/etc/trajetoria/trajetoria.env` tem custódia própria (cofre de segredos), separada
dos dumps.

---

## 7. Restauração

Procedimento completo, com troca segura de bancos:
[guia de implantação, seção 17.4](datacenter-ubuntu.md#174-restauração). Resumo dos
comandos:

```bash
sudo systemctl stop trajetoria
```

Com o processador de vídeo:

```bash
sudo systemctl stop trajetoria-videos
```

```bash
sudo -u postgres createdb --owner=trajetoria --encoding=UTF8 --template=template0 --locale=C.UTF-8 --locale-provider=icu --icu-locale=pt-BR trajetoria_restaurado
```

```bash
sudo -u postgres pg_restore --dbname=trajetoria_restaurado --no-owner --role=trajetoria --exit-on-error /var/backups/trajetoria/<ARQUIVO>.dump
```

```bash
sudo systemctl stop trajetoria-backup.timer trajetoria-limpar-sessoes.timer
```

```bash
sudo -u postgres psql -Atc "select count(*) from pg_stat_activity where datname in ('trajetoria', 'trajetoria_restaurado');"
```

Esperado: `0` (a troca falha com conexões abertas).

```bash
sudo -u postgres psql -c "alter database trajetoria rename to trajetoria_antes_restauracao;" -c "alter database trajetoria_restaurado rename to trajetoria;"
```

```bash
sudo trajetoria-manage migrate --check && sudo systemctl start trajetoria
```

Com o processador de vídeo:

```bash
sudo systemctl start trajetoria-videos
```

```bash
sudo systemctl start trajetoria-backup.timer trajetoria-limpar-sessoes.timer
```

Depois: smoke test (seção 9). Restaurar um dump exige as **mesmas chaves** que estavam em
vigor quando ele foi gerado.

Teste mensal de restauração: [seção 17.5](datacenter-ubuntu.md#175-teste-periódico-de-restauração).

---

## 8. Atualizar a aplicação

Runbook completo: [guia de implantação, seção 19](datacenter-ubuntu.md#19-procedimento-de-deploy-e-atualização).
Sequência resumida:

```bash
sudo git -C /opt/trajetoria/app describe --tags --always | sudo tee /opt/trajetoria/release-anterior
```

```bash
sudo git -C /opt/trajetoria/app fetch --tags origin
```

```bash
sudo git -C /opt/trajetoria/app diff --stat HEAD <NOVA_TAG> -- '*/migrations/*' pyproject.toml uv.lock config/ video/package-lock.json
```

```bash
sudo systemctl start trajetoria-backup.service
```

```bash
sudo systemctl stop trajetoria
```

Com o processador de vídeo:

```bash
sudo systemctl stop trajetoria-videos
```

```bash
sudo git -C /opt/trajetoria/app checkout --detach <NOVA_TAG>
```

```bash
sudo trajetoria-uv sync --locked && sudo trajetoria-uv pip install --python /opt/trajetoria/app/.venv/bin/python "gunicorn==23.0.0"
```

Com vídeo, também:

```bash
sudo env PATH=/opt/trajetoria/node/bin:/usr/bin:/bin npm ci --prefix /opt/trajetoria/app/video && sudo env PATH=/opt/trajetoria/node/bin:/usr/bin:/bin npm --prefix /opt/trajetoria/app/video run garantir-navegador && sudo install -d -o trajetoria -g trajetoria -m 0750 /opt/trajetoria/app/video/.bundle /opt/trajetoria/app/video/node_modules/.cache
```

```bash
sudo trajetoria-manage check --deploy && sudo trajetoria-manage migrate && sudo trajetoria-manage migrate --check
```

```bash
sudo systemctl start trajetoria
```

Com o processador de vídeo:

```bash
sudo systemctl start trajetoria-videos
```

Não use `git pull` no servidor. Não há `collectstatic` neste projeto.

---

## 9. Validar depois de implantar ou restaurar

Lista completa: [smoke test](datacenter-ubuntu.md#20-smoke-test-pós-deploy). Mínimo:

```bash
systemctl is-active trajetoria
```

```bash
sudo trajetoria-manage migrate --check && echo migrations-ok
```

```bash
curl -s -o /dev/null -w '%{http_code}\n' https://<DOMAIN>/acesso/
```

Esperado: `404` em modo fechado; `200` em modo de demonstração.

```bash
sudo journalctl -u trajetoria --since "10 min ago" -p err --no-pager
```

Esperado: vazio. Em modo de demonstração, entre com Ana Exemplo (`000.000.001-91`,
`12/04/1998`) e confira que chega a `/formacoes/`.

---

## 10. Rollback

Sem migrations novas:

```bash
sudo systemctl stop trajetoria
```

Com o processador de vídeo:

```bash
sudo systemctl stop trajetoria-videos
```

```bash
sudo git -C /opt/trajetoria/app checkout --detach "$(sudo cat /opt/trajetoria/release-anterior)"
```

```bash
sudo trajetoria-uv sync --locked && sudo trajetoria-uv pip install --python /opt/trajetoria/app/.venv/bin/python "gunicorn==23.0.0"
```

Com vídeo, também:

```bash
sudo env PATH=/opt/trajetoria/node/bin:/usr/bin:/bin npm ci --prefix /opt/trajetoria/app/video && sudo env PATH=/opt/trajetoria/node/bin:/usr/bin:/bin npm --prefix /opt/trajetoria/app/video run garantir-navegador && sudo install -d -o trajetoria -g trajetoria -m 0750 /opt/trajetoria/app/video/.bundle /opt/trajetoria/app/video/node_modules/.cache
```

```bash
sudo systemctl start trajetoria
```

Com o processador de vídeo:

```bash
sudo systemctl start trajetoria-videos
```

Com migrations novas já aplicadas: **não existe rollback automático seguro**. Prefira
restaurar o backup feito imediatamente antes da atualização (seção 7) e então voltar o
código. Reverter migrations com `migrate <app> <anterior>` só depois de revisar cada
operação inversa ([seção 19.3](datacenter-ubuntu.md#193-rollback)).

---

## 11. Certificado TLS

Ver validade:

```bash
sudo openssl x509 -noout -subject -enddate -in /etc/ssl/trajetoria/fullchain.pem
```

Trocar (certificado renovado pela instituição):

```bash
sudo install -o root -g root -m 0644 <NOVO_CERTIFICADO_COM_CADEIA> /etc/ssl/trajetoria/fullchain.pem
```

```bash
sudo install -o root -g root -m 0600 <NOVA_CHAVE_PRIVADA> /etc/ssl/trajetoria/privkey.pem
```

Conferir que a chave corresponde ao certificado (as duas linhas devem ser iguais):

```bash
sudo openssl x509 -noout -pubkey -in /etc/ssl/trajetoria/fullchain.pem | sha256sum && sudo openssl pkey -pubout -in /etc/ssl/trajetoria/privkey.pem | sha256sum
```

```bash
sudo nginx -t && sudo systemctl reload nginx
```

```bash
echo | openssl s_client -connect <DOMAIN>:443 -servername <DOMAIN> 2>/dev/null | openssl x509 -noout -enddate
```

Na variante B (TLS no proxy institucional), a troca é feita pela equipe do proxy.

---

## 12. Espaço em disco

```bash
df -h / /var
```

```bash
sudo du -xh --max-depth=2 /var 2>/dev/null | sort -h | tail -n 15
```

```bash
journalctl --disk-usage
```

```bash
sudo du -sh /var/backups/trajetoria /var/log/nginx /var/lib/postgresql /opt/trajetoria
```

Liberar espaço, nesta ordem e com cuidado:

1. Journal: `sudo journalctl --vacuum-size=500M`.
2. Backups locais antigos: só depois de confirmar que existem na cópia externa:
   `sudo find /var/backups/trajetoria -name 'trajetoria-*.dump' -mtime +7 -delete`.
3. Cache de pacotes: `sudo apt-get clean`.
4. Cache do uv (refeito no próximo deploy): `sudo trajetoria-uv cache clean`.

Nunca apague arquivos dentro de `/var/lib/postgresql`. Com o disco cheio, o PostgreSQL deixa
de aceitar escrita; libere espaço antes de reiniciar serviços.

---

## 13. Recuperação após reboot

Os serviços sobem sozinhos (`enabled`). Depois de um reboot, confira:

```bash
systemctl is-enabled postgresql nginx trajetoria trajetoria-backup.timer trajetoria-limpar-sessoes.timer
```

```bash
systemctl --failed --no-pager
```

```bash
systemctl is-active postgresql nginx trajetoria
```

Se `trajetoria` falhou por ter subido antes do banco ficar pronto, ele tenta de novo
sozinho (`Restart=on-failure`). Persistindo:

```bash
sudo systemctl restart postgresql && sudo systemctl restart trajetoria
```

Efeitos esperados de um reboot: sessões continuam (estão no banco); a limitação de
tentativas é zerada (está em memória); pedidos de vídeo em andamento são marcados como
falha pela limpeza e podem ser pedidos de novo.

---

## 14. Rotinas

| Frequência | Tarefa | Comando ou referência |
|---|---|---|
| Diária | Serviços ativos e sem falhas | `systemctl --failed`; seção 1 |
| Diária | Erros 5xx e erros no journal | `sudo journalctl -u trajetoria --since yesterday -p err` |
| Diária | Backup gerado e copiado para fora | Seção 6 |
| Semanal | Disco, memória, tamanho do banco | Seções 4 e 12; `free -m` |
| Semanal | Atualizações do sistema aplicadas | `sudo apt list --upgradable`; reboot se `/var/run/reboot-required` existir |
| Mensal | Teste de restauração | Seção 7 |
| Mensal | Validade do certificado | Seção 11 |
| A cada release | Atualização e smoke test | Seções 8 e 9 |
| Com vídeo, a cada atualização do Remotion | Rever o Chrome provisionado e suas bibliotecas | [Seção 13.3](datacenter-ubuntu.md#133-opcional-processador-de-vídeos) |

---

## 15. Incidentes

Em qualquer incidente: registre o horário, o sintoma e cada comando executado. Não altere
código no servidor.

### 15.1 Aplicação fora do ar (502/504 ou sem resposta)

```bash
systemctl status trajetoria nginx postgresql --no-pager
```

```bash
sudo journalctl -u trajetoria -n 80 --no-pager
```

```bash
curl -s -o /dev/null -w '%{http_code}\n' -H 'Host: <DOMAIN>' http://127.0.0.1:8000/acesso/
```

- Gunicorn parado ou em loop de reinício → leia o erro, corrija (ambiente, venv,
  Gunicorn ausente) e `sudo systemctl restart trajetoria`.
- Gunicorn responde localmente mas o domínio não → Nginx, TLS, firewall ou proxy
  institucional: `sudo nginx -t`, `sudo ufw status`.
- Mais causas: [troubleshooting](datacenter-ubuntu.md#21-troubleshooting).

### 15.2 Banco indisponível

```bash
sudo systemctl status postgresql@16-main --no-pager
```

```bash
sudo tail -n 80 /var/log/postgresql/postgresql-16-main.log
```

```bash
df -h /var/lib/postgresql
```

Disco cheio → seção 12. Corrupção ou perda → restauração (seção 7), com a release
compatível com o dump.

### 15.3 Todos recebem "Aguarde alguns instantes…" (429)

A limitação de tentativas vê todo o tráfego como vindo de `127.0.0.1` (lacuna L3 do guia
de implantação). Medida imediata, que zera os contadores:

```bash
sudo systemctl restart trajetoria
```

Registre a ocorrência: ela reforça a necessidade da correção no código antes de qualquer
exposição a egressos.

### 15.4 Suspeita de vazamento ou de acesso indevido

1. Preserve evidências antes de mexer: copie os logs relevantes para um local protegido.

```bash
sudo journalctl -u trajetoria --since "<INICIO>" --no-pager | sudo tee /root/incidente-trajetoria-$(date +%Y%m%d%H%M).log > /dev/null
```

```bash
sudo cp /var/log/nginx/access.log* /root/
```

2. Restrinja o acesso, se necessário: em modo de demonstração, coloque o modo fechado
   (seção 16) ou limite o Nginx a uma origem conhecida.
3. Acione os responsáveis institucionais por segurança da informação e por proteção de
   dados. As decisões de comunicação do incidente não cabem à operação técnica.
4. Se uma chave pode ter vazado, **não** a troque sem avaliar o efeito (tabela da
   [seção 10.4](datacenter-ubuntu.md#104-custódia-dos-segredos)):
   trocar `TRAJETORIA_CHAVE_CONSULTA_ACERVO` torna ilegíveis os dados já cifrados.

### 15.5 Vídeo não é gerado (modo de demonstração com vídeo)

```bash
systemctl status trajetoria-videos --no-pager
```

```bash
sudo journalctl -u trajetoria-videos -n 50 --no-pager
```

```bash
sudo trajetoria-manage processar_videos --uma-vez
```

Motivos registrados: `navegador_ausente`, `tempo_esgotado`, `indisponivel`, `codigo_<n>`.
Sem o processador, a página continua funcionando, só sem o vídeo.

---

## 16. Trocar o modo da instância

Trocar o modo muda o que a instância expõe. Faça só com autorização registrada.

**Demonstração → fechado** (seguro a qualquer momento):

```bash
sudo sed -i 's/^TRAJETORIA_DEMONSTRACAO=.*/TRAJETORIA_DEMONSTRACAO=/' /etc/trajetoria/trajetoria.env && sudo systemctl restart trajetoria
```

```bash
curl -s -o /dev/null -w '%{http_code}\n' https://<DOMAIN>/acesso/
```

Esperado: `404`.

**Fechado → demonstração** (só com banco exclusivamente fictício e autorização registrada).
Restrinja a rede **antes** de ligar o modo:

1. Firewall só para a rede institucional:

```bash
sudo ufw delete allow 'Nginx Full'; sudo ufw allow from <REDE_INSTITUCIONAL_CIDR> to any app 'Nginx Full'
```

2. Descomente `allow <REDE_INSTITUCIONAL_CIDR>;` e `deny all;` em
   `/etc/nginx/sites-available/trajetoria` e recarregue:

```bash
sudo nginx -t && sudo systemctl reload nginx
```

3. Ligue o modo, prepare o cenário fictício e reinicie:

```bash
sudo sed -i 's/^TRAJETORIA_DEMONSTRACAO=.*/TRAJETORIA_DEMONSTRACAO=1/' /etc/trajetoria/trajetoria.env
```

```bash
sudo trajetoria-manage preparar_demonstracao
```

```bash
sudo systemctl restart trajetoria
```

4. De fora da rede institucional, o domínio deve recusar o acesso (403 do Nginx ou sem
   conexão); de dentro, `/acesso/` deve responder 200.
