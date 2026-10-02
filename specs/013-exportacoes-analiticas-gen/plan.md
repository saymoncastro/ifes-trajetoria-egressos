# Implementation Plan: Exportações analíticas e contrato de dados para o GeN

**Branch**: `claude/feature-013-analytics-exports-190965` | **Date**: 2026-10-02 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/013-exportacoes-analiticas-gen/spec.md`

## Summary

A exportação é uma **representação** de um snapshot analítico explicitamente informado.
Ela não cria verdade nova, não persiste nada e não conhece o GeN. Um dataset lógico único
(Dados, Dicionário, Metadados) é montado a partir da fronteira de leitura da 012 e da Versão
imutável, e duas funções explícitas o serializam em CSV (pacote ZIP) e XLSX.

Abordagem técnica (detalhes em [research.md](research.md)):

- **Fonte** (R1): `linhas_do_dataset` (012), que recebe o conteúdo já lido,
  `conteudo_da_versao` (002), campos da Campanha fixados na abertura. Há dois acréscimos
  pontuais:
  - `perguntas_do_percurso` em `LinhaDoDataset`, na 012, com a mesma composição das regras
    puras da 006 que a 012 já usa;
  - uma consulta da 013 à referência Conclusão → Pessoa, só a chave estrangeira.
- **Pacote `trajetoria/exportacao/`, sem app Django** (R2), com seis módulos pequenos:
  `contrato`, `regras`, `pseudonimos`, `dataset`, `formatos` e o `__init__` documental.
  Não há modelo, migration, view, rota, comando ou regra de governança.
- **Dataset lógico tipado** (R3). O tipo Python decide a representação em cada formato, e
  há uma única semântica para CSV e XLSX.
- **Chaves técnicas** (R4): `pergunta_<uuid.hex>`, `__aplicavel`, `__opcao_<uuid.hex>`,
  `__complemento`, na ordem Seção → Pergunta → Opção.
- **Pseudônimos** (R5): HMAC-SHA-256 sobre `conclusao:<uuid>` e `pessoa:<uuid>`.
  - A chave é dedicada (`TRAJETORIA_CHAVE_PSEUDONIMIZACAO`), com pelo menos 32 caracteres e
    diferente de `SECRET_KEY`.
  - Sem chave, a exportação é recusada. Nada é persistido.
- **Aplicabilidade** (R6): verdadeiro/falso pela pertença ao percurso; vazio sem
  Participação ou com percurso não determinável. Concluída sem percurso, ou com Resposta
  fora dele, é inconsistência.
- **Respostas validadas por forma** (R7). Escolha múltipla vira indicadores; complemento
  tem coluna própria.
- **Metadados fixos** (R8): sem nome da Pesquisa, sem `encerrada_em`, sem `gerado_em`.
- **Dicionário** (R9): 24 colunas, um-para-um com Dados, mais os valores possíveis da
  escolha única e as regras de navegação por posição.
- **CSV** (R10): biblioteca padrão, RFC 4180, UTF-8 sem BOM, escape contra fórmula com
  reversão universal, ZIP determinístico.
- **XLSX** (R11, R12):
  - **XlsxWriter** (dependência nova) com escrita tipada explícita e `strings_to_formulas`
    desligado, em memória;
  - verificação prévia de valores não representáveis;
  - **openpyxl** só nos testes, para leitura independente.
- **Erros** (R14): `ExportacaoRecusada`, `ExportacaoInconsistente` e
  `ValorNaoRepresentavel`, sem arquivo parcial e sem valores nas mensagens.

## Technical Context

**Language/Version**: Python 3.13 (ADR 0001).

**Primary Dependencies**:

- Django 5.2 LTS e psycopg 3, como hoje.
- Biblioteca padrão: `csv`, `zipfile`, `io`, `hmac`, `hashlib`.
- **Nova**: `XlsxWriter>=3.2,<4`, só para escrever XLSX (R11).
- **Nova, só desenvolvimento**: `openpyxl>=3.1,<4`, para os testes lerem o XLSX.

**Storage**: PostgreSQL 16+ (ADR 0001), **somente leitura**. Nenhuma tabela nova nem
alteração. Os arquivos são produzidos em memória e devolvidos como `bytes`, sem gravação em
disco.

**Testing**: pytest + pytest-django.

- Fixture `settings` para a chave fictícia.
- `CaptureQueriesContext` para o número fixo de consultas.
- Leitura independente com `zipfile`, `csv` e `openpyxl`.
- Construções existentes de `tests/analitico/construcao.py` e
  `tests/participacao/construcao.py`.
- Marcador `volume` (fora da suíte padrão) para SC-012.

**Target Platform**: servidor Linux; desenvolvimento local em macOS.

**Project Type**: aplicação web Django monolítica (ADR 0001). Esta feature não acrescenta
interface.

**Performance Goals**: SC-012 (hipótese): menos de 1 minuto por formato para 20 mil
registros e um instrumento do porte do formulário 2024, no ambiente de desenvolvimento.
Consultas em número fixo por exportação (R15).

**Constraints**:

- snapshot sempre explícito (FR-001);
- nenhuma leitura de contexto acadêmico atual (FR-003);
- nenhuma escrita (FR-005, FR-130);
- nenhuma PII nem identificador interno exportado (FR-026, FR-110);
- nenhum job, cache ou transporte (FR-121, FR-131);
- nenhum arquivo em disco (FR-114).

**Scale/Scope**: dezenas de Campanhas; até dezenas de milhares de registros por snapshot;
instrumento da ordem de 50 Perguntas e de 150 colunas de Pergunta; exportações raras.

Nenhum item `NEEDS CLARIFICATION`. A escolha da biblioteca de XLSX está resolvida em R11.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Verificação | Princípios | Pré-Fase 0 | Pós-Fase 1 | Evidência / observação |
|---|-------------|------------|------------|------------|------------------------|
| 1 | Longitudinalidade (Pessoa → Conclusão → Participação → Respostas) | I | ✅ Conforme | ✅ Conforme | Grão Conclusão; pseudônimos estáveis de Conclusão e Pessoa permitem seguir formações e Pessoas entre Campanhas sem fundir linhas (R5; data-model §1.1) |
| 2 | Pessoa versus Conclusão Acadêmica (campus/curso no contexto da conclusão) | I, XI | ✅ Conforme | ✅ Conforme | Contexto é o da Conclusão congelado no snapshot; Pessoa só como referência pseudonimizada, nenhum atributo (R1, R5) |
| 3 | Múltiplas formações da mesma Pessoa sem fusão artificial | I, XI | ✅ Conforme | ✅ Conforme | Uma linha por Conclusão; mesmo `pessoa_analitica_id`, `conclusao_analitica_id` distintos (spec US3, US12) |
| 4 | Múltiplas participações sem sobrescrita | I, VIII | ✅ Conforme | ✅ Conforme | Nada é escrito; cada exportação é de um snapshot (uma Campanha); nenhuma concatenação (FR-002) |
| 5 | Definição institucional de egresso respeitada | II | ✅ Conforme | ✅ Conforme | Elegibilidade é a congelada pela 012; nenhum recálculo (FR-004) |
| 6 | Preservação histórica | VIII, XXVII | ✅ Conforme | ✅ Conforme | Valores congelados e textos exatos; Metadados só com valores fixos (R8); dataset reprodutível (R13); nenhuma migration |
| 7 | Versionamento; Pesquisa/Versão/Campanha/Participação distintas | VII, VIII | ✅ Conforme | ✅ Conforme | Chaves locais à Versão; Metadados identificam snapshot, Campanha e Versão separadamente; nome da Pesquisa não usado (R4, R8) |
| 8 | Proveniência proporcional à finalidade e ao risco | IV | ✅ Conforme | ✅ Conforme | Proveniência por coluna no Dicionário; snapshot e captura nos Metadados (data-model §2, §3) |
| 9 | Separação entre dado institucional, derivado e declarado; divergências explícitas | III | ✅ Conforme | ✅ Conforme | Categorias `institucional`/`derivado`/`coleta`/`declarado`; contexto nunca rotulado como Resposta; Q14 continua declarada (ADR 0003) |
| 10 | Desacoplamento de integrações (providers/adaptadores, mock com mesmo contrato) | V, XV, XXV | ✅ Conforme | ✅ Conforme | Nenhum transporte nem conector; contrato de dados neutro; teste proíbe nomes de ferramentas downstream (R17; FR-121, FR-122) |
| 11 | Fronteira do NIAE (5 perguntas do Princípio VI, se aplicável) | VI | ✅ Conforme | ✅ Conforme | spec, "Fronteira do NIAE"; BI fica no GeN |
| 12 | Governança institucional (periodicidade, publicação, competências normativas) | IX, X | ✅ Conforme | ✅ Conforme | Nenhum snapshot oficial (nota fixa; DP-1201); nenhum papel novo (R16) |
| 13 | Escopo por unidade e visão institucional consolidada | XII | ✅ Conforme | ✅ Conforme | Capacidade institucional, não exposta; nada à CSAEG (R16; FR-103) |
| 14 | Privacidade, minimização e dados pessoais em logs/exportações | XVI, XVII | ✅ Conforme | ✅ Conforme | Sem PII; pseudônimos com chave dedicada fora do repositório; datas por dia; "pseudonimizado, não anônimo" declarado; mensagens sem valores; sem disco; dados fictícios (R5, R14; FR-110 a FR-115) |
| 15 | Autorização (menor privilégio; competência técnica ≠ normativa) | X, XII | ✅ Conforme | ✅ Conforme | Nenhuma superfície exposta; CPAEG registrada para quem expuser (contracts/exportacao.md) |
| 16 | Acessibilidade (WCAG 2.1 AA / eMAG, quando houver interface) | XX | N/A | N/A | Sem interface |
| 17 | Responsividade e jornada móvel | XIV, XXI | N/A | N/A | Sem interface; jornada do egresso intocada |
| 18 | Testes proporcionais ao risco cobrindo invariantes afetados | XXV, XXVI | ✅ Conforme | ✅ Conforme | "Estratégia de testes" abaixo; casos A a V; leitura independente dos dois formatos |
| 19 | Risco de over engineering (YAGNI; sem form builder universal) | XXII, XXIII, XXIV | ✅ Conforme | ✅ Conforme | Zero modelos; duas funções de formato; um campo novo na 012; uma dependência de produção justificada (R11); nenhum framework |
| 20 | Exportabilidade e semântica das exportações (se aplicável) | XVIII | ✅ Conforme | ✅ Conforme | CSV obrigatório + XLSX equivalente; Dicionário e Metadados no pacote; contrato versionado (contracts/pacote-de-dados.md) |
| 21 | Decisões pendentes explicitadas; nenhuma hipótese virou regra | XXIX | ✅ Conforme | ✅ Conforme | DP-1301 a DP-1303 e herdadas abaixo; mínimo de 32 caracteres da chave e SC-012 marcados como hipótese |

**Resultado do gate**: **APROVADO** antes da Fase 0 e depois da Fase 1.

**Conflitos identificados**: nenhum.

- A tensão "Qualidade das Exportações × identificadores" (spec, Invariantes) está
  resolvida no desenho. O "identificador permitido da pessoa" é o pseudônimo com chave, e
  nenhum identificador interno sai (R5).
- A vedação de pseudônimo exportável da 012 (012 FR-122) valia para o snapshot. A 012 a
  remeteu a feature futura, e esta é a decisão consciente, tomada na clarificação.
- O acréscimo na 012 é aditivo. `fora_do_percurso`, as invariantes da 012 e o teste
  "dataset sem tabela da 001" ficam intactos (R1, R6).

## Decisões Pendentes

| ID | DECISÃO PENDENTE | Instância competente (se conhecida) | Solução provisória (hipótese) | Como reverter |
|----|------------------|-------------------------------------|-------------------------------|---------------|
| DP-1301 | Quem gera, recebe, guarda e compartilha o dataset; **custódia e rotação da chave de pseudonimização** | CPAEG/Proex, com o encarregado de dados | Nada exposto; chave fictícia só em ambiente não produtivo; CPAEG como hipótese para exposição futura | A feature de exposição aplica a regra decidida; rotação é troca da variável de ambiente |
| DP-1302 | Mecanismo de consumo pelo GeN; se o transporte leva as três tabelas ou só Dados | CPAEG/Proex, com a TI do GeN | Contrato de dados v1 (pacote CSV); nenhum transporte | Um adaptador de transporte consome `exportar_csv` sem mudar o domínio; se só Dados viajar, reavaliar colunas constantes (spec FR-021) |
| DP-1303 | Respostas sensíveis e risco de reidentificação; suficiência da pseudonimização por finalidade | Encarregado de dados, com CPAEG | Todas as Perguntas exportadas; pseudônimos sempre presentes; "não anônimo" declarado; dados fictícios | Filtro ou generalização decididos viram nova versão de contrato |
| 012/DP-1201 | Snapshot de referência para publicação | CPAEG/Proex | Toda exportação recebe o snapshot; nota fixa nos Metadados | — |
| 012/DP-1202 | Retenção de snapshots | Encarregado de dados, com CPAEG | A 013 não persiste arquivos | — |
| 002/DP-006 | Comparabilidade entre Versões | CPAEG | Chaves locais à Versão; nenhuma correspondência | Uma correspondência futura seria tabela própria, não nome de coluna |
| 005/DP-503 | Uso analítico de Participações não concluídas | CPAEG, encarregado de dados | Respostas válidas aparecem, marcadas por `participacao_concluida` | Filtrar no consumo; mudança no contrato exigiria nova versão |
| 005/DP-504, 001/DP-009 | Base legal, consentimento, retenção | Encarregado de dados | Somente dados fictícios | — |
| 005/DP-505 | Acesso a dados identificados | CPAEG/Proex | Nenhum identificador interno; só pseudônimos | — |
| 006/DP-601, 007/DP-703 | Recusa; "iniciada" | CPAEG/Proex | Concluída por recusa = concluída; sem coluna derivada | — |
| 010/DP-1001 | Identificação produtiva | DTI, Proex | Nada exposto | — |
| 011/DP-1101 | Pequenos grupos | CPAEG/Proex | Nenhuma supressão; acesso restrito quando exposto | — |
| 001/DP-003 | Reconciliação de identidade | CPAEG | `pessoa_analitica_id` = registro de Pessoa do sistema | Quem reconciliar decide o efeito sobre pseudônimos |

## Project Structure

### Documentation (this feature)

```text
specs/013-exportacoes-analiticas-gen/
├── spec.md
├── plan.md                 # este arquivo
├── research.md             # Fase 0 (R1–R18)
├── data-model.md           # Fase 1: dataset lógico, acréscimo na 012, configuração
├── quickstart.md           # Fase 1: validação de ponta a ponta
├── contracts/
│   ├── exportacao.md       # dataset_exportado, exportar_csv, exportar_xlsx, erros, configuração
│   └── pacote-de-dados.md  # contrato de dados v1 para consumidores (GeN e outros)
├── checklists/
│   └── requirements.md
└── tasks.md                # Fase 2 (/speckit-tasks — NÃO criado por este comando)
```

### Source Code (repository root)

```text
trajetoria/
├── exportacao/                        # NOVO pacote (não é app Django)
│   ├── __init__.py                    # docstring: escopo, exposição futura (CPAEG), DPs
│   ├── contrato.py                    # VERSAO_CONTRATO, ESQUEMA_PSEUDONIMIZACAO,
│   │                                  # colunas base e descrições, cabeçalhos do
│   │                                  # Dicionário e dos Metadados, notas, gatilhos de escape
│   ├── regras.py                      # Motivo, ExportacaoRecusada,
│   │                                  # ExportacaoInconsistente, ValorNaoRepresentavel
│   ├── pseudonimos.py                 # chave validada; HMAC-SHA-256 com domínio
│   ├── dataset.py                     # Tabela, DatasetExportado, dataset_exportado
│   └── formatos.py                    # exportar_csv, exportar_xlsx,
│                                      # csv_do_dataset, xlsx_do_dataset
└── analitico/
    └── consultas.py                   # ALTERADO: LinhaDoDataset.perguntas_do_percurso
