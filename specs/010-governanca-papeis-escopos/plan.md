# Implementation Plan: Governança, papéis e escopos institucionais

**Branch**: `claude/feature-010-governanca-d28809` | **Date**: 2026-10-01 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/010-governanca-papeis-escopos/spec.md`

## Summary

O plan entrega a menor implementação capaz de responder:

> "Dado um operador já identificado, quais capacidades institucionais ele possui agora?"

e aplica essa resposta ao editor da Feature 009. Não implementa autenticação.

Abordagem técnica (detalhes em [research.md](research.md)):

- **Um app pequeno de domínio, `trajetoria/governanca`, com um modelo** (R1):
  `VinculoDeGovernanca` = identificador opaco do operador, papel (`CPAEG` | `CSAEG`),
  unidade (texto não nulo: vazio para CPAEG, não vazio para CSAEG) e `ativo`. Escopo derivado do papel,
  não persistido. Quatro restrições locais à linha (R3).
- **Operador = string** no vínculo; sem modelo de operador, conta ou identidade (R2). O
  contrato futuro de identidade (DP-1001) terá de resolver a requisição para esse
  identificador antes da autorização.
- **Duplicidade**: uma linha por (operador, papel, unidade), ativa ou inativa;
  registrar de novo reativa; registrar ativo é recusado; desativar não apaga (R4).
- **Três regras puras**, predicados explícitos: `pode_consultar_publicado`,
  `pode_consultar_rascunho`, `pode_elaborar_instrumento`, sobre os vínculos ativos. Sem
  enum de capacidade, registro, composição ou motor de políticas. Capacidade = existência de algum
  vínculo ativo que a conceda; sem precedência; unidade fora das regras (R5).
- **Identificação só no modo de demonstração**: operador fictício escolhido entre três
  fixos no código, por cookie assinado revalidado, no adaptador `demonstracao` da 008. A
  escolha identifica; o vínculo autoriza (R6).
- **Produção continua fechada**: o middleware da 008 segue respondendo 404 com o modo
  desligado; a identificação devolve `None` fora do modo; nenhum identificador do
  cliente é aceito (R7).
- **Gate central do editor**: decorador `@exige(regra)`, o mais externo de cada uma das
  25 views, e `_exigir_consulta` nas 5 leituras que dependem do estado da Versão. Ordem:
  identificar → vínculos → regra → view (objeto, formulário, operação da 002). A recusa
  nunca valida formulário nem chama operação (R8).
- **Listas filtradas na consulta** para quem não consulta rascunhos (R9).
- **Sem operador no modo de demonstração**: encaminhamento (302) fixo para a escolha de
  operador fictício, que volta ao início do editor; sem `next`, login ou sessão (R8,
  R14).
- **403 explícito** para operador identificado sem vínculo ativo ou cujo vínculo não
  permite a ação, com texto operacional sem número de artigo; 404 da 009 para
  inexistente; 404 global com o modo desligado (R14).
- **Publicação: nada muda** (R11). **Privilégio técnico**: nada adicionado; independência
  verificada por construção (R10).
- **Vínculos fictícios pelo preparo da demonstração**; nenhum mecanismo de gestão além das
  operações de aplicação (R12, R13).

## Technical Context

**Language/Version**: Python 3.13 (ADR 0001).

**Primary Dependencies**: Django 5.2 LTS (modelos, `CheckConstraint`, `UniqueConstraint`
simples, views de função, templates, assinatura de cookie) e psycopg 3.
**Nenhuma dependência nova.** Nenhum `django.contrib.*` acrescentado (sem `auth`,
`sessions`, `admin`, `contenttypes`).

**Storage**: PostgreSQL 16+. **Uma tabela nova** (`governanca_vinculodegovernanca`), uma
migração aditiva. Nenhuma tabela existente alterada.

**Testing**: pytest + pytest-django e `django.test.Client` (sem JavaScript); `ast` para
fronteiras; `verificar` da 008 para acessibilidade; `monkeypatch` para provar que nenhuma
operação da 002 é chamada na recusa.

**Target Platform**: servidor local de desenvolvimento com `TRAJETORIA_DEMONSTRACAO=1` e
o CI existente (GitHub Actions, Postgres 16).

**Project Type**: aplicação web monolítica server-rendered (monólito modular Django).

**Performance Goals**: uma consulta a mais por requisição do editor (vínculos ativos do
operador, dezenas de linhas no máximo). Listas filtradas no banco.

**Constraints**:

- sem autenticação, sessão, conta ou senha;
- sem identificador de operador vindo de parâmetro, cabeçalho ou campo;
- sem JavaScript e sem recurso de terceiros nas páginas novas;
- WCAG 2.1 AA como direção, 320 px a desktop;
- textos institucionais, sem termo técnico de autorização.

**Scale/Scope**:

- 1 app novo com 1 modelo, 1 enumeração, 3 regras, 1 consulta e 2 operações;
- 1 módulo novo no editor (`acesso.py`) e 1 template novo (`recusa.html`);
- 1 módulo novo no adaptador de demonstração (`operador.py`), 3 rotas e 1 template;
- 25 views do editor decoradas, sem mudança de comportamento editorial;
- 0 alterações na 002, 003, 004, 005, 006, 007 e na jornada da 008.

## Constitution Check

*GATE: aprovado antes da Fase 0 e reavaliado depois da Fase 1.*

| # | Verificação | Princípios | Pré-Fase 0 | Pós-Fase 1 | Evidência / observação |
|---|-------------|------------|------------|------------|------------------------|
| 1 | Longitudinalidade | I | N/A | N/A | A feature não lê nem grava Pessoa, Conclusão, Participação ou Resposta (spec FR-027; contrato de governança, importações proibidas) |
| 2 | Pessoa versus Conclusão Acadêmica | I, XI | ✅ | ✅ | Operador nunca é Pessoa nem Conclusão (spec FR-008; R2). Escolha de operador e de Pessoa usam cookies distintos (R6) |
| 3 | Múltiplas formações sem fusão | I, XI | N/A | N/A | Fora do alcance |
| 4 | Múltiplas participações sem sobrescrita | I, VIII | N/A | N/A | Fora do alcance |
| 5 | Definição institucional de egresso | II | N/A | N/A | Fora do alcance |
| 6 | Preservação histórica | VIII, XXVII | ✅ | ✅ | Elaborar não abre exceção à imutabilidade: as recusas 302/409 da 009 ficam inalteradas para CPAEG; sem elaborar, a recusa é 403 antes (contrato acesso-editor, "Respostas"). Migração aditiva e reversível (data-model §8) |
| 7 | Pesquisa/Versão/Campanha/Participação distintas | VII, VIII | ✅ | ✅ | Nenhuma alteração nessas entidades. Nenhuma capacidade de Campanha (spec FR-073) |
| 8 | Proveniência proporcional | IV | ✅ | ✅ | O vínculo declara refletir designação externa sem verificá-la (contrato de governança; DP-1002). Sem trilha de auditoria (009/DP-903 aberta) |
| 9 | Institucional, derivado e declarado | III | N/A | N/A | Nenhum dado de egresso. Capacidades são derivadas e calculadas a cada requisição (data-model §5) |
| 10 | Desacoplamento de integrações | V, XV, XXV | ✅ | ✅ | Identificação isolada num adaptador (`demonstracao.operador`), importado num único ponto (`editor/acesso.py`); regras com um único parâmetro, `vinculos` (R2, R8, R10) |
| 11 | Fronteira do NIAE | VI | ✅ | ✅ | Spec, "Fronteira do NIAE": autorização das superfícies do NIAE pertence ao domínio; identidade fica fora (DP-1001) |
| 12 | Governança institucional (publicação, competências) | IX, X | ✅ | ✅ | Só CPAEG e CSAEG, da PAEG; elaboração só CPAEG (Art. 21, VI); CSAEG consulta publicadas (interpretação B6, confirmada); **sem publicação**, papel publicador ou fluxo de aprovação (R11); privilégio técnico não autoriza (R10) |
| 13 | Escopo por unidade e visão consolidada | XII | ✅ | ✅ | Escopo derivado do papel; unidade obrigatória em CSAEG por restrição; sem tenant, catálogo ou hierarquia (R3). Unidade não amplia capacidade (R5). Catálogo canônico: DP-1005 |
| 14 | Privacidade e minimização | XVI, XVII | ✅ | ✅ | Só o identificador do operador é gravado (data-model §3). Recusa antes de qualquer conteúdo; recusas sem detalhe interno (R14). Rascunhos não carregados para a CSAEG (R9) |
| 15 | Autorização (menor privilégio; técnica ≠ normativa) | X, XII | ⏸ | ✅ | Antes: DP-901 aberta. Depois: matriz fixa (data-model §5), gate no servidor em 25 rotas com verificação de cobertura (contrato acesso-editor), sem superusuário ou modo de demonstração na regra. DP-901 parcialmente resolvida; restante em DP-1003 e DP-1004 |
| 16 | Acessibilidade | XX | ✅ | ✅ | `verificar` da 008 nas recusas e na escolha de operador; recusa com `<h1>`, texto e ligação (R14, R15) |
| 17 | Responsividade | XIV, XXI | ✅ | ✅ | Páginas novas usam a base e a folha da 008/009; roteiro de 320 px (quickstart) |
| 18 | Testes proporcionais ao risco | XXV, XXVI | ✅ | ✅ | `tests/governanca/` (4 arquivos), `test_editor_autorizacao.py` parametrizado por rota, `test_demonstracao_operador.py`, suíte da 009 executada como CPAEG (R15; mapa SC abaixo) |
| 19 | Over engineering | XXII, XXIII, XXIV | ✅ | ✅ | Ver "Sinais de over engineering": nenhum presente |
| 20 | Exportabilidade | XVIII | N/A | N/A | Não exporta |
| 21 | Decisões pendentes explícitas | XXIX | ✅ | ✅ | Interpretações B1–B9 marcadas na spec; publicação, identificação produtiva, evidência de registro, alcance da CPAEG, rascunhos para CSAEG, unidades e demais instâncias em DPs (tabela abaixo) |

**Resultado do gate**: APROVADO antes da Fase 0 e depois da Fase 1. Nenhuma violação. O
único ⏸ pré-Fase 0 (autorização, DP-901) é exatamente o que esta feature resolve na
parte sustentada pela PAEG.

**Conflitos identificados**: nenhum.

**Sinais de over engineering**:

| Sinal | Presente? | Observação |
|-------|-----------|------------|
| Mais de um modelo novo | Não | Só `VinculoDeGovernanca` |
| Operador, Usuário, Conta, Identidade, Credencial | Não | Operador é string (R2) |
| Papel, Permissão, Papel-Permissão, Escopo, Organização, Unidade, Tenant como tabela | Não | `Papel` é `TextChoices`; escopo derivado; unidade texto (R3) |
| Papéis genéricos (admin, editor, leitor, gestor, publicador) | Não | Verificado por teste (R15) |
| Motor de políticas, registro de capacidades, ABAC, ACL por objeto, biblioteca externa | Não | Três funções de uma linha (R5) |
| Middleware de autorização ou framework de decoradores | Não | Um decorador do editor com três valores aceitos (R8) |
| Tela, CRUD, comando ou API de vínculos | Não | Operações de aplicação (R13) |
| Histórico, datas, portaria, autor, soft-delete genérico | Não | Só `ativo` (R4) |
| Workflow de aprovação, publicação | Não | R11 |
| Autenticação, sessão, `django.contrib.auth` | Não | R6, R10 |
| Abstração "para a 011" | Não | A unidade existe por significado do vínculo; nenhuma regra a usa |

## Decisões Pendentes

| ID | DECISÃO PENDENTE | Instância competente (se conhecida) | Solução provisória (hipótese) | Como reverter |
|----|------------------|-------------------------------------|-------------------------------|---------------|
| DP-1001 | Identificação de operadores em produção | Ifes (DTI, com Proex) | Só operador fictício no modo de demonstração; editor fechado fora dele (R6, R7) | Novo adaptador substitui a importação de `operador_em_uso` em `editor/acesso.py`; regras, vínculo e gate não mudam |
| DP-1002 | Quem autoriza o registro de vínculos e com qual evidência | Proex/CPAEG; Diretorias das unidades | Operações de aplicação que declaram refletir designação externa; sem portaria ou datas (R13) | Campo aditivo no vínculo e restrição sobre quem chama as operações, por spec própria |
| DP-1003 | Quem atua pela CPAEG no sistema | CPAEG, com Proex | O sistema não distingue membro de quem atua em nome da comissão | Registrar ou desativar vínculos; sem mudança de código |
| DP-1004 | Rascunhos ou reporte para a CSAEG | CPAEG | CSAEG só consulta publicadas (Clarifications) | `pode_consultar_rascunho` passa a incluir CSAEG, ou feature própria de reporte |
| DP-1005 | Designação canônica das unidades | Ifes (fonte acadêmica oficial) | Texto como na fonte acadêmica e na Campanha; sem catálogo (R3) | Validação contra catálogo futuro, aditiva |
| DP-1006 | Atuação de Proex, DIREC, Proen, Reitoria, Diretorias | Proex | Não representadas | Novo valor em `Papel` e regra correspondente, por spec com consumidor |
| 009/DP-901 | Quem elabora e edita rascunhos | Proex/CPAEG | **Parcialmente resolvida**: elaborar = vínculo CPAEG ativo (PAEG Art. 21, VI) | Restante em DP-1003, DP-1004, DP-1001 |
| 002/DP-001 | Quem publica | CPAEG com Pró-reitoria (Art. 26) decide a omissão | Publicação indisponível; nenhuma estrutura antecipada (R11) | Spec futura cria a menor autorização (por exemplo, regra nova) e expõe `publicar` |
| 002/DP-002 | Fluxo de elaboração e aprovação | CPAEG, Proex, Proen | Só RASCUNHO e PUBLICADA | Spec futura |
| 009/DP-902 | Estatuto da baseline | CPAEG | Rascunho comum, editável só por CPAEG | Spec futura |
| 009/DP-903 | Autoria e histórico | CPAEG/Proex | Nenhum registro | Acréscimo aditivo, com o identificador do operador já disponível na requisição |
| 004/DP-402, 004/DP-403 | Quem gere Campanha; Campanhas de unidade | Proex/CPAEG | Nenhuma capacidade de Campanha | Feature 011 usa papel e unidade do vínculo |
| 005/DP-505 | Quem consulta respostas identificadas | CPAEG/Proex + encarregado de dados | Nenhuma superfície | Spec futura usa papel e unidade do vínculo |

## Desenho

### Camadas

```text
templates/editor/*.html, recusa.html ── leem request.atuacao (rótulos e três booleanos)
        ▲
trajetoria/editor/views.py ─────────── 25 views, cada uma com @exige(regra);
        │                               5 leituras chamam _exigir_consulta(request, versao)
        ▼
trajetoria/editor/acesso.py ────────── exige, Atuacao, recusa (403)
   │            │
   │            └─ identificação ──▶ trajetoria/demonstracao/operador.py
   │                                   operador_em_uso(request) -> str | None
   │                                   (só modo de demonstração; lista fechada; cookie assinado)
   ▼
trajetoria/governanca ──────────────── consultas.vinculos_ativos(identificador)
                                        regras.pode_consultar_publicado / _rascunho / _elaborar
                                        operacoes.registrar_vinculo / desativar_vinculo
                                        models.Papel, VinculoDeGovernanca
```

Importações permitidas a `trajetoria/editor`, acrescidas às da 009 (verificadas por
`ast`):

| Módulo | Nomes |
|--------|-------|
| `trajetoria.demonstracao.operador` | `operador_em_uso` (só em `acesso.py`) |
| `trajetoria.governanca.consultas` | `vinculos_ativos` |
| `trajetoria.governanca.regras` | `pode_consultar_publicado`, `pode_consultar_rascunho`, `pode_elaborar_instrumento` |

`trajetoria.governanca.operacoes` **não** é importável pelo editor: o editor nunca grava
vínculo. No app `demonstracao`, `trajetoria.governanca.operacoes` só pode ser importado
por `cenario.py` (acrescentado a `SO_NO_CENARIO` do teste de fronteira da 008).

### Fluxo de uma escrita (009 + 010)

```text
POST → middleware do modo (404 se desligado) → CSRF (403 se ausente)
     → @exige(pode_elaborar_instrumento)
          operador_em_uso → None?          → 302 /demonstracao/operador/ (nada lido nem gravado)
          vinculos_ativos → []?            → 403 sem atuação
          pode_elaborar_instrumento falso? → 403 "Seu vínculo institucional atual não
                                              permite editar este instrumento."
     → (009, inalterado) objeto → _exigir_rascunho → formulário → operação 002 → 302
```

### Fluxo de uma leitura por estado

```text
GET → @exige(pode_consultar_publicado) → objeto (404 se inexistente)
    → _exigir_consulta(request, versao): rascunho sem consultar_rascunho → 403
    → página (ações de criação só com elaborar)
```

### Concorrência

- Autorização avaliada a cada requisição; desativar um vínculo vale na seguinte (spec
  FR-024).
- Operações de vínculo em `transaction.atomic()` com `select_for_update`; corrida de
  criação recusada pela restrição única e convertida em `JA_ATIVO`.
- Edição concorrente de rascunho: a da 009 (serialização da 002, sem bloqueio).

### Erros

Tabela completa em [contracts/acesso-editor.md](contracts/acesso-editor.md#respostas) e
justificativa em [research R14](research.md#r14--respostas-http-e-textos-de-recusa).
Resumo: 404 com o modo desligado; 302 para a escolha de operador sem operador escolhido;
403 para sem atuação e vínculo que não permite; 404 da 009 para inexistente quando autorizado; 302/409 da 009 para publicada
quando CPAEG.

## Project Structure

### Documentation (this feature)

```text
specs/010-governanca-papeis-escopos/
├── spec.md
├── plan.md                       # este arquivo
├── research.md                   # Fase 0 (R1–R15)
├── data-model.md                 # Fase 1 (1 entidade, restrições, ciclo, matriz)
├── quickstart.md                 # Fase 1 (preparo, validação, roteiro dos casos A–L)
├── contracts/
│   ├── governanca.md             # modelo, regras, consulta, operações, rejeições
│   ├── acesso-editor.md          # gate, rota → regra, respostas, recusas, cabeçalho
│   └── demonstracao-operador.md  # operador fictício, rotas, preparo
├── checklists/requirements.md
└── tasks.md                      # /speckit-tasks (não criado aqui)
```

### Source Code (repository root)

```text
config/
└── settings.py                    # ALTERADO: INSTALLED_APPS += "trajetoria.governanca"

trajetoria/
├── governanca/                    # NOVO — app de domínio, 1 modelo
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py                  # Papel, VinculoDeGovernanca (+ rotulo_de_atuacao)
│   ├── regras.py                  # pode_consultar_publicado, pode_consultar_rascunho,
│   │                              #   pode_elaborar_instrumento
│   ├── consultas.py               # vinculos_ativos
│   ├── operacoes.py               # registrar_vinculo, desativar_vinculo, Motivo,
│   │                              #   VinculoRejeitado
│   └── migrations/
│       ├── __init__.py
│       └── 0001_initial.py
├── editor/                        # 009
│   ├── acesso.py                  # NOVO: exige, Atuacao, recusa
│   ├── views.py                   # ALTERADO: @exige nas 25 views; _exigir_consulta em 5;
│   │                              #   filtro de rascunhos em pesquisas e pesquisa;
│   │                              #   _render repassa a atuação; docstring
│   ├── mensagens.py               # ALTERADO: BANNER; textos das recusas
│   ├── apresentacao.py            # ALTERADO: rótulo do cabeçalho de atuação
│   └── templates/editor/
│       ├── base.html              # ALTERADO: linha de atuação e "Trocar operador fictício"
│       ├── recusa.html            # NOVO
│       ├── pesquisas.html         # ALTERADO: "Nova Pesquisa" condicionada; aviso de
│       │                          #   somente publicadas
│       ├── pesquisa.html          # ALTERADO: idem para "Nova Versão"
│       └── versao.html            # ALTERADO: "Nova Versão a partir desta" condicionada
└── demonstracao/                  # 008 (adaptador temporário)
    ├── operador.py                # NOVO: OPERADORES_FICTICIOS, operador_em_uso,
    │                              #   usar_operador, esquecer_operador
    ├── urls.py                    # ALTERADO: 3 rotas de operador
    ├── views.py                   # ALTERADO: operadores, escolher_operador,
    │                              #   encerrar_operador
    ├── cenario.py                 # ALTERADO: recusa vínculo não fictício; vínculos A e B
    └── templates/demonstracao/
        └── operador.html          # NOVO

tests/
├── governanca/                    # NOVO (sem __init__.py, padrão do projeto)
│   ├── test_governanca_vinculo.py
│   ├── test_governanca_regras.py
│   ├── test_governanca_consultas.py
│   └── test_governanca_fronteiras.py
├── editor/
│   ├── conftest.py                # ALTERADO: `client` atua como operador A (CPAEG);
│   │                              #   fixtures cliente_csaeg, cliente_sem_vinculo,
│   │                              #   cliente_inativo, cliente_nao_identificado
│   ├── test_editor_autorizacao.py # NOVO
│   ├── test_editor_acesso.py      # ALTERADO: modo desligado também com cookie, cabeçalho
│   │                              #   e parâmetro de operador
│   ├── test_editor_fronteiras.py  # ALTERADO: PERMITIDOS acrescido (tabela acima)
│   └── test_editor_acessibilidade.py  # ALTERADO: recusas
└── interface/
    ├── test_demonstracao_operador.py  # NOVO
    ├── test_interface_demonstracao.py # ALTERADO: rotas de operador na lista do modo
    │                                  #   desligado
    ├── test_interface_fronteiras.py   # ALTERADO: governanca.operacoes em SO_NO_CENARIO
    └── test_interface_acessibilidade.py # ALTERADO: página de operador

README.md                          # ALTERADO: uma linha para o quickstart da 010
```

**Structure Decision**: monólito modular existente (ADR 0001), com **um app novo de
domínio** (`governanca`, um modelo) e extensões pequenas e localizadas no editor (009) e
no adaptador de demonstração (008).

- **Não mudam**: `academico` (001), `instrumento` (002), `formulario_2024` (003),
  `campanha` (004), `participacao` (005–007), `interface` (jornada da 008).
- **Testes existentes alterados**: só fixtures e listas de fronteira, nunca expectativas
  de comportamento editorial ou da jornada. O teste de ausência de autenticação da 005
  continua **sem alteração** e verde.

## Estratégia de testes

Detalhada em [research R15](research.md#r15--estratégia-de-testes).

| SC (spec) | Como é verificado |
|-----------|-------------------|
| SC-001 | `test_editor_autorizacao.py::test_toda_rota_declara_regra` e `::test_escritas_exigem_elaborar`: percorrem `editor.urls` e falham diante de rota sem `exige` ou de escrita sem `pode_elaborar_instrumento` |
| SC-002 | `test_editor_autorizacao.py::test_post_csaeg_recusado_em_toda_escrita`, parametrizado pelas 17 rotas: 403, `retrato` e `contagens` idênticos, operações da 002 com `monkeypatch` que falha se chamadas, sem erros de validação mesmo com dados inválidos. Perfis sem vínculo, inativo e não identificado numa rota representativa (o decorador é o mesmo em todas, garantido por SC-001) |
| SC-003 | Suíte existente da 009 executada com a fixture `client` como CPAEG, sem alteração de expectativas |
| SC-004 | `test_governanca_regras.py::test_regras_dependem_so_dos_vinculos` (assinatura) e `test_governanca_fronteiras.py` (sem `auth`, `is_staff`, `is_superuser`, modo de demonstração); `test_editor_autorizacao.py`: modo ligado + sem vínculo → 403 (rota representativa; cobertura por SC-001) |
| SC-005 | `test_editor_autorizacao.py::test_desativacao_vale_na_requisicao_seguinte` (GET do formulário, desativar, POST → 403, nada gravado) |
| SC-006 | `test_editor_fronteiras.py` (sem `publicar`, sem rotas de publicação/aprovação) e `test_governanca_fronteiras.py` (sem nomes de publicação/aprovação; `Papel` com exatamente 2 valores) |
| SC-007 | `test_governanca_fronteiras.py::test_um_modelo_cinco_campos` e `makemigrations --check`; `get_models()` dos demais apps inalterado |
| SC-008 | `test_governanca_fronteiras.py`: `Papel` = {CPAEG, CSAEG}; `regras` expõe exatamente 3 funções públicas; nenhum papel genérico |
| SC-009 | `test_editor_acesso.py::test_modo_desligado_nenhuma_rota_responde` (com cookie de operador, cabeçalho e parâmetro) e `test_interface_demonstracao.py` (rotas de operador → 404) |
| SC-010 | Roteiro manual do quickstart (passos 3, 6, 7) e `test_editor_autorizacao.py::test_textos_das_recusas` (cada variante com seu texto operacional e sem "Art.") |
| SC-011 | `test_editor_autorizacao.py::test_recusas_sem_termos_tecnicos`: `padroes_tecnicos` da 009 vazio e ausência de "role", "permission", "ACL", "policy", "scope" e do identificador do operador; as comissões aparecem sempre pelo nome por extenso da PAEG |

Testes da lista do solicitante, todos cobertos:

| Caso | Teste |
|------|-------|
| CPAEG ativo consulta publicada, consulta rascunho, edita rascunho | `test_editor_autorizacao.py::test_cpaeg_*` + suíte da 009 |
| CSAEG consulta publicada; não consulta rascunho; não edita | `::test_csaeg_*` |
| Sem vínculo não acessa; vínculo inativo não autoriza | `::test_sem_vinculo_*`, `::test_vinculo_inativo_*`; `test_governanca_regras.py` |
| CPAEG com unidade / CSAEG sem unidade inválidos | `test_governanca_vinculo.py` (restrição de banco e operação) |
| Múltiplos vínculos ativos | `test_governanca_regras.py`; `test_editor_autorizacao.py::test_cpaeg_e_csaeg`, `::test_duas_csaeg` |
| POST direto; recusa antes da validação; nenhuma operação da 002 | `::test_post_direto_recusado` |
| Publicação inexistente | `test_editor_fronteiras.py`, `test_governanca_fronteiras.py` |
| Demo identifica, vínculo autoriza; demo sem vínculo não autoriza | `test_demonstracao_operador.py`; `::test_operador_c_recusado` |
| Modo não demo sem identidade não expõe editor | `test_editor_acesso.py`; `test_demonstracao_operador.py::test_operador_em_uso_none_com_modo_desligado` |
| Demo sem operador leva à escolha | `test_editor_autorizacao.py::test_sem_operador_leva_a_escolha` (GET e POST → 302 fixo, nada gravado) e `test_demonstracao_operador.py` (escolha volta a `/editor/`) |
| Nenhum papel genérico; zero workflow | `test_governanca_fronteiras.py` |

Regressão: toda a suíte de 001 a 009 roda; só as fixtures e listas de fronteira
indicadas mudam.

## Complexity Tracking

**Vazio.** Não há violação da Constituição a justificar.

Escolhas registradas para revisão, sem violação:

- o app `governanca` (R1), uma responsabilidade transversal distinta, com um modelo;
- a condição `ativo` (R4; Clarifications), única informação além do mínimo absoluto;
- a ampliação explícita das listas de importação permitidas do editor e do adaptador de
  demonstração (R12), que preserva as fronteiras em vez de removê-las.

**Não adotado** (reavaliável com necessidade concreta): comando de gestão de vínculos;
tabela de operador; catálogo de unidades; regra de publicação; registro de autoria.

## Necessidade de voltar à spec ou às features anteriores

- **Spec da 010**: nenhuma mudança necessária. As decisões pré-plan estão em
  *Clarifications*. O plan não encontrou requisito impossível nem ambíguo.
- **009**: alterações de integração listadas (R12), sem mudança editorial. Os FR-003,
  FR-004 e FR-080 da 009 são substituídos conforme a spec da 010 (seção "Relação com
  outras features").
- **008**: só o adaptador de demonstração ganha o operador fictício e o preparo ganha
  vínculos. A jornada do egresso e a escolha de Pessoa não mudam.
- **002, 003, 004, 005, 006, 007, 001**: nada muda. O teste de ausência de autenticação
  da 005 continua sem alteração.
