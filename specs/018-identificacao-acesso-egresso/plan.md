# Implementation Plan: Identificação e acesso do egresso por dados acadêmicos

**Branch**: `claude/018-identificacao-acesso-egresso` | **Date**: 2026-10-04 | **Spec**: [spec.md](spec.md)

**Input**: `specs/018-identificacao-acesso-egresso/spec.md`, com Clarifications de
2026-10-04. Base: `main` `05d5469` (017 mergeada no PR #27).

## Summary

Novo app `trajetoria.acesso`. O egresso informa CPF e data de nascimento, que são
conferidos contra um material protegido por HMAC: dois valores derivados com chaves
distintas, guardados em `MaterialDeVerificacao`, 1:1 com a Pessoa e fora dela. O material
é derivado no mesmo ato da incorporação acadêmica.

O resultado é sempre um destes:

- `Confirmada`: abre uma sessão do framework que guarda só o UUID da Pessoa;
- `NaoConfirmada`: idêntica para todas as causas e sem gravar nada;
- `Indisponivel`: causas internas distintas (chave, limite, falha técnica).

A limitação de tentativas usa o cache, em dois níveis: origem e CPF protegido.

A jornada (005 a 008) só troca a origem de `pessoa_em_uso`. O seletor de Pessoa fictícia
sai de `demonstracao`. A fronteira acadêmica ganha `cpf` e `data_nascimento` opcionais, e a
fonte simulada recebe dados fictícios para todos os casos da spec. A 016 passa a apontar o
convite para `/acesso/`.

Migrações: `acesso/0001` e as sessões do framework. Nenhuma mudança em Pessoa, Conclusão,
Participação ou Resposta.

## Technical Context

**Language/Version**: Python >=3.13,<3.14 (`pyproject.toml`).

**Primary Dependencies**: Django >=5.2,<5.3. Novo uso, sem dependência nova:
- `django.contrib.sessions` (sessão do egresso, R9);
- framework de cache com `LocMemCache` (limitação, R8);
- `hmac` e `hashlib` da biblioteca padrão (R3).

Sem JavaScript.

**Storage**: PostgreSQL existente.
- **Tabela nova de domínio:** `acesso_materialdeverificacao`.
- **Tabela do framework:** `django_session`.
- **Contadores:** cache local em memória, sem tabela.

**Testing**: pytest >=8.4,<9, pytest-django >=4.11,<5 e ruff >=0.14,<0.15. Relógio
controlado como na 008, `caplog` para a varredura de vazamento e espiões para a
uniformidade da verificação (R16).

**Target Platform**: execução local, navegador, `runserver` com
`TRAJETORIA_DEMONSTRACAO=1` e as duas chaves de acesso exportadas.

**Project Type**: monólito Django modular, HTML renderizado no servidor.

**Performance Goals**: escala da demonstração (11 Pessoas fictícias). A verificação faz
duas derivações HMAC e uma consulta indexada; a sessão faz uma leitura por requisição.
Nenhuma meta produtiva foi inventada.

**Constraints**:
- **Dados.** CPF e data nunca em claro no banco, logs, URLs ou cache.
- **Respostas.** `NAO_CONFIRMADA` indistinguível entre causas; nenhuma gravação de domínio
  no caminho de acesso.
- **Ambiente.** Só modo de demonstração e só base simulada.
- **Jornada.** 005 a 008 inalteradas.
- **Visual.** Baseline 015 preservada.
- **Fora do escopo.** Gov.br, SSO, OTP e CAPTCHA.

**Scale/Scope**: um app, um modelo, três rotas novas (GET e POST `/acesso/`, POST
`/acesso/sair/`), um redirecionamento e dois campos novos no contrato da fonte.

## Constitution Check

Gate executado antes da Fase 0 e repetido após a Fase 1, sobre o data-model e os
contratos. Constituição 1.0.0.

| # | Verificação | Princípios | Pré-Fase 0 | Pós-Fase 1 | Evidência / observação |
| --- | --- | --- | --- | --- | --- |
| 1 | Longitudinalidade | I | ✅ Conforme | ✅ Conforme | Nenhuma escrita em Participação ou Resposta; data-model "Mudanças em entidades" |
| 2 | Pessoa versus Conclusão | I, XI | ✅ Conforme | ✅ Conforme | Material fora da Pessoa e sem atributo acadêmico (R2); a sessão guarda só a Pessoa |
| 3 | Múltiplas formações sem fusão | I, XI | ✅ Conforme | ✅ Conforme | A associação de matrículas fica na fonte (contracts/material.md); colisão nunca funde (R6, R7); seleção pela 007 |
| 4 | Múltiplas participações | I, VIII | ✅ Conforme | ✅ Conforme | Jornada intacta (R10) |
| 5 | Definição de egresso | II | ✅ Conforme | ✅ Conforme | Só há material para Pessoa materializada com conclusão (001 FR-039 inalterado) |
| 6 | Preservação histórica | VIII, XXVII | ✅ Conforme | ✅ Conforme | Migração aditiva; o material não é dado histórico e não altera respostas; a atualização (R6) não toca dados acadêmicos |
| 7 | Pesquisa/Versão/Campanha/Participação distintas | VII, VIII | N/A | N/A | Não toca esses conceitos |
| 8 | Proveniência proporcional | IV | ✅ Conforme | ✅ Conforme | O material deriva da fonte da Pessoa; `atualizado_em`; sinais com `fonte:id_externo` |
| 9 | Institucional × derivado × declarado | III | ✅ Conforme | ✅ Conforme | CPF e data institucionais; material derivado; valores digitados não são Resposta (data-model) |
| 10 | Desacoplamento de integrações | V, XV, XXV | ✅ Conforme | ✅ Conforme | Contrato estendido, com a mesma regra para simulada e real; app separável (R1); dependência só `acesso → academico` (R5) |
| 11 | Fronteira do NIAE | VI | ✅ Conforme | ✅ Conforme | Spec, "Fronteira do NIAE"; não cria gestão de identidade |
| 12 | Governança institucional | IX, X | N/A | N/A | Não toca competências nem periodicidade |
| 13 | Escopo por unidade / visão institucional | XII | N/A | N/A | O egresso não tem escopo administrativo; operadores inalterados |
| 14 | Privacidade e logs | XVI, XVII | ⏸ DECISÃO PENDENTE | ⏸ DECISÃO PENDENTE | Desenho conforme: HMAC, `repr=False`, `no-store`, R14, varredura SC-005. O uso real depende de DP-1801 a DP-1803 |
| 15 | Autorização | X, XII | ✅ Conforme | ✅ Conforme | Posse por formação continua na 007; sessão revalidada a cada requisição (R9); sessão do egresso não concede capacidade institucional |
| 16 | Acessibilidade | XX | ✅ Conforme | ✅ Conforme | R15; contracts/rotas.md "Tela de entrada"; sem CAPTCHA |
| 17 | Responsividade | XIV, XXI | ✅ Conforme | ✅ Conforme | Shell da 015; 320 px; teclado numérico |
| 18 | Testes proporcionais ao risco | XXV, XXVI | ✅ Conforme | ✅ Conforme | R16; matriz da spec; tabela R6; varredura de vazamento |
| 19 | Over engineering | XXII, XXIII, XXIV | ✅ Conforme | ✅ Conforme | Um modelo; sem estrutura genérica de provedores; sem tabela de tentativas; framework para sessão e cache |
| 20 | Exportabilidade | XVIII | ✅ Conforme | ✅ Conforme | O material nunca é exportado (FR-015); exportações inalteradas |
| 21 | Decisões pendentes explicitadas | XXIX | ✅ Conforme | ✅ Conforme | Spec DP-1801 a DP-1809; limiares e tempos como parâmetros, não regra |

**Resultado do gate**: APROVADO. O item 14 não é violação. O desenho cumpre o Princípio
XVI com dados fictícios, e o bloqueio do uso real está registrado nas decisões pendentes,
como na 001 (DP-009) e na 005 (DP-504).

**Conflitos identificados**:

- **001 FR-005 ("não incorporar CPF e data de nascimento nesta feature") e o invariante da
  001 "dados incorporados nunca são atualizados".** Análise:
  1. *A feature está incorreta?* Não. A própria 001 FR-005 prevê a entrada desses dados
     "quando uma feature com consumidor concreto precisar".
  2. *O escopo é excessivo?* Não. Entram só como material derivado, nunca em claro, e
     fora da Pessoa.
  3. *Existe alternativa compatível?* Sim. A atualização vale só para o material (FR-024,
     R6), que não é dado acadêmico. Isso fica registrado em notas de revisão na 001.
  4. Não há emenda constitucional.
- **007 FR-002 e 008 FR-004 vedavam entrada por CPF.** Eram limites de escopo daquelas
  features ("Esta feature NÃO DEVE…"). A 018 cria a entrada fora delas. A 007 continua
  recebendo a Pessoa resolvida, e as notas de revisão registram a mudança. Não há emenda.

## Decisões Pendentes

| ID | DECISÃO PENDENTE | Instância competente | Solução provisória (hipótese) | Como reverter |
| --- | --- | --- | --- | --- |
| DP-1801 | Aceitação do nível de garantia (verificação por conhecimento) | Encarregado com CPAEG/Proex | Decisão de produto; só dados fictícios | Trocar o mecanismo no app `acesso` (FR-016) |
| DP-1802 | Base legal para CPF, data e material | Encarregado | Só dados fictícios | Nenhum código; bloqueia o uso real |
| DP-1803 | Custódia e rotação das chaves; HTTPS; cookie seguro; cache compartilhado; proxy | DTI com o encarregado | Chaves locais por variável; `LocMemCache`; `SESSION_COOKIE_SECURE` por variável; `REMOTE_ADDR` | Configuração; a troca de chave exige reimportação |
| DP-1804 | Profiling da base real | DTI, registro acadêmico, CPAEG | Não bloqueia | — |
| DP-1805 | Cadência de importação | DTI e registro acadêmico | Preparo explícito da demonstração | Rotina futura que chama `incorporar_com_material` |
| DP-1806 | Registro de eventos de segurança | DTI e encarregado | Contadores transitórios; logs sem dados pessoais (R14) | Feature própria, se decidido |
| DP-1807 | Orientação e canal para quem não confirma | Proex/CPAEG, DIREC/CSAEG, registro acadêmico | Mensagem genérica e "Conferir os dados" | 019 |
| DP-1808 | Mecanismo de garantia maior; Portal do Egresso | Proex, DTI, encarregado | Inexistente | Substituir o app `acesso` |
| DP-1809 | Remoção ou revogação explícita pela fonte | DTI e registro acadêmico | Ausência numa carga não apaga (R6) | Novo sinal no contrato da fonte |
| 001/DP-003 | Reconciliação entre fontes | A identificar | Colisão nunca funde | — |
| 004/DP-406 | Forma definitiva de acesso (URL, Portal) | Proex, DTI | `/acesso/` na demonstração | Rota e configuração |

## Project Structure

### Documentation (this feature)

```text
specs/018-identificacao-acesso-egresso/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── verificacao.md
│   ├── material.md
│   └── rotas.md
├── checklists/requirements.md
└── tasks.md              # /speckit-tasks
```

### Source Code (repository root)

```text
config/
├── settings.py      # + django.contrib.sessions, SessionMiddleware, CACHES, chaves e
│                    #   parâmetros de acesso/sessão; comentário "sem sessions" revisado;
│                    #   padrão da URL do convite → /acesso/
└── urls.py          # + include("trajetoria.acesso.urls")

trajetoria/
├── acesso/                          # NOVO app (R1)
│   ├── __init__.py, apps.py
│   ├── models.py                    # MaterialDeVerificacao
│   ├── migrations/0001_initial.py
│   ├── chaves.py                    # validação de chaves e derivações HMAC (R3)
│   ├── normalizacao.py              # CPF (DV) e data (R15)
│   ├── material.py                  # incorporar_com_material, registrar_material (R5, R6)
│   ├── limitacao.py                 # contadores no cache (R8)
│   ├── verificacao.py               # verificar → resultado tipado (R7)
│   ├── sessao.py                    # estabelecer, pessoa_em_uso, encerrar (R9)
│   ├── demonstracao.py              # painel de credenciais fictícias a partir de cenarios (R13)
│   ├── formularios.py               # EntradaForm
│   ├── mensagens.py                 # vocabulário fechado
│   ├── views.py, urls.py            # /acesso/, /acesso/sair/
│   └── templates/acesso/entrada.html
├── fonte_academica/
│   ├── contrato.py                  # PessoaEncontrada + cpf, data_nascimento (R4)
│   ├── cenarios.py                  # PessoaSimulada + campos; valores R13
│   └── simulada.py                  # repassa os campos
├── academico/incorporacao.py        # extrai incorporar_encontrada, sem mudança de comportamento (R5)
├── demonstracao/
│   ├── entrada.py                   # REMOVIDO (seletor de Pessoa)
│   ├── views.py, urls.py            # remove escolher/encerrar; /demonstracao/ → 301 /acesso/
│   ├── templates/demonstracao/entrada.html  # REMOVIDO
│   ├── contexto.py                  # lê a Pessoa de acesso.sessao
│   ├── base.py                      # NOVO: base_somente_simulada(), predicado único (018, preparo, 016)
│   └── cenario.py                   # usa incorporar_com_material; recusa sem chaves
├── interface/
│   ├── views.py                     # importa pessoa_em_uso de acesso.sessao; redireciona a /acesso/
│   └── templates/interface/base.html  # faixa de demonstração: texto novo e "Sair"
└── comunicacao/seguranca.py         # validar_url aceita /acesso/ (R12); validar_origem usa base_somente_simulada

specs/001-nucleo-academico-fonte-simulada/contracts/cenarios-simulados.md
                                     # + tabela "Dados de verificação — fictícios"
.env.example                         # + chaves de acesso, sessão, cookie seguro; URL do convite

tests/
├── conftest.py                      # + fixture autouse com chaves de teste
├── test_fonte_simulada.py           # + tabela de dados de verificação ↔ cenarios
├── test_contrato_fonte.py           # + cpf canônico, repr sem cpf ou data
├── test_incorporacao.py             # + incorporar_encontrada equivalente
├── acesso/                          # NOVO
│   ├── construcao.py
│   ├── test_chaves.py               # validação; derivações; separação de domínio
│   ├── test_normalizacao.py
│   ├── test_material.py             # tabela R6; colisão; sem valores em claro; recusa sem chaves
│   ├── test_preparo.py              # preparo com e sem chaves; 8 materiais, 7 verificadores
│   ├── test_verificacao.py          # matriz da spec; causas internas; uniformidade (espiões)
│   ├── test_limitacao.py            # unidade dos contadores (fundação)
│   ├── test_limitacao_fluxo.py      # US3 por POST real, com relógio controlado
│   ├── test_sessao.py               # US4; invalidação por material
│   ├── test_rotas.py                # contracts/rotas.md; status; no-store; sem dados em URL
│   ├── test_vazamento.py            # SC-005: caplog, Location, banco, sessão, cache
│   ├── test_demonstracao.py         # painel lido só de cenarios; base não simulada
│   └── test_acessibilidade.py       # rótulos, aria, resumo de erros
├── interface/construcao_interface.py  # entrar_como abre a sessão por acesso.sessao.dados_de_sessao
├── interface/test_interface_*.py    # banner, rotas da demonstração e redirecionamentos atualizados
└── comunicacao/                     # URL /acesso/ nos testes que fixam o caminho
```

**Structure Decision**: monólito Django existente, com **um app novo**, `trajetoria.acesso`.
Ele tem domínio e persistência próprios (material, regras de derivação, atualização e
verificação), pelo mesmo critério que fez da 016 um app. Concentrar o mecanismo num app
torna-o substituível sem tocar o núcleo (FR-016). `demonstracao` volta a conter só o
operador fictício e o preparo.

### Impacto nas features anteriores (aplicar com a implementação)

- **Notas de revisão.** Notas "*(Revisado pela 018)*" nas cláusulas listadas na spec
  ("Impacto nas features anteriores"): 001 FR-005, FR-006, FR-028, FR-033 e data-model;
  007 FR-002; 008 FR-004, FR-007, FR-008; 016 FR-021.
- **001.** Tabela nova em `contracts/cenarios-simulados.md`.
- **008.** Os testes que usam `/demonstracao/escolher/` ou o texto antigo do banner são
  atualizados. A jornada não muda.
- **016.** Os testes que fixam `/demonstracao/` na URL do convite são atualizados.
- **017, 011, 010.** Sem mudança.

## Complexity Tracking

Sem violações a justificar. O app novo e a tabela de sessão do framework estão
justificados em R1 e R9 e não contrariam o Princípio XXII: há consumidor concreto e não há
estrutura genérica de identidade.
