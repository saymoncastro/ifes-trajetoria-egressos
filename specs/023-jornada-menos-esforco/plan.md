# Implementation Plan: Jornada de resposta com menos esforço (sem mudar o instrumento)

**Branch**: `claude/trajetoria-ifes-friction-audit-e237ee` | **Date**: 2026-10-05 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/023-jornada-menos-esforco/spec.md`

## Summary

Tirar da jornada do egresso o trabalho desperdiçado medido pela
[auditoria de esforço](../../docs/auditorias/2026-10-05-auditoria-esforco-preenchimento.md),
sem tocar no instrumento. Abordagem técnica:

- **Envio pendente** (EF-01): quando um envio de Seção chega sem sujeito válido, os campos
  da Seção vão para um registro de sessão **separado** (outra chave do armazenamento de
  sessões já existente, validade de 30 min), apontado por uma única chave que atravessa a
  nova confirmação. A sessão do sujeito continua só com o sujeito. A restauração mostra a
  Seção preenchida com o que foi enviado, sem gravar.
- **Indicador de partes** (EF-07, EF-19): função pura nova em `participacao/percurso.py`
  (`maximo_restante`), o caminho mais longo no grafo de Seções da Versão a partir da Seção
  exibida. `SituacaoDaJornada` ganha o campo `conteudo` (aditivo) para a interface calcular.
- **Próxima formação** (EF-06): a confirmação consulta `situacao_de_entrada` (007) e
  oferece a primeira pendente pela entrada existente.
- **Interface** (EF-08, EF-09, EF-11, EF-12, EF-13, EF-17, EF-18, EF-22, EF-23, EF-25,
  EF-26, EF-02): templates, textos fixos e folha de estilo. O complemento usa
  `@supports selector(:has(*))`; sem suporte, nada muda.

Nenhum modelo, migração ou JavaScript. Nenhuma mudança na Versão.

## Technical Context

**Language/Version**: Python 3.13 (uv), como o projeto

**Primary Dependencies**: Django 5.2 (sessões em banco, `django.contrib.sessions`); nada novo

**Storage**: PostgreSQL 16. O envio pendente usa o mesmo armazenamento de sessões
(`django_session`), sem tabela nova

**Testing**: pytest + pytest-django, testes por requisição com o cliente de teste (como
008/014); propriedade do indicador sobre os 17 percursos esperados
(`tests/instrumento/formulario_2024_esperado.py`)

**Target Platform**: servidor Linux; navegadores móveis atuais; funciona sem JavaScript

**Project Type**: aplicação web Django renderizada no servidor

**Performance Goals**: sem meta nova. O indicador é O(Seções) por tela; a tela de formações
calcula a jornada só das formações em andamento (uma ou duas por Pessoa)

**Constraints**: sem JavaScript, sem armazenamento local, sem migração (spec FR-034,
FR-035); sessão do sujeito só com o sujeito (018 FR-040); textos provisórios (008/DP-801)

**Scale/Scope**: cerca de 12 templates, 6 módulos Python e 1 folha de estilo; +1 função
pura de domínio; testes novos e atualização dos testes de texto da 008/014

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Verificação | Princípios | Pré-Fase 0 | Pós-Fase 1 | Evidência / observação |
|---|-------------|------------|------------|------------|------------------------|
| 1 | Longitudinalidade (Pessoa → Conclusão → Participação → Respostas) | I | ✅ Conforme | ✅ Conforme | Resposta só pela 005, por envio da pessoa (spec FR-009, FR-033) |
| 2 | Pessoa versus Conclusão Acadêmica | I, XI | ✅ Conforme | ✅ Conforme | Nada muda; contexto continua da Conclusão |
| 3 | Múltiplas formações sem fusão artificial | I, XI | ✅ Conforme | ✅ Conforme | A próxima formação usa a entrada da 007, uma Participação por formação ([contracts/telas.md](contracts/telas.md)) |
| 4 | Múltiplas participações sem sobrescrita | I, VIII | ✅ Conforme | ✅ Conforme | Envio pendente vale só para a mesma Participação e Seção ([data-model.md](data-model.md)) |
| 5 | Definição institucional de egresso | II | N/A | N/A | Elegibilidade e entrada inalteradas |
| 6 | Preservação histórica | VIII, XXVII | ✅ Conforme | ✅ Conforme | Sem mudança na Versão nem migração; teste de não regressão do instrumento (FR-037) |
| 7 | Pesquisa/Versão/Campanha/Participação distintas | VII, VIII | ✅ Conforme | ✅ Conforme | Indicador lê a Versão aplicada; nada é persistido |
| 8 | Proveniência proporcional | IV | ✅ Conforme | ✅ Conforme | Envio pendente nunca vira Resposta sem envio; origem "declarado, não gravado" |
| 9 | Institucional, derivado e declarado separados | III | ✅ Conforme | ✅ Conforme | Nenhum pré-preenchimento a partir da Conclusão ou da Formação Declarada (FR-033) |
| 10 | Desacoplamento de integrações | V, XV, XXV | ✅ Conforme | ✅ Conforme | Armazenamento do envio pendente fica em `acesso/pendente.py`, com conteúdo opaco; a 018 não importa a interface |
| 11 | Fronteira do NIAE | VI | N/A | N/A | Dentro da jornada de acompanhamento |
| 12 | Governança institucional | IX, X | N/A | N/A | Nada de periodicidade, publicação ou competência |
| 13 | Escopo por unidade | XII | N/A | N/A | Só jornada do egresso |
| 14 | Privacidade, minimização, logs | XVI, XVII | ✅ Conforme | ✅ Conforme | Envio pendente sem CPF/data, fora da URL e da tela de confirmação, validade de 30 min, apagado ao consumir, ao sair e ao trocar de sujeito; nada em log ([research.md](research.md) R1, R2). Termos continuam visíveis (FR-025) |
| 15 | Autorização | X, XII | ✅ Conforme | ✅ Conforme | Restauração só para o sujeito dono da Participação; a posse é verificada como hoje (`_participacao_do_sujeito`) |
| 16 | Acessibilidade | XX | ✅ Conforme | ✅ Conforme | "(obrigatória)" continua para tecnologia assistiva; alvos de 44 px; `details` nativo ([research.md](research.md) R5, R6) |
| 17 | Responsividade e jornada móvel | XIV, XXI | ✅ Conforme | ✅ Conforme | É o propósito; medição a 375×812 no fechamento (FR-038) |
| 18 | Testes proporcionais ao risco | XXV, XXVI | ✅ Conforme | ✅ Conforme | Propriedade do indicador nos 17 percursos; ciclo do envio pendente; igualdade de `NAO_CONFIRMADA` ([quickstart.md](quickstart.md)) |
| 19 | Over engineering | XXII, XXIII, XXIV | ✅ Conforme | ✅ Conforme | Sem modelo, sem JS, sem abstração genérica; um registro de sessão e uma função pura |
| 20 | Exportabilidade | XVIII | N/A | N/A | Exportações inalteradas (FR-036) |
| 21 | Decisões pendentes explícitas | XXIX | ✅ Conforme | ✅ Conforme | Hipóteses (limiar de 8 Perguntas, 15 caracteres) marcadas como tal; nenhuma regra institucional nova |

**Resultado do gate**: APROVADO

**Conflitos identificados**:

- **008 FR-091 / 014 FR-042 (nada de rascunho não enviado persistido) e 008 FR-095 / 014
  FR-043 (sem indicador de progresso).** Análise: (1) a feature não está incorreta: o
  solicitante decidiu preservar o envio expirado (S1) e incluir o indicador (escopo
  aprovado); (2) o escopo não é excessivo: a exceção cobre só o envio que já ia ser
  gravado; (3) alternativa compatível: sim. O registro é transitório, separado da sessão do
  sujeito, nunca vira Resposta sozinho, e o indicador não persiste nada. Encaminhamento:
  revisão explícita dos requisitos das features anteriores (spec, "Requisitos revisados").
  Não é conflito constitucional.

## Decisões Pendentes

Nenhuma nova. As DPs do instrumento (003/DP-301 a DP-309), de linguagem (008/DP-801) e de
identidade (018/DP-1801 a DP-1808) continuam abertas e fora do escopo.

## Project Structure

### Documentation (this feature)

```text
specs/023-jornada-menos-esforco/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── rotas.md         # mudanças de rota, redirecionamento e avisos
│   └── telas.md         # ordem e conteúdo de cada tela alterada
├── checklists/requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
trajetoria/
├── acesso/
│   ├── pendente.py            # NOVO: guardar/ler/descartar o envio pendente (registro separado)
│   ├── sessao.py              # sinal de sessão expirada; a chave do envio pendente atravessa estabelecer/encerrar
│   ├── mensagens.py           # avisos "sessao" e "selo"
│   ├── views.py               # aviso por código na entrada; esconder "Continuar…" após falha
│   └── templates/acesso/entrada.html   # dois passos; dica; avisos
├── declaracao/
│   ├── sessao.py              # sinal de expiração; chave do envio pendente atravessa estabelecer_declarante
│   ├── formularios.py         # autocomplete do nome; nível em rádios
│   ├── views_egresso.py       # aviso de selo; "Corrigir"; reconciliar envio pendente; "você parou em"
│   └── templates/declaracao/egresso.html
├── participacao/
│   ├── percurso.py            # NOVO: maximo_restante (função pura)
│   └── consultas.py           # SituacaoDaJornada.conteudo (aditivo)
└── interface/
    ├── views.py               # redirecionamento com aviso; envio pendente; parte/máximo; próxima formação; "parte anterior salva"
    ├── formularios.py         # itens sem erro (restauração); lado a lado; complemento visível; rótulo
    ├── mensagens.py           # textos novos
    ├── apresentacao.py        # rótulo "Parte X"; "você parou em"
    └── templates/interface/   # secao, perguntas/*, conclusao, concluida, formacoes, estilo.css, jornada.css

