# Implementation Plan: Oportunidades curadas do Portal do Egresso

**Branch**: `claude/025-plan` | **Date**: 2026-10-08 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/025-oportunidades-curadas-portal/spec.md`

> **Situação.** O plan e as tasks foram antecipados com autorização do solicitante (roadmap,
> Revisão 4). **A implementação continua vedada** até a leitura do Checkpoint 1, que está
> **NÃO APLICADO**. Antes de implementar, o roadmap precisa registrar se a antecipação também
> a abrange.

## Summary

O plan entrega a área de Oportunidades como primeiro fato persistente da camada do Portal
([ADR 0008](../../docs/adr/0008-portal-do-egresso-camada-de-relacionamento.md); Constituição
2.1.0). Abordagem técnica:

- **Um modelo, `Oportunidade`, no app `trajetoria/portal`.** Não há app novo (R1).
  - Migração aditiva e nenhuma chave estrangeira para o núcleo.
  - Estado derivado de dois momentos (publicada e retirada) e das datas. Nenhum processo
    agendado (R5).
- **Pertinência por função pura** sobre as Conclusões da Pessoa (R7).
  - Todos os critérios precisam valer na mesma Conclusão, por igualdade exata.
  - A explicação é gerada por modelos fixos e cita **todos** os critérios definidos, com o
    valor satisfeito.
- **Experiência do egresso:**
  - página `/oportunidades/`;
  - bloco com **um** destaque no Início, com orçamento de 270 px e compactação sem perda de
    informação (R9);
  - quinto item na navegação, com largura estável dos itens (R10; A5 da avaliação por IA).
- **Curadoria** em `/curadoria/oportunidades/`, no padrão da gestão de Campanha (017).
  - Regra nomeada e escopo de administração na própria camada (R2).
  - Público independente da unidade responsável (FR-026; DP-2502).
- **Três pontos de extensão neutros no núcleo,** nenhum citando a camada:
  - destino registrável da escolha de operador (R3);
  - sinal `cenario_preparado` (R4);
  - `data-rotulo` na navegação (R10).

  Os slots `produto`, `acao_sair` e `retorno` da revisão da 024 (PR #47) são reaproveitados.

Nenhuma dependência nova, nenhum JavaScript, nenhuma mudança em Pessoa, Conclusão, Campanha,
Participação, snapshot ou exportação.

## Technical Context

**Language/Version**: Python 3.13 (uv)

**Primary Dependencies**: Django 5.2. Nada novo (`tests/dependencias.py` inalterado). Da
biblioteca padrão: `urllib.parse` e `ipaddress` (R6); `uuid5` no catálogo (R4)

**Storage**: PostgreSQL 16. Uma tabela nova, `portal_oportunidade`, com `ArrayField` para o
público, como a Campanha

**Testing**:
- pytest + pytest-django;
- funções puras testadas sem banco (pertinência, estado, endereço);
- testes por requisição para páginas e curadoria;
- Portal desligado com `pytest.mark.urls`, como na 024;
- medidas a 375×812 e 320×812 no navegador, como na 024 e na avaliação por IA

**Target Platform**: servidor Linux; navegadores móveis atuais; sem JavaScript

**Project Type**: aplicação web Django renderizada no servidor

**Performance Goals**: sem meta nova. A página do egresso faz uma consulta das oportunidades
em divulgação e uma das Conclusões. A curadoria lista dezenas de registros

**Constraints**:
- só demonstração;
- camada desligável;
- o núcleo não cita a camada;
- o egresso não grava;
- convite do Início ≤ 270 px abaixo;
- textos provisórios (008/DP-801)

**Scale/Scope**:
- 1 modelo e 1 migração no `portal`;
- subpacote `portal/oportunidades/` com cerca de 8 módulos (regras, operações, pertinência,
  consultas, governança, formulários, views do egresso, views da curadoria, mensagens,
  demonstração);
- cerca de 7 templates;
- 3 pontos neutros no núcleo;
- cerca de 8 arquivos de teste novos e 4 da 024 revisados

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Verificação | Princípios | Pré-Fase 0 | Pós-Fase 1 | Evidência / observação |
|---|---|---|---|---|---|
| 1 | Longitudinalidade | I | ✅ | ✅ | Oportunidade não se liga a Participação nem a Campanha. O egresso não grava (data-model, "Leituras") |
| 2 | Pessoa × Conclusão | I, XI | ✅ | ✅ | O público é testado por Conclusão, nunca por atributos fundidos da Pessoa (R7) |
| 3 | Múltiplas formações | I, XI | ✅ | ✅ | Todas as Conclusões são avaliadas, cada uma sozinha. Todas as que satisfazem são citadas na ordem da 007 (contracts/pertinencia.md) |
| 4 | Múltiplas participações | I, VIII | N/A | N/A | A feature não lê Participação |
| 5 | Definição de egresso | II | ✅ | ✅ | Só a Pessoa com Conclusão Acadêmica vê. "Todos os egressos" não inclui quem não tem Conclusão nem o declarante (FR-011) |
| 6 | Preservação histórica e migrações | VIII, XXVII | ✅ | ✅ | Migração aditiva de uma tabela nova; nenhuma tabela existente muda; nada é excluído (FR-010) |
| 7 | Pesquisa/Versão/Campanha/Participação | VII | ✅ | ✅ | O público reaproveita a semântica da 004, mas não lê nem altera Campanha (FR-008; ADR 0004) |
| 8 | Proveniência | IV | ✅ | ✅ | A explicação cita a formação institucional. A origem do site é explícita (R6, R7) |
| 9 | Institucional × derivado × declarado | III | ✅ | ✅ | Formação Declarada e Respostas ficam fora, com teste de consultas como na 024 |
| 10 | Desacoplamento | V, XXV | ✅ | ✅ | Funções puras. Nenhuma integração externa. O endereço não é acessado (R6) |
| 11 | Fronteira do NIAE / Camada de relacionamento | VI; 2.1.0 | ✅ | ✅ | Tudo no `portal`. Três pontos neutros no núcleo, sem citar a camada (contracts/rotas.md). Desligável. Fora do analítico por construção e por teste (R13) |
| 12 | Governança | X | ✅ | ✅ | Competência nomeada só para CPAEG e CSAEG. Sem aprovação inventada. CPAEG institucional como hipótese (DP-2501) |
| 13 | Escopo por unidade | XII | ✅ | ✅ | Administração restrita às unidades da CSAEG. Fora do escopo dá 404. O público é independente (DP-2502) |
| 14 | Privacidade e minimização | XVI | ✅ | ✅ | Nenhum dado novo do egresso; nada gravado ao exibir; `rel="noreferrer"`; sem parâmetros; o operador não vê quem é alcançado (R12; FR-026) |
| 15 | Autorização | X, XII | ✅ | ✅ | Egresso: sessão da 018 e Conclusão. Operador: vínculos relidos a cada pedido; escopo revalidado na escrita (R5) |
| 16 | Acessibilidade | XX | ✅ | ✅ | Hierarquia h1/h2/h3; links com nome completo; `fieldset` e `legend` no público; erros associados; 44×44 px; foco da 015 |
| 17 | Mobile e esforço | XIV, XXI | ✅ | ✅ | Nada a preencher pelo egresso. Um toque do Início à oportunidade. Orçamento do convite (R9). Navegação estável (R10) |
| 18 | Testes | XXV, XXVI | ✅ | ✅ | Os 12 casos do FR-043, o oráculo por persona (SC-002) e os testes revisados da 024 (R11) |
| 19 | Over engineering | XXII, XXIII | ✅ | ✅ | Um modelo; nenhum app novo; sem CMS, histórico, exclusão, busca, paginação nem JavaScript |
| 20 | Exportações | XVIII | N/A | N/A | Nada exportado. Fora de snapshot e exportação (FR-038) |
| 21 | Decisões pendentes | XXIX | ✅ | ✅ | DP-2501 a DP-2507 com solução provisória reversível (tabela abaixo) |

**Resultado do gate**: APROVADO. Não há violação. Os pontos neutros no núcleo e a regra de
curadoria fora de `governanca` estão justificados em *Complexity Tracking*.

**Conflitos identificados**: nenhum com a Constituição.

Uma correção de fato foi feita na spec durante o plan. A demonstração **não** tem duas grafias
do mesmo curso: Ana e Maria usam a mesma constante `TADS`. A spec foi corrigida, e o caso
passa a ser exercitado só nos testes.

## Decisões Pendentes

| ID | DECISÃO PENDENTE | Instância competente | Solução provisória (hipótese) | Como reverter |
|---|---|---|---|---|
| DP-2501 | Quem cura e quem atua pelo Ifes inteiro | CPAEG, Proex | CSAEG nas próprias unidades; CPAEG institucional | Mudar `pode_curar_oportunidades` e o escopo em `portal/oportunidades/governanca.py` |
| DP-2502 | Limite de alcance entre unidades | CPAEG, Proex | Público livre | Acrescentar a validação do público em `operacoes.py`, sem migração |
| DP-2503 | Finalidade e base legal da pertinência | Encarregado, CPAEG | Só demonstração; calculada na consulta | Desligar o Portal |
| DP-2504 | O que conta como endereço oficial | CPAEG, DTI, ACS | Validação de forma e classificação Ifes × externo | Lista de domínios em `regras.py` |
| DP-2505 | Categorias definitivas | CPAEG, ACS | Seis categorias provisórias | Migração de `choices` |
| DP-2506 | Retenção e histórico | CPAEG, encarregado | Nada é excluído; só publicação e retirada registradas | Política futura |
| DP-2507 | Código de curso estável | DTI, Proen (Portão A) | Texto exato | Evoluir o contrato da fonte (001) |
| D1, D2, DP-1001, DP-1005, 001/DP-007 | Herdadas | — | Como na 024 | — |

## Project Structure

### Documentation (this feature)

```text
specs/025-oportunidades-curadas-portal/
├── spec.md
├── plan.md              # este arquivo
├── research.md          # R1–R14
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── rotas.md
│   ├── pertinencia.md   # regra, explicação, catálogo e oráculo por persona
│   ├── oportunidades-egresso.md
│   └── curadoria.md
├── checklists/requirements.md
└── tasks.md             # /speckit-tasks (autorizado, ainda não gerado)
```

### Source Code (repository root)

```text
trajetoria/portal/
├── models.py                      # Oportunidade (novo)
├── migrations/0001_oportunidade.py
├── apps.py                        # ready(): registrar destino "curadoria"; conectar o sinal
├── contexto.py                    # navegação com "Oportunidades"; /oportunidades/ na lista fechada
├── inicio.py                      # bloco com um destaque (FR-021)
├── urls.py                        # /oportunidades/ e /curadoria/oportunidades/…
├── oportunidades/
│   ├── regras.py                  # estado, endereço (R6), Motivo, OportunidadeRejeitada
│   ├── operacoes.py               # cadastrar, editar, publicar, retirar (único caminho de escrita)
│   ├── pertinencia.py             # função pura (R7)
│   ├── consultas.py               # em_divulgacao, da_curadoria, opcoes_de_publico
│   ├── governanca.py              # pode_curar_oportunidades, escopo (R2)
│   ├── formularios.py
│   ├── views_egresso.py
│   ├── views_curadoria.py
│   ├── mensagens.py
│   └── demonstracao.py            # catálogo fictício + receptor do sinal (R4)
└── templates/portal/
    ├── oportunidades.html
    ├── _oportunidade.html         # item compartilhado (página, Início, prévia)
    ├── inicio.html                # + bloco
    └── curadoria/{lista,formulario,publicar,retirar,conflito}.html

