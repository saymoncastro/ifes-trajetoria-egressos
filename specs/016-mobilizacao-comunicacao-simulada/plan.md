# Implementation Plan: Mobilização e comunicação simulada da pesquisa

**Branch**: `016-mobilizacao-comunicacao-simulada` | **Date**: 2026-10-03 | **Spec**: [spec.md](spec.md)

**Input**: `specs/016-mobilizacao-comunicacao-simulada/spec.md`, conceito aprovado e ajustes
explícitos incorporados. Main sincronizada por fast-forward em `0c911b5`, PR #24/015.

## Summary

Comunicação local contextual no acompanhamento da Campanha: conferir público autorizado,
prévia de modelo institucional não editável e simular uma mensagem por Pessoa para Mailpit.
Consultar/prévia nos três estados; simular em preparação/coleta; encerrada recusa.
Pipeline 004 → escopo 010/011 → Pessoas distintas → contato fictício → renderer comum →
Django email. A própria operação rejeita domínio diferente de `example.invalid`, com guard
SMTP independente. Resultado transitório e falhas parciais compreensíveis. Nenhuma mudança
em modelos, migrações, Campanha ou Participação. Plano e tasks aprovados; implementação
posterior autorizada em 2026-10-03, com evidências em [quickstart.md](quickstart.md).

## Technical Context

**Language/Version**: Python >=3.13,<3.14, conforme `pyproject.toml`.

**Primary Dependencies**: Django >=5.2,<5.3 e templates/email nativos; psycopg atual. Mailpit
como executável local somente para demonstração. Sem nova dependência Python/frontend.

**Storage**: PostgreSQL existente, somente leitura nesta feature. Mailpit caixa local temporária;
locmem/outbox no teste. Nenhuma persistência de comunicação ou resultado no aplicativo.

**Testing**: pytest >=8.4,<9, pytest-django >=4.11,<5, locmem e injeção seletiva de falhas;
ruff atual. Suíte não usa Mailpit/SMTP. QA manual de caixa/teclado/responsividade.

**Target Platform**: execução local nativa como atual, navegador, servidor Django 8000,
Mailpit loopback SMTP 1025/UI 8025. Sem hosting/produção/fila/container obrigatório.

**Project Type**: monólito Django modular, HTML server-side, sem JavaScript obrigatório.

**Performance Goals**: cenário canônico pequeno (11 Pessoas, 13 Conclusões incorporáveis);
uma tentativa síncrona por Pessoa contactável, timeout SMTP 5 s por conexão; sem SLA
produtivo inventado. Consultas agregadas/deduplicação SQL, não varrer Participações.

**Constraints**: zero envio externo por múltiplas barreiras; domínio exato não configurável;
sem auth nova, sem lista/editável do navegador, sem modelos/migrations; baseline 015 e
jornada preservadas. Operação não abre coleta nem usa `admite_participacao`.

**Scale/Scope**: uma tela administrativa de público-alvo/prévia, uma resposta POST, duas rotas, uma capacidade fixa,
um resolver fictício, um renderer e uma operação. Somente e-mail local, sem API Mailpit.

## Constitution Check

Gate executado antes da Fase 0 sobre a spec ajustada e repetido após Fase 1 sobre estes
contratos. Constituição 1.0.0 lida; estados não pertinentes recebem N/A com motivo.