config/
└── settings.py                        # ALTERADO: TRAJETORIA_CHAVE_PSEUDONIMIZACAO
pyproject.toml, uv.lock                # ALTERADOS: XlsxWriter; openpyxl (dev); marcador volume

tests/
├── dependencias.py                    # NOVO: lista única de dependências aprovadas
├── exportacao/                        # NOVO
│   ├── __init__.py
│   ├── conftest.py                    # chave fictícia (autouse); cenário com casos A a V
│   ├── leitura.py                     # leitores independentes: ZIP/CSV + reversão; openpyxl;
│   │                                  # normalização para comparação com o dataset lógico
│   ├── test_exportacao_regras.py      # vocabulário de erro (FR-090 a FR-093)
│   ├── test_exportacao_pseudonimos.py # fundação e US12
│   ├── test_exportacao_formatos.py    # US1, US2, US10
│   ├── test_exportacao_grao.py        # US3, US7
│   ├── test_exportacao_contexto.py    # US4
│   ├── test_exportacao_perguntas.py   # US5 (tipos, complemento, aplicabilidade, inconsistências)
│   ├── test_exportacao_dicionario.py  # US6
│   ├── test_exportacao_metadados.py   # US8
│   ├── test_exportacao_seguranca.py   # US9 (escape, fórmulas, valores não representáveis)
│   ├── test_exportacao_fronteiras.py  # US11; FR-100, FR-122, FR-130
│   ├── test_exportacao_consultas.py   # FR-005, FR-133
│   └── test_exportacao_volume.py      # SC-012, marcado `volume`
├── analitico/
│   ├── conftest.py                    # ALTERADO: cenario delega a cenario_de_referencia
│   ├── construcao.py                  # ALTERADO: + Cenario, cenario_de_referencia(inst)
│   ├── test_analitico_dataset.py      # ALTERADO: testes de perguntas_do_percurso
│   └── test_analitico_fronteiras.py   # ALTERADO: compara com tests/dependencias.py
├── interface/
│   └── test_interface_fronteiras.py   # ALTERADO: compara com tests/dependencias.py
└── editor/
    └── test_editor_fronteiras.py      # ALTERADO: compara com tests/dependencias.py
