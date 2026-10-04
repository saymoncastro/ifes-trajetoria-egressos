# Quickstart — validar a Feature 016

Feature implementada e validada localmente em 2026-10-03. O registro de execução ao final
distingue as verificações automáticas e manuais. Ver [plan.md](plan.md),
[contratos](contracts/rotas.md) e [segurança](contracts/configuracao-seguranca.md).

## Pré-requisitos

Python 3.13, uv, PostgreSQL local e banco exclusivo fictício `trajetoria_demo`, conforme
[001/quickstart](../001-nucleo-academico-fonte-simulada/quickstart.md).
Mailpit instalado como executável local pelo processo habitual de sua máquina;
[documentação oficial](https://mailpit.axllent.org/docs/install/).
Nenhuma conta, credencial SMTP ou endereço real; Mailpit não integra a suíte.
Os comandos são executados na raiz do repositório, em terminais separados quando indicado.

## Preparar banco e dados fictícios

Criar o banco caso ainda não exista, com servidor PostgreSQL local já iniciado:

```bash
createdb trajetoria_demo
uv sync --extra dev
PGDATABASE=trajetoria_demo uv run python manage.py migrate
PGDATABASE=trajetoria_demo TRAJETORIA_DEMONSTRACAO=1 uv run python manage.py preparar_demonstracao
```

Não recriar banco existente para repetir este roteiro. Preparo mantém três Campanhas e
operadores A CPAEG, B CSAEG Vitória, C sem vínculo. Recusa base com outra origem; não misturar
dados reais. Não executar nenhuma abertura/prorrogação para testar Comunicação.
Contatos são mapa de aplicação, não inserção no banco ou importação de e-mail em Pessoa.

## Iniciar Mailpit (terminal 1)

```bash
env -i "$(command -v mailpit)" --listen 127.0.0.1:8025 --smtp 127.0.0.1:1025
```

Usar ambiente sem configurações herdadas de relay/forward/webhook/release. Não habilitar
nenhuma delas nem publicar portas na rede. Caixa temporária sem volume basta. UI:
`http://127.0.0.1:8025/`. Pode remover mensagens fictícias pela UI antes de nova execução
para conferir contagens; não consultar API Mailpit nem inferir estado da Campanha da caixa.

## Iniciar aplicação (terminal 2)

Configuração mínima explicitamente local:

```bash
export PGDATABASE=trajetoria_demo
export TRAJETORIA_DEMONSTRACAO=1
export EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
export EMAIL_HOST=127.0.0.1
export EMAIL_PORT=1025
export EMAIL_HOST_USER=''
export EMAIL_HOST_PASSWORD=''
export EMAIL_USE_TLS=0
export EMAIL_USE_SSL=0
export TRAJETORIA_URL_ENTRADA_DEMONSTRACAO=http://127.0.0.1:8000/demonstracao/
uv run python manage.py runserver 127.0.0.1:8000
```

Timeout é 5 s fixo e remetente institucional fictício. `.env` não é lido automaticamente.
O app deve recusar backend não explicitamente habilitado, credencial/transporte indevido
ou destinatário fora de `example.invalid`, antes de qualquer envio. Não configurar
locmem como backend da demonstração manual; ele serve somente à suíte.

## Roteiro completo pré-operacional

Abrir `http://127.0.0.1:8000/acompanhamento/`, selecionar operador **B** pelo seletor existente.

| Passo | Ação | Resultado esperado |
| --- | --- | --- |
| 1 | Abrir “Demonstração — rodada em preparação” | EM PREPARAÇÃO; instrumento rascunho continua oculto para B |
| 2 | Seguir “Comunicação simulada” | Shell administrativo, aviso de demo, escopo Vitória, momento da consulta |
| 3 | Conferir público | 3 Conclusões, 2 Pessoas, 1 com contato, 1 sem, 1 mensagem prevista |
| 4 | Conferir prévia fixa | Bruno representativo, `sim-p-0002@example.invalid`, remetente institucional fictício; assunto Campanha; texto/HTML/CTA/URL neutra; sem editor |
| 5 | Acionar “Simular envio local” sem abrir coleta | 1 submetida, 1 aceita pelo transporte, 0 falhas; Campanha continua EM PREPARAÇÃO |
| 6 | Abrir Mailpit | Uma mensagem para Bruno, apesar de suas duas formações; nenhuma para Carla `SIM-P-0010` sem contato |
| 7 | Inspecionar texto e HTML | Mesmo conteúdo da prévia, um destinatário, nenhum CC/BCC/anexo/recurso externo; não há curso/unidade/identidade na URL |
| 8 | Seguir CTA em navegador sem Pessoa selecionada | Entrada `/demonstracao/`, escolha fictícia; nenhum login, formação ou Participação criada |
| 9 | Seguir CTA no navegador com Pessoa previamente selecionada | Entrada neutra; link não troca Pessoa nem inicia/retoma pesquisa |
| 10 | Voltar à Comunicação por GET | Nenhuma mensagem adicional; resultado anterior não é histórico recuperável |
| 11 | Repetir simulação explicitamente | Mais uma mensagem; interface avisa duplicação entre execuções, sem retry automático |

Agora escolher **A**, abrir mesma Campanha, voltar à Comunicação: 13 Conclusões, 9 Pessoas,
8 com contato, 1 sem, 8 previstas. Simular: 8 submissões/aceites, 0 falhas. *(Revisado pela ADR 0004 — ver `docs/adr/0004-abrangencia-da-campanha-nao-e-foco-de-mobilizacao.md`.)* A Campanha
em preparação não tem critério; antes era restrita a Serra e Vitória. Carla Serra e
Carla Vitória não são fundidas pelo nome; Carla Vitória segue sem contato. Inspecionar
endereços distintos, todos `example.invalid`. Não somar caixa antiga como resultado atual.

Como A, a coleta ampla permite simular em EM COLETA. Inspecionar mensagem de
`SIM-P-0009` sem nome: saudação “Olá!”, link igual aos demais. Quantidades/estado de
Participações pré-existentes não selecionam nem alteram o mailing fictício.

## Falha de transporte e recusa

Encerrar Mailpit no terminal 1 e repetir ação na Campanha em preparação. Esperado: falhas
compreensíveis e zero aceites confirmados, sem retry/fallback; o app não abre coleta nem
muda domínio. Reiniciar Mailpit não reenvia automaticamente; nova ação deve ser explícita.
Falha após aceite remoto pode deixar mensagem na caixa: o aviso não promete ausência.

Escolher C: recusa sem conteúdo da Campanha ou público. Como B, tentar URL direta da
Comunicação da coleta sobreposta (Vila Velha): 403 sem nome/números. Somente escolher Pessoa não autoriza.
Desligar modo demo e reiniciar app: páginas 404, operação recusada.

ENCERRADA (por data ou fechamento), falha parcial seletiva, contato externo injetado,
SMTP incorreto, CSRF, revogação e chamadas diretas são validados automaticamente em fixtures.
Não modificar Campanha canônica, operador B ou fonte para produzir esses casos manuais.
Não testar endereço real com transporte real: suíte locmem/spy prova rejeição sem rede.

## Validar automaticamente sem Mailpit

Parar Mailpit não afeta os comandos abaixo. PostgreSQL de testes segue requisitos da 001.

```bash
uv run pytest tests/comunicacao tests/governanca tests/acompanhamento
uv run pytest
uv run ruff check .
uv run python manage.py makemigrations --check --dry-run
```

Esperado: tudo verde e “No changes detected”. A suíte força locmem e
flags de teste internas via override_settings, inspeciona `mail.outbox`, MIME, conteúdo,
contagens, guard de domínio independente de SMTP, zero conexões em recusa e snapshots
completos de domínio. Falha parcial por injeção no backend, sem Mailpit ou rede externa.
Ver matriz/FRs em [spec.md](spec.md); estratégia detalhada em [plan.md](plan.md#estratégia-de-testes).

## Verificação visual e preservação

Sem JavaScript, somente teclado, largura 320 px e zoom 200%: alcançar link contextual,
ler todos os números/ambas versões e operar ação/retorno com foco visível. Erros não usam
somente cor. HTML do convite na caixa legível com CTA descritivo e texto equivalente.
Conferir que acompanhamento conserva seu shell e que entrada/jornada conservam baseline015.

Snapshots automatizados comprovam zero alteração de Campanha, Participação, Respostas,
Opções e demais modelos antes/depois da operação, falha/repetição e clique neutro.
Não chamar `entrar` no teste de link: iniciar pesquisa manualmente pertence à jornada existente.
Nenhum Convite, Destinatário, Disparo, Evento de entrega, mailing ou histórico no banco.

## Campanha em preparação e repetição independente

Serra/Vitória permanece EM PREPARAÇÃO durante todo o roteiro. Seu CTA pode conduzir à
entrada neutra da demonstração sem tornar essa Campanha respondível. A 016 não abre
Campanha, cria Participação ou contorna 004/007 apenas para demonstrar o convite. Outras
Campanhas já abertas continuam respondíveis conforme as regras existentes.

Cada POST legítimo de “Simular envio” é nova execução independente. Sem “já enviado”,
histórico, deduplicação/idempotência entre simulações ou chave persistida. No passo 11,
duas execuções de B devem produzir duas mensagens para Bruno na caixa, uma por execução.
Não repetir POST por refresh como mecanismo de teste; usar ação explícita para cada execução.

Resultado informa totais por situação: submetida ao transporte com confirmação de aceite
local, falha de transporte, sem contato, e não tentada se houver interrupção inesperada.
Falha não desfaz mensagens anteriores; SMTP não participa de transação de banco e não
tem retry automático. A comunicação é administrativa: somente operador fictício autorizado
pode abrir suas telas; “público” no roteiro significa público-alvo, não acesso de egresso.

## Registro de execução — 2026-10-03

Execução nativa em banco fictício separado `trajetoria016_validacao`, criado exclusivamente
para esta validação. Nenhum banco existente foi recriado. Preparo canônico e migrations
existentes aplicados; cenário, providers acadêmicos, modelos e shell 015 preservados.

| Verificação manual | Resultado observado |
| --- | --- |
| B, Serra/Vitória em preparação | 3 Conclusões / 2 Pessoas / 1 contato / 1 sem / 1 prevista; 1 tentativa e 1 aceite |
| Segundo POST explícito de B | Mais 1 aceite; caixa exibiu duas mensagens para a mesma Pessoa, uma por execução |
| A, mesma Campanha | 6 / 5 / 4 / 1 / 4; 4 tentativas, 4 aceites, zero falhas; caixa totalizou 6 mensagens das três execuções |
| Mailpit texto e HTML | Saudação, assunto, remetente fixo, um destinatário reservado e CTA local iguais à prévia; versões legíveis |
| CTA sem Pessoa, depois com Pessoa | Entrada neutra manteve seletor; seleção fictícia existente não iniciou pesquisa; formação exibiu ausência de pesquisa disponível |
| Mailpit parado, A | 4 tentativas, 0 aceites, 4 falhas, 1 sem contato; sem retry/fallback; resultado explica incerteza |
| C e B fora do escopo | Recusa administrativa sem nome, conteúdo ou contagens da Campanha |
| 320 px | `innerWidth=320`, `scrollWidth=320`; prévia renderizada dentro do iframe sandbox |
| Zoom 200% | Chrome confirmou 200%; largura útil 756 px e scrollWidth 756 px; leitura preservada; zoom restaurado |
| Teclado / JavaScript desligado | Formulário e retorno funcionaram; POST nativo confirmado com DevTools indicando JavaScript bloqueado; configuração restaurada |

A caixa foi inspecionada pela UI, sem API, relay ou envio externo. Serra/Vitória permaneceu
em preparação, com zero Participações. Coleta/encerramento e saudação sem nome foram
comprovados nos testes, sem mudar a Campanha canônica para demonstração.

Testes dos blocos funcionais foram escritos e executados antes da implementação, com RED
por ausência/comportamento da 016 e GREEN posterior. A inspeção visual encontrou escape
incompleto de `SafeString` em srcdoc/código; revisão final também encontrou markup do nome
na versão texto administrativa. Testes de regressão reproduziram ambos antes da correção
com `force_escape` nas três exibições; isolamento, conteúdo literal e reflow foram confirmados.
Inventários antigos de governança foram atualizados para incluir a capacidade explícita da
016, preservando as autorizações do analítico/exportação. Convite usa a cor administrativa
existente; os tokens e as escolhas da 015 permanecem intactos.

Validação focada de integração: `uv run pytest tests/comunicacao -q` — **95 passed**, Mailpit parado.
Falhas seletivas, retorno zero, timeout após submissão, interrupção inesperada, conexões
individuais fechadas e SMTP fora de atomic foram injetados em locmem. Snapshots completos
confirmam zero escrita, inclusive nas falhas. Preflight integral e guarda final recusam
endereços externos/subdomínios/listas/CRLF, inclusive com host SMTP incorreto; spy confirma
zero transporte nas recusas. Respostas/logs de erro não expõem sentinelas sensíveis.

`uv run python manage.py makemigrations --check --dry-run` — **No changes detected**.
Nenhum modelo, coluna, migration, editor, fila, retry, histórico, sessão de resultado ou
infraestrutura produtiva foi criado. As decisões de envio real continuam fora da 016.

Auditoria complementar: três Conclusões elegíveis da mesma Pessoa produziram uma mensagem,
com contagens **4/2/1/1/1**. Conclusão inelegível, unidade com grafia diferente e unidade
NULL não entraram no recorte CSAEG. O snapshot completo permaneceu intacto.

Validação final após as correções e casos complementares, com Mailpit parado:

- `uv run pytest -q` — **1950 passed, 1 deselected**, em 232,18 s. A desseleção é a
  configuração padrão de testes de volume do projeto; nenhum teste da Comunicação foi omitido.
- `uv run ruff check .` — **All checks passed!**
- `uv run python manage.py makemigrations --check --dry-run` — **No changes detected**.
- `git diff --check` — sem problemas.

**50/50 tasks concluídas.** Os **38 FRs e 10 SCs foram preservados**, com alteração somente
da informação documental de autorização/execução. Checklist de qualidade mantido como
registro de revisão, sem alterar seus arquivos ou marcadores. `.specify/extensions.yml`
ausente antes e depois da implementação; nenhum hook aplicável. Serviços iniciados para
validação foram encerrados ao final; o banco fictício isolado foi mantido.

## Code review (2026-10-03)

Correções após revisão de código, cada uma com regressão que falhava antes:

- Barreira das rotas: `@comunicacao` passa a ter marcador próprio, em vez de se apresentar
  como `@acompanhamento`; o inventário da 011 e o da 016 distinguem as duas barreiras.
- Contagem: erro antes do send (barreira final, conexão) deixa a mensagem **não tentada**;
  submetidas/falhas contam só tentativas reais de transporte.
- Situação da Campanha com o rótulo da 011 ("Em preparação"), não o nome do enum.
- Link ou markup ativo no nome da Campanha recusa prévia **e** simulação pelo mesmo critério
  (`validar_conteudo`), com mensagem explicativa, em vez de recusar só o POST.
- Limpeza: verificação de modo morta no decorator (o middleware já responde 404), validação
  repetida por mensagem, autorização duplicada na view do POST e respostas no-store num helper.
- Mantida: `pode_simular_comunicacao` como regra nomeada própria (R2), mesmo com o critério
  igual ao do acompanhamento.

`uv run pytest -q` — **1954 passed, 1 deselected**; `ruff check`, `manage.py check` e
`makemigrations --check` limpos.
