# Implementation Plan: Pesquisa, versão e estrutura do instrumento

**Branch**: `claude/feature-002-pesquisa-versao-6b2c5d` | **Date**: 2026-10-01 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/002-pesquisa-versao-instrumento/spec.md`

## Summary

A 002 entrega o modelo canônico do instrumento — **Pesquisa → Versão → Seções →
Perguntas → Opções**, com escala, encaminhamento de Seção e regra de navegação — e nada
além disso. Os elementos técnicos são:

- **Novo app Django `trajetoria.instrumento`**, independente do núcleo acadêmico, com
  **cinco modelos**: `Pesquisa`, `Versao`, `Secao`, `Pergunta` e `Opcao`.
  - A escala são quatro colunas da Pergunta (R5).
  - A regra de navegação são duas colunas da Opção (R6). Isso torna impossível, por
    construção, duas regras por Opção ou regra com Opção de outra Pergunta.
  - O encaminhamento é uma FK opcional da Seção (R7).
  - A ordem é uma `posicao` inteira com unicidade adiada por conjunto (R4).
- **Operações de domínio** (`operacoes.py`): único caminho de escrita. Cada uma é
  atômica, bloqueia a Versão e rejeita violações com `OperacaoRejeitada`, que traz o
  motivo e o elemento (R8). `publicar` reúne todas as pendências de completude.
  `criar_versao_a_partir_de` faz cópia profunda com tradução de referências (R11).
- **Leitura** (`conteudo.py`): árvore imutável de dataclasses, comparável por igualdade.
  O mesmo contrato documenta o percurso de Seções (para onde se vai depois de cada
  Seção), que esta feature não executa. O **momento** de aplicação da regra não é
  modelado (FR-053; R13, R14).
- **Imutabilidade na aplicação**: a Versão publicada é protegida pelas operações, único
  caminho de escrita, e por testes de invariante por operação. Sem gatilhos de banco
  (R9; [ADR 0002](../../docs/adr/0002-imutabilidade-versao-publicada.md) rejeitado nesta
  fase).
- **Tipo da Pergunta imutável**: definido na criação; para mudar, remove-se e recria-se
  (FR-062).

Decisões e alternativas estão em [research.md](research.md).

## Technical Context

- **Language/Version**: Python 3.13 ([ADR 0001](../../docs/adr/0001-stack-inicial.md)).
- **Primary Dependencies**: Django 5.2 LTS e psycopg 3. Nenhuma dependência nova (R1).
- **Storage**: PostgreSQL 16+. Integridade local em CHECK e UNIQUE (inclusive adiada e
  parcial) (R4, R5). Regras que dependem de outra linha (estado da Versão, mesma
  Versão, tipo da Pergunta) ficam nas operações (R8, R9).
- **Testing**: pytest, pytest-django e ruff, em PostgreSQL, sem rede.
- **Target Platform**: servidor Linux, para operação futura; nesta feature, execução local
  e CI.
- **Project Type**: aplicação web monolítica (Django), ainda sem camada web, interface ou
  API.
- **Performance Goals**: N/A (spec, Assumptions).
- **Constraints**:
  - sem dado pessoal e sem dependência de Pessoa ou Conclusão Acadêmica;
  - textos preservados exatamente como recebidos;
  - nenhuma interface expõe edição ou publicação (DP-001).
- **Scale/Scope**: dezenas de Seções e centenas de Perguntas e Opções por Versão (o
  instrumento atual tem 13 Seções, 54 Perguntas e cerca de 385 Opções); 5 modelos; 1
  migração; cerca de 20 operações.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Verificação | Princípios | Pré-Fase 0 | Pós-Fase 1 | Evidência / observação |
|---|-------------|------------|------------|------------|------------------------|
| 1 | Longitudinalidade (Pessoa → Conclusão → Participação → Respostas) | I | N/A | N/A | Nenhum elo da cadeia é criado. A Versão com identidades estáveis (R3) é o que Respostas futuras referenciarão |
| 2 | Pessoa versus Conclusão Acadêmica (campus/curso no contexto da conclusão) | I, XI | N/A | N/A | App independente, sem import nem FK para `academico` (R2, FR-065) |
| 3 | Múltiplas formações da mesma Pessoa sem fusão artificial | I, XI | N/A | N/A | Fora do escopo |
| 4 | Múltiplas participações sem sobrescrita | I, VIII | N/A | N/A | Participação fora do escopo |
| 5 | Definição institucional de egresso respeitada | II | N/A | N/A | Fora do escopo |
| 6 | Preservação histórica | VIII, XXVII | ✅ | ✅ | Versão publicada imutável em toda operação de escrita, sem operação de volta a rascunho nem de exclusão; cópia sem compartilhamento; testes por operação (R8, R9, R11, SC-002, SC-003). Migração cria tabelas novas, sem dados existentes |
| 7 | Versionamento; Pesquisa/Versão/Campanha/Participação distintas | VII, VIII | ✅ | ✅ | `Pesquisa` e `Versao` são modelos distintos; conteúdo só na Versão; sem "versão vigente"; nenhum modelo de Campanha ou Participação ([data-model](data-model.md)) |
| 8 | Proveniência proporcional à finalidade e ao risco | IV | ✅ | ✅ | `origem` e `publicada_em` na Versão; sem histórico de edição nem correspondência entre elementos (R11, DP-006) |
| 9 | Separação entre dado institucional, derivado e declarado; divergências explícitas | III | N/A | N/A | Nenhum dado das três categorias; a classificação das perguntas atuais é da Feature 003 |
| 10 | Desacoplamento de integrações (providers/adaptadores, mock com mesmo contrato) | V, XV, XXV | N/A | N/A | Sem integração externa. Importação do Google Formulários fora do escopo |
| 11 | Fronteira do NIAE (5 perguntas do Princípio VI, se aplicável) | VI | ✅ | ✅ | Respondidas na spec |
| 12 | Governança institucional (periodicidade, publicação, competências normativas) | IX, X | ⏸ | ⏸ | Só dois estados, sem workflow. `publicar` não é exposta por nenhum ponto de entrada até DP-001 (R17, [contrato](contracts/operacoes.md#publicar)) |
| 13 | Escopo por unidade e visão institucional consolidada | XII | N/A | N/A | Pesquisa institucional única; sem vínculo com unidade |
| 14 | Privacidade, minimização e dados pessoais em logs/exportações | XVI, XVII | ✅ | ✅ | Nenhum dado pessoal. Termo e Q1 só como texto e pergunta, sem registro de consentimento (DP-007) |
| 15 | Autorização (menor privilégio; competência técnica ≠ normativa) | X, XII | N/A | N/A | Sem interface, admin, comando ou API (R17) |
| 16 | Acessibilidade (WCAG 2.1 AA / eMAG, quando houver interface) | XX | N/A | N/A | Sem interface. Textos de pergunta, explicativos e rótulos de escala ficam disponíveis para a futura jornada |
| 17 | Responsividade e jornada móvel | XIV, XXI | N/A | N/A | Sem jornada. A forma de apresentação não é fixada no modelo (FR-035) |
| 18 | Testes proporcionais ao risco cobrindo invariantes afetados | XXV, XXVI | ✅ | ✅ | Matriz em [Estratégia de testes](#estratégia-de-testes); imutabilidade testada por operação suportada |
| 19 | Risco de over engineering (YAGNI; sem form builder universal) | XXII, XXIII, XXIV | ✅ | ✅ | 4 tipos, 2 estados, 5 modelos, regra em duas colunas, sem JSON de configuração. Sem gatilhos (ADR 0002 rejeitado); tipo imutável em vez de matriz de transições. Ver [Complexity Tracking](#complexity-tracking) |
| 20 | Exportabilidade e semântica das exportações (se aplicável) | XVIII | N/A | N/A | Exportação fora do escopo. UUIDs estáveis e modelo relacional facilitam exportações futuras (R3, R10) |
| 21 | Decisões pendentes explicitadas; nenhuma hipótese virou regra | XXIX | ✅ | ✅ | DP-001 a DP-007 abaixo; hipóteses da spec (FR-042, FR-059 b, c) implementadas como restrições localizadas e reversíveis |

**Resultado do gate**: APROVADO (pré-Fase 0 e pós-Fase 1). O item 12 está como DECISÃO
PENDENTE, sem violação: a feature especifica o efeito da publicação e não atribui a
ninguém a competência de publicar.

**Conflitos identificados**: nenhum. A tensão com o Princípio X (publicação sem
competência definida) está tratada por não exposição (R17) e registrada em DP-001.

## Decisões Pendentes

| ID | DECISÃO PENDENTE | Instância competente (se conhecida) | Solução provisória (hipótese) | Como reverter |
|----|------------------|-------------------------------------|-------------------------------|---------------|
| DP-001 | Quem pode publicar uma Versão | Proex/CPAEG (PAEG Art. 21, VI; Art. 26) | `publicar` existe só como operação de domínio; nenhum ponto de entrada a expõe | Feature futura acrescenta autorização no ponto de entrada; a operação não muda |
| DP-002 | Workflow de elaboração e aprovação | CPAEG, Proex, Proen | Só `RASCUNHO` e `PUBLICADA` | Novos estados anteriores à publicação por migração aditiva; `publicar` ajustado |
| DP-003 | Correções editoriais após a publicação | CPAEG | Imutabilidade total nas operações, como regra operacional provisória, não decisão institucional | Nova operação de correção editorial, por spec própria, preservando a interpretação histórica |
| DP-004 | Melhorias metodológicas do instrumento | CPAEG e áreas de ensino, pesquisa e extensão | Nenhuma; a estrutura não altera conteúdo | Novas Versões |
| DP-005 | Novos tipos ou capacidades de pergunta | CPAEG (necessidade); spec própria (capacidade) | Só os quatro tipos (CHECK) | Ampliar o CHECK e o enum por migração |
| DP-006 | Comparabilidade de perguntas entre Versões | CPAEG | Só `origem` na Versão | Tabela ou coluna de correspondência, aditiva |
| DP-007 | Forma institucional do termo de consentimento e base legal | A identificar (encarregado de dados, CPAEG) | Termo como texto de Seção; Q1 como escolha única com finalização | Artefato próprio de termo, por spec futura, sem alterar Versões publicadas |

## Desenho

### Modelo

Cinco modelos em [data-model.md](data-model.md). Pontos principais:

- **Identidade**: UUID em todas as entidades (R3).
- **Ordem**: `posicao` com `UNIQUE … DEFERRABLE INITIALLY DEFERRED` por conjunto (R4).
- **Ausência**: `NULL`; cadeia vazia proibida (R16).
- **Tipos e escala**: CHECKs na Pergunta garantem os quatro tipos e a coerência da
  escala (R5).
- **Regra**: `regra_destino` ou `regra_finaliza` na Opção, nunca os dois (R6).
- **Encaminhamento**: FK opcional da Seção (R7).
- **Versão**: `estado`, `publicada_em` coerentes por CHECK; `origem` opcional.

### Operações e rejeições

[contracts/operacoes.md](contracts/operacoes.md) define cada operação, seus efeitos e
seus motivos de rejeição. Fluxo de toda operação de escrita:

1. abre transação;
2. bloqueia a Versão (`select_for_update`);
3. se publicada, rejeita com `VERSAO_PUBLICADA`;
4. verifica as regras daquela operação, na ordem do contrato;
5. grava; a unicidade adiada é conferida no fim da transação.

`publicar` usa uma função de completude que devolve **todas** as violações (FR-014). Não
há framework de validação: cada operação verifica explicitamente as suas regras.

### Nova Versão

`criar_versao_a_partir_de` copia em quatro passos (R11): Versão, Seções, Perguntas e
Opções, e por fim encaminhamentos e regras traduzidos por um mapa de identidades.
Teste-chave: nenhum `id` da árvore nova aparece na origem, e a leitura da origem é igual
antes e depois.

### Leitura e percurso

[contracts/conteudo.md](contracts/conteudo.md) define a árvore `ConteudoVersao` e o
percurso de Seções: o destino de uma regra acionada prevalece sobre encaminhamento e
fluxo padrão, e a terminação é garantida por destinos posteriores. Em que momento a regra
é aplicada dentro da Seção (e se as perguntas seguintes a X aparecem) fica para a
Feature 003 e a jornada de resposta: não há atributo, enumeração ou estratégia para
isso. Não há código de produção que execute a navegação.

### Imutabilidade

Garantida só pela aplicação (R9). Não há gatilho, hook de modelo nem camada de
permissões. O que sustenta a garantia:

- toda escrita passa por `operacoes.py`, e toda operação chama `_bloquear` e
  `_exigir_rascunho` antes de qualquer verificação;
- nenhuma operação recebe `estado`, volta a `RASCUNHO`, muda a Pesquisa da Versão ou
  exclui Versão;
- `publicar` em Versão publicada não grava nada (`JA_PUBLICADA`);
- testes de invariante tentam, numa Versão publicada, cada operação de escrita sobre
  Versão, Seção, Pergunta e Opção e comparam o conteúdo antes e depois (SC-002).

## Estratégia de testes

O foco são os invariantes da spec, não um percentual de cobertura (XXVI). Um auxiliar de
teste (`tests/instrumento/construcao.py`) constrói Versões e enumera percursos de Seções
segundo o [contrato](contracts/conteudo.md#percurso-de-seções).

| Teste | Dado | Requisito |
|-------|------|-----------|
| Pesquisa e Versões distintas; várias Versões; designação repetida rejeitada; nada depende de Pessoa | Banco sem Pessoa | US1, FR-001–FR-008, FR-065 |
| Ordem segue as posições e não a criação; reordenação completa; movimentação de Pergunta | Criação embaralhada | US2, FR-045–FR-047, SC-005 |
| Quatro tipos, cada um aceitando só sua configuração; quinto tipo rejeitado | Uma pergunta por tipo | US3, FR-034–FR-038 |
| Opções com identidade estável ao mudar o texto; complemento textual; escala com e sem rótulo; listas iguais independentes | Q8/Q9 fictícias | US4, FR-040–FR-044 |
| Publicação com e sem pendências; todas as pendências listadas; `JA_PUBLICADA` sem mudar `publicada_em` | Versões completa e incompleta | US5, FR-013–FR-015, FR-059 |
| Versão publicada: editar Versão; voltar a rascunho; adicionar, alterar, mover, reordenar e remover Seção, Pergunta e Opção; regras e encaminhamentos — tudo rejeitado, com conteúdo idêntico (`==`) | Uma tentativa por operação e atributo | FR-013, FR-016, FR-017, SC-002 |
| Renomear Pesquisa não altera Versão publicada | — | FR-003 |
| Cópia profunda: identidades novas, referências internas, origem intocada e registrada | Versão com regras e encaminhamentos | US6, FR-019–FR-023, SC-003 |
| Percursos de Seções: fluxo padrão, regra para Seção, convergência por encaminhamento, salto de ramo, finalização, regra redundante, pergunta opcional sem resposta; pergunta com regras no meio da Seção representável sem atributo de momento | Padrões de Q1, Q14, Q33, Q46, Q51 com textos fictícios | US7, US8, FR-048–FR-055 |
| Cada `Motivo` provocado; elemento identificado; estado igual após rejeição | Uma operação por motivo | US9, FR-058–FR-062, SC-004 |
| Remoção em rascunho: Pergunta leva Opções e regras; Seção referenciada ou com Perguntas rejeitada | — | FR-061 |
| Tipo imutável: `alterar_pergunta` não aceita `tipo` | — | FR-062 |
| Versão de demonstração cobre as características de "intenção" da tabela de cobertura e é publicável | Construída pelo auxiliar | SC-001 |
| Exatamente 4 tipos e 2 estados; app sem import de `academico`; suíte da 001 inalterada | — | SC-006, SC-007 |

## Project Structure

### Documentation (this feature)

```text
specs/002-pesquisa-versao-instrumento/
├── spec.md
├── plan.md               # este arquivo
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── operacoes.md
│   └── conteudo.md
├── checklists/requirements.md
└── tasks.md              # gerado por /speckit-tasks (não por este comando)
```

### Source Code (repository root)

```text
config/
└── settings.py           # INSTALLED_APPS ganha "trajetoria.instrumento"
trajetoria/
├── academico/            # Feature 001 — não alterado
├── fonte_academica/      # Feature 001 — não alterado
└── instrumento/          # app Django desta feature
    ├── __init__.py
    ├── apps.py
    ├── models.py         # Pesquisa, Versao, Secao, Pergunta, Opcao; TipoPergunta, EstadoVersao
    ├── regras.py         # Motivo, Violacao, OperacaoRejeitada, verificação de completude
    ├── operacoes.py      # operações de escrita, publicar, criar_versao_a_partir_de
    ├── conteudo.py       # ConteudoVersao e demais dataclasses; conteudo_da_versao
    └── migrations/
        └── 0001_initial.py