tests/
├── acesso/test_pendente.py              # NOVO
├── participacao/test_jornada_maximo.py  # NOVO (propriedade nos 17 percursos)
├── interface/test_interface_esforco.py  # NOVO (FRs da 023)
└── (atualizações) interface/test_interface_secao.py, _rodape.py, _conclusao.py,
    _acessibilidade.py, editor/test_editor_previa.py, declaracao/test_rotas_egresso.py,
    acesso/test_rotas.py
```

**Structure Decision**: mantém a estrutura modular existente. O único módulo novo de
produção (`acesso/pendente.py`) fica na 018, porque trata de sessão. O conteúdo do envio é
opaco para ela: quem monta e interpreta os campos é a interface.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Registro de sessão separado para o envio pendente | Limitar a retenção a 30 min mais a limpeza diária, mesmo se a pessoa confirmar e sair sem enviar (FR-004), e manter a sessão do sujeito só com o sujeito (FR-005) | Guardar na própria sessão: depois da confirmação, ela vive até 2 semanas no banco (`SESSION_COOKIE_AGE`) e passaria a carregar Participação e respostas (contraria 018 FR-040). Tabela nova: contraria FR-034 |
| Campo `conteudo` em `SituacaoDaJornada` | O indicador precisa do grafo da Versão já carregado | Reler a Versão na interface: segunda leitura da mesma árvore; a 008 FR-092 pede registrar a lacuna em vez de suprir com regra na interface |