trajetoria/demonstracao/views.py    # registrar_destino (neutro)
trajetoria/demonstracao/sinais.py   # cenario_preparado (neutro, novo)
trajetoria/demonstracao/cenario.py  # envia o sinal no fim de preparar()
trajetoria/interface/templates/interface/_navegacao.html  # data-rotulo
trajetoria/interface/templates/interface/jornada.css      # largura estável da navegação

tests/portal/
├── test_oportunidades_regras.py       # estado, endereço, validações
├── test_oportunidades_pertinencia.py  # regra, explicação, ordem, mesma Conclusão, grafias
├── test_oportunidades_egresso.py      # página, vazio, acessos, nada gravado
├── test_oportunidades_inicio.py       # bloco, destaque, convite inalterado
├── test_oportunidades_curadoria.py    # escopo, operações, conflito, avisos
├── test_oportunidades_oraculo.py      # catálogo da demonstração × oráculo (SC-002)
├── test_oportunidades_fronteiras.py   # analítico idêntico; núcleo intacto; um modelo
└── (revisados) test_fronteiras.py, test_inicio.py, test_navegacao.py, test_desabilitado.py
```

**Structure Decision.** Fica tudo no app `portal` (R1). O núcleo recebe só três pontos
neutros, que não citam a camada.

## Complexity Tracking

| Desvio | Por que é necessário | Alternativa mais simples rejeitada porque |
|---|---|---|
| A regra de curadoria fica na camada, não em `governanca/regras.py` (010 FR-034 sugere o módulo de governança) | O núcleo não pode conhecer competências da camada. O conjunto de regras do núcleo está congelado por teste | Colocá-la no núcleo acoplaria o núcleo à camada |
| Três pontos de extensão neutros no núcleo (destino de operador, sinal do cenário, `data-rotulo`) | Sem eles, a curadoria não teria entrada, a demonstração não teria catálogo e a navegação não seria estável | Importar a camada no núcleo é vetado. Um comando à parte seria passo esquecível. Rótulos mais curtos mudariam o que o Checkpoint 1 testa |
| Revisão de testes da 024 (sem modelo; vocabulário do Início) | A 025 revisa a 024 explicitamente (spec, "Requisitos revisados") | — |

## Riscos de implementação

- **Orçamento de 270 px** (R9). A compactação é feita em três etapas, sem remover
  informação exigida (FR-004, FR-013). Se não couber, o caso volta ao solicitante. *(A versão
  anterior previa tirar a linha de origem, o que violaria a spec; corrigido na revisão do
  plan.)*
- **Lista de cursos longa na fonte real** (R8). Fica para quando houver volume real.
- **Datas do catálogo relativas a `D`.** Um banco preparado em outro dia mostra outro
  recorte. O quickstart exige banco recriado.
- **A5.** A largura estável depende do `::after`. A medida em seis telas é obrigatória na
  validação.

## Ajustes registrados na implementação (2026-10-08)

- **`cadastrar(…, id=None)`.** Um `id` opcional permite a carga idempotente do catálogo com
  `uuid5` fixos (R4). Só a carga da demonstração o usa.
- **`itens_da_pessoa`** fica em `oportunidades/consultas.py`, e não na view. Página e Início
  usam a mesma função, e o Início não importa views.
- **Compactação do destaque.** A medida (T046) exigiu a **variante 3**: explicação e origem
  num parágrafo, tipo de 15 px e margens de `--espaco-1`. Diego caiu de 290 para 253 px.
  Nenhuma informação foi removida.
- **Largura estável da navegação.** O `::after` só reserva largura com o link em coluna
  (`flex-direction: column`). Em linha, ele somaria a largura do rótulo duas vezes.
- **Quebra de palavras.** Os textos da oportunidade e as telas da curadoria ganharam
  `overflow-wrap: anywhere`, para domínios e palavras longas a 320 px com fonte a 200%. A
  tabela da lista não quebra: rola na própria região, como na 011.
- **Include de campo da curadoria** (`portal/curadoria/_campo.html`). O `editor/_campo.html`
  trata caixa de seleção como "Sim" único. Os três grupos do público precisam de
  `fieldset` e `legend` com uma caixa por valor.
- **Ações da lista com `aria-label`.** Substituem o `span.visualmente-oculto`, que, posicionado
  fora da região de rolagem, alargava a página.
- **Servidor de validação em `127.0.0.1:8025`.** A porta 8000 estava ocupada por outro
  projeto do solicitante. A exigência da porta 8000 vale só para o envio por Lote (020), que
  a 025 não usa.
- **Comentário de template.** `{# … #}` não aceita várias linhas no Django: o texto vazava
  para a página e foi pego pelo teste de vocabulário do Início. Corrigido para uma linha.
