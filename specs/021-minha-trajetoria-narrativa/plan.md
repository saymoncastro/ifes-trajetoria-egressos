# Implementation Plan: Minha Trajetória — narrativa visual personalizada

**Branch**: `claude/academic-data-structure-c7318c` | **Date**: 2026-10-04 | **Spec**:
[spec.md](spec.md)

**Input**: Feature specification from `specs/021-minha-trajetoria-narrativa/spec.md`, com
o clarify de 2026-10-04 e a revisão do plan pelo solicitante.

## Summary

Depois de concluir uma Participação ancorada em Conclusão Acadêmica, o egresso abre
"Minha trajetória no Ifes". A página reúne todas as Conclusões da sua Pessoa numa
narrativa determinística, feita de fatos institucionais, derivados seguros e, em P2,
contexto agregado institucional. O egresso leva para a rede social um **card vertical
9:16** (1080 × 1920), pensado para o story do Instagram.

- **PNG** é o artefato principal: a prévia, o salvar e o compartilhar usam ele.
- **SVG** é a representação-base de onde o PNG sai.

**Abordagem técnica:**

- **App `trajetoria/narrativa/`, sem models:** consultas, montagem pura, catálogo de
  formulações, template da página, template SVG do card com área segura, rasterização
  isolada (`resvg-py` com Open Sans Regular e Bold), três rotas GET e um script inline
  opcional de compartilhamento nativo.
- **P1 não altera o modelo.**
- **P2 entra por uma fronteira separada da `FonteAcademica`:**
  - `FonteDeContextoDaTrajetoria`, contrato puro em
    `fonte_academica/contexto_da_trajetoria.py`;
  - simulada em `fonte_academica/contexto_simulado.py`;
  - carregada por `contexto_trajetoria/carga.py` num app próprio, com dois models.
- **Isolamento:**
  - `obter_pessoa()`, `PessoaEncontrada`, `ConclusaoNaFonte` e `CAMPOS_DE_CONTEXTO` não
    mudam;
  - incorporação, acesso (018) e declaração (019) não importam nada da 021;
  - falha do enriquecimento não afeta identidade nem incorporação.
- **Vídeo fica fora**, na Feature 022.

## Technical Context

**Language/Version**: Python 3.13.

**Primary Dependencies**:
- As existentes: Django 5.2, psycopg 3, cryptography, XlsxWriter.
- **Nova:** `resvg-py` (MIT; *wheels* abi3 sem biblioteca de sistema), só para o PNG, com
  spike no CI antes de virar requisito (research R11).
- **Ativos novos:** Open Sans Regular e Bold (SIL OFL 1.1).
- Nenhuma dependência de front-end. Um script inline de cerca de 20 linhas, opcional
  (research R8).

**Storage**:
- PostgreSQL 16.
- P1 não cria tabelas.
- P2 cria duas tabelas no app novo `contexto_trajetoria` (migração `0001`), com
  `UniqueConstraint(nulls_distinct=False)`.

**Testing**:
- pytest e pytest-django em `tests/narrativa/` e `tests/contexto_trajetoria/`.
- Ajustes em `tests/interface/` e no teste do preparo da demonstração.
- Teste de volume marcado `volume`.

**Target Platform**:
- Servidor Linux (CI ubuntu-latest) e desenvolvimento em macOS arm64.
- Celulares (Safari no iOS, Chrome no Android) como alvo principal da página e do card.
- Desktop secundário.

**Project Type**: aplicação web Django modular, monólito.

**Performance Goals**:
- A página é montada com poucas consultas.
- A rasterização do PNG é síncrona, sob demanda. O spike mede o tempo; espera-se menos de
  1 s por card.

**Constraints**:
- Sem CDN e sem `staticfiles`. A fonte embutida não é servida ao navegador.
- Página e card funcionam sem JavaScript.
- SVG determinístico byte a byte.
- Nada persistido da narrativa ou do card.
- Restrito ao modo de demonstração.

**Scale/Scope**:
- Três rotas novas e três telas existentes com ajustes de texto ou ligação (confirmação,
  `/formacoes/` e `aviso.html`).