tests/
├── (arquivos da Feature 001 — não alterados)
└── instrumento/
    ├── construcao.py     # auxiliares, Versão de demonstração, enumeração de percursos
    ├── test_instrumento_modelo.py
    ├── test_instrumento_estrutura.py
    ├── test_instrumento_publicacao.py
    ├── test_instrumento_nova_versao.py
    ├── test_instrumento_navegacao.py
    ├── test_instrumento_rejeicoes.py
    └── test_instrumento_aceitacao.py
docs/adr/0002-imutabilidade-versao-publicada.md   # rejeitado nesta fase (adiado)
```

**Structure Decision**:

- Um app novo, `instrumento`, que não importa nada de `academico` nem de
  `fonte_academica` (R2). Campanha, Participação e Resposta terão apps próprios que
  dependerão dele.
- `regras.py` separa o vocabulário de rejeição das operações, para que testes e
  consumidores importem `Motivo` sem importar as operações.
- Os testes desta feature ficam em `tests/instrumento/`, porque são sete arquivos mais
  um auxiliar. Os nomes têm prefixo `test_instrumento_` para não colidir com os da 001
  (a pasta `tests/` não é pacote). Os testes da 001 não são movidos.
- Sem admin, comando de gestão, URLs ou API (R17).

## Complexity Tracking

Nenhuma violação a justificar.

Complexidade adicional adotada, com justificativa (não é violação):

- **Unicidade adiada (R4)**: necessária para reordenar sem estados intermediários
  inválidos.

Considerados e **não** adotados:

- form builder genérico, JSON Schema, configuração por tipo em JSON;
- motor de regras, expressões, condição de exibição, tabela de regras;
- workflow de aprovação, estados intermediários, histórico de edição, event sourcing;
- banco global de perguntas, catálogo de Opções, códigos de pergunta;
- documento JSON congelado por Versão;
- correspondência entre elementos de Versões;
- admin, CRUD, API, comando de gestão;
- repository pattern, framework de validação;
- gatilhos PL/pgSQL, hooks de `save()`/`delete()`, sinais ou camada de permissões para
  imutabilidade (ADR 0002 rejeitado nesta fase);
- matriz de mudança de tipo de pergunta (tipo imutável, FR-062);
- função de produção que execute o percurso;
- atributo, enumeração ou estratégia de momento de aplicação da regra.

Ver [research.md](research.md), R5 a R10, R13, R14 e R17.

## Para specs futuras

- **Feature 003 (migração semântica do instrumento)**: usar estas operações; classificar
  cada peculiaridade (O-8, O-10, O-15, O-16) como intenção ou acidente. Em especial,
  decidir se Q47 e Q48 devem ser respondidas antes do desvio de Q46 (FR-053 deixa isso em
  aberto) e representar a resposta com a estrutura existente — por exemplo, a ordem das
  Perguntas e a divisão em Seções. Decidir quem publica a Versão migrada depende de
  DP-001.
- **Campanha**: escolhe uma Versão publicada; nada aqui define "Versão vigente".
- **Jornada de resposta**: implementa o percurso de Seções do
  [contrato](contracts/conteudo.md#percurso-de-seções) e define o momento de aplicação das
  regras dentro da Seção, além de obrigatoriedade, complemento textual e apresentação
  (botões ou lista).
- **Editor administrativo e autorização**: dependem de DP-001 e DP-002.
- **Exportação**: depende de DP-006 para séries entre Versões.