| # | Verificação | Princípios | Pré-Fase 0 | Pós-Fase 1 | Evidência / observação |
| --- | --- | --- | --- | --- | --- |
| 1 | Longitudinalidade | I | ✅ Conforme | ✅ Conforme | FR-032/033; nenhuma escrita; data-model |
| 2 | Pessoa versus Conclusão | I, XI | ✅ Conforme | ✅ Conforme | Escopo nas Conclusões antes de PK distintas |
| 3 | Múltiplas formações | I, XI | ✅ Conforme | ✅ Conforme | Uma mensagem/Pessoa/execução, sem fundir formações |
| 4 | Múltiplas participações | I, VIII | ✅ Conforme | ✅ Conforme | Não consultar para segmentar, não alterar |
| 5 | Definição de egresso | II | ✅ Conforme | ✅ Conforme | Consumir 004, não reimplementar elegibilidade |
| 6 | Preservação histórica | VIII, XXVII | ✅ Conforme | ✅ Conforme | Sem migrations ou escrita; snapshots em testes |
| 7 | Versionamento e conceitos distintos | VII, VIII | ✅ Conforme | ✅ Conforme | Campanha não vira mailing; sem convite persistido |
| 8 | Proveniência proporcional | IV | ✅ Conforme | ✅ Conforme | Origem simulada obrigatória; sem histórico fictício |
| 9 | Institucional/derivado/declarado | III | ✅ Conforme | ✅ Conforme | Contato demo separado; contagens derivadas; sem respostas |
| 10 | Desacoplamento de integrações | V, XV, XXV | ✅ Conforme | ✅ Conforme | Resolver pequeno; Django SMTP/locmem; sem API da caixa |
| 11 | Fronteira NIAE | VI | ✅ Conforme | ✅ Conforme | Cinco perguntas respondidas na spec; não criar CRM |
| 12 | Governança institucional | IX, X | ✅ Conforme | ✅ Conforme | Capacidade demo explícita; DP-407/1602 abertas |
| 13 | Escopo por unidade | XII | ✅ Conforme | ✅ Conforme | Reusar 011; igualdade exata; NULL fora de CSAEG |
| 14 | Privacidade/minimização | XVI, XVII | ✅ Conforme | ✅ Conforme | Fictícios, sem PII em logs; no-store; domínio exato |
| 15 | Autorização | X, XII | ✅ Conforme | ✅ Conforme | Operador/vínculos atuais em rota e operação direta |
| 16 | Acessibilidade | XX | ✅ Conforme | ✅ Conforme | Teclado, labels, foco, HTML simples, QA no quickstart |
| 17 | Responsividade | XIV, XXI | ✅ Conforme | ✅ Conforme | Base administrativa preservada; 320 px/200%/sem JS |
| 18 | Testes de invariantes | XXV, XXVI | ✅ Conforme | ✅ Conforme | Estratégia locmem, negativos e snapshots abaixo |
| 19 | YAGNI/stack simples | XXII, XXIII, XXIV | ✅ Conforme | ✅ Conforme | Templates/email nativos, sem filas/editor/plugins |
| 20 | Exportabilidade | XVIII | N/A | N/A | Não exporta contatos/dados; 012/013 inalteradas |
| 21 | Decisões pendentes | XXIX | ✅ Conforme | ✅ Conforme | Tabela abaixo preserva decisões reais, sem liberação produtiva |

**Resultado do gate**: APROVADO antes da pesquisa e após o desenho; nenhuma violação.
Conformidade do desenho não significa feature implementada ou QA já executado.

**Conflitos identificados**: nenhum. Não há motivo para corrigir feature por conflito,
reduzir escopo constitucional, escolher alternativa de exceção ou emendar Constituição.

## Decisões Pendentes

