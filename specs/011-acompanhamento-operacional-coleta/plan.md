# Implementation Plan: Acompanhamento operacional da coleta

**Branch**: `claude/feature-011-acompanhamento-coleta-20772c` | **Date**: 2026-10-02 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/011-acompanhamento-operacional-coleta/spec.md`

## Summary

O plan entrega a menor implementação capaz de responder, para um operador institucional
já identificado:

> "Quais Campanhas posso acompanhar, qual é a população elegível atual, quantas
> Participações existem, quantas foram concluídas, quantas não foram, e como isso se
> distribui em recortes acadêmicos simples?"

Usa exclusivamente os dados transacionais de 001, 004, 005, 006 e 010. **Não é
plataforma analítica.**

Abordagem técnica (detalhes em [research.md](research.md)):

- **Zero modelos, zero migrations, zero índices** (R1).
- **App pequeno `trajetoria/acompanhamento`, sem models** (R2): consultas, apresentação
  (inclui os textos), acesso, duas views, duas rotas e templates.
- **Uma regra concreta na governança** (R3): `pode_acompanhar_coleta(vinculos)` e
  `escopo_de_acompanhamento(vinculos)`.
  - Semântica explícita: CPAEG ativo → institucional; CSAEG ativo → suas unidades; sem
    vínculo ativo → nada.
  - Sem `Permission`, registro, policy engine ou "qualquer vínculo".
- **Elegibilidade da 004 reutilizada sem regra paralela e sem mudança na 004** (R4): o
  contrato público é `populacao_no_momento(campanha)`, que já existe e devolve um
  QuerySet componível. A 011 só o refina com o escopo e agrega. `_filtro` continua
  privado.
- **Escopo aplicado na consulta** (R5): `Q(unidade__in=escopo.unidades)` antes de
  contar, nos dois lados (elegíveis e Participações), pela unidade da Conclusão. O
  critério de unidades da Campanha **não** é reaplicado: entra só via
  `populacao_no_momento`. As "unidades relevantes" servem só à apresentação;
  `ArrayField overlap` para a visibilidade.
- **Consultas claras** (R6): as mesmas duas consultas de totais por Campanha servem à
  lista e ao detalhe. A lista é proporcional ao número de Campanhas, o que é aceito. O
  detalhe soma uma consulta por lado para o recorte, sem consulta por linha. Nenhum
  registro individual é carregado e nenhuma Resposta é lida. O número de consultas é
  proteção contra regressão, não requisito.
- **Seis recortes, todos existentes na Conclusão** (R7), por GET fechado `?recorte=`, um
  por vez; "não informado" como linha; ordem textual ou cronológica (R8).
- **Taxas `Decimal | None` em memória** (R9): `None` → "—" / "não se aplica"; sem teto.
- **Rótulos por estado da 004, sem estado novo** (R10). **"Instrumento ainda não
  publicado"** para quem não consulta rascunho (R11).
- **Acesso**: identificação (010) → vínculos → regra → escopo → Campanha visível. Recusa
  403 sem dados; 404 para inexistente e para recorte inválido (R12).
- **Demonstração** (R13, R14):
  - destino fechado `?destino=acompanhamento` na escolha de operador;
  - operadores A/B/C da 010 **preservados** (B = CSAEG Vitória);
  - **uma** Campanha fictícia acrescentada ao preparo: nunca aberta, Versão baseline em
    rascunho, critério {Serra, Vitória}. B a vê com 3 elegíveis de Vitória; A a vê com 6.
    Não muda a jornada 007/008.

## Technical Context

**Language/Version**: Python 3.13 (ADR 0001).

**Primary Dependencies**: Django 5.2 LTS (ORM com `Count(filter=…)`, `aggregate`,
`values().annotate()`, lookup `overlap` de `ArrayField` de `django.contrib.postgres`,
views de função, templates) e psycopg 3. **Nenhuma dependência nova**, nenhum
`django.contrib.*` acrescentado, nenhuma biblioteca de gráficos.

**Storage**: PostgreSQL 16+ (ADR 0001). **Somente leitura** nesta feature.

**Testing**: pytest + pytest-django. Recursos usados:

- `django_assert_max_num_queries` como proteção contra N+1 (comparação entre volumes,
  não número fixo);
- `CaptureQueriesContext` para provar que a tabela de Resposta não é lida;
- `ast` para fronteiras estruturais, como na 010.

**Target Platform**: aplicação web server-rendered, ambiente local de demonstração
(modo `TRAJETORIA_DEMONSTRACAO`). Não há exposição produtiva (010/DP-1001).

**Project Type**: monólito Django modular (apps em `trajetoria/`).

**Performance Goals**: sem consulta por linha de recorte, por Conclusão ou por
Participação; detalhe com número de consultas independente do número de linhas; lista
proporcional ao número de Campanhas (≈ 2 consultas por Campanha), aceito no MVP.
Referência observada (não contrato): lista ≈ 2 + 2N, detalhe ≈ 6. Sem meta de latência
além de páginas responsivas no ambiente local; sem otimização sem medida.

**Constraints**:

- sem persistência;
- sem cache, Redis, Celery, visão materializada ou SQL bruto;
- sem JavaScript obrigatório;
- sem leitura de `Resposta`/`RespostaOpcao`/`Pessoa`;
- escopo aplicado no banco;
- WCAG 2.1 AA / eMAG como direção, a partir de 320 px.

**Scale/Scope**: dezenas de Campanhas, até dezenas de milhares de Conclusões e
Participações no futuro; poucos operadores. Duas telas, uma recusa e um ajuste na
escolha de operador fictício.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Verificação | Princípios | Pré-Fase 0 | Pós-Fase 1 | Evidência / observação |
|---|-------------|------------|------------|------------|------------------------|
| 1 | Longitudinalidade (Pessoa → Conclusão → Participação → Respostas) | I | ✅ Conforme | ✅ Conforme | Somente leitura; contagem por Campanha, sem fundir Campanhas nem eleger "a mais recente" (spec FR-001, FR-111; data-model §4) |
| 2 | Pessoa versus Conclusão Acadêmica | I, XI | ✅ Conforme | ✅ Conforme | Unidade e curso vêm da Conclusão; contagens de Conclusões e Participações, nunca de Pessoas (FR-039; R5, R16) |
| 3 | Múltiplas formações sem fusão | I, XI | ✅ Conforme | ✅ Conforme | Cada Conclusão conta separadamente; texto permanente na lista (contracts/rotas.md) |
| 4 | Múltiplas participações sem sobrescrita | I, VIII | ✅ Conforme | ✅ Conforme | Nada é escrito; a mesma Conclusão conta em cada Campanha (spec, Edge Cases) |
| 5 | Definição institucional de egresso | II | ✅ Conforme | ✅ Conforme | Elegíveis = predicado da 004 sobre Conclusões reconhecidas pela 001 (R4) |
| 6 | Preservação histórica | VIII, XXVII | ✅ Conforme | ✅ Conforme | Zero migrations e zero escrita; aviso de população atual em ENCERRADA (R1, R10) |
| 7 | Pesquisa/Versão/Campanha/Participação distintas | VII, VIII | ✅ Conforme | ✅ Conforme | Nenhuma estrutura alterada; Versão só identificada (R11) |
| 8 | Proveniência proporcional | IV | ✅ Conforme | ✅ Conforme | Legenda "dados do registro acadêmico institucional" em todo recorte (FR-060; contracts/rotas.md) |
| 9 | Institucional × derivado × declarado | III | ✅ Conforme | ✅ Conforme | Recortes só com atributos da Conclusão; Q14 e demais Respostas não lidas, verificado por SQL capturado (FR-061, FR-090; R6, R16) |
| 10 | Desacoplamento de integrações | V, XV, XXV | ✅ Conforme | ✅ Conforme | Identificação continua no adaptador `demonstracao` (010); a regra não depende dele (R3, R12) |
| 11 | Fronteira do NIAE | VI | ✅ Conforme | ✅ Conforme | "Acompanhamento operacional da coleta" está na Fronteira do Domínio; sem BI, exportação ou comunicação (spec, Fronteira do NIAE) |
| 12 | Governança institucional | IX, X | ✅ Conforme | ✅ Conforme | Regra fundada em PAEG Art. 21, I, III; Art. 22, I, IV, como interpretação B; nenhuma ação de Campanha (004/DP-402 aberta); periodicidade não inferida (R3; contracts/governanca.md) |
| 13 | Escopo por unidade e visão institucional | XII | ✅ Conforme | ✅ Conforme | CPAEG institucional; CSAEG pelas unidades dos vínculos; aplicado no banco; sem tenant nem banco por unidade (R5) |
| 14 | Privacidade, minimização, logs | XVI, XVII | ⏸ DECISÃO PENDENTE | ⏸ DECISÃO PENDENTE | Só agregados; nenhum identificador individual; teste de ausência de nomes e UUIDs (R16). **DP-1101** (pequenos grupos) aberta: sem limiar; exposição produtiva dos recortes finos deve revisitá-la |
| 15 | Autorização (menor privilégio; técnico ≠ normativo) | X, XII | ✅ Conforme | ✅ Conforme | Verificação no servidor antes de qualquer consulta; recusa sem dados; nenhuma marca técnica consultada; teste estrutural de cobertura das rotas (R12) |
| 16 | Acessibilidade | XX | ✅ Conforme | ✅ Conforme | HTML semântico; `caption`, `th scope`; "—" com texto acessível; troca de recorte por link (R15) |
| 17 | Responsividade | XIV, XXI | ✅ Conforme | ✅ Conforme | 320 px e zoom 200%; só a tabela rola, em região rotulada e focável (R15) |
| 18 | Testes proporcionais ao risco | XXV, XXVI | ✅ Conforme | ✅ Conforme | "Estratégia de testes" abaixo cobre escopo, recusa, definições, soma, orçamento, privacidade e demonstração |
| 19 | Over engineering | XXII, XXIII, XXIV | ✅ Conforme | ✅ Conforme | Zero modelos; nenhuma abstração de métrica, dimensão ou dashboard; `Recorte` é Enum fechado; sem cache ou fila (R1, R2, R7; "Sinais de over engineering") |
| 20 | Exportabilidade | XVIII | N/A | N/A | Sem exportação nesta feature (Feature 013) |
| 21 | Decisões pendentes explicitadas | XXIX | ✅ Conforme | ✅ Conforme | DP-703, DP-601, DP-408, DP-507, DP-1101, DP-1102 e demais mantidas com tratamento provisório declarado ("Decisões Pendentes") |

**Resultado do gate**: **APROVADO** (pré-Fase 0 e pós-Fase 1). O item 14 depende de
decisão pendente (DP-1101) e não de violação: a exposição atual é não produtiva, com dados
fictícios e agregados restritos ao escopo.

**Conflitos identificados**: Nenhum.

- A capacidade nova não conflita com a 010: a 010 previu a 011 como consumidora
  (010 FR-017).
- O "exatamente três capacidades" da 010 (SC-008) passa a "três do editor e uma do
  acompanhamento", registrado na spec (FR-141).

## Decisões Pendentes

| ID | DECISÃO PENDENTE | Instância competente | Solução provisória (hipótese) | Como reverter |
|----|------------------|----------------------|-------------------------------|---------------|
| DP-1101 | Tratamento de grupos pequenos nos recortes | CPAEG/Proex + encarregado de dados | Nenhuma supressão nem limiar; agregados restritos ao escopo; só ambiente não produtivo. **A exposição produtiva dos recortes finos (curso, ano) DEVE revisitar esta DP antes de ocorrer** | Tratamento localizado em `consultas.campanha_acompanhada` e no template da tabela; nenhuma estrutura a migrar |
| DP-1102 | Definição institucional de coorte | CPAEG/Proex | Recorte "Ano de conclusão", sem faixas nem o nome "coorte" | Novo membro do Enum `Recorte` quando houver definição |
| 004/DP-408 | Fotografia da população | Proex/CPAEG | "Elegíveis atuais" sob demanda, com rótulo e aviso | Feature 012; o acompanhamento passaria a ler a fotografia |
| 007/DP-703 | Participação sem Respostas conta como iniciada? | CPAEG/Proex | Conta (existência da Participação) | Filtro adicional em `Participacao`, sem ler conteúdo, só existência de Resposta, se a decisão vier |
| 006/DP-601 | Concluída por recusa (Q1) | CPAEG/Proex + encarregado | Conta como concluída; rótulo "Participações concluídas" | Exigiria ler Q1; decisão e feature próprias |
| 005/DP-503 | Destino das não concluídas | CPAEG/Proex | Rótulo "em andamento" / "iniciadas e não concluídas", sem "abandono" | Só rótulo em `apresentacao.py` |
| 005/DP-507 | Correção acadêmica × Participação | CPAEG | Sem filtro retroativo; taxa sem teto; nenhuma infraestrutura (hoje não ocorre) | Feature 012 (reconciliação histórica) |
| 005/DP-505 | Acesso a dados identificados | CPAEG/Proex + encarregado | Nada identificado exposto | Feature própria |
| 010/DP-1005 | Designação canônica de unidades | Ifes | Igualdade textual exata entre vínculo, Campanha e Conclusão | Normalização na fonte ou catálogo futuro |
| 010/DP-1001 | Identificação produtiva de operadores | Ifes (DTI, Proex) | Só modo de demonstração | Trocar o adaptador; a regra não muda |
| 010/DP-1006 | Atuação de Proex/DIREC/Proen | Proex | Não representadas | Nova atuação nomeada na regra, se decidido |
| 004/DP-402 | Gestão de Campanha | Proex/CPAEG | Nenhuma ação exposta | Feature própria |

Demais DPs herdadas (004/DP-401, DP-404, DP-405, DP-407, DP-409; 001/DP-004, DP-005,
DP-007, DP-009; 005/DP-501, DP-504; 008/DP-803; 002/DP-001, DP-006) permanecem abertas e
não são afetadas pelo desenho (spec, "Decisões Pendentes").

## Project Structure

### Documentation (this feature)

```text
specs/011-acompanhamento-operacional-coleta/
├── spec.md
├── plan.md              # este arquivo
├── research.md          # Fase 0 (R1–R16)
├── data-model.md        # Fase 1: nenhuma entidade; objetos de valor e regras de derivação
├── quickstart.md        # Fase 1: validação de ponta a ponta
├── contracts/
│   ├── rotas.md         # rotas, ordem de verificação, conteúdo das páginas, recusas
│   ├── consultas.md     # funções de consulta e apresentação, invariantes
│   └── governanca.md    # pode_acompanhar_coleta e escopo_de_acompanhamento
├── checklists/
│   └── requirements.md
└── tasks.md             # Fase 2 (/speckit-tasks — NÃO criado por este comando)
```

### Source Code (repository root)

```text
trajetoria/
├── acompanhamento/                    # NOVO app, sem models.py e sem migrations/
│   ├── __init__.py
│   ├── apps.py
│   ├── consultas.py                   # campanhas_visiveis, unidades_relevantes,
│   │                                  # campanhas_acompanhadas, campanha_acompanhada,
│   │                                  # recortes_oferecidos; Indicadores, Recorte,
│   │                                  # LinhaDeRecorte, CampanhaAcompanhada
│   ├── apresentacao.py                # percentual, rótulos, avisos, textos, instrumento, ordem
│   ├── acesso.py                      # @acompanhamento + recusa
│   ├── views.py                       # campanhas, campanha
│   ├── urls.py                        # 2 rotas
│   └── templates/acompanhamento/
│       ├── base.html
│       ├── campanhas.html
│       ├── campanha.html
│       ├── _tabela_recorte.html
│       └── recusa.html
├── governanca/regras.py               # ALTERADO: + EscopoDeAcompanhamento, pode_acompanhar_coleta,
│                                      #           escopo_de_acompanhamento
├── demonstracao/
│   ├── cenario.py                     # ALTERADO: + Campanha fictícia nunca aberta {Serra, Vitória}
│   │                                  #   com a baseline; operadores A/B/C intactos
│   ├── views.py                       # ALTERADO: destino fechado após escolher operador
│   ├── middleware.py                  # docstring: menciona /acompanhamento/ (sem mudança de código)
│   └── templates/demonstracao/operador.html   # ALTERADO: campo oculto destino + links às duas áreas
config/
├── settings.py                        # ALTERADO: + "trajetoria.acompanhamento" em INSTALLED_APPS
└── urls.py                            # ALTERADO: + path("acompanhamento/", include(...))