```

**Structure Decision**: monólito Django existente, com um pacote novo e pequeno.

- `exportacao` depende de `analitico` (consultas e, para a referência à Pessoa, o modelo
  `RegistroDoSnapshot`) e de `instrumento` (`conteudo_da_versao`, `EstadoVersao`,
  `TipoPergunta`).
- Nenhuma app importa `exportacao`.
- `exportacao` **não** importa `academico` (a Pessoa é alcançada pela junção, R5),
  `participacao`, `campanha.consultas`, `acompanhamento`, `interface`, `editor`,
  `demonstracao` nem `governanca`.

## Alterações em features anteriores

| Feature | Alteração | Semântica |
|---------|-----------|-----------|
| 001–011 | Nenhuma | Inalteradas |
| 012 — `consultas.py` | `LinhaDoDataset.perguntas_do_percurso` (último campo, padrão `None`); percurso calculado uma vez por Participação, e `fora_do_percurso` derivado dele para não concluídas | **Aditiva**; `fora_do_percurso`, indicadores, recortes e a regra "sem tabela da 001" inalterados (R6) |
| 012 — `consultas.py` (revisão de código) | `linhas_do_dataset(snapshot, *, conteudo=None)`: conteúdo da Versão opcional, já lido por quem chama; `ValueError` se não for o da Campanha | Aditiva; sem `conteudo`, o comportamento é o de antes |
| 012 — testes | Testes do campo novo e do parâmetro `conteudo`; `cenario` extraído para `construcao.cenario_de_referencia`; `test_nenhum_outro_app_importa_o_analitico` passa a aceitar `exportacao` (a consumidora prevista da fronteira, 012 FR-070), com comentário | Sem mudança de comportamento; as regras da 012 continuam verdadeiras para todos os outros apps |
| 008, 009, 012 — testes de fronteira de dependências | Passam a comparar `pyproject.toml` com a lista única `tests/dependencias.py::DEPENDENCIAS_APROVADAS`, que inclui `XlsxWriter` (revisão de código) | Código de produção inalterado; a regra de cada feature continua verdadeira para ela |
| Demonstração, governança | Nenhuma | Intactas |
| `config/settings.py` | `TRAJETORIA_CHAVE_PSEUDONIMIZACAO = os.environ.get(..., "")` | Técnico; sem valor padrão utilizável |
| `pyproject.toml` | `XlsxWriter` em `dependencies`; `openpyxl` em `dev`; marcador `volume` registrado e excluído por padrão (`-m "not volume"`) | Técnico |

## Estratégia de testes

Cada linha é ao menos um teste automatizado, com dados fictícios construídos pelas
operações das features anteriores. Alterações acadêmicas e o encerramento retroativo são
simulados por `update` direto no teste, como na 012 (R17).

**Grão e universo** (US3, US7; FR-001, FR-002, FR-010 a FR-014; casos A, B, C, D, R, S)

| Teste | Resultado |
|-------|-----------|
| Linhas de Dados × registros do snapshot | Iguais em número; uma por Conclusão |
| Elegível sem Participação | Linha com contexto e pseudônimos; Participação e Perguntas vazias |
| Não elegível com Participação | Linha presente; denominador inalterado; taxa > 100% reproduzível a partir de Dados |
| Pessoa com três Conclusões | Três linhas, mesmo `pessoa_analitica_id`, três `conclusao_analitica_id` |
| Totais de Dados × `indicadores_do_snapshot` × Metadados (contagens derivadas das linhas) | Iguais |
| Dois snapshots da mesma Campanha, exportados um a um | Cada exportação reflete só o seu; mesmo cabeçalho |
| Nenhuma função pública recebe Campanha ou escolhe snapshot | Assinaturas verificadas |

**Contexto** (US4; FR-003, FR-022 a FR-025; casos P, Q)

| Teste | Resultado |
|-------|-----------|
| Alteração direta do contexto de todas as Conclusões depois da captura | Dados idênticos |
| Conclusões novas elegíveis incorporadas depois | Ausentes |
| Atributo não informado | Célula vazia, nunca "Não informado" |
| Cursos homônimos em unidades diferentes | Distinguíveis pela unidade |
| Concluída / não concluída / sem Participação | Estados e datas conforme FR-024; datas na timezone institucional |
| SQL da exportação | Nenhuma coluna de contexto da tabela da 001; a única leitura dela é a junção da referência à Pessoa |

**Perguntas e aplicabilidade** (US5; FR-030 a FR-047; casos E a O, L, M)

| Teste | Resultado |
|-------|-----------|
| Escolha única | Texto exato da Opção |
| Múltipla com uma e com várias Opções | `True`/`False` por Opção; sem delimitador |
| Múltipla com complemento; única com complemento | Coluna `__complemento` com o texto; rótulo intacto |
| Texto com acento, emoji, aspas, vírgula, quebra de linha, espaços nas pontas | Idêntico após leitura nos dois formatos |
| Escala | Inteiro tipado |
| Duas Perguntas de mesmo texto; Opções de rótulos parecidos | Chaves e valores distintos |
| Aplicável não respondida (Pergunta opcional) | `__aplicavel = True`; valor vazio |
| Seção não alcançada; Resposta de rascunho fora do percurso | `__aplicavel = False`; valor vazio |
| Percurso não determinável (Versão com estrutura não suportada, rascunho) | Aplicabilidade e valores vazios; contagem nos Metadados |
| Concluída por Q1 = "Não" | Concluída; Q1 = "Não"; Perguntas da Seção de Q1 aplicáveis, demais `False` |
| Invariantes de data-model §1.3 sobre todo o cenário | Verdadeiras |
| Versão derivada (`instrumento_derivado`) | Nenhuma chave em comum com a origem |

**Dicionário** (US6; FR-050 a FR-058)

| Teste | Resultado |
|-------|-----------|
| Linhas `coluna` × cabeçalho de Dados | Mesma sequência; `ordem` correta |
| Valores possíveis da escolha única | Uma linha por Opção, após a coluna |
| Regra "finaliza" e regra "ir para Seção"; encaminhamento da Seção | Por posição |
| Proveniência de cada coluna | Conforme data-model §2 |
| Descrições das colunas base | Iguais às do contrato |
| Nenhuma coluna de sensibilidade, identificador global ou equivalência | Ausentes |

**Metadados e reprodutibilidade** (US8, US10; FR-060 a FR-067, FR-081 a FR-084)

| Teste | Resultado |
|-------|-----------|
| Chaves, ordem e tipos | Conforme data-model §3 |
| Ausência de nome da Pesquisa, `encerrada_em`, momento de exportação, chave | Ausentes |
| Renomear a Pesquisa; gravar `encerrada_em` retroativo; alterar contexto | `dataset_exportado` igual (`==`) |
| Duas exportações CSV do mesmo snapshot | Bytes idênticos |
| Duas exportações XLSX do mesmo snapshot | Tabelas lidas idênticas |
| Ordem das colunas em Versão com Seções e Perguntas em posições variadas (caso T) | Seção → Pergunta → Opção |

**Formatos e segurança** (US1, US2, US9; FR-070 a FR-079, FR-091)

| Teste | Resultado |
|-------|-----------|
| Pacote ZIP | Exatamente três entradas; UTF-8 sem BOM; CRLF; cabeçalhos técnicos |
| Representação CSV | `true`/`false`, ISO, vazio para ausência |
| Escape | Textos com `=`, `+`, `-`, `@`, tab, CR, `'` escapados nas três tabelas; inteiros negativos não |
| Reversão universal | Round-trip exato sem informação de tipo |
| CSV lido × XLSX lido × dataset lógico | Idênticos |
| XLSX | Três abas na ordem; nenhuma célula de fórmula; texto `=1+1` como texto; booleanos, números e datas nativos |
| Texto com caractere de controle proibido; texto com mais de 32.767 caracteres | `ValorNaoRepresentavel` no XLSX; CSV exporta normalmente |
| Texto com o padrão literal `_x0041_` | Round-trip intacto ou `ValorNaoRepresentavel` (R12) |
| Propriedade de criação do XLSX | Igual a `capturado_em` |

