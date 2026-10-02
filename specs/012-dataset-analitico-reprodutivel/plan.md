# Implementation Plan: Dataset analítico institucional reprodutível

**Branch**: `claude/feature-012-dataset-analitico-bdc50a` | **Date**: 2026-10-02 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/012-dataset-analitico-reprodutivel/spec.md`

## Summary

O plan entrega a menor persistência capaz de congelar o que hoje pode derivar numa Campanha
encerrada:

1. pertencimento ao universo analítico;
2. elegibilidade naquele momento;
3. contexto acadêmico naquele momento.

Todo o resto (Campanha, Versão e estrutura, Participação, `concluida_em`, Respostas,
seleções, complementos) já é historicamente imutável depois do encerramento e é
**referenciado** na leitura, nunca copiado.

Abordagem técnica (detalhes em [research.md](research.md)):

- **Verificação no código primeiro** (R1): só pertencimento à população e contexto
  acadêmico derivam. O nome da Pesquisa muda, mas não é dado analítico.
- **App novo `trajetoria/analitico`** (R2), dependente das features anteriores e do qual
  nenhuma depende.
- **Dois modelos** (R3): `SnapshotAnalitico` (`id`, `campanha`, `capturado_em`) e
  `RegistroDoSnapshot` (`snapshot`, `conclusao`, `elegivel_no_snapshot` e os sete
  atributos de contexto da 001). `UNIQUE (snapshot, conclusao)`. Uma migration aditiva.
- **Ano e data: ambos** (R4). São atributos independentes na 001 (a fonte pode dar só o
  ano); nenhum é derivado do outro.
- **Contexto = `CAMPOS_DE_CONTEXTO` da 001**, copiado sem transformação e sem repetir CHECKs
  (R5).
- **`on_delete`** (R6): Conclusão `PROTECT` (a origem não destrói snapshot em silêncio);
  Campanha `PROTECT`; snapshot → registros `CASCADE` (o registro é parte do snapshot).
- **Universo e elegibilidade por duas consultas claras** (R7): população pela
  `populacao_no_momento(campanha)` da 004 (elegíveis) e Conclusões com Participação na
  Campanha (as que sobram, não elegíveis), unidas e deduplicadas por Conclusão na
  operação. Contrato público da 004, sem critério copiado; sem UNION, SQL manual ou
  query builder.
- **`capturar_snapshot(campanha)`** (R8): transação única; momento lido pela própria
  operação, sem parâmetro `agora`, como momento técnico da captura; um `bulk_create`;
  verificações de integridade na mesma transação. Atomicidade = snapshot e todos os
  registros, ou nada; **sem** leitura isolada, nível de isolamento ou lock adicional. A
  escrita concorrente iniciada antes do encerramento é detectada pela verificação final e
  desfaz tudo. Recusas `CAMPANHA_NUNCA_ABERTA` e `COLETA_NAO_ENCERRADA` (R10).
- **Rascunhos** (R9): Respostas fora do percurso calculadas pelas funções puras da 006, na
  composição de `situacao_da_jornada`. Concluídas não são recalculadas nem limpas.
- **Reprodução sem a Conclusão atual** (R11): agregação só sobre os registros e
  `Exists(Participacao)` por `conclusao_id`. Nenhuma tabela da 001 nem de Resposta no SQL.
- **Fronteira de leitura mínima** (R12): iterador de objetos de valor pequenos
  (`LinhaDoDataset`), sem N+1, com Respostas na semântica da 005 como `RespostaNoDataset`
  (nunca instâncias de `Resposta`, que levariam à Conclusão atual e à Pessoa). Não é a
  013: sem schema, colunas, serializador, achatamento, nomes externos, CSV ou GeN.
- **Vários snapshots, sem lock, sem "atual"** (R13).
- **Sem interface, sem regra nova, sem command** (R14); **demonstração inalterada**,
  fixtures isoladas nos testes (R15).

## Technical Context

**Language/Version**: Python 3.13 (ADR 0001).

**Primary Dependencies**: Django 5.2 LTS e psycopg 3. Recursos usados: `transaction.atomic`,
`bulk_create`, `values_list`, `Exists`/`OuterRef` (só na reprodução de indicadores),
`aggregate`/`values().annotate()` com `Count(filter=…)`. **Nenhuma dependência nova.**

**Storage**: PostgreSQL 16+ (ADR 0001). Duas tabelas novas; nenhuma alteração em tabela
existente. Nível de isolamento padrão, sem mudança e sem lock adicional (R7, R8).

**Testing**: pytest + pytest-django. Recursos usados:

- `django_db` padrão; `django_db(transaction=True)` só no teste opcional de capturas
  simultâneas em threads (mesmo padrão da 005);
- `CaptureQueriesContext` para verificar que a reprodução não lê tabelas da 001 nem de
  Resposta;
- `monkeypatch` para falha simulada no meio da captura;
- construções existentes de `tests/acompanhamento/construcao.py` e
  `tests/participacao/construcao.py`.

**Target Platform**: servidor Linux; desenvolvimento local em macOS.

**Project Type**: aplicação web Django monolítica (ADR 0001). Esta feature não acrescenta
interface.

**Performance Goals**: nenhuma meta numérica. Captura e leitura proporcionais ao universo
da Campanha, sem consulta por Conclusão (spec FR-110, FR-112).

**Constraints**:

- nenhum dado das Features 001 a 011 é alterado (spec FR-002);
- reprodução nunca lê a Conclusão atual (spec FR-080);
- nenhuma PII nem Resposta copiada (spec FR-120, FR-121);
- sem cache, visão materializada, job, fila, worker, lock distribuído (spec FR-111).

**Scale/Scope**: dezenas de Campanhas; até dezenas de milhares de Conclusões por Campanha;
poucas capturas por Campanha.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Verificação | Princípios | Pré-Fase 0 | Pós-Fase 1 | Evidência / observação |
|---|-------------|------------|------------|------------|------------------------|
| 1 | Longitudinalidade (Pessoa → Conclusão → Participação → Respostas) | I | ✅ Conforme | ✅ Conforme | Snapshot por Campanha; registro por Conclusão; Participação e Respostas referenciadas pela cadeia existente (data-model §1.3) |
| 2 | Pessoa versus Conclusão Acadêmica (campus/curso no contexto da conclusão) | I, XI | ✅ Conforme | ✅ Conforme | Contexto congelado da Conclusão; Pessoa não lida (R1, R16) |
| 3 | Múltiplas formações da mesma Pessoa sem fusão artificial | I, XI | ✅ Conforme | ✅ Conforme | Grão Conclusão; `UNIQUE (snapshot, conclusao)`; união por Conclusão (R7) |
| 4 | Múltiplas participações sem sobrescrita | I, VIII | ✅ Conforme | ✅ Conforme | Nenhuma escrita em Participação; snapshots independentes por Campanha (R13) |
| 5 | Definição institucional de egresso respeitada | II | ✅ Conforme | ✅ Conforme | Elegibilidade só por `populacao_no_momento` (R7) |
| 6 | Preservação histórica | VIII, XXVII | ✅ Conforme | ✅ Conforme | Snapshot imutável; Conclusão `PROTECT`; migration aditiva; nada existente alterado (R6, R8) |
| 7 | Versionamento; Pesquisa/Versão/Campanha/Participação distintas | VII, VIII | ✅ Conforme | ✅ Conforme | Snapshot ≠ Campanha; Versão referenciada pela Campanha; Respostas pela Pergunta da Versão aplicada (R2, R12) |
| 8 | Proveniência proporcional à finalidade e ao risco | IV | ✅ Conforme | ✅ Conforme | Contexto marcado institucional no momento da captura; referência à Conclusão de origem; `capturado_em` (data-model §2) |
| 9 | Separação entre dado institucional, derivado e declarado; divergências explícitas | III | ✅ Conforme | ✅ Conforme | `ContextoCongelado` × `respostas` × elegibilidade/situação em campos separados; Q14 declarada (contracts/consultas.md) |
| 10 | Desacoplamento de integrações (providers/adaptadores, mock com mesmo contrato) | V, XV, XXV | ✅ Conforme | ✅ Conforme | Nenhuma integração; a fonte acadêmica não é consultada na captura (R5) |
| 11 | Fronteira do NIAE (5 perguntas do Princípio VI, se aplicável) | VI | ✅ Conforme | ✅ Conforme | spec, "Fronteira do NIAE" |
| 12 | Governança institucional (periodicidade, publicação, competências normativas) | IX, X | ✅ Conforme | ✅ Conforme | Nenhuma competência criada; nenhum snapshot "oficial" (DP-1201); exposição futura restrita à CPAEG (R14) |
| 13 | Escopo por unidade e visão institucional consolidada | XII | ✅ Conforme | ✅ Conforme | Capacidade institucional, não exposta; nada à CSAEG (R14) |
| 14 | Privacidade, minimização e dados pessoais em logs/exportações | XVI, XVII | ✅ Conforme | ✅ Conforme | Campos exatos sem PII; sem cópia de Resposta; sem hash; mensagens sem valores; dados fictícios (R16) |
| 15 | Autorização (menor privilégio; competência técnica ≠ normativa) | X, XII | ✅ Conforme | ✅ Conforme | Nenhuma superfície exposta; nenhuma regra por simetria (R14) |
| 16 | Acessibilidade (WCAG 2.1 AA / eMAG, quando houver interface) | XX | N/A | N/A | Sem interface |
| 17 | Responsividade e jornada móvel | XIV, XXI | N/A | N/A | Sem interface; jornada do egresso intocada |
| 18 | Testes proporcionais ao risco cobrindo invariantes afetados | XXV, XXVI | ✅ Conforme | ✅ Conforme | "Estratégia de testes" abaixo; casos A a O |
| 19 | Risco de over engineering (YAGNI; sem form builder universal) | XXII, XXIII, XXIV | ✅ Conforme | ✅ Conforme | Dois modelos; nenhum framework, warehouse, ETL, cache, job ou API (R3, R12) |
| 20 | Exportabilidade e semântica das exportações (se aplicável) | XVIII | ✅ Conforme | ✅ Conforme | Fronteira de leitura estável com categorias de dado preservadas; formato é da 013 (R12) |
| 21 | Decisões pendentes explicitadas; nenhuma hipótese virou regra | XXIX | ✅ Conforme | ✅ Conforme | "Decisões Pendentes" abaixo; nenhuma regra de "mais recente" (R13) |

**Resultado do gate**: **APROVADO** antes da Fase 0 e depois da Fase 1.

**Conflitos identificados**: nenhum.

- A tensão "004 FR-032 × snapshot" (spec, Invariantes) foi reexaminada no desenho: o
  snapshot não toca a Campanha nem a população dinâmica, e nenhuma regra transacional o
  consulta (R2, R7).
- O desvio do padrão `agora=` das operações (R8) não é conflito constitucional. É decisão
  da spec (FR-016) para que o momento histórico gravado não seja escolhido pelo chamador.

## Decisões Pendentes

| ID | DECISÃO PENDENTE | Instância competente (se conhecida) | Solução provisória (hipótese) | Como reverter |
|----|------------------|-------------------------------------|-------------------------------|---------------|
| DP-1201 | Qual fotografia sustenta publicação institucional; denominador de referência | CPAEG/Proex | Vários snapshots independentes, sem status; toda leitura recebe o snapshot explicitamente; nenhuma função "atual/último" | Uma decisão futura pode acrescentar designação explícita sem alterar snapshots existentes |
| DP-1202 | Retenção e eliminação de snapshots | Encarregado de dados, com CPAEG | Nenhuma remoção; `PROTECT` na Conclusão faz qualquer eliminação futura exigir decisão explícita; dados fictícios | Operação de eliminação específica, decidida; o `CASCADE` snapshot → registros já remove o snapshot inteiro |
| 004/DP-408 | Fotografia na abertura; fotografia de referência | Proex/CPAEG | Parcialmente resolvida: fotografia após o encerramento | Nova captura em outro momento exigiria spec própria |
| 005/DP-507 | Efeito transacional de correção acadêmica | CPAEG | Analítico resolvido: registro não elegível; snapshot não muda | — |
| 001/DP-005 | Correção de dado acadêmico | CPAEG, registro acadêmico | Nenhuma operação de correção; testes simulam por escrita direta no teste | Operação de correção futura não afeta snapshots existentes |
| 005/DP-503 | Uso analítico de Participações não concluídas | CPAEG, encarregado de dados | Preservadas e distinguíveis no dataset (R9) | A 013 decide representação |
| 005/DP-505 | Acesso a dados identificados | CPAEG/Proex, encarregado de dados | Nada exposto; referências técnicas internas | A feature que expuser decide |
| 006/DP-601, 007/DP-703 | Recusa; "iniciada" | CPAEG/Proex | Mesmas definições da 011 | Mudam só a reprodução |
| 011/DP-1101, DP-1102 | Pequenos grupos; coorte | CPAEG/Proex | Sem supressão interna; ano e data congelados | A 013 aplica supressão |
| 002/DP-006 | Comparabilidade entre Versões | CPAEG | Nenhuma correspondência entre Perguntas | — |
| 001/DP-009, 005/DP-504 | Base legal, retenção | Encarregado de dados | Somente dados fictícios | — |
| 010/DP-1001 | Identificação produtiva | DTI, Proex | Nada exposto; sem registro de solicitante | — |

## Project Structure

### Documentation (this feature)

```text
specs/012-dataset-analitico-reprodutivel/
├── spec.md
├── plan.md              # este arquivo
├── research.md          # Fase 0 (R1–R16)
├── data-model.md        # Fase 1: dois modelos, objetos de valor, derivações
├── quickstart.md        # Fase 1: validação de ponta a ponta
├── contracts/
│   ├── operacoes.md     # capturar_snapshot, vocabulário de recusa
│   └── consultas.md     # snapshots_da_campanha, indicadores, recortes, dataset
├── checklists/
│   └── requirements.md
└── tasks.md             # Fase 2 (/speckit-tasks — NÃO criado por este comando)
```

### Source Code (repository root)

```text
trajetoria/
└── analitico/                         # NOVO app
    ├── __init__.py
    ├── apps.py
    ├── models.py                      # SnapshotAnalitico, RegistroDoSnapshot
    ├── regras.py                      # Motivo, SnapshotRecusado, CapturaInconsistente
    ├── operacoes.py                   # capturar_snapshot (único caminho de escrita)
    ├── consultas.py                   # snapshots_da_campanha, indicadores_do_snapshot,
    │                                  # recorte_do_snapshot, linhas_do_dataset;
    │                                  # ContextoCongelado, ParticipacaoNoDataset,
    │                                  # RespostaNoDataset,
    │                                  # LinhaDoDataset, IndicadoresDoSnapshot,
    │                                  # RecorteDoSnapshot, LinhaDoRecorte
    └── migrations/
        ├── __init__.py
        └── 0001_initial.py            # aditiva