- Dois apps novos, dois models (P2) e um módulo de contrato novo.

## Constitution Check

*GATE: executado antes da Fase 0 e repetido depois da Fase 1, inclusive depois da revisão
de 2026-10-04.*

| # | Verificação | Princípios | Pré-Fase 0 | Pós-Fase 1 | Evidência / observação |
|---|-------------|------------|------------|------------|------------------------|
| 1 | Longitudinalidade | I | ✅ Conforme | ✅ Conforme | Só leitura. A Participação é gatilho (`exists`); nenhuma escrita (FR-008; `test_sem_efeito.py`) |
| 2 | Pessoa versus Conclusão Acadêmica | I, XI | ✅ Conforme | ✅ Conforme | Curso e unidade vêm de cada Conclusão. O agregado não tem FK para Pessoa ou Conclusão (data-model §2.2) |
| 3 | Múltiplas formações sem fusão | I, XI | ✅ Conforme | ✅ Conforme | A narrativa reúne as Conclusões da Pessoa e não une Pessoas (FR-016) |
| 4 | Múltiplas participações sem sobrescrita | I, VIII | ✅ Conforme | ✅ Conforme | N Participações → uma narrativa (SC-012) |
| 5 | Definição institucional de egresso | II | ✅ Conforme | ✅ Conforme | A métrica conta Conclusões pela mesma regra da fonte (contracts/contexto-da-trajetoria.md, obrigação 2) |
| 6 | Preservação histórica | VIII, XXVII | ✅ Conforme | ✅ Conforme | Snapshot e exportação inalterados (teste). Complemento e agregado nunca atualizados. Migração aditiva num app novo |
| 7 | Pesquisa / Versão / Campanha / Participação | VII, VIII | ✅ Conforme | ✅ Conforme | Narrativa e antecipação fora da Versão (FR-009, FR-070) |
| 8 | Proveniência | IV | ✅ Conforme | ✅ Conforme | `obtido_em`, `apurado_em` e `fonte`; `origem` em cada elemento serializado |
| 9 | Institucional × derivado × declarado | III | ✅ Conforme | ✅ Conforme | Derivados não gravados; Respostas não lidas; divergência de complemento só sinalizada |
| 10 | Desacoplamento de integrações | V, XV, XXV | ✅ Conforme | ✅ Conforme | **Capacidade separada da `FonteAcademica`** (R12). O adaptador real pode ler uma view larga e alimentar os dois contratos. 018, 019 e incorporação não conhecem a capacidade (teste de importação). `ContextoSimulado` obedece ao mesmo contrato |
| 11 | Fronteira do NIAE | VI | ✅ Conforme | ✅ Conforme | As cinco perguntas estão na spec. Relação com o Portal pendente (DP-2108) |
| 12 | Governança institucional | IX, X | ✅ Conforme | ✅ Conforme | Nenhuma competência normativa. Compartilhamento, marca e agregados reais ficam pendentes |
| 13 | Escopo por unidade | XII | N/A | N/A | Sem tela de operador |
| 14 | Privacidade, minimização, logs | XVI, XVII | ✅ Conforme | ✅ Conforme | Card conservador; nome por escolha; nome de arquivo neutro; `no-store`; nada guardado. O compartilhamento nativo é ação do egresso, sem envio a terceiros pelo sistema. Script inline sem recurso externo. Logs sem dado pessoal |
| 15 | Autorização | X, XII | ✅ Conforme | ✅ Conforme | Sessão da 018; elegibilidade em todas as rotas |
| 16 | Acessibilidade | XX | ✅ Conforme | ✅ Conforme | HTML semântico; `alt` na prévia; SVG com `title`/`desc`; conteúdo do card também em texto; corpo mínimo no card; contraste AA |
| 17 | Responsividade e jornada móvel | XIV, XXI | ✅ Conforme | ✅ Conforme | Celular como alvo; card 9:16 com área segura; salvar pelo gesto nativo; uma ação da confirmação até a página |
| 18 | Testes proporcionais ao risco | XXV, XXVI | ✅ Conforme | ✅ Conforme | Matriz da spec em research R17, com fronteiras 001/018/021, isolamento sob indisponibilidade e área segura |
| 19 | Risco de over engineering | XXII, XXIII, XXIV | ⚠ Atenção | ✅ Conforme, com justificativa | Dependência nativa, fontes, dois apps e o primeiro script. Ver Complexity Tracking. Duas métricas fechadas, um tema, um formato, nada persistido, sem vídeo, sem abstração genérica de "enriquecimento" |
| 20 | Exportabilidade | XVIII | N/A | N/A | A 021 não exporta. 013 intacta |
| 21 | Decisões pendentes explicitadas | XXIX | ✅ Conforme | ✅ Conforme | DP-2101 a DP-2109 e as herdadas. Acesso, nome e botão "Compartilhar" são hipóteses reversíveis |