As decisões abaixo são **DECISÃO PENDENTE** institucional, não perguntas bloqueantes para
esta simulação. IDs/contextos completos em [spec.md](spec.md#decisões-pendentes-mandatory--write-nenhuma-if-empty).

| ID | DECISÃO PENDENTE | Instância competente | Solução provisória | Como reverter |
| --- | --- | --- | --- | --- |
| 004/DP-406; 010/DP-1001 | Identidade/acesso de egresso e operador | Proex/DTI/relação Portal, a confirmar | Adaptadores fictícios separados; URL neutra | Substituir fronteiras após spec própria |
| 004/DP-407; DP-1602 | Serviço/canal/governança de envio real | CPAEG/Proex/DIREC/CSAEG/comunicação, a confirmar | Capacidade fixa exclusiva desta demonstração | Nova spec formaliza competência produtiva |
| DP-1601 | Origem/qualidade/atualização de contato real | Fonte/DTI/Proex/encarregado, a confirmar | Mapa fictício zero/um, fora de Pessoa | Substituir resolver com contrato autorizado |
| DP-1603; 001/DP-009; 005/DP-504; 002/DP-007 | Base legal, finalidade, consentimento e retenção | Encarregado/instâncias institucionais | Só dados fictícios, sem uso de Q1 | Nova spec antes de dado real |
| DP-1604 | SMTP/infra/operação produtiva | DTI e responsável de DP-407 | SMTP loopback + guard específico 016 | Desenhar transporte produtivo em feature própria |
| DP-1605; DP-1606 | Lembretes/frequência/opt-out | CPAEG/Proex/encarregado | Nenhuma segmentação por participação ou Q1 | Mudança explícita de público/regra futura |
| DP-1607; DP-1608 | Histórico de disparos/outros canais | Comunicação/DTI/encarregado | Nada persistido, somente e-mail local | Nova necessidade e spec, sem extensões antecipadas |
| 010/DP-1002/1003/1006; DP-1005; 001/DP-007 | Vínculos legítimos, órgãos e vocabulário de unidade | Instância institucional competente | Vínculos atuais fictícios e igualdade exata | Resolver adaptação na governança/fonte |
| 004/DP-402/403/405 | Gestão, prorrogação e reabertura | Instância competente de Campanha | Nenhuma gestão exposta | Feature de gestão autorizada |
| 004/DP-404; 007/DP-701; 005/DP-501 | Sobreposição e múltiplas formações | Instância metodológica competente | Link neutro não escolhe formação/Campanha | Jornada futura explicitamente aprovada |
| 004/DP-408; 005/DP-505 | Snapshot e consulta identificada | Instância competente/encarregado | Público atual transitório; sem respostas | Features próprias autorizadas |
| 008/DP-801 | Linguagem/identidade definitiva | Comunicação institucional | Modelo demo e baseline 015 já aprovada | Revisão editorial sem editor nesta feature |

## Project Structure

### Documentation (this feature)

```text
specs/016-mobilizacao-comunicacao-simulada/
├── spec.md
├── checklists/requirements.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── tasks.md             # execução autorizada e marcadores de conclusão
└── contracts/
    ├── rotas.md
    ├── operacao.md
    └── configuracao-seguranca.md
```

`tasks.md` gerado após as precisões aprovadas e executado posteriormente mediante
autorização explícita de implementação.

### Source Code (repository root, arquivos implementados)

```text
config/settings.py                        # app/templates e configuração email local
.env.example                              # valores fictícios/documentação do ambiente
trajetoria/governanca/regras.py            # capacidade explícita, export público
trajetoria/acompanhamento/urls.py          # duas rotas contextualizadas
trajetoria/acompanhamento/templates/acompanhamento/campanha.html  # link contextual
trajetoria/comunicacao/
├── __init__.py
├── acesso.py                             # identificação/capacidade/visibilidade
├── consultas.py                          # 004 -> escopo -> Pessoas -> contagens
├── contatos.py                           # mapa fictício zero/um
├── convite.py                            # renderer texto+HTML e cabeçalhos fixos
├── seguranca.py                          # domínio exato, origem, URL e transporte
├── operacoes.py                          # preflight, tentativas individuais, resultado
├── views.py                              # GET e POST/CSRF, resultado transitório
└── templates/comunicacao/
    ├── comunicacao.html
    ├── resultado.html
    ├── convite.txt
    └── convite.html
tests/comunicacao/
├── conftest.py
├── test_acesso.py
├── test_contatos.py
├── test_origem.py
├── test_publico.py
├── test_publico_http.py
├── test_convite.py
├── test_convite_mime.py
├── test_preview.py
├── test_configuracao.py
├── test_seguranca.py
├── test_simulacao.py
├── test_simulacao_http.py
├── test_falhas.py
└── test_demonstracao.py
tests/governanca/test_governanca_regras.py # capacidade explícita
tests/acompanhamento/                    # regressão da entrada contextual
tests/analitico/test_analitico_fronteiras.py   # inventário da governança atual
tests/exportacao/test_exportacao_fronteiras.py # inventário da governança atual
```

**Structure Decision**: pacote pequeno de aplicação com app instalada apenas para templates;
sem `models.py`/migrations. Reusar base/estilos administrativos, sem CSS novo por padrão.
Nenhuma alteração esperada em `academico`, `campanha`, `participacao`, provider canônico,
`demonstracao/cenario.py`, seleção A/B/C, `interface/base.html` ou jornada da 015.
Arquivos de teste foram inicialmente previstos no plan; implementação autorizada posterior
criou os módulos em `tests/comunicacao/`, conforme tasks e registro do quickstart.

## Contratos e decisões técnicas

- [HTTP/interface](contracts/rotas.md): GET administrativo de público-alvo/prévia e POST separado com CSRF,
  sem payload de mailing, resultado no próprio POST e no-store.
- [Operação](contracts/operacao.md): autorização reobtida, pipeline, resolver zero/um,
  modelo fixo/renderer único, uma mensagem/Pessoa e contagens/falhas.
- [Configuração/segurança](contracts/configuracao-seguranca.md): allowlist de transporte,
  domínio exato constante, URL local e Mailpit isolado. Não há contrato público produtivo.
- [Data model](data-model.md): nenhum modelo ou migração; valores apenas transitórios.
- [Research](research.md): escolhas, razões, alternativas e fontes primárias.

## Estratégia de segurança

Defesa em profundidade: origem fictícia, modo explícito, capacidade separada, escopo antes
de deduplicação, preflight de todos os destinatários independentemente do SMTP, validação
final de `to`, transporte loopback permitido, conteúdo/remetente/URL local, Mailpit sem
relay. Destinatário real invalida execução inteira, mesmo com configuração SMTP incorreta.
Nenhum valor enviado pelo navegador decide público/conteúdo/URL. Sem dado sensível em erro/log,
sem histórico, sem tracking e sem leitura de Participações/Respostas. Restrição exclusiva 016.

## Falha parcial

Tudo é preparado antes do primeiro envio. Uma conexão nova por mensagem evita reusar sessão
corrompida. Retorno 1 aceito; 0/exceção esperada falha; restantes tentados uma vez. Sem retries,
sem rollback, sem garantia de entrega. Erro inesperado interrompe com contagens conhecidas, tentativa sem confirmação contada
como falha e restantes não tentadas. Resultado no POST, sem redirecionamento que exija estado persistido.

## Estratégia de testes

1. **Público/escopo:** uma/múltiplas formações, inelegíveis, duas unidades, NULL, várias CSAEG,
   CPAEG+CSAEG e revogação. Provar que deduplicação ocorre após recorte. Pessoa distinta por PK.
2. **Contato/conteúdo:** mapa por fonte+ID, ausência, homônimos, nome ausente/caracteres HTML,
   From com nome institucional/mailbox fixos validados separadamente, destinatário simples
   sem display name e cabeçalho com CR/LF, renderer idêntico à prévia/outbox, MIME texto+HTML, um `to`, nenhum
   CC/BCC/anexo, URL neutra e nenhum recurso externo. Exibir genérico se não houver contato.
3. **Operação locmem:** 1/Pessoa, zero contato sem backend, estados preparo/coleta/encerrada,
   alteração entre preview e POST, encerramento por data/explícito, repetição explícita,
   retorno zero e exceção seletiva com aceites anteriores/posteriores, erro inesperado e
   contagens de não tentadas. Spy prova uma tentativa e nova conexão/fechamento por mensagem.
4. **Segurança negativa:** domínio real, subdomínio/sufixo, endereço malformado/lista/CRLF,
   destino externo antes/depois de destinatário válido; backend/config SMTP incorreto,
   credentials/TLS/SSL, host DNS/não loopback, URL externa/Host forjado, origem indevida,
   adapter indevido, flag off, locmem fora de teste. Guard de domínio testado isoladamente
   sob settings SMTP incorretas e com transporte mockado; zero conexão/mensagem em preflight.
5. **Rotas:** falta de operador/vínculo, cookie somente de Pessoa, UUID inexistente e fora
   de escopo, todas as GET/POST protegidas, CSRF real habilitado, método errado/payload
   adulterado, encerrada 409, preparação insegura 422, resultado sem sessão/cookie/cache.
6. **Invariantes:** snapshot de campos/relações/momentos de todos os modelos de domínio,
   incluindo opções de respostas, antes/depois de GET/preview/POST/falha/repetição/link.
   `makemigrations --check --dry-run` comprova nenhum schema novo.
   Antes de cada implementação, testes capturam logs e HTML/resultado de falhas de origem,
   resolver, renderer, SMTP e erro inesperado usando sentinelas fictícias de nome/endereço/
   conteúdo/respostas/credenciais; nenhuma sentinela, exceção bruta ou traceback é exposta.
   Testar projeção agregada do template sem coleção individual interna.
7. **Regressão/manual:** preservar cenário A/B/C, rascunho oculto de B, shell admin e jornada
   015. Suíte existente após testes focados; Mailpit somente no roteiro manual. Teclado,
   320 px, zoom 200%, sem JavaScript, leitura equivalente de texto/HTML.

Todos os testes de conteúdo e envio usam `override_settings` com locmem + modo demo + flag
interna de teste; nunca Mailpit, SMTP externo ou rede. Testes de guards podem monkeypatchar
instanciação de backend para provar ausência de tentativa; não criar backend genérico novo.

## Configuração e validação manual

Mailpit nativo: `mailpit --listen 127.0.0.1:8025 --smtp 127.0.0.1:1025`, sem relay/forwarding,
sem volume. Django SMTP explícito `127.0.0.1:1025`, sem usuário/senha/TLS/SSL; flag demo ligada.
Passos completos em [quickstart.md](quickstart.md), incluindo teste pré-operacional com B,
inspeção de caixa e link neutro, falha de transporte e negativos cobertos sem rede na suíte.

## Complexity Tracking

Nenhuma violação constitucional; nenhuma exceção ou complexidade a justificar.

## Resultado do planejamento

Fases 0/1 concluídas. Nenhum esclarecimento bloqueante antes de `/speckit-tasks` para o
escopo fictício aprovado. Decisões produtivas permanecem abertas e não autorizadas.
Hooks before/after plan: `.specify/extensions.yml` ausente; nada a executar.
Verificação desta entrega é documental; não afirmar testes da 016 ou roteiro já executados.

## Precisões para decomposição em tasks

“Público” é público-alvo, jamais rota aberta. Todas as telas/endpoints de Comunicação são
administrativos, somente operador fictício autorizado no modo demo e escopo 010/011.
Nenhum egresso acessa Comunicação. O link neutro não é acesso a essa administração.

Cada POST legítimo é nova execução independente. Não existe “já enviado”, histórico,
deduplicação ou idempotência entre execuções. Duas simulações podem gerar duas mensagens
para a mesma Pessoa. Sem chave de idempotência, tabela ou estado persistido adicional.

Resultado por Pessoa/mensagem é apenas valor transitório: submetida ao transporte com
aceite local confirmado; falha de transporte sem confirmação; sem contato, sem tentativa.
A operação retorna em memória PK de Pessoa e situação junto aos totais, sem nomes,
endereços ou conteúdo. A view projeta somente totais/categorias, instante e escopo para
o template; não repassa coleção individual. Ambas as representações são transitórias,
sem catálogo/evento persistido. UI mostra totais por situação, não lista nominal. Preservar contadores de tentativas/aceites:
submetidas no contador = tentativas; aceitas = situações com confirmação. Interrupção
inesperada também informa não tentadas. Não envolver SMTP em transaction.atomic/transação
de banco; falha não desfaz mensagens anteriores; sem retry automático.

Quickstart mantém Serra/Vitória em preparação. CTA abre entrada neutra, não torna a Campanha
respondível, não abre coleta nem cria Participação; regras 004/007 continuam intactas.