config/
└── settings.py                        # ALTERADO: + "trajetoria.analitico" em INSTALLED_APPS

tests/
└── analitico/                         # NOVO
    ├── conftest.py                    # cenário de referência fictício (Campanhas E, V, C, P, X)
    ├── construcao.py                  # Campanha encerrada com coleta no passado; reusa
    │                                  # tests/acompanhamento/construcao.py e
    │                                  # tests/participacao/construcao.py
    ├── test_analitico_modelo.py
    ├── test_analitico_regras.py
    ├── test_analitico_captura.py
    ├── test_analitico_universo.py
    ├── test_analitico_contexto.py
    ├── test_analitico_reproducao.py
    ├── test_analitico_multiplos.py
    ├── test_analitico_dataset.py
    └── test_analitico_fronteiras.py
```

**Structure Decision**: monólito Django existente, com um app novo e pequeno. `analitico`
depende de `campanha` (estado, `populacao_no_momento`, `momento_de_referencia`),
`participacao` (modelos; `percurso` puro), `academico` (modelo, só na captura),
`instrumento` (`conteudo_da_versao`, `EstadoVersao`) e `fonte_academica.contrato`
(`CAMPOS_DE_CONTEXTO`). Nenhum deles importa `analitico`. `analitico` **não** importa
`acompanhamento`, `interface`, `editor`, `demonstracao` nem `governanca`.

## Alterações em features anteriores

| Feature | Alteração | Semântica |
|---------|-----------|-----------|
| 001 | Nenhuma. `CAMPOS_DE_CONTEXTO` consumida como está | Inalterada |
| 002/003 | Nenhuma | Inalterada |
| 004 | Nenhuma. `populacao_no_momento`, `estado`, `momento_de_referencia` consumidos como estão | **Inalterada** |
| 005/006 | Nenhuma. Modelos lidos; `percorrer`, `respondidas`, `perguntas_do_percurso` reutilizadas | **Inalteradas** |
| 007 | Só teste: `tests/participacao/test_entrada_aceitacao.py::test_12_nada_de_gen_ou_dashboard` deixa de considerar o app `analitico` (a FR-051 da 007 é escopo negativo da própria 007; a 012 é a feature prevista pela 004/DP-408). Mesmo padrão da 011 com o teste da 010 | Regra da 007 **inalterada**; a proibição continua para todos os outros apps |
| 008/009 | Nenhuma | Inalteradas |
| 010 | Nenhuma | Nenhuma regra nova |
| 011 | Nenhuma. Não passa a usar snapshot | **Inalterada**, operacional atual |
| Demonstração | Nenhuma | Cenário intacto |
| `config/settings.py` | + app em `INSTALLED_APPS` | Técnico |

Nenhum bloqueio exigiu mudança semântica em feature anterior.

## Estratégia de testes

Cada linha é ao menos um teste automatizado. Os dados são fictícios e construídos pelas
operações das features anteriores. A **única** exceção é a alteração acadêmica simulada
(casos G, J, K): `ConclusaoAcademica.objects.filter(…).update(…)` dentro do teste,
documentada como simulação de 001/DP-005 (R15).

**Captura e momento** (US1, US2; FR-010 a FR-016, FR-052, FR-053; casos A, B, L, M)

| Teste | Resultado |
|-------|-----------|
| Campanha aberta e encerrada explicitamente | Snapshot criado, referência à Campanha, `antes ≤ capturado_em ≤ depois` |
| Campanha aberta e encerrada pelo fim do período, sem `encerrada_em` | Aceita |
| Campanha EM COLETA | `COLETA_NAO_ENCERRADA`; zero snapshots e registros |
| Campanha nunca aberta, EM PREPARAÇÃO | `CAMPANHA_NUNCA_ABERTA`; nada gravado |
| Campanha nunca aberta e expirada (ENCERRADA pelo tempo) | `CAMPANHA_NUNCA_ABERTA` (não `COLETA_NAO_ENCERRADA`) |
| Argumento que não é `Campanha` | `TypeError`, sem consulta |
| A operação não aceita momento informado | Assinatura sem parâmetro de momento |
| Campanha encerrada sem Participações (caso B) | Todos os registros elegíveis; nenhuma Participação |
| População vazia e sem Participações | Snapshot com zero registros, sem erro |
| Falha simulada durante a gravação dos registros (`bulk_create` substituído no teste) | Nenhum snapshot nem registro órfão |
| Falha simulada na verificação final | `CapturaInconsistente`; nada gravado |
| Versão não publicada forçada no teste | `CapturaInconsistente`; nada gravado |

**Universo e elegibilidade** (US3, US5; FR-020 a FR-034; casos F, G)

| Teste | Resultado |
|-------|-----------|
| Universo = elegíveis ∪ Conclusões com Participação | Conjunto exato de `conclusao_id` |
| Uma linha por Conclusão (elegível e com Participação) | Exatamente um registro |
| Elegível sem Participação | Registro elegível |
| Participação elegível | Registro elegível |
| Participação de Conclusão que deixou de satisfazer os critérios (simulação) | Registro **não elegível**, com contexto congelado |
| Elegíveis do snapshot = `populacao_no_momento(campanha).count()` | Igual |
| Para cada registro, `elegivel_no_snapshot == avaliar(campanha, conclusao).elegivel` | Igual (equivalência com a 004) |
| Duas Conclusões da mesma Pessoa | Dois registros, nenhuma marca de relação |
| Conclusão incorporada depois do encerramento e antes da captura | Registro elegível |
| Campanha sem critérios (população ampla) | Universo = todas as Conclusões; todas elegíveis (a combinação `\|` com filtro vazio não restringe) |
| Captura sem N+1 | Número de consultas igual com 3 e com 30 Conclusões (sem orçamento fixo) |
| Participação confirmada depois da leitura do universo (simulada no teste) | `CapturaInconsistente`; nada gravado |

**Contexto congelado** (US4; FR-040 a FR-047; casos H, I)

| Teste | Resultado |
|-------|-----------|
| Sete atributos copiados | Iguais aos da Conclusão no momento da captura |
| Atributos ausentes | `None` preservado |
| Ano sem data | Ano congelado, data `None` |
| Ano e data | Ambos congelados |
| Grafia como registrada (espaços, maiúsculas) | Idêntica, sem normalização |
| Cursos homônimos na Serra e em Vitória | Duas linhas no recorte por curso |

**Reprodução** (US6, US8, US9, US10; FR-080 a FR-091; casos J, K)

| Teste | Resultado |
|-------|-----------|
| Alteração direta dos seis atributos de todas as Conclusões depois da captura | Registros, indicadores e seis recortes idênticos |
| Incorporação de novas Conclusões elegíveis depois da captura | Elegíveis do snapshot inalterados; 011 mostra elegíveis atuais maiores |
| Indicadores do conjunto de referência | Iguais à contagem manual, por elegibilidade |
| Concluída por Q1 = "Não" | Conta como concluída |
| Participação não elegível | Conta no numerador, não no denominador; taxa > 100% sem truncamento |
| Zero elegíveis | Taxas `None` |
| Seis recortes | Soma das linhas = totais; linha de não informado |
| Logo após a captura, sem deriva | Totais e linhas com contagem iguais aos da 011 em escopo institucional |
| SQL da reprodução | Nenhuma tabela da 001 e nenhuma tabela de Resposta |
| Enum de recortes | Campos iguais aos da `Recorte` da 011 (importada só no teste) |

**Vários snapshots e concorrência** (US11; FR-060 a FR-064; caso N)

| Teste | Resultado |
|-------|-----------|
| Snapshot A, alteração simulada, snapshot B | B reflete o novo estado; A idêntico |
| A e B da mesma Campanha | Coexistem; registros independentes; ambos em `snapshots_da_campanha`, em ordem `(capturado_em, id)` |
| Capturas repetidas sem mudança | Snapshots distintos e equivalentes, sem deduplicação |
| Uma captura completa ocorrendo durante outra (determinístico) | Dois snapshots completos e independentes |
| Duas capturas simultâneas em threads (`transaction=True`, opcional, como na 005) | Dois snapshots completos e independentes |

**Dataset** (US7, US12; FR-070 a FR-077; casos C, D, E, F, O)

| Teste | Resultado |
|-------|-----------|
| Participação concluída normalmente | `participacao.concluida`; Respostas presentes; `fora_do_percurso = ∅` |
| Concluída por Q1 = "Não" | Concluída, com a única Resposta |
| Rascunho com Respostas fora do percurso | Não concluída; Respostas preservadas; `fora_do_percurso` = o de `situacao_da_jornada` |
| Versão com estrutura não suportada (rascunho) | `fora_do_percurso = None` (não determinável); Respostas preservadas |
| Elegível sem Participação | `participacao = None`; `respostas` vazio |
| Escolha múltipla | Conjunto de Opções da estrutura existente |
| Respostas associadas à Pergunta da Versão aplicada | `pergunta.secao.versao == campanha.versao` |
| Dataset depois da alteração acadêmica | Contexto inalterado; nenhuma consulta à tabela da 001 |
| Consultas do dataset | Número igual com 3 e com 30 registros (sem N+1) |
| Objetos entregues, inclusive aninhados | Nenhuma instância de `Resposta`, `Participacao`, `RegistroDoSnapshot`, `ConclusaoAcademica` ou `Pessoa`; nenhum atributo de objeto entregue leva a eles |
| Q14 da baseline publicada respondida | Em `respostas`, separada do `nivel` congelado (ADR 0003) |

**Fronteiras e privacidade** (FR-001, FR-050, FR-061, FR-100 a FR-125; SC-008, SC-009)

| Teste | Resultado |
|-------|-----------|
| Campos dos dois modelos | Exatamente os de data-model §1 |
| Campos de contexto do registro | Iguais a `CAMPOS_DE_CONTEXTO` |
| Nenhum campo de PII, `fonte`, `id_externo`, Pessoa, Resposta, Pergunta, Opção, texto | Ausentes |
| `on_delete` | Conclusão e Campanha `PROTECT`; snapshot → registros `CASCADE` |
| Exclusão de Conclusão referenciada (forçada no teste) | `ProtectedError`; snapshot intacto |
| Apps do projeto | Exatamente dois modelos novos; nenhum modelo de cópia de Participação, Resposta, Opção, Pergunta, Versão ou Pessoa |
| `consultas.__all__` | Sem "atual", "vigente", "ultimo", "recente" |
| `operacoes` | Só `capturar_snapshot` escreve; nenhuma operação de edição ou remoção |
| Imports de `analitico` | Nenhum de `acompanhamento`, `interface`, `editor`, `demonstracao`, `governanca` |
| Nenhuma URL, view ou management command novo | Ausentes |
| Mensagens de recusa e de inconsistência | Sem valores acadêmicos |
| Suíte da 011 | Passa sem alteração |

## Sinais de over engineering (parar se aparecerem)

Nenhum destes é necessário, e qualquer um deles bloqueia a implementação até nova
discussão:

- terceiro modelo sem dado mutável concreto; `SnapshotParticipacao`, `SnapshotResposta`,
  `SnapshotOpcao`, `SnapshotPergunta`, `SnapshotVersao`, `SnapshotPessoa`;
- totais, status, título, autor ou sequência no snapshot;
- fato, dimensão, star schema, warehouse, data mart, banco analítico;
- ETL, pipeline, extractor/loader, DAG, scheduler, framework de lotes;
- modelo base genérico de snapshot, tabelas de histórico genéricas, event sourcing;
- serializador genérico, nomes finais de coluna, achatamento Q01…, formato GeN;
- visão materializada, cache, tabela de agregação, Celery, job, fila, Redis, worker;
- `select_for_update` na Campanha, lock distribuído, deduplicação de capturas;
- função "snapshot atual/vigente/último";
- API, endpoint, view, rota, management command, exportação, dashboard;
- `pode_capturar_snapshot` ou outra regra de governança por simetria;
- mudança em `trajetoria/demonstracao`, na 011 ou em qualquer feature anterior.

## Volta à spec?

**Não é necessária.** O research confirmou as premissas da spec:

- nenhum dado presumido imutável se mostrou mutável de forma relevante;
- ano e data são atributos independentes, como a spec consolidada prevê;
- o contrato da 004 basta;
- as funções puras da 006 bastam para o Achado A1.

Ajustes de redação já consolidados na spec, sem efeito novo no comportamento:
Clarifications de 2026-10-02 (FR-016, FR-048, FR-064) e precisões da aprovação do plan
(FR-054 reescrito: o corte é o que a captura leu, sem leitura isolada; FR-062; FR-070
fronteira mínima).

## Complexity Tracking

Vazio. Nenhuma violação da Constituição a justificar: dois modelos com dado mutável
concreto, uma migration aditiva, nenhuma abstração genérica e nenhuma infraestrutura.
