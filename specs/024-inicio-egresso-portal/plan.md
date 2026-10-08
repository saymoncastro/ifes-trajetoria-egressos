# Implementation Plan: Início do egresso e shell do Portal

**Branch**: `claude/024-inicio-egresso-portal` | **Date**: 2026-10-07 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/024-inicio-egresso-portal/spec.md`

## Summary

Primeira camada do Portal do Egresso ([ADR 0008](../../docs/adr/0008-portal-do-egresso-camada-de-relacionamento.md);
Constituição 2.1.0). O egresso passa a ser reconhecido antes de ser chamado a responder, e
a coleta continua sem depender do Portal. Abordagem técnica:

- **App novo `trajetoria/portal`, só de experiência.** Contém a entrada `/`, a identificação
  `/entrar/`, o `/inicio/` e um *context processor* de navegação. Não tem `models.py`,
  migração nem gravação.
- **Duas entradas com destino fixo** (alternativa A da spec).
  - O convite continua em `/acesso/` → `/formacoes/`.
  - O Portal entra por `/` → `/entrar/` → `/inicio/`.
  - A identificação é a mesma da 018: a view do `acesso` é parametrizada internamente
    (destino, ação do formulário e rótulo), sem conhecer o Portal.
- **Regra positiva da trajetória.** `narrativa.consultas.elegivel` passa a exigir só uma
  Conclusão Acadêmica. O vídeo (022) acompanha, porque usa a mesma função. Sai a
  antecipação de `/formacoes/`, e entra "A pesquisa tem no máximo N partes." (função pura
  da 023).
- **Shell.** `interface/base.html` ganha dois blocos neutros, `produto` e `navegacao`. As
  telas fora das Seções optam pelo include de navegação, que só renderiza se o provedor do
  Portal fornecer itens.
- **Início.** Monta-se a partir da `TrajetoriaNarrativa` (021) e da `SituacaoDeEntrada`
  (007), nesta ordem: reconhecimento, proveniência, ações e convite. Não lê o contato.
- **Desligamento.** `TRAJETORIA_PORTAL=0` tira as rotas do Portal do `urlconf` e esvazia a
  navegação. Com o Portal desligado, a raiz volta a `interface.views.inicio`.

Nenhum modelo, migração, dependência ou JavaScript. Nenhuma mudança em Campanha, Versão,
instrumento, jornada das Seções ou convite.

## Technical Context

**Language/Version**: Python 3.13 (uv), como o projeto

**Primary Dependencies**: Django 5.2. Nada novo (`tests/dependencias.py` inalterado)

**Storage**: PostgreSQL 16. Nenhuma tabela nova. A sessão é a da 018

**Testing**:
- pytest + pytest-django, com testes por requisição;
- `pytest.mark.urls` mais `override_settings` para o Portal desligado (research R8);
- teste de fronteira por varredura de arquivos, como `tests/video/test_fronteira.py`;
- medidas a 375×812 no navegador, como na reauditoria.

**Target Platform**: servidor Linux; navegadores móveis atuais; funciona sem JavaScript

**Project Type**: aplicação web Django renderizada no servidor

**Performance Goals**: sem meta nova. O Início faz as mesmas leituras que `/minha-trajetoria/`
e `/formacoes/` já fazem, uma vez cada

**Constraints**:
- só demonstração;
- sem dado no endereço;
- destino fixo por entrada;
- shell da 015 idêntico nas Seções;
- textos provisórios (008/DP-801).

**Scale/Scope**:
- 1 app novo, com cerca de 4 módulos e 2 templates;
- cerca de 8 templates do núcleo ajustados (blocos e include);
- 3 funções do núcleo ajustadas: `elegivel`, a entrada do `acesso` e a tela de formações;
- 6 arquivos de teste novos (mais 2 auxiliares: construção e `urlconf` sem Portal) e cerca de 4 atualizados.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Verificação | Princípios | Pré-Fase 0 | Pós-Fase 1 | Evidência / observação |
|---|-------------|------------|------------|------------|------------------------|
| 1 | Longitudinalidade | I | ✅ | ✅ | Nada grava. Participação e jornada intocadas (spec FR-011, FR-029; data-model) |
| 2 | Pessoa × Conclusão | I, XI | ✅ | ✅ | O Início lista as formações da Conclusão; nada é atribuído à Pessoa (contracts/inicio.md, bloco 4) |
| 3 | Múltiplas formações | I, XI | ✅ | ✅ | Todas as Conclusões, na ordem da 007. Convite com `SELECAO_NECESSARIA` |
| 4 | Múltiplas participações | I, VIII | ✅ | ✅ | O convite só lê a situação (007) |
| 5 | Definição de egresso | II | ✅ | ✅ | A regra positiva usa Conclusão Acadêmica incorporada (001), que já é egresso. Matrícula ativa ou evasão não são incorporadas (R13) |
| 6 | Preservação histórica | VIII, XXVII | N/A | N/A | Sem migração nem alteração de dado |
| 7 | Pesquisa/Versão/Campanha/Participação | VII, VIII | ✅ | ✅ | Nenhum desses conceitos muda. O "no máximo N" lê a Versão sem alterá-la (R5) |
| 8 | Proveniência | IV | ✅ | ✅ | "Registro do Ifes" por formação; derivados com explicação; nota de proveniência (FR-018) |
| 9 | Institucional × derivado × declarado | III | ✅ | ✅ | Só institucional e derivado. Nenhuma Resposta lida (contracts/inicio.md, vedações) |
| 10 | Desacoplamento e autenticação substituível | V, XV, XXV | ✅ | ✅ | A identificação da 018 é reaproveitada por parâmetro, sem mecanismo novo (R3). A narrativa continua com contrato serializável |
| 11 | Fronteira do NIAE / Camada de relacionamento | VI; 2.1.0 | ✅ | ✅ | App `portal` com dependência num só sentido, verificada por teste. Slots neutros no núcleo (R7). Desligável (R8). Cinco perguntas na spec |
| 12 | Governança | IX, X | N/A | N/A | Sem operador, papel ou periodicidade |
| 13 | Escopo por unidade | XII | N/A | N/A | Tela do egresso; sem visão administrativa |
| 14 | Privacidade e minimização | XVI, XVII | ✅ | ✅ | Sem dado no endereço; destino fixo; contato não lido; logs sem dado pessoal (R6). DP-2401 registrada |
| 15 | Autorização | X, XII | ✅ | ✅ | O Início só aceita a Pessoa da sessão. A trajetória é da própria Pessoa. O declarante é encaminhado à sua tela |
| 16 | Acessibilidade | XX | ✅ | ✅ | `nav` com `aria-current`, um `h1`, alvos de 44 px, foco da 015, nada só por cor (contracts/navegacao.md) |
| 17 | Mobile e esforço | XIV, XXI | ✅ | ✅ | Convite sem tela extra (SC-002); um toque até a trajetória (SC-003); acima da dobra a 375 px (SC-004); Seções sem navegação (SC-007) |
| 18 | Testes | XXV, XXVI | ✅ | ✅ | Os 10 casos do FR-033 em `tests/portal/`; testes revisados com referência (R12) |
| 19 | Over engineering | XXII, XXIII, XXIV | ✅ | ✅ | Sem entidade; sem mecanismo genérico de destino; sem menu com JavaScript; um app só |
| 20 | Exportações | XVIII | N/A | N/A | Nada exportado. O Portal fica fora do snapshot e das exportações por construção |
| 21 | Decisões pendentes | XXIX | ✅ | ✅ | Regra da trajetória e ordem do Início marcadas como hipótese; nome provisório; DP-2401 nova |

**Resultado do gate**: APROVADO (pré e pós-Fase 1).

**Conflitos identificados**: nenhum com a Constituição. Duas decisões de projeto anteriores
são revistas explicitamente, com registro na spec ("Requisitos revisados"):

- **021 E2 / FR-001 / FR-002 / FR-070 e 022 FR-001.** Eram hipóteses do solicitante. A
  revisão foi feita por ele mesmo (spec S2).
- **Veto visual da auditoria de identidade a hero e cards.** É reaberto só para a abertura
  ilustrada do Início, que a 021 já usa. Grade de cartões e saudação continuam vetadas
  (FR-026; research R10).

## Decisões Pendentes

| ID | DECISÃO PENDENTE | Instância competente | Solução provisória (hipótese) | Como reverter |
|----|------------------|----------------------|-------------------------------|---------------|
| DP-2401 | Trajetória antes de qualquer participação no uso real (finalidade e base legal) | Encarregado de dados, CPAEG/Proex | Só na demonstração (FR-030) | Restaurar a condição em `narrativa.consultas.elegivel` |
| D2 (definitivo) | Nome institucional da experiência | ACS, Proex | "Portal do Egresso" no bloco `produto` dos templates do Portal | Trocar o texto em `portal/mensagens.py` |
| DP-2108 / D1 (produção) | Relação com o Portal da PAEG | Proex, CPAEG, DTI | Camada só na demonstração | `TRAJETORIA_PORTAL=0` ou remover o app |
| DP-2103 | Nome civil × social | Registro acadêmico, encarregado | O Início não exibe nome | — |
| 008/DP-801 | Linguagem e identidade definitivas | ACS, CPAEG | Textos provisórios em `portal/mensagens.py` | Trocar os textos |

## Project Structure

### Documentation (this feature)

```text
specs/024-inicio-egresso-portal/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── rotas.md        # entradas, destinos, matriz dos dois caminhos
│   ├── navegacao.md    # slots do shell, telas com e sem navegação, provedor
│   └── inicio.md       # ordem dos blocos, convite por situação, vedações, medidas
├── checklists/requirements.md
└── tasks.md            # /speckit-tasks
```

### Source Code (repository root)

```text
config/
├── settings.py                  # TRAJETORIA_PORTAL ("0" desliga); app e context processor do portal
└── urls.py                      # rotas(com_portal): portal antes de interface quando ativo