**Pseudônimos** (US12; FR-026 a FR-029; casos U, V)

| Teste | Resultado |
|-------|-----------|
| Mesma Conclusão em snapshots de duas Campanhas, mesma chave | Mesmos pseudônimos |
| Outra chave | Nenhum pseudônimo coincide |
| Chave ausente, curta ou igual a `SECRET_KEY` | `ExportacaoRecusada`, sem arquivo e antes de ler linhas |
| Mesmo UUID nos domínios Pessoa e Conclusão | Pseudônimos diferentes |
| Valor conhecido (vetor fixo de teste) | Igual ao HMAC-SHA-256 calculado à parte |
| Nenhum UUID interno (com ou sem hífens) em nenhum arquivo | Ausente |

**Erros e fronteiras** (US11; FR-090 a FR-093, FR-100 a FR-134; SC-006, SC-011)

| Teste | Resultado |
|-------|-----------|
| Argumento não snapshot; snapshot não gravado | `TypeError`; `ExportacaoRecusada` |
| Resposta malformada, Opção alheia, complemento sem Opção que o admita, concluída com Resposta fora do percurso, Versão devolvida a rascunho, tipo de Pergunta desconhecido (forçados no teste) | `ExportacaoInconsistente`, sem valor na mensagem |
| Cabeçalho de Dados | Exatamente 14 colunas base + colunas de Pergunta (sem coluna constante; FR-021) |
| Nada em disco (`tempfile.tempdir` num `tmp_path`; funções de `tempfile` proibidas) | Diretório vazio depois das duas exportações; nenhum log com valor (FR-114) |
| Consultas | Número igual com 3 e com 30 registros |
| Pacote sem modelos, sem `apps.py`, fora de `INSTALLED_APPS` | Verdadeiro |
| Nenhuma URL, view, template ou comando | Ausentes |
| Imports | Só `analitico`, `instrumento`, `django`, biblioteca padrão, `xlsxwriter` |
| Identificadores do pacote (AST) | Nenhum contém `looker`, `google`, `bigquery`, `datastudio`, `dashboard` |
| Nenhuma PII ou `id_externo` nos arquivos | Ausentes |
| `makemigrations --check` | Sem mudanças |

