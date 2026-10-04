# Quickstart — validar a Feature 018

Roteiro de validação. Ver [plan.md](plan.md), [rotas](contracts/rotas.md),
[verificação](contracts/verificacao.md), [material](contracts/material.md) e
[data-model](data-model.md). Só dados fictícios.

## Pré-requisitos

Python 3.13, uv, PostgreSQL local e o banco fictício `trajetoria_demo`, conforme
[001/quickstart](../001-nucleo-academico-fonte-simulada/quickstart.md). Os comandos rodam
na raiz do repositório.

**Chaves de acesso.** Sem valor padrão. São dois valores distintos, com pelo menos 32
caracteres, diferentes da `DJANGO_SECRET_KEY` e da chave de pseudonimização. São gerados
localmente e nunca versionados:

```bash
export TRAJETORIA_CHAVE_ACESSO_LOCALIZACAO="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
```

```bash
export TRAJETORIA_CHAVE_ACESSO_VERIFICACAO="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
```

**Banco e servidor.** Use um banco fictício novo e isolado: o material é derivado na
incorporação com as chaves atuais. Preserve qualquer banco existente; o preparo é
idempotente e também pode derivar o material de um cenário anterior após as migrações.

```bash
createdb trajetoria_demo_018
```

```bash
uv sync --extra dev && PGDATABASE=trajetoria_demo_018 uv run python manage.py migrate
```

```bash
PGDATABASE=trajetoria_demo_018 TRAJETORIA_DEMONSTRACAO=1 uv run python manage.py preparar_demonstracao
```

```bash
PGDATABASE=trajetoria_demo_018 TRAJETORIA_DEMONSTRACAO=1 uv run python manage.py runserver 127.0.0.1:8000
```

As chaves usadas no preparo e no servidor precisam ser **as mesmas**. Com chaves
diferentes, todo acesso resulta em "não foi possível confirmar".

## Verificação automática

```bash
uv run pytest tests/acesso
```

```bash
uv run pytest
```

```bash
uv run ruff check .
```

```bash
PGDATABASE=trajetoria_demo_018 uv run python manage.py makemigrations --check --dry-run
```

**Esperado:**

- **Testes.** Toda a suíte passa. As regras e asserções da jornada de 005 a 008
  permanecem; os auxiliares, rotas de entrada e verificações técnicas são adaptados à
  confirmação e à sessão do framework.
- **Migrações.** Só `acesso/0001` e a migração de sessões do framework.

## Verificação manual

Abra `http://127.0.0.1:8000/` em viewport de 375 px e repita os passos 1, 5 e 7 a
320 px (FR-071). Os dados vêm de research R13 e do
painel da entrada.

1. **Entrada.** `/` leva a `/acesso/`. Confira o título, os dois campos com rótulos e o
   painel "Dados fictícios para demonstração". Nenhum nome ou formação aparece fora do
   painel.
2. **Confirmação, uma formação.** Ana: `000.000.001-91`, `12/04/1998`. Você vai para
   `/formacoes/`. O cabeçalho mostra Ana e "Sair". A URL não contém CPF nem data.
3. **Formatos aceitos.** Repita com `00000000191` e `12041998`. O resultado é o mesmo.
4. **Várias formações.** Diego: `000.000.003-53`, `08/02/1994`. Aparecem as três
   formações, com a escolha da 007.
5. **Não confirmação idêntica.** Envie cada caso e compare o texto e o status (ferramentas
   do navegador):
   - Ana com `13/04/1998` (data errada);
   - `000.000.009-49`, CPF válido e inexistente (calcule outro, se preferir);
   - Elisa, sem CPF, com qualquer CPF válido e `30/06/2001`;
   - SIM-P-0009: `000.000.007-87` com qualquer data (sem data na fonte);
   - Carla: `000.000.008-68`, `05/05/1992` (colisão);
   - João: `000.000.004-34`, `14/03/2003` (não incorporado).

   Todos mostram "Não foi possível confirmar os dados informados." e o formulário
   preenchido, com status 200. Nenhuma tabela muda.
