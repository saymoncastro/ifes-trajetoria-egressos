# Implementation Plan: Gestão mínima de Campanha

**Branch**: `claude/spec-017-campaign-management-e96f8f` | **Date**: 2026-10-03 | **Spec**: [spec.md](spec.md)

**Input**: `specs/017-gestao-minima-campanha/spec.md`, com Clarifications de 2026-10-03.
Main sincronizada por fast-forward em `5e50fec` (PR #26, ADR 0004).

## Summary

Interface administrativa mínima, só no modo de demonstração, para a CPAEG fictícia criar
(nome + Versão publicada; período opcional), completar ou corrigir enquanto nunca aberta,
abrir e encerrar Campanhas. Tudo pelas operações da 004. A integração acontece nas páginas
da 011: "Nova Campanha" na lista e um painel de gestão no detalhe, visíveis só para quem
tem `pode_gerir_campanha`. Há quatro rotas novas sob `/acompanhamento/`, num subpacote
`trajetoria/acompanhamento/gestao/` com barreira própria (`@gestao`); `trajetoria/campanha`
continua sendo o domínio. Nenhum app novo (R1).

Há duas mudanças pequenas fora desse subpacote. A verificação de abertura sai de `abrir` para
uma consulta compartilhada `impedimentos_de_abertura`, sem mudar comportamento. O rótulo de
situação da 011 distingue "Período encerrado — Campanha nunca aberta". Nenhuma migração.

## Technical Context

**Language/Version**: Python >=3.13,<3.14 (`pyproject.toml`).

**Primary Dependencies**: Django >=5.2,<5.3 (forms, templates e CSRF nativos). Sem
dependência nova, sem JavaScript.

**Storage**: PostgreSQL existente. Escrita só pelas operações da 004 em `Campanha`; nenhuma
tabela, coluna ou migração.

**Testing**: pytest >=8.4,<9, pytest-django >=4.11,<5, ruff >=0.14,<0.15. Fixtures e
construtores do acompanhamento (011) e da Campanha (004).

**Target Platform**: execução local, navegador, `runserver` com `TRAJETORIA_DEMONSTRACAO=1`.

**Project Type**: monólito Django modular, HTML renderizado no servidor.

**Performance Goals**: escala da demonstração (poucas Campanhas e Versões). O painel
acrescenta ao detalhe uma consulta de impedimentos (uma leitura da Versão). A confirmação
de abertura faz uma consulta das Campanhas em coleta. Sem meta produtiva inventada.

**Constraints**: CPAEG apenas; modo de demonstração apenas; nenhum critério, lote ou
publicação na interface; regra de abertura única (004); lista e detalhe da 011 somente GET;
HTML da 011 inalterado para CSAEG, salvo o rótulo de FR-023a; baseline 015 preservada.

**Scale/Scope**: quatro rotas (nova, editar, abrir, encerrar), um formulário, duas
confirmações, um painel incluído no detalhe, uma regra de governança, uma consulta de
domínio extraída e um rótulo de apresentação.

## Constitution Check

Gate executado antes da Fase 0 e repetido após a Fase 1 sobre os contratos. Constituição
1.0.0.

| # | Verificação | Princípios | Pré-Fase 0 | Pós-Fase 1 | Evidência / observação |
| --- | --- | --- | --- | --- | --- |
| 1 | Longitudinalidade | I | ✅ Conforme | ✅ Conforme | Nenhuma escrita em Participação/Resposta (FR-015, FR-025) |
| 2 | Pessoa versus Conclusão | I, XI | N/A | N/A | Não lê Pessoa nem Conclusão além dos indicadores da 011 |
| 3 | Múltiplas formações | I, XI | N/A | N/A | Idem; sobreposição só informada (FR-019) |
| 4 | Múltiplas participações | I, VIII | ✅ Conforme | ✅ Conforme | Encerrar preserva Participações (004) |
| 5 | Definição de egresso | II | ✅ Conforme | ✅ Conforme | Campanha criada sem critério; nenhum critério na interface |
| 6 | Preservação histórica | VIII, XXVII | ✅ Conforme | ✅ Conforme | Só Versão PUBLICADA; Campanha aberta imutável; contracts/dominio.md |
| 7 | Pesquisa/Versão/Campanha/Participação distintas | VII, VIII | ✅ Conforme | ✅ Conforme | Nenhum modelo alterado; Versão nunca alterada |
| 8 | Proveniência proporcional | IV | ✅ Conforme | ✅ Conforme | Sem autoria com operadores fictícios; DP-1701 |
| 9 | Institucional × derivado × declarado | III | ✅ Conforme | ✅ Conforme | Impedimentos e rótulos derivados, não persistidos (data-model) |
| 10 | Desacoplamento de integrações | V, XV, XXV | N/A | N/A | Sem integração externa |
| 11 | Fronteira do NIAE | VI | ✅ Conforme | ✅ Conforme | Spec, "Fronteira do NIAE" |
| 12 | Governança institucional | IX, X | ⏸ DECISÃO PENDENTE | ⏸ DECISÃO PENDENTE | DP-402, 002/DP-001, DP-401 abertas; interpretação C1 só na demonstração; nenhuma periodicidade |
| 13 | Escopo por unidade / visão institucional | XII | ✅ Conforme | ✅ Conforme | CPAEG institucional; CSAEG sem gestão (C2) |
| 14 | Privacidade e logs | XVI, XVII | ✅ Conforme | ✅ Conforme | Nenhum dado pessoal nas telas novas; mensagens sem identificador |
| 15 | Autorização (menor privilégio) | X, XII | ✅ Conforme | ✅ Conforme | `pode_gerir_campanha` relido por requisição; R2, R3 |
| 16 | Acessibilidade | XX | ✅ Conforme | ✅ Conforme | `editor/_campo.html`, foco em erros, teclado; quickstart passo 13 |
| 17 | Responsividade | XIV, XXI | ✅ Conforme | ✅ Conforme | Shell da 011; 320 px |
| 18 | Testes proporcionais ao risco | XXV, XXVI | ✅ Conforme | ✅ Conforme | Matriz da spec; equivalência de impedimentos (R5) |
| 19 | Over engineering | XXII, XXIII, XXIV | ✅ Conforme | ✅ Conforme | Zero entidades; sem critérios, remoção, lote, scheduler, workflow |
| 20 | Exportabilidade | XVIII | N/A | N/A | Nada exportado |
| 21 | Decisões pendentes explicitadas | XXIX | ✅ Conforme | ✅ Conforme | Spec, "Decisões Pendentes"; C1–C4 marcadas [Interpretação] |

**Resultado do gate**: APROVADO. O item 12 não é violação: X é respeitado porque a
capacidade nasce de interpretação identificada, reversível e restrita à demonstração,
e as decisões pendentes continuam registradas.

**Conflitos identificados**:

- **004 FR-056, 010 FR-033/FR-073 e 011 FR-001/FR-016/FR-100 proíbem expor gestão de
  Campanha enquanto DP-402 estiver aberta.** Análise pelos quatro passos:
  1. *A feature está incorreta?* Não; o solicitante pediu a gestão mínima.
  2. *O escopo é excessivo?* Foi reduzido: só CPAEG, só demonstração, sem critérios nem
     remoção.
  3. *Existe alternativa compatível?* Sim. Interpretação operacional reversível
     (Princípio XXIX), no mesmo formato já usado na 010, 011 e 016, com notas de revisão
     nas cláusulas afetadas.
  4. Não há emenda constitucional.

## Decisões Pendentes

| ID | DECISÃO PENDENTE | Instância competente | Solução provisória (hipótese) | Como reverter |
| --- | --- | --- | --- | --- |
| 004/DP-402 | Quem gere Campanha | Proex/CPAEG (Art. 26) | `pode_gerir_campanha` = CPAEG ativa, só na demonstração (C1) | Trocar a regra única em `governanca/regras.py`; operações não mudam |
| 002/DP-001, DP-002 | Quem publica Versão e como se aprova | Proex/CPAEG | Só Versões já PUBLICADA; nenhuma superfície de publicação | Feature própria antes do piloto |
| 004/DP-401 | Periodicidade e duração das rodadas | Proex/Proen | Nenhum padrão; datas livres | Nenhum código a reverter |
| 004/DP-403 | Campanhas de unidade | CPAEG com Proex | CSAEG sem gestão | Nova regra, se decidido |
| 004/DP-404 | Sobreposição em coleta | CPAEG | Aviso simples na confirmação, sem bloqueio | Remover o aviso ou aplicar a política decidida |
| 004/DP-405 | Prorrogação e reabertura | CPAEG/Proex | Inexistentes | Feature própria |
| DP-1701 | Autoria da gestão | CPAEG/Proex, DTI, encarregado | Nenhum registro | Feature própria com identidade real (010/DP-1001) |

## Project Structure

### Documentation (this feature)

```text
specs/017-gestao-minima-campanha/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── rotas.md
│   └── dominio.md
├── checklists/requirements.md
└── tasks.md              # /speckit-tasks
```

### Source Code (repository root)

```text
trajetoria/
├── governanca/regras.py                   # + pode_gerir_campanha (C1)
├── campanha/
│   ├── consultas.py                       # + impedimentos_de_abertura (extraída)
│   └── operacoes.py                       # abrir usa impedimentos_de_abertura; sem mudança de comportamento
└── acompanhamento/
    ├── acesso.py                          # Atuacao.gerir_campanha; + @gestao (modo, operador, regra)
    ├── apresentacao.py                    # + rótulo "Período encerrado — Campanha nunca aberta"
    ├── consultas.py                       # CampanhaAcompanhada.situacao usa o rótulo novo
    ├── views.py                           # (011, só GET) detalhe: contexto do painel se gerir_campanha
    ├── urls.py                            # + 4 rotas de gestão
    ├── gestao/                            # escrita e orquestração da 017; sem modelos
    │   ├── __init__.py
    │   ├── formularios.py                 # CampanhaForm (nome, versao, inicio, fim)
    │   ├── mensagens.py                   # vocabulário fechado
    │   ├── painel.py                      # painel(campanha, agora), versões oferecidas, abrangência
    │   └── views.py                       # nova, editar, abrir, encerrar
    └── templates/acompanhamento/
        ├── campanhas.html                 # + "Nova Campanha" se gerir_campanha
        ├── campanha.html                  # + aviso pós-ação; include do painel se gerir_campanha
        └── gestao/
            ├── formulario.html
            ├── confirmar_abertura.html
            ├── confirmar_encerramento.html
            ├── conflito.html              # 409
            └── _painel.html

tests/
├── campanha/test_campanha_impedimentos.py # equivalência com abrir
├── governanca/                            # + pode_gerir_campanha
├── comunicacao/test_demonstracao.py      # inventário semântico (sem contagem de rotas)
└── acompanhamento/
    ├── test_acompanhamento_acesso.py      # inventário semântico: uma barreira por rota
    ├── test_gestao_acesso.py              # US5, FR-001–FR-005
    ├── test_gestao_criar_editar.py        # US1, US2
    ├── test_gestao_abrir_encerrar.py      # US3, US4
    ├── test_gestao_painel.py              # FR-016, FR-017, FR-022, FR-023, FR-023a
    └── test_gestao_acessibilidade.py      # FR-029
```

**Structure Decision**: monólito Django existente, sem app novo. A escrita e a orquestração
da 017 ficam no subpacote `trajetoria/acompanhamento/gestao/`, dentro do shell
administrativo que já é da 011; `trajetoria/campanha` continua sendo o domínio, e
`acompanhamento/views.py` continua somente leitura (R1, R4). Um app separado só se
justificaria com domínio ou persistência próprios, que a 017 não tem.

### Impacto nas features anteriores (aplicar com a implementação)

- Notas "*(Revisado pela 017)*" nas cláusulas listadas na spec ("Impacto nas features
  anteriores").
- Testes de inventário de rotas da 011 e da 016: deixam de fixar a quantidade de rotas e
  passam a verificar barreiras e métodos semanticamente (R12).
- Teste da 011 com "Encerrada" em Campanha nunca aberta e expirada, se houver: rótulo novo.
  Os testes atuais da lista usam a Campanha E, encerrada explicitamente, que não muda.

## Complexity Tracking

Sem violações a justificar.