**Resultado do gate**: APROVADO. A linha 19 só avança com a Complexity Tracking aceita em
revisão.

**Conflitos identificados e encaminhados:**

- **Títulos parecidos (FR-006):** `/formacoes/` passa a "Suas formações no Ifes". Aprovado
  pelo solicitante (R16).
- **Acoplamento da P2 com a 018 (versão anterior do plan):** o enriquecimento viajava em
  `PessoaEncontrada`. Corrigido com uma capacidade e um app separados (R1, R12, R13;
  FR-071).

## Decisões Pendentes

| ID | DECISÃO PENDENTE | Instância competente | Solução provisória (hipótese) | Como reverter |
|----|------------------|----------------------|-------------------------------|---------------|
| DP-2101 | Compartilhamento pelo egresso de representação com o nome do Ifes | CPAEG/Proex, ACS, encarregado de dados | Salvar, baixar ou compartilhar pelo celular, só na demonstração; nenhuma publicação pelo sistema | Remover a seção do card e suas rotas. A narrativa continua |
| DP-2102 | Marca no card | ACS | Sem marca gráfica; nome da instituição em texto | Acrescentar o ativo ao template |
| DP-2103 | Nome civil × nome social | Registro acadêmico, encarregado de dados | Nome da fonte; no card, só por escolha | Trocar a origem do nome em `consultas.py` |
| DP-2104 | Ingresso na fonte real | Registro acadêmico/DTI (Portão A) | Só `ContextoSimulado` informa | O adaptador real implementa a capacidade ou não |
| DP-2105 | Definição e exibição dos agregados reais | CPAEG/Proex, registro acadêmico, encarregado de dados | Só simulados, só na demonstração, sem limiar | Desligar a seção, ou aplicar o limiar em `consultas.py` |
| DP-2106 | Acervo de imagens | ACS, unidades | Nenhuma imagem | Ativo decorativo futuro, sem afirmação |
| DP-2107 | Correspondência entre Versões (= 002/DP-006) | CPAEG | Nenhum dado declarado | Spec futura |
| DP-2108 | Relação com o Portal do Egresso | Proex/CPAEG | Página no NIAE; contrato serializável | Outro sistema renderiza o mesmo JSON |
| DP-2109 | Vigência entre apurações | Registro acadêmico/DTI, CPAEG/Proex | Exibe só com exatamente uma apuração | Trocar a seleção em `consultas.py`, com teste |
| 008/DP-801 | Identidade visual definitiva | Proex/CPAEG, ACS | Tokens da 015 | Trocar os tokens |
| 001/DP-006 | Gatilho de incorporação e de carga de contexto | — | O preparo da demonstração carrega o contexto depois da incorporação | Mesmo gatilho real, chamando `carregar_contexto` à parte |

## Project Structure

### Documentation (this feature)

```text
specs/021-minha-trajetoria-narrativa/
├── spec.md
├── plan.md              # este arquivo
├── research.md          # Fase 0 (R1–R18), revisado em 2026-10-04
├── data-model.md        # Fase 1
├── quickstart.md        # Fase 1
├── contracts/
│   ├── narrativa.md               # JSON da TrajetoriaNarrativa (versão 1)
│   ├── catalogo.md                # formulações e vedações
│   ├── rotas.md                   # rotas novas e telas alteradas
│   ├── card.md                    # card 9:16 para rede social
│   └── contexto-da-trajetoria.md  # capacidade P2 separada da FonteAcademica
├── checklists/requirements.md
└── tasks.md             # /speckit-tasks
```

