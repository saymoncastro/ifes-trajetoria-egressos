# Implementation Plan: Encontros propostos por egressos

**Branch**: `claude/031-plan-tasks` | **Date**: 2026-10-11 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/031-encontros-propostos-egressos/spec.md`
(com o clarify de 2026-10-11).

> **Situação.** Plan e tasks autorizados na
> [revisão 15 do roadmap](../../docs/roadmap/2026-10-07-portal-do-egresso-arquitetura-e-roadmap.md).
> **A implementação não está autorizada**: código e migração continuam condicionados à
> leitura do Checkpoint 1 e do Checkpoint 2 (bloco Comunidade), ambos **NÃO APLICADOS**, e à
> escolha entre 031 e 030. A T001 das tasks é o portão. Se autorizada, vale só para a
> demonstração.

## Summary

Um egresso com Conclusão propõe um encontro virtual. A moderação (CSAEG da unidade ou CPAEG,
hipótese H-3102) publica, recusa ou retira, sempre com motivo. Outros egressos descobrem o
encontro pela formação, confirmam e veem o link. Quem organiza vê só a quantidade de
confirmações.

Abordagem técnica, no molde da 025 e da 026:

- **Três modelos novos no app `portal`**: `Encontro`, `Confirmacao` e `Denuncia`, numa
  migração aditiva.
  - Nenhuma chave estrangeira para o núcleo. Chaves internas à camada ligam Confirmação e
    Denúncia ao Encontro (R2).
- **Subpacote `portal/encontros/`**, com:
  - regras puras (situação, visibilidade, limites);
  - `operacoes.py` como único caminho de escrita;
  - consultas, governança, formulários, mensagens, calendário, demonstração e views do
    egresso e da moderação.
- **Reaproveita da 025** a pertinência (`satisfaz`, `explicacao`) e a validação do link (R6,
  R7).
- **`.ics` gerado na camada**, sem dependência nova (R11).
- **Destino preservado por lista fechada** para o endereço compartilhado (R12).
- **No Início**, a seção de encontros passa a ter F e A. A navegação ganha "Encontros" (R13).

Nenhuma mudança em Pessoa, Conclusão, Contato, Campanha, Participação, Resposta, snapshot,
exportação analítica, mobilização ou instrumento. Nenhum JavaScript, nenhuma notificação.

## Technical Context

**Language/Version**: Python 3.13 (uv)

**Primary Dependencies**: Django 5.2. Nada novo (`tests/dependencias.py` inalterado). Da
biblioteca padrão: `datetime`, `zoneinfo`, `uuid`

**Storage**: PostgreSQL 16. Três tabelas novas: `portal_encontro`, `portal_confirmacao`,
`portal_denuncia`

**Testing**:
- pytest + pytest-django;
- regras, visibilidade, situação e `.ics` testados sem banco;
- testes por requisição para os fluxos do egresso, do organizador e da moderação;
- Portal desligado com `pytest.mark.urls`;
- fronteira: núcleo sem menção à camada; nenhuma FK para fora do `portal`; nada no analítico,
  na mobilização ou no contato;
- medidas no navegador com o arnês do protótipo

**Target Platform**: servidor Linux; navegadores atuais; sem JavaScript

**Project Type**: aplicação web Django renderizada no servidor

**Performance Goals**: sem meta nova.
- O Início ganha uma consulta: os encontros publicados e futuros, filtrados em Python pela
  pertinência, como as oportunidades.
- Volume de demonstração: dezenas de encontros

**Constraints**:
- só demonstração; camada desligável; o núcleo não cita a camada;
- o link da reunião nunca vai ao HTML de quem não pode vê-lo (FR-021, SC-002);
- visibilidade por situação (FR-024a);
- convite à pesquisa continua por último no Início (ADR 0009, decisão 8);
- textos provisórios (DP-801)

**Scale/Scope**:
- 3 modelos e 1 migração;
- cerca de 12 módulos em `portal/encontros/`;
- cerca de 18 rotas (14 do egresso e do organizador, 4 da moderação, com GET e POST
  agrupados);
- cerca de 15 templates;
- cerca de 9 arquivos de teste novos e 5 revisados

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Verificação | Princípios | Pré-Fase 0 | Pós-Fase 1 | Evidência / observação |
|---|-------------|------------|------------|------------|------------------------|
| 1 | Longitudinalidade | I | ✅ | ✅ | Encontros não se ligam a Participação nem a Campanha; nada no núcleo muda |
| 2 | Pessoa versus Conclusão | I, XI | ✅ | ✅ | A origem é uma Conclusão escolhida; a pertinência usa uma mesma Conclusão por vez (R6) |
| 3 | Múltiplas formações | I, XI | ✅ | ✅ | O organizador escolhe a origem; a explicação cita as formações que satisfazem |
| 4 | Múltiplas participações | I, VIII | N/A | N/A | Não há Participação; a "confirmação" do encontro é outro conceito, com nome próprio |
| 5 | Definição de egresso | II | ✅ | ✅ | Só Pessoa com Conclusão propõe, confirma ou denuncia; Formação Declarada fora (FR-001) |
| 6 | Preservação histórica | VIII, XXVII | ✅ | ✅ | Migração aditiva; nada é apagado; cancelamentos e decisões registram momento (data-model) |
| 7 | Pesquisa/Versão/Campanha/Participação | VII, VIII | ✅ | ✅ | Não lê nem altera; termos versionados por constante, sem relação com a Versão do instrumento |
| 8 | Proveniência | IV | ✅ | ✅ | Origem marcada como registro do Ifes; nome e textos como declarados pelo organizador |
| 9 | Institucional × declarado | III | ✅ | ✅ | Origem copiada da Conclusão (R3), separada do nome de apresentação |
| 10 | Desacoplamento de integrações | V, XV, XXV | ✅ | ✅ | Sem integração com videoconferência; o link não é acessado; identificação da 018, substituível |
| 11 | Fronteira do NIAE | VI | ✅ | ✅ | Spec, "Fronteira do NIAE"; tudo na camada (R1); teste de fronteira revisado (R2) |
| 12 | Governança institucional | IX, X | ⏸ | ⏸ | Moderação como hipótese H-3102 (D8), sem fluxo inventado: uma decisão por ação, sem segunda aprovação |
| 13 | Escopo por unidade | XII | ✅ | ✅ | `responsavel()` e `modera()` (R8); CPAEG institucional age em todos (clarify 2) |
| 14 | Privacidade e minimização | XVI, XVII | ⏸ | ⏸ | Sem e-mail; link restrito; contagem só para quem organiza; denunciante não exibido; termo e ciência versionados; logs sem `pessoa_id`, link da reunião nem complemento de denúncia (teste em T032); base legal e retenção em D9 |
| 15 | Autorização | X, XII | ✅ | ✅ | Matriz em [contracts/rotas.md](contracts/rotas.md); visibilidade como função pura (R10); conflito com trava (R8) |
| 16 | Acessibilidade | XX | ✅ | ✅ | Padrões da 015 e da 026 (`fieldset`, resumo de erros, foco, 44 px), sem JavaScript; protótipo medido |
| 17 | Responsividade | XIV, XXI | ✅ | ✅ | Celular como referência; a 375×812, título e data sem rolar; medidas de 320 a 1440 px |
| 18 | Testes | XXV, XXVI | ✅ | ✅ | Ver "Testes" |
| 19 | Over engineering | XXII, XXIII, XXIV | ✅ | ✅ | Três fatos específicos; sem notificação, workflow, histórico de edições nem dependência; pertinência reaproveitada |
| 20 | Exportações | XVIII | N/A | N/A | Nenhuma exportação; confirmações nunca são exportadas (FR-032) |
| 21 | Decisões pendentes | XXIX | ✅ | ✅ | H-3101 a H-3108 localizadas em `encontros/`; D8, D9, D10, DP-1808 bloqueiam só o uso real |

**Resultado do gate**: APROVADO para planejamento. Os itens ⏸ são decisões institucionais com
hipótese reversível registrada (XXIX). Nenhum deles é violação.

**Conflitos identificados**:
- Revisões explícitas de requisitos anteriores: spec, "Requisitos revisados".
- O teste de fronteira da 025 e da 026 proibia **qualquer** chave estrangeira na camada. A
  regra constitucional é não depender do núcleo. A revisão (R2) mantém a proibição para o
  núcleo e admite chaves internas. Não é violação: é a mesma regra, aplicada com mais
  precisão.

## Testes

| Área | Casos |
|---|---|
| Regras, sem banco | situação nas nove combinações e na ordem do data-model; ativo; limites de data, duração e texto; mesmo domínio; visibilidade (FR-024a) em cada situação × quem; link (FR-021); `.ics` (campos, dobra, CRLF, `SEQUENCE`, `STATUS`, ausência do link e do nome) |
| Propor | Conclusão de outra Pessoa recusada; Formação Declarada não oferecida; erros por campo sem gravar; versão do termo gravada; origem copiada; limite de 3 ativos, inclusive em dois envios simultâneos |
| Moderar | CSAEG só na unidade única; CPAEG em todos; CSAEG de outra unidade recebe "não encontrado"; sem competência, recusa; publicar, recusar e retirar com operador e motivo; complemento obrigatório em "outro"; conflito; nova análise mostra os campos alterados; recusa da alteração retira |
| Organizador | editar em análise; corrigir data; link no mesmo domínio vale na hora; outro domínio vira nova análise; alteração substancial sai das listas e esconde o link; cancelar; "Seus encontros" com contagem e sem nomes |
| Participante | descobrir por curso, por unidade, por nível e aberto a todos; explicação; não aparece fora do público, mas abre pelo endereço (H-3108); confirmar; uma ativa; cancelar e confirmar de novo; o link some ao cancelar e em revisão |
| Página | conteúdo por situação e por quem (FR-024a); página neutra sem sessão; o link fora do HTML de quem não pode vê-lo (SC-002) |
| Entrada | `/entrar/?encontro=` com UUID existente leva ao encontro; URL, caminho, UUID inexistente ou lixo levam ao Início; `sem_pessoa` em `/encontros/<id>/` |
| Denúncia | uma por pessoa; a moderação vê motivo e complemento e não vê quem; o organizador não vê; "Você denunciou…" |
| Fronteira | núcleo sem menção à camada; quatro modelos no `portal`, sem FK para fora; migração só aditiva; `ContatoDaPessoa` inalterado; analítico, exportações e mobilização sem os três fatos; nada gravado ao só abrir as telas (`test_portal_nao_grava` revisado) |
| Portal desligado | rotas inexistentes; Início sem a seção; coleta inalterada |
| Início e navegação | seção com F e A; ausente sem nenhum; convite por último; "Encontros" na navegação com Conclusão, item atual nas telas `/encontros/` |
| Vocabulário | "comunidade" só na página Encontros e na seção do Início; sem "inscrição" ou "presença" afirmadas; vedações da ADR 0009 nas demais telas |

## Critérios de entrega (antes do merge da implementação)

1. `ruff check .`, `manage.py check`, `makemigrations --check --dry-run` e a suíte completa
   passam, com o número de testes registrado na `validacao.md`.
2. Capturas reais das telas do egresso (375×812 e 1440×900) e da moderação (1280×720), lado
   a lado com o [protótipo](prototipo/index.html).
3. Medidas: sem rolagem horizontal de 320 a 1440 px com fonte a 200%; um h1; alvos de 44 px;
   navegação com cinco itens em até duas linhas a 375 px.
4. Roteiro manual com teclado nos cenários 2, 5, 7 e 10 do [quickstart](quickstart.md).
5. Nenhuma escrita além das previstas no data-model, verificada por contagens.

## Decisões Pendentes

| ID | DECISÃO PENDENTE | Instância competente | Solução provisória (hipótese) | Como reverter |
|----|------------------|----------------------|-------------------------------|---------------|
| D8 | Quem modera, critérios, prazo, canal de denúncias, reincidência | CPAEG, com as CSAEG e a Proex | H-3102, H-3104, H-3107 em `encontros/governanca.py` e `mensagens.py` | Trocar a regra de `responsavel()` e as listas de motivos; a Denúncia sai do modelo se o canal for externo |
| D9 | Base legal e retenção de encontro, confirmação, denúncia, nome e origem | Encarregado de dados, com a CPAEG | Só demonstração; nada é apagado | Política futura; anonimizar `pessoa_id` de confirmações encerradas sem migração destrutiva |
| D10 | Outras soluções institucionais | Proex, DIREC, CPAEG | Nenhuma integração | — |
| DP-1808 | Garantia de identidade do organizador | Proex, DTI, encarregado | Identificação da 018 | Trocar a identificação sem mudar o domínio (XV) |
| DP-3102 | Página sem sessão neutra ou com título e data | Solicitante | Neutra (FR-022) | Um template |
| DP-801 | Textos, termo, ciência e motivos | CPAEG, ACS | Provisórios em `mensagens.py`, com versões | Trocar textos e subir as versões |
| Checkpoints | — | — | NÃO APLICADOS; T001 bloqueia a implementação | — |

## Project Structure

### Documentation (this feature)

```text
specs/031-encontros-propostos-egressos/
├── spec.md
├── plan.md              # este arquivo
├── research.md          # R1 a R16
├── data-model.md        # Encontro, Confirmacao, Denuncia; situação; transições
├── quickstart.md        # validação depois da implementação
├── contracts/
│   ├── rotas.md         # rotas e matriz de autorização
│   └── calendario.md    # .ics
├── prototipo/           # 33 telas estáticas (gerar.py, index.html, medidas, capturas)
└── tasks.md             # /speckit-tasks
```

### Source Code (repository root)

```text
trajetoria/portal/
├── models.py                        # + Encontro, Confirmacao, Denuncia
├── migrations/0003_encontros.py     # aditiva
├── urls.py                          # + rotas da 031
├── destinos.py                      # + caso /encontros/<id>/ (R12)
├── views.py                         # entrar: destino por lista fechada (R12)
├── inicio.py                        # seção de encontros com F e A (R13)
├── contexto.py                      # item "Encontros" na navegação (R13)
├── mensagens.py                     # ENCONTROS_TEXTO revisto
├── encontros/
│   ├── regras.py                    # situação, ativo, limites, visibilidade, link, mesmo domínio
│   ├── operacoes.py                 # único caminho de escrita (propor, editar, publicar, recusar, retirar, corrigir, alterar, cancelar, confirmar, cancelar participação, denunciar)
│   ├── consultas.py                 # pertinentes da Pessoa; seus; escopo da moderação
│   ├── governanca.py                # pode_moderar_encontros, responsavel, modera
│   ├── formularios.py
│   ├── mensagens.py                 # textos, VERSAO_DO_TERMO, VERSAO_DA_CIENCIA, motivos
│   ├── calendario.py                # .ics
│   ├── demonstracao.py              # encontros fictícios (sinal cenario_preparado)
│   ├── views_egresso.py             # Encontros, página, confirmar, denunciar
│   ├── views_organizador.py         # propor, seus, editar, corrigir, alterar, cancelar
│   └── views_moderacao.py
└── templates/portal/encontros/      # egresso, organizador e moderação