trajetoria/
├── portal/                      # NOVO — camada de relacionamento (sem models.py)
│   ├── apps.py
│   ├── urls.py                  # "", "entrar/", "inicio/"
│   ├── views.py                 # entrada, entrar (delegação à 018), inicio
│   ├── inicio.py                # composição do Início a partir da narrativa e da situação de entrada
│   ├── contexto.py              # context processor `navegacao`
│   ├── mensagens.py             # textos provisórios
│   └── templates/portal/inicio.html
├── acesso/
│   ├── views.py                 # entrada → função interna parametrizada (destino, ação, rótulo, continuar)
│   └── templates/acesso/entrada.html   # {{ acao }}, rótulo e "continuar" por parâmetro
├── narrativa/
│   ├── consultas.py             # elegivel = ao menos uma Conclusão Acadêmica
│   └── templates/narrativa/minha_trajetoria.html   # opta pela navegação
├── contato/templates/contato/meu_email.html        # opta pela navegação
└── interface/
    ├── views.py                 # formacoes: sem antecipação; "no máximo N partes" ao iniciar
    ├── mensagens.py             # remove ANTECIPACAO; frase do tamanho
    └── templates/interface/
        ├── base.html            # blocos neutros `produto` e `navegacao`
        ├── _navegacao.html      # NOVO include neutro
        ├── formacoes.html, concluida.html   # optam pela navegação
        └── jornada.css          # estilo da navegação (tokens 015)

tests/
├── portal/                      # NOVO
│   ├── test_entradas.py
│   ├── test_inicio.py
│   ├── test_navegacao.py
│   ├── test_desabilitado.py
│   ├── urls_sem_portal.py
│   └── test_fronteiras.py
└── (atualizações) narrativa/test_rotas.py, narrativa/test_catalogo.py,
    interface/test_interface_formacoes.py, video/ (acesso sem Participação, se houver)
```

**Structure Decision**: mantém a aplicação modular única. O Portal é um app próprio, para
que a fronteira de dependência seja verificável (Constituição 2.1.0). O núcleo ganha só
pontos de extensão neutros (dois blocos de template e um include) e uma parametrização
interna da identificação. Nenhum desses pontos menciona o Portal.

## Complexity Tracking

Nenhuma violação a justificar. Uma nota de projeto: o padrão "ligado salvo `0`" do
`TRAJETORIA_PORTAL` difere do padrão "só `1` liga" do modo de demonstração. A razão é que a
camada inteira já fica atrás do modo de demonstração, e uma variável obrigatória nova
quebraria ambientes já preparados (research R8).