6. **Formato inválido.** `123.456.789-00` e `31/02/2000`: erro no campo, sem a mensagem
   genérica.
7. **Limitação.** Quatro falhas seguidas com o mesmo CPF dão, na quinta tentativa
   imediata, "Aguarde alguns instantes…" com status 429. Espere cerca de 5 s e confirme
   com os dados corretos: funciona. Repita com um CPF inexistente: o comportamento é
   idêntico.
8. **Sessão.** Clique em "Sair": a jornada volta a `/acesso/`. Confirme Ana e depois
   Diego na mesma aba: só Diego fica em uso. Feche e reabra o navegador: a sessão
   acabou. Para inatividade, rode o servidor com
   `TRAJETORIA_SESSAO_INATIVIDADE=1` (minuto), espere e recarregue `/formacoes/`.
9. **Jornada intacta.** Com Ana, inicie, salve uma Seção, saia, entre de novo e retome:
   as respostas salvas aparecem. Conclua: a formação aparece como "pesquisa já
   respondida", sem respostas.
10. **Convite (016).** Com o operador A, prepare a comunicação simulada e confira na
    prévia que a URL é `http://127.0.0.1:8000/acesso/`. Abra o link: formulário vazio.
11. **Chaves ausentes.** Rode o servidor sem as variáveis e envie qualquer dado:
    "Não foi possível verificar agora…" (503). Rode o preparo sem elas num banco novo:
    recusa com orientação, sem gravar nada.
12. **Vazamento.** Procure os CPFs e as datas usados nos passos anteriores no console do
    servidor e no banco: zero ocorrências, inclusive em `django_session`, onde só há UUID e
    instantes. Exemplo de verificação no banco:

    ```bash
    PGDATABASE=trajetoria_demo_018 psql -c "select count(*) from acesso_materialdeverificacao where identificador_cpf like '%00000000191%'"
    ```

13. **Acessibilidade.** Navegue só pelo teclado. Com erros, o foco vai para o resumo; o
    leitor de tela anuncia os erros dos campos. Ampliação de 200% sem rolagem horizontal.

## Rotina operacional

Sessões expiradas permanecem em `django_session` até a limpeza do framework:

```bash
PGDATABASE=trajetoria_demo_018 uv run python manage.py clearsessions
```

## Evidências de execução — 2026-10-04

Implementação validada no worktree `auditoria-identidade-acesso-10c0b0`, branch
`claude/018-identificacao-acesso-egresso`, a partir de `05d5469`.

**Verificações automáticas.** `uv run pytest`: **2.103 passaram**, em 218,46 s;
o teste de volume permaneceu fora da seleção padrão configurada no projeto.
`tests/acesso`: **72 passaram**. Ruff passou; os arquivos Python novos da 018 estavam
formatados; Django sem problemas; nenhuma migração pendente; `git diff --check` limpo.
Não houve alteração dos modelos acadêmicos, de participação ou de campanha, nem novas
dependências. As únicas migrações novas são `acesso/0001` e `sessions/0001` do framework.
A varredura SC-005 cobriu banco, sessões decodificadas, cache, logs DEBUG, cookies,
redirecionamentos e comunicação simulada, sem CPF ou nascimento em claro.

**Ambiente manual.** Para preservar os bancos existentes, foram criados os bancos
fictícios isolados `trajetoria018_validacao_20261004` e
`trajetoria018_sem_chaves_20261004`, ambos migrados do zero. O primeiro foi preparado
com duas chaves geradas no processo, não versionadas: **9 Pessoas, 13 Conclusões,
8 materiais e 7 verificadores completos**. Uma varredura adicional das tabelas,
sessões decodificadas e log desse servidor encontrou **zero valores em claro**.
O segundo começou sem chaves: o preparo recusou com a orientação contratada e deixou
**zero Pessoas, materiais ou campanhas**. Depois foi preparado com novas chaves para
verificar uma sessão com inatividade de um minuto. Os servidores escutaram apenas em
loopback, nas portas 8000 e 8001.