### Source Code (repository root)

```text
trajetoria/
├── narrativa/                         # NOVO (P1), sem models
│   ├── apps.py
│   ├── contrato.py                    # dataclasses; serializar()
│   ├── montagem.py                    # montar(entrada) — pura
│   ├── catalogo.py                    # formulações e condições
│   ├── consultas.py                   # elegibilidade; banco → EntradaDaNarrativa; seleção de agregados (P2, só leitura)
│   ├── card.py                        # card_svg(compartilhavel, tema, nome); constantes do tema e da área segura
│   ├── rasterizacao.py                # png_de(svg) -> bytes | None — única importação de resvg_py
│   ├── fontes/                        # OpenSans-Regular.ttf, OpenSans-Bold.ttf, OFL.txt
│   ├── views.py                       # 3 rotas GET
│   ├── urls.py
│   └── templates/narrativa/
│       ├── minha_trajetoria.html      # inclui o script inline opcional de compartilhamento
│       ├── narrativa.css
│       └── card.svg
├── contexto_trajetoria/               # NOVO (P2)
│   ├── apps.py
│   ├── models.py                      # ComplementoDaConclusao, ContextoInstitucionalAgregado
│   ├── carga.py                       # carregar_contexto(fonte_de_contexto, pessoa)
│   └── migrations/0001_initial.py
├── fonte_academica/
│   ├── contrato.py                    # INALTERADO
│   ├── contexto_da_trajetoria.py      # NOVO (P2): contrato puro da capacidade
│   ├── contexto_simulado.py           # NOVO (P2): ContextoSimulado
│   ├── cenarios.py                    # P2: COMPLEMENTOS, AGREGADOS (fictícios)
│   └── simulada.py                    # INALTERADO
├── academico/                         # INALTERADO
├── demonstracao/cenario.py            # P2: carga de contexto após a incorporação, em savepoint por Pessoa
├── interface/
│   ├── mensagens.py                   # ANTECIPACAO; TITULO_TRAJETORIA → "Suas formações no Ifes"
│   ├── views.py                       # concluida: ligação para a narrativa; formacoes: ligação + antecipação
│   └── templates/interface/{concluida,aviso,formacoes}.html
config/
├── settings.py                        # INSTALLED_APPS += narrativa, contexto_trajetoria
└── urls.py                            # include("trajetoria.narrativa.urls")
docs/adr/0006-rasterizacao-do-card.md  # resultado do spike e decisão sobre o PNG
tests/
├── dependencias.py                    # + resvg-py, com justificativa
├── interface/test_interface_{conclusao,formacoes}.py   # ajustes
├── narrativa/                         # NOVO
└── contexto_trajetoria/               # NOVO
specs/001-nucleo-academico-fonte-simulada/contracts/{fonte-academica,cenarios-simulados}.md  # P2: notas
specs/014-polish-jornada-egresso/spec.md        # nota FR-030/FR-041
specs/018-identificacao-acesso-egresso/spec.md  # nota: Minha Trajetória → 021
```

**Structure Decision**:
- A apresentação fica em `narrativa`, sem models.
- O enriquecimento P2 fica em `contexto_trajetoria`, com models e carga.
- O contrato da capacidade fica em `fonte_academica`, num módulo separado de
  `contrato.py`.
- `academico`, `acesso`, `declaracao` e `simulada.py` não mudam.

### Ordem sugerida para as tasks (revisada em 2026-10-04)

1. **Comprovar o objetivo primeiro (porta de decisão):**
   - spike do PNG no macOS e no CI;
   - card SVG 9:16 com o pior caso (nome longo, quatro cursos longos, "e mais N", um par
     de agregados);
   - PNG do pior caso inspecionado no celular.
   - Se algo falhar, parar e decidir com o solicitante. O SVG sozinho não atende ao story.