tests/portal/
├── construcao_encontros.py
├── test_encontros_regras.py
├── test_encontros_calendario.py
├── test_encontros_propor.py
├── test_encontros_moderacao.py
├── test_encontros_organizador.py
├── test_encontros_participante.py
├── test_encontros_pagina.py
├── test_encontros_fronteira.py
└── (revisados) test_fronteiras.py, test_entradas.py, test_inicio_convergencia.py, test_navegacao.py, test_desabilitado.py
```

**Structure Decision**: Django modular, sem app novo. Tudo na camada `portal`, num subpacote
próprio, como a 025 e a 026 (R1).

## Complexity Tracking

| Item | Por que é necessário | Alternativa mais simples rejeitada |
|------|----------------------|------------------------------------|
| Três modelos | Proposta, confirmação e denúncia têm ciclos e donos distintos (spec, "Fatos novos") | Um modelo só misturaria a autoria do organizador com dados de outras pessoas |
| Chaves internas à camada | Integridade de Confirmação e Denúncia | UUID solto deixaria órfãos possíveis sem ganho de fronteira (R2) |
| Destino preservado na entrada | O endereço compartilhado precisa voltar ao encontro | Sem isso, quem está fora do público não acha o encontro depois de entrar (H-3108) |

## Riscos de implementação

- **Vazamento do link**: o link entra no contexto do template só pela função de
  visibilidade. Um teste lê o HTML de cada situação e de cada quem (SC-002).
- **Navegação com cinco itens no celular**: já medida na 025. Repetir.
- **Relógio nos testes**: as situações dependem de `agora`. As regras recebem o momento por
  parâmetro, como na 025.
- **Corrida no limite e na moderação**: travas com `select_for_update` (R8, R9) e testes de
  dois pedidos.
- **Protótipo como referência**: as 33 telas já existem. A implementação as segue, e
  divergências são registradas na `validacao.md`.