| Passos | Evidência observada |
| --- | --- |
| 1–3 | A raiz abriu o formulário vazio; Ana confirmou tanto com pontuação e barras quanto com os dois valores sem formatação; destino `/formacoes/` e nome na faixa. |
| 4 | A confirmação de Diego substituiu Ana; duas formações tinham pesquisa disponível e a terceira apareceu em outras formações, segundo a jornada existente. |
| 5–6 | Data errada, CPF inexistente, ausência de CPF/material completo, colisão e pessoa não incorporada produziram o mesmo aviso; formato inválido apresentou os erros dos campos e colocou o foco no resumo. |
| 7 | Falhas sucessivas chegaram ao aviso de espera; após o prazo, Ana confirmou normalmente. Status 429, `Retry-After`, progressão 5/15/45/135/300 s e igualdade com CPF inexistente foram verificados pelos testes HTTP. |
| 8 | Sair voltou ao formulário; a troca de pessoa foi observada; no servidor com inatividade de um minuto, recarregar as formações após o prazo levou a `/acesso/`. A expiração de oito horas, revogação do material e cookie sem `Expires`/`Max-Age` foram verificados automaticamente, sem encerrar o navegador do usuário. |
| 9 | Ana salvou a resposta “Não” em Termos e condições, saiu, confirmou novamente, retomou e revisou a opção marcada; concluiu e depois viu apenas “Pesquisa já respondida”, sem respostas. A jornada completa com aceite e múltiplas seções passou na regressão E2E. |
| 10 | O operador A abriu a prévia: texto e HTML tinham a URL neutra `http://127.0.0.1:8000/acesso/`; abrir esse destino mostrou o formulário vazio. Nenhuma mensagem foi enviada pelo navegador. O operador anterior B foi restaurado. |
| 11–12 | Sem chaves, o formulário mostrou “Não foi possível verificar agora. Tente novamente em instantes.”; HTTP 503 provado nos testes e no log do servidor; preparo recusado sem escrita; varreduras sem vazamento. |
| 13 | Teclado passou do link de conferência ao CPF; foco automático no aviso e no resumo; rótulos e descrições presentes na árvore de acessibilidade. Entrada, erros, não confirmação e espera tiveram `innerWidth == scrollWidth == 320`; a entrada passou também em 375 px e em zoom real de 200% (756 px disponíveis, sem overflow). Sem JavaScript novo; a associação dos erros foi verificada estruturalmente, sem alegar uma sessão de leitor de tela. |

[Evidência visual da entrada a 320 px](../../docs/auditorias/evidencias-018/acesso-320.png).
Overrides de viewport e zoom foram restaurados; os processos de validação foram
encerrados. Os bancos fictícios isolados foram preservados para inspeção; as chaves
existiam apenas nos processos, portanto uma nova execução exige reimportação com as
novas chaves.

**Limite de ativação.** DP-1801, DP-1802 e DP-1803 continuam abertas e impedem uso com
dados reais; o caminho excepcional da 019 continua fora desta implementação.

## Correções do code review — 2026-10-04

- **Limitação:** janela fixa desde a primeira contagem, espera nunca além do fim da
  janela, confirmação descontada da origem, incremento atômico e trava por CPF durante a
  verificação. Regressões: laboratório com 45 confirmações seguidas sem espera; verificação
  simultânea do mesmo CPF recusada com `Retry-After: 1`; tráfego contínuo não prolonga a
  espera além da janela.
- **Data de nascimento:** validação pela data local (America/Sao_Paulo).
- **Sessão:** a barreira da fonte simulada usa `FonteSimulada.codigo`, documentada como
  barreira da demonstração (008 FR-008).
- **Material:** `registrar_divergencias` público na 001; ausência de data só sinalizada
  quando havia data antes.
- **Estilo:** painel movido para `interface/estilo.css`, com cor literal (regra da 015).
- **Diff:** `cenarios.py`, `academico/incorporacao.py` e `interface/views.py` voltaram ao
  formato da `main`, com só as mudanças da 018.

Depois das correções: `uv run pytest` **2.110 passaram** (1 desmarcado, volume) em
217 s; `ruff check`, `makemigrations --check --dry-run` e `git diff --check` limpos.