tests/
├── acompanhamento/                    # NOVO
│   ├── conftest.py                    # cenário de referência: Conclusões em Serra, Vitória,
│   │                                  # Cefor e sem unidade; Campanhas I, R, P, E; vínculos
│   ├── construcao.py                  # fábricas pequenas (reusa tests/campanha/construcao.py)
│   ├── test_acompanhamento_regra.py   # (ou em tests/governanca) matriz da regra
│   ├── test_acompanhamento_visibilidade.py
│   ├── test_acompanhamento_indicadores.py
│   ├── test_acompanhamento_recortes.py
│   ├── test_acompanhamento_estados.py
│   ├── test_acompanhamento_acesso.py
│   ├── test_acompanhamento_consultas.py   # anti-N+1 (comparação); nenhuma Resposta no SQL
│   ├── test_acompanhamento_privacidade.py
│   ├── test_acompanhamento_apresentacao.py
│   ├── test_acompanhamento_acessibilidade.py
│   └── test_acompanhamento_fronteiras.py  # sem models/migrations; imports proibidos; termos
├── governanca/test_governanca_regras.py      # ALTERADO: + matriz e invariante da regra nova
├── governanca/test_governanca_fronteiras.py  # ALTERADO: docstring/conjunto de nomes
└── interface/test_demonstracao_operador.py   # + destino fechado (expectativas existentes intactas)
```

**Structure Decision**: monólito Django existente, com um app novo e pequeno de
**leitura**. O app depende de `campanha`, `participacao`, `academico`, `instrumento`
(só leitura), `governanca` e `demonstracao` (identificação). Nenhum desses depende dele.
`governanca` continua sem importar nenhum app de domínio (teste existente da 010).

## Alterações em features anteriores

| Feature | Alteração | Semântica |
|---------|-----------|-----------|
| 001 | Nenhuma | — |
| 002/003 | Nenhuma | — |
| 004 | Nenhuma. `populacao_no_momento` é consumida como está | **Inalterada** |
| 005/006 | Nenhuma | `Participacao` e `concluida_em` lidos como estão |
| 007 | Nenhuma | DP-703 permanece |
| 008 | Nenhuma de comportamento; docstring do middleware cita a nova área | Jornada intacta |
| 009 | Nenhuma | Editor e matriz intactos |
| 010 | `governanca/regras.py`: + 1 dataclass + 2 funções; `demonstracao`: destino fechado após a escolha e uma Campanha fictícia no preparo | Modelo de vínculo, papéis, três regras, operadores A/B/C, editor e autenticação **intactos** |

## Estratégia de testes

Cada linha é ao menos um teste automatizado. Os dados são fictícios, construídos pelas
operações das features anteriores, nunca por escrita direta que contorne regra.

**Visibilidade e escopo** (US1, US3, US4, US12; FR-012 a FR-023; casos C, D, E, F, G)

| Teste | Resultado |
|-------|-----------|
| CPAEG lista todas as Campanhas, inclusive EM PREPARAÇÃO, EM COLETA, ENCERRADA e nunca aberta expirada | Todas |
| CSAEG Vitória lista Campanha sem critério de unidades | Visível |
| CSAEG Serra lista Campanha restrita a {Serra, Cefor} | Visível |
| CSAEG Vitória **não** lista Campanha restrita a {Serra, Cefor} | Ausente |
| Campanha restrita a {Serra} com zero elegíveis de Serra | Visível ao CSAEG Serra, com 0 |
| Campanha sem critério de unidade e com critério de nível | Visível a CSAEG de qualquer unidade |
| Grafia diferente ("Campus Serra") | Não visível; sem normalização |
| CPAEG vê total institucional, inclusive Conclusões sem unidade | Total = `populacao_no_momento(c).count()` |
| CSAEG vê só sua unidade | Total = contagem só de Vitória; nenhuma linha de outra unidade nem "Unidade não informada" |
| Dois CSAEG (Serra, Vitória) | União nas Campanhas e nos números; em Campanha restrita a {Serra}, só Serra |
| CPAEG + CSAEG | Institucional |
| Vínculo CPAEG desativado entre requisições | Requisição seguinte só com a unidade CSAEG (SC-013) |
| Matriz da regra (`contracts/governanca.md`) e invariante `pode ⇔ escopo is not None` | Conforme |

**Acesso** (US5; FR-150 a FR-158; caso N)

| Teste | Resultado |
|-------|-----------|
| Sem operador (modo ligado), lista e detalhe | 302 para a escolha com `destino=acompanhamento`; após escolher, 302 para `/acompanhamento/` |
| Operador C (sem vínculo), lista e detalhe | 403 "sem atuação" |
| CSAEG Vitória → URL do detalhe de Campanha R, com e sem `?recorte=` | 403 "fora do escopo"; HTML sem nome, período, instrumento nem números de R |
| Campanha inexistente, com vínculo | 404. Sem vínculo: 403 antes |
| `?recorte=coorte`, `?recorte=` vazio, `?recorte=unidade&recorte=curso` | 404 |
| Modo desligado | 404 em todas as rotas |
| POST nas duas rotas | 405 |
| Estrutural: toda rota de `acompanhamento.urls` marcada pelo decorador | Falha se surgir rota sem marca |
| Escolha de operador com `destino` desconhecido | `/editor/` |

**Indicadores** (US2, US6; FR-030 a FR-039; casos H, I, J, K)

| Teste | Resultado |
|-------|-----------|
| Elegíveis atuais corretos para população ampla, ano, unidade, nível, modalidade e forma de oferta | Igual à 004 |
| Iniciadas corretas, inclusive Participação sem nenhuma Resposta | Conta |
| Concluídas corretas, inclusive concluída só com Q1 = "Não" | Conta; nenhuma Resposta lida |
| Iniciadas e não concluídas = iniciadas − concluídas | Conforme |
| Campanha sem Participações | 0, 0, 0; taxas 0,0% |
| Elegíveis atuais = 0 | Taxas `None` → "—" / "não se aplica"; nunca "0%", "NaN", "∞" |
| Arredondamento | 1/8 → 12,5%; 1/3 → 33,3%; 2/3 → 66,7%; `ROUND_HALF_UP` |
| Taxa > 100% (construída em teste por Conclusão alterada diretamente, simulando 001/DP-005) | Mostrada como calculada, sem teto nem erro. Sem código específico para o caso |
| Nova Conclusão elegível incorporada entre duas consultas | Elegíveis +1 |
| Participação concluída entre duas consultas | Concluídas +1, não concluídas −1 |
| Banco idêntico antes e depois de abrir todas as páginas | Nenhuma escrita (contagem de linhas por tabela) |

**Estados** (US10, US11; FR-043 a FR-046; caso L)

| Teste | Resultado |
|-------|-----------|
| EM PREPARAÇÃO | "A coleta ainda não começou"; elegíveis exibidos; Participações reais (0) |
| EM COLETA | "Em andamento"; aviso de momento da consulta |
| ENCERRADA (explícita e por fim do período) | Aviso de população atual; data e forma do encerramento; "Iniciadas e não concluídas" |
| ENCERRADA nunca aberta | "Não chegou a entrar em coleta" |
| Versão em RASCUNHO, operador CSAEG | "Instrumento ainda não publicado"; sem designação, nome da Pesquisa nem link `/editor/` |
| Versão em RASCUNHO, operador CPAEG | Pesquisa — designação + link |
| Período não definido | "Período não definido" |

**Recortes** (US7, US8, US9; FR-050 a FR-061; caso M)

| Teste | Resultado |
|-------|-----------|
| Por unidade, CPAEG, Campanha I | Uma linha por unidade presente + "Unidade não informada" |
| Por unidade, Campanha R | Unidades do critério, inclusive com 0 |
| Por unidade, CSAEG de duas unidades, Campanha sem critério | As duas unidades, inclusive com 0 |
| Por curso: homônimo em Serra e Vitória | Duas linhas; CSAEG Serra vê só Serra; coluna Unidade omitida para unidade única |
| Por nível, modalidade, forma de oferta e ano | Valores como registrados; "Graduação" ≠ "graduação" |
| "Não informado" em cada dimensão | Linha própria, por último |
| Ordem | Texto previsível (dobrado/exato), ano crescente; nunca por indicador (teste com dados em que a ordem por taxa difere) |
| **Soma das linhas = total** | Seis recortes × escopos institucional, CSAEG uma unidade, CSAEG duas unidades |
| Q14 com valor diferente do nível institucional | Recorte usa o nível da Conclusão |
| Recortes oferecidos | Seis para CPAEG e CSAEG múltipla; cinco (sem unidade) para CSAEG única |

**Consultas e proveniência** (FR-070 a FR-073, FR-090; SC-008, SC-009)

| Teste | Resultado |
|-------|-----------|
| Detalhe, cada recorte, com 3 e com 30 valores distintos na dimensão | Mesmo número de consultas nos dois casos (anti-N+1; não é número fixo da spec) |
| Lista com 1 e com 3 Campanhas | Crescimento ≤ 2 consultas por Campanha acrescentada; nenhuma consulta por Participação ou Conclusão |
| SQL capturado de todas as páginas | Não referencia as tabelas de `Resposta` nem de `RespostaOpcao` |
| Elegíveis da lista = elegíveis do detalhe | Para cada Campanha e escopo |

**Privacidade** (FR-080 a FR-084; SC-005)

| Teste | Resultado |
|-------|-----------|
| HTML de lista, detalhe e seis recortes, para CPAEG e CSAEG | Não contém nomes, `id_externo` de Pessoa/Conclusão, UUID de Conclusão ou de Participação, nem texto de Resposta |
| Estrutural (AST) | `trajetoria/acompanhamento` não importa `Pessoa`, `Resposta`, `RespostaOpcao` nem operações de escrita (`operacoes`) |

**Fronteiras e linguagem** (FR-100, FR-101, FR-110, FR-111, FR-125, FR-130, FR-131)

| Teste | Resultado |
|-------|-----------|
| App sem `models.py` com modelos e sem `migrations/`; `makemigrations --check` | Nada |
| Nenhum nome definido no app contém `metric`, `dimension`, `dashboard`, `widget`, `snapshot`, `cache`, `ranking`, `permission`, `policy` | Conforme |
| HTML sem "dashboard", "KPI", "funil", "abandono", "desistência", "ranking", "melhor", "pior", "questionários integralmente respondidos", "role", "permission", "scope" | Conforme |
| Nenhum formulário, botão ou link de criar, editar, abrir, encerrar, reabrir ou excluir Campanha, nem de convite, lembrete ou e-mail | Conforme |

**Acessibilidade e responsividade** (US13; FR-120 a FR-124; SC-011)

| Teste | Resultado |
|-------|-----------|
| Marcação | Um `h1`; `caption`; `th scope="col"` e `scope="row"`; `nav` de recortes com `aria-current`; região rolável rotulada e focável; "não se aplica" visualmente oculto junto ao "—"; `lang="pt-BR"`; "Pular para o conteúdo" |
| Sem `<script>` | Nas páginas do acompanhamento |
| Revisão manual | 320 px, zoom 200%, teclado (quickstart, passo 14) |

**Demonstração** (FR-142, FR-157)

| Teste | Resultado |
|-------|-----------|
| Preparo | Vínculos `(A, CPAEG, "")` e `(B, CSAEG, "Vitória")` **inalterados**; a Campanha "Demonstração — acompanhamento Serra e Vitória" existe, nunca aberta, com a baseline em RASCUNHO e critério {Serra, Vitória}; repetir o preparo não duplica nada |
| Após o preparo, B (Vitória) | Lista contém só a Campanha de acompanhamento ("coleta ampla" e "coleta sobreposta" ausentes); detalhe: 3 elegíveis, "Instrumento ainda não publicado", "A coleta ainda não começou"; sem opção de recorte por unidade |
| Após o preparo, A | Três Campanhas; "coleta ampla" com 9 elegíveis; a de acompanhamento com 6 (Serra 3, Vitória 3) e instrumento identificado |
| Cenários da 007/008 | `situacao_de_entrada` de todas as Pessoas fictícias idêntica à anterior; suítes existentes verdes |
| Modo desligado | `operador_em_uso` → `None`; 404; nenhuma identificação aceita (010/DP-1001) |

**Regressão**: suítes completas da 001 à 010 verdes.

## Sinais de over engineering (parar se aparecerem)

Nenhum destes é necessário, e qualquer um deles bloqueia a implementação até nova
discussão:

- novo modelo, migration ou índice;
- snapshot, contador gravado, `CampaignMetric`, `Aggregate`, tabela materializada;
- `Metric`, `Dimension`, `Dashboard`, `Widget`, `ChartConfiguration`, `SavedView`;
- `QueryBuilder`, `FilterBuilder`, linguagem de filtros, combinação de recortes;
- `ReportEngine`, repositório genérico, serviço genérico de relatório;
- cache, Redis, Celery, fila, job, visão materializada, SQL bruto;
- API, endpoint JSON, exportação, biblioteca de gráficos, JavaScript obrigatório;
- `Permission`, registro de capacidades, `RolePermission`, policy engine, seletor de
  atuação;
- alteração no editor, na matriz da 009, no modelo de vínculo ou em autenticação.

## Volta à spec?

**Não é necessária.** Todos os seis recortes existem na Conclusão (R7). Nenhuma
definição precisou mudar.

Ajustes de redação já consolidados na spec, sem efeito no comportamento:

- Clarifications de 2026-10-02.
- O nome do parâmetro de destino da escolha de operador (R13) é detalhe de demonstração
  da 010, coerente com FR-151 e com o "sem mecanismo genérico de retorno" da 010.

## Complexity Tracking

Vazio. Nenhuma violação da Constituição a justificar: zero modelos, zero migrations,
nenhuma abstração genérica e nenhuma infraestrutura.