**012** (acréscimo)

| Teste | Resultado |
|-------|-----------|
| `perguntas_do_percurso` de concluída, rascunho, recusa, sem Participação, estrutura não suportada | Conforme data-model §0 |
| `fora_do_percurso` | Inalterado em todos os testes existentes |
| Dataset da 012 continua sem tocar a tabela da 001 | Verdadeiro |

## Sinais de over engineering (parar se aparecerem)

- modelo, migration ou tabela: exportação, arquivo, job, histórico, esquema, coluna,
  dicionário, pseudônimo, mapa de identidade;
- classe base de exportador, registro de serializadores, plugin, adaptador, parâmetro de
  formato genérico;
- formato long paralelo, tabela de Respostas, dimensão de Opções, star schema, ETL;
- Celery, fila, job, worker, cache, estado "processando", streaming obrigatório;
- view, rota, API, management command, download, regra de governança "pode exportar";
- integração ou nome de Looker, Google, BigQuery, Sheets, conector, credencial de serviço;
- identificador global de Pergunta, código de Opção, linhagem, correspondência entre
  Versões;
- coluna de recusa, completude ou abandono; classificação de sensibilidade; supressão;
- gravar arquivo em disco, em diretório temporário ou em log;
- variante "raw" do CSV;
- mudança em feature anterior além do campo `perguntas_do_percurso` e do teste de
  dependências da 012.

## Volta à spec?

**Não é necessária.** O research confirmou as premissas da spec clarificada:

- a fronteira da 012 basta, com o acréscimo previsto em FR-134;
- a referência à Pessoa é lida na própria 013, sem tocar a 012. FR-134 a admitia como
  acréscimo à 012, e a forma escolhida é menor;
- os Metadados verificados como fixos dispensam persistência (FR-063);
- o escape e a reversão universal cumprem FR-075 e FR-076 sem variantes.

## Complexity Tracking

Vazio. Nenhuma violação da Constituição a justificar. A única dependência nova de produção
(`XlsxWriter`) substitui a escrita manual de um formato de arquivo e é a forma mais simples
de garantir "texto nunca vira fórmula" (R11).