2. **P1-a — Narrativa pura:** contrato, catálogo, montagem e serialização.
3. **P1-b — Página:** consultas, view e template; confirmação e `/formacoes/`; fronteiras e
   não interferência.
4. **P1-c — Card na página:** rotas, prévia `<img>`, atualização com nome, baixar,
   "Compartilhar" (destinos decididos pelo dispositivo), acessibilidade e validação no
   celular. **Parar para validação antes da P2.**
5. **P2-a — Capacidade e carga:** contrato, `ContextoSimulado`, app
   `contexto_trajetoria`, carga, preparo e isolamento.
6. **P2-b — Narrativa com P2:** ingresso e agregados na página e no card.
7. **Fechamento:** notas de revisão, quickstart e evidências.

**P3 (fora deste plan):** segundo tema (FR-065), formato 4:5 para o feed, marcos, dados
declarados, imagens e vídeo (022). Dependem de spec ou de decisão pendente.

### Revisão de 2026-10-05 — convergência visual

A [auditoria de convergência visual](../../docs/auditorias/2026-10-04-021-convergencia-visual.md)
reabriu a P1 visual. As decisões do solicitante foram:

- **V1:** assinatura oficial no card de demonstração.
- **V2:** ilustração vetorial própria.
- **V3:** fecho "Essa história também é minha." com `#SouEgressoIfes`.

O que muda:

- **Card:** o `narrativa/card.py` passa a compor por zonas (research R19).
- **Imagens:** entra o catálogo `narrativa/imagens.py` com uma ilustração genérica
  (research R20).
- **Página:** passa a ter capítulos (research R21).

Domínio, montagem, P2 e rotas não mudam. Entra uma fase nova de tasks, "Convergência
visual", com porta de revisão do solicitante sobre os PNGs de referência antes do merge.

**Constitution Check, linha 19 (overengineering), revisitada.** Continua conforme:

- componentes são funções, sem framework;
- um ativo vetorial próprio;
- nenhuma dependência nova;
- nenhuma fonte nova.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Dependência nativa nova (`resvg-py`) | O PNG é o artefato que vai para o story. Precisa sair do mesmo SVG (FR-031) e ser reprodutível (FR-032) | cairosvg/pyvips exigem biblioteca do sistema (Cairo vetado); Pillow cria dois renderizadores; canvas exige JavaScript e depende do dispositivo; Chromium é a 022. **Mitigação:** spike no CI, módulo único, fallback SVG |
| Arquivos de fonte versionados (só Open Sans Regular e Bold) | Sem fonte embutida, o PNG depende da máquina | Fontes do sistema não são determinísticas; base64 no SVG infla um formato secundário |
| Dois apps novos (`narrativa`, `contexto_trajetoria`) | `narrativa` isola a devolutiva da jornada (008/014). `contexto_trajetoria` garante que 001, 018 e 019 não importem nada da 021 (FR-071) | `interface` mistura regras; models em `academico` seriam carregados pela 018; models em `narrativa` quebrariam "não persiste nada" |
| Duas tabelas novas (P2) | Fatos institucionais com proveniência, carregados à parte e lidos depois sem consultar a fonte | Ampliar `ConclusaoAcademica` muda o núcleo para enriquecer a narrativa (E4); consulta na hora não serve a fonte em lote e acoplaria a página à fonte |
| Ativo de imagem versionado (uma ilustração vetorial própria) e catálogo de imagens em código | A peça precisa de um elemento visual dominante (SC-015), e a imagem precisa de procedência e legenda honesta | Sem imagem, o card volta a ser relatório; foto de terceiros exige licença e crédito; IA é vedada |
| Primeiro JavaScript do projeto (cerca de 20 linhas inline, opcional) | No celular, o menu de compartilhamento do sistema leva o PNG ao aplicativo escolhido com um toque. Os destinos dependem do dispositivo, e o Instagram não é garantido | Só salvar e baixar funciona e continua sendo o caminho base. O script só encurta o caminho, sem recurso externo, e não é necessário para nenhuma função |
