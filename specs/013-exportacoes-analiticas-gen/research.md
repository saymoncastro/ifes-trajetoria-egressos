# Research: Exportações analíticas e contrato de dados para o GeN (Feature 013)

Fase 0 do plan. O Technical Context tinha um único ponto aberto: **com que se escreve
XLSX** (R11). Os demais itens decorrem do código existente e da spec clarificada. Cada
item registra **Decisão**, **Justificativa** e **Alternativas consideradas**.

---

## R1 — Fonte dos dados: a fronteira da 012, mais dois acréscimos pontuais

**Decisão**: a exportação lê somente:

| O quê | De onde | Observação |
|-------|---------|------------|
| Registros, contexto congelado, elegibilidade, Participação, Respostas, classificação de percurso | `linhas_do_dataset(snapshot, conteudo=conteudo)` (012) | Mais o campo novo `perguntas_do_percurso` (R6) e o parâmetro opcional `conteudo`, para não reler a Versão (revisão de código) |
| Contagens dos Metadados | As próprias linhas montadas | Mesmas definições da 012; os testes as comparam com `indicadores_do_snapshot` (revisão de código: sem consulta extra) |
| Estrutura, textos e regras do instrumento; identificação da Versão | `conteudo_da_versao(snapshot.campanha.versao)` (002) | Árvore imutável, já ordenada por posição |
| Identificação, nome, período e abertura da Campanha | `snapshot.campanha` (004) | Só campos fixados na abertura (R8) |
| Referência Conclusão → Pessoa | Uma consulta própria da 013 sobre os registros do snapshot (R5) | Só a coluna de chave estrangeira; nenhum atributo da Pessoa |

**Justificativa**:

- A 012 já entrega tudo o que é histórico, sem ler a Conclusão atual (012 FR-076). A 013 só
  representa (spec FR-003, FR-004).
- Os dois acréscimos são os previstos pela spec (FR-134, FR-028). Eles ficam em lugares diferentes
  de propósito:
  - o **percurso** fica na 012, porque a composição das regras da 006 já mora lá
    (`_fora_do_percurso`), e duplicá-la seria implementação paralela (spec FR-004);
  - a **referência à Pessoa** fica na 013, porque a 012 garante, por documentação e por
    teste, que sua leitura do dataset nunca toca a tabela da 001. Essa garantia continua
    literal, e a única leitura da 001 fica onde a spec a admite (FR-003, FR-028).

**Alternativas consideradas**:

- Acrescentar `pessoa_id` a `LinhaDoDataset`: obrigaria reescrever a invariante e o teste
  "dataset sem tabela da 001" da 012. Rejeitada.
- Recalcular o percurso na 013 com as funções puras da 006: repetiria a composição
  `secoes_nao_suportadas` + `percorrer` + tratamento de `ParticipacaoRejeitada` que a 012
  já faz. Rejeitada.
- Ler `Participacao`/`Resposta` diretamente na 013: contornaria a fronteira e a
  classificação de percurso. Rejeitada.

---

## R2 — Onde fica o código: pacote `trajetoria/exportacao`, sem app Django

**Decisão**: pacote Python `trajetoria/exportacao/`, **não registrado** em
`INSTALLED_APPS`. Módulos:

| Módulo | Responsabilidade |
|--------|------------------|
| `__init__.py` | Docstring com escopo e decisões pendentes; nenhum código |
| `contrato.py` | Constantes do contrato: versões, colunas base, cabeçalhos de Dicionário e Metadados, notas fixas, caracteres de gatilho do escape |
| `regras.py` | `Motivo`, `ExportacaoRecusada`, `ExportacaoInconsistente`, `ValorNaoRepresentavel` |
| `pseudonimos.py` | Leitura e validação da chave; cálculo do pseudônimo |
| `dataset.py` | `dataset_exportado(snapshot)`: o dataset lógico, com valores tipados |
| `formatos.py` | `exportar_csv(snapshot)` e `exportar_xlsx(snapshot)`; `csv_do_dataset(dataset)` e `xlsx_do_dataset(dataset)` para serializar um dataset já montado nos dois formatos sem refazê-lo (revisão de código) |

**Justificativa**:

- Não há modelo, migration, template, signal nem view (spec FR-130, FR-100). Um app Django
  só existiria para ser registrado. O ORM das outras apps funciona normalmente a partir de
  um pacote comum.
- Separar o dataset lógico (`dataset.py`) dos formatos (`formatos.py`) é o que garante uma
  única semântica para CSV e XLSX (spec FR-070). Os formatos só serializam, sem decidir
  valor.
- São duas funções explícitas de formato, sem classe base, registro de serializadores nem
  parâmetro de formato (spec FR-132). Por isso o erro "formato não suportado" de FR-090 não
  tem onde ocorrer.

**Alternativas consideradas**:

- App Django `exportacao` com `apps.py`: registro sem uso. Rejeitada.
- Colocar a exportação dentro de `analitico`: misturaria a fotografia (012) com sua
  representação (013), e a 012 declarou explicitamente que formato não é dela (012
  FR-070). Rejeitada.
- Módulo `csv.py` no pacote: o nome sombrearia o módulo `csv` da biblioteca padrão para
  leitores. Rejeitada; usa-se `formatos.py`.

---

## R3 — Dataset lógico: três tabelas de valores Python tipados

**Decisão**: `dataset_exportado(snapshot)` devolve um objeto de valor imutável
`DatasetExportado(dados, dicionario, metadados)`. Cada tabela é
`Tabela(cabecalho: tuple[str, ...], linhas: tuple[tuple, ...])`. Os valores são Python
tipados, e **o tipo Python decide a representação** em cada formato:

| Valor lógico | Tipo Python | CSV | XLSX |
|--------------|-------------|-----|------|
| ausência | `None` | campo vazio | célula não escrita |
| booleano | `bool` | `true` / `false` | booleano nativo |
| inteiro | `int` (não `bool`) | decimal | número |
| data | `datetime.date` | `AAAA-MM-DD` | data com formato `yyyy-mm-dd` |
| momento | `datetime.datetime` com fuso | ISO 8601 com deslocamento | texto ISO 8601 |
| texto | `str` | texto com escape (R10) | texto, nunca fórmula |

**Justificativa**:

- O tipo vai junto com o valor, e não existe tabela paralela de tipos para manter em
  sincronia. O Dicionário documenta o tipo de cada coluna de Dados (`tipo_valor`) para o
  consumidor, e o Metadados documenta o tipo de cada valor (coluna `tipo`).
- `bool` é subclasse de `int` em Python, então o teste de tipo nos formatos verifica `bool`
  antes de `int`. Isso é coberto por teste.
- Momentos ficam na timezone institucional (`timezone.localtime`), o que dá deslocamento
  explícito e o mesmo texto em qualquer execução.

**Alternativas consideradas**:

- Dataset como lista de dicionários: repetiria nomes de coluna por linha, sem ganho.
  Rejeitada.
- Tipos declarados por coluna, com conversão no formato: dois lugares para decidir o mesmo
  fato. Rejeitada.
- pandas/DataFrame: dependência pesada para três tabelas. Rejeitada.

---

## R4 — Chaves técnicas e ordem das colunas

**Decisão**:

- Nomes: `pergunta_<id.hex>`, `pergunta_<id.hex>__aplicavel`,
  `pergunta_<id.hex>__opcao_<id.hex>` e `pergunta_<id.hex>__complemento`, com `UUID.hex`
  (32 dígitos hexadecimais minúsculos).
- Ordem: as 14 colunas base, depois `ConteudoVersao.secoes` → `perguntas` → `opcoes`, que
  já vêm ordenadas por posição pela 002. Dentro da Pergunta: aplicabilidade, valor (ou
  Opções), complemento.
- Ao final, uma verificação de unicidade dos nomes.

**Justificativa**:

- `UUID.hex` atende FR-033 (só `[a-z0-9_]`, começa por letra pelo prefixo) e não depende
  de texto.
- O identificador é local à Versão (C1), então nenhuma chave se repete entre Versões
  (002/DP-006).
- O nome mais longo tem 81 caracteres, abaixo de qualquer limite usual de nome de coluna.

**Alternativas consideradas**: posição (`s02_p05`) sugeriria comparabilidade entre Versões
de mesma posição; slug do texto não é estável nem único (C2); UUID com hífens não é
identificador válido em várias ferramentas. Todas rejeitadas.

---

## R5 — Pseudonimização analítica

**Decisão**:

- **Configuração**: `config/settings.py` ganha
  `TRAJETORIA_CHAVE_PSEUDONIMIZACAO = os.environ.get("TRAJETORIA_CHAVE_PSEUDONIMIZACAO", "")`.
  Não há valor padrão utilizável, e o valor nunca é gravado em banco, arquivo exportado ou
  log.
- **Validação**, a cada exportação e antes de qualquer leitura de linhas:
  - vazia → `ExportacaoRecusada(Motivo.CHAVE_AUSENTE)`;
  - menos de 32 caracteres, ou igual a `SECRET_KEY` → `ExportacaoRecusada(Motivo.CHAVE_INADEQUADA)`.
- **Cálculo**: `hmac.new(chave.encode("utf-8"), f"{dominio}:{uuid}".encode("utf-8"), hashlib.sha256).hexdigest()`,
  - com `dominio` ∈ {`conclusao`, `pessoa`};
  - com `uuid` na forma canônica `str(UUID)` (minúscula, com hífens);
  - resultado: 64 dígitos hexadecimais minúsculos.
- **Esquema**: constante `ESQUEMA_PSEUDONIMIZACAO = "hmac-sha256-v1"`, publicada nos
  Metadados. O significado da constante (algoritmo, mensagem `dominio:uuid-canônico`,
  saída hexadecimal) está em [contracts/pacote-de-dados.md](contracts/pacote-de-dados.md).
- **Pessoa**: uma consulta por exportação,
  `RegistroDoSnapshot.objects.filter(snapshot=snapshot).values_list("conclusao_id", "conclusao__pessoa_id")`.
  - Lê só a coluna de chave estrangeira da Conclusão.
  - Usa junção, e não uma lista `IN`, para não esbarrar no limite de parâmetros do
    PostgreSQL com dezenas de milhares de registros.
- **Sem persistência**: nenhum modelo, migration, tabela de correspondência, cache de
  pseudônimos ou serviço de identidade. O cálculo é refeito a cada exportação (spec FR-027).

**Justificativa**:

- HMAC-SHA-256 é padronizado (RFC 2104, FIPS 198-1), está na biblioteca padrão
  (`hmac`, `hashlib`) e é não reversível sem a chave. É determinístico sob a mesma chave,
  e por isso estável, e trocar a chave rompe a ligação, como a clarificação exige.
- A separação de domínio garante que `conclusao:X` e `pessoa:X` nunca coincidam, mesmo para
  o mesmo UUID.
- **Chave dedicada, distinta de `SECRET_KEY`** (clarificação):
  - rotacionar o segredo da aplicação (sessões, CSRF) não pode romper a análise
    longitudinal;
  - vazar esse segredo não pode permitir derivar pseudônimos.
- O mínimo de 32 caracteres é salvaguarda barata contra chave trivial, compatível com o
  tamanho de bloco do SHA-256. É hipótese técnica, reversível.
- O UUID interno não serve como identificador exportado:
  - o da Conclusão aparece na interface do egresso (spec C14);
  - não é revogável.

**Alternativas consideradas**:

- UUID interno direto (rejeitado na clarificação).
- `SECRET_KEY` como chave (rejeitado na clarificação).
- SHA-256 sem chave: o UUID é conhecido em algumas superfícies, então qualquer pessoa
  recalcularia o pseudônimo. Rejeitada.
- Tabela de correspondência aleatória: persistência e serviço de identidade. Rejeitada.
- Truncar o HMAC para 32 dígitos: menor, mas criaria uma decisão de colisão sem ganho
  concreto. Rejeitada.

---

## R6 — Aplicabilidade: `perguntas_do_percurso` na fronteira da 012

**Decisão**: `LinhaDoDataset` (012) ganha o último campo, com padrão `None`:
`perguntas_do_percurso: frozenset | None`.

- **Valores do campo**:
  - Participação com percurso determinável: as Perguntas das Seções do percurso
    calculado pelas regras puras da 006 (`perguntas_do_percurso(percorrer(conteudo,
    respondidas(respostas)))`). Isso vale para **toda** Participação, concluída ou não.
  - `None` quando não há Participação ou o percurso não é determinável (Versão com
    estrutura não suportada, ou Respostas que a 006 rejeita).
- **Mudança na 012**: o cálculo interno passa a produzir o percurso uma vez e derivar dele
  `fora_do_percurso` (Respostas − percurso) para não concluídas. Para concluídas,
  `fora_do_percurso` continua `∅`, como hoje. **Nenhum comportamento existente muda.**
- **Na 013**, por linha:

  | Situação | Aplicabilidade | Valores |
  |----------|----------------|---------|
  | Sem Participação | todas `None` | todos `None` |
  | Não concluída, percurso `None` | todas `None` | todos `None`; soma 1 em `participacoes_com_percurso_nao_determinavel` |
  | **Concluída**, percurso `None` | — | `ExportacaoInconsistente`: a 006 só conclui com percurso determinável |
  | Concluída com Resposta fora do percurso | — | `ExportacaoInconsistente`: a 006 remove as inativas ao concluir |
  | Demais | `pergunta.id in percurso` | valores só das Perguntas do percurso com Resposta |

**Justificativa**:

- A spec exige a coluna (FR-047), sem implementação paralela (FR-004).
- A composição já existe na 012 e as funções da 006 são puras, sem consulta nova.
- As duas inconsistências preservam a invariante "valor preenchido ⇒ aplicável verdadeiro"
  sem esconder dado escrito fora das operações.

**Alternativas consideradas**:

- Expor só `fora_do_percurso` e inferir a aplicabilidade: impossível para Perguntas não
  respondidas de Seções não alcançadas. Rejeitada.
- Função nova separada na 012 (`percurso_da_participacao`): obrigaria recarregar conteúdo
  e Respostas por Participação. Rejeitada.

---

## R7 — Respostas → células, com validação de forma

**Decisão**: para cada Pergunta do percurso com Resposta:

| Tipo | Forma exigida da Resposta | Células |
|------|---------------------------|---------|
| Escolha única | `opcao` presente e da Pergunta; sem `texto`, `escala` nem `opcoes` | `pergunta_<id>` = `opcao.texto` |
| Escolha múltipla | `opcoes` não vazio, todas da Pergunta; sem `opcao`, `texto` nem `escala` | Cada Opção: `True` se escolhida, `False` se não |
| Texto curto | `texto` presente; demais ausentes | `pergunta_<id>` = `texto` |
| Escala | `escala` presente; demais ausentes | `pergunta_<id>` = `escala` (`int`) |
| Complemento (escolha) | Só se a Pergunta tem Opção que o admite e essa Opção está escolhida | `pergunta_<id>__complemento` |

- Qualquer forma diferente gera `ExportacaoInconsistente`, citando o snapshot, a Pergunta e
  o motivo, nunca o valor.
- Os limites da escala **não** são revalidados (spec FR-006): isso é regra de escrita da
  005, não de representação.

**Justificativa**: a validação é de representação (spec FR-092). Uma forma incompatível só
existe por escrita fora das operações (ADR 0002) e não deve virar célula silenciosamente
errada.

**Alternativas consideradas**: ignorar a Resposta malformada, ou exportar o que der.
Rejeitadas, porque esconderiam inconsistência.

---

## R8 — Metadados: só valores fixos para o snapshot

**Decisão**: uma tabela `chave`, `valor`, `tipo`, com as chaves na ordem fixa de
[data-model.md §3](data-model.md#3-metadados).

- **Fontes**: snapshot (identificador, `capturado_em`); Campanha (identificador, nome,
  `inicio`, `fim`, `aberta_em`); Versão (identificador, designação, título, `publicada_em`);
  contagens derivadas das linhas montadas (iguais às de `indicadores_do_snapshot`,
  verificado em teste) mais a contagem de percurso não determinável da própria construção; número de colunas de Dados; constantes e notas do contrato.
- **Omitidos**:
  - o **nome da Pesquisa**, mutável (spec C10);
  - o **momento de encerramento explícito** (`encerrada_em`). Uma Campanha encerrada pelo
    fim do período pode recebê-lo depois da captura, se `encerrar` for chamada com `agora`
    anterior ao fim (spec C13).
- **Sem** `gerado_em`.

**Justificativa** (verificado no código):

- `alterar_campanha` e `definir_periodo` exigem Campanha nunca aberta, e `abrir` grava
  `aberta_em` uma única vez.
- `alterar_versao` exige rascunho, e a Versão de Campanha aberta é PUBLICADA.
- Todo snapshot é de Campanha aberta (012 FR-010).

**Alternativas consideradas**:

- Congelar `encerrada_em` no snapshot: exigiria campo e migration na 012, o que a
  clarificação vedou ("não criar infraestrutura nova apenas para guardar rótulos").
  Rejeitada.
- Ler `encerramento(campanha)` da 004 no momento da exportação: o valor pode mudar.
  Rejeitada.

---

## R9 — Dicionário: uma linha por coluna, mais os valores possíveis da escolha única

**Decisão**: cabeçalho fixo de 24 colunas ([data-model.md §2](data-model.md#2-dicionário)).

- **Linhas**:
  - `elemento = "coluna"` para cada coluna de Dados, na mesma ordem e com `ordem` igual à
    posição 1-based em Dados;
  - para cada Pergunta de escolha única, após a linha da coluna de valor, uma linha
    `elemento = "valor_possivel"` por Opção.
- **Conteúdo**:
  - descrições das colunas base fixas no contrato;
  - descrições das colunas de Pergunta geradas por modelos de frase fixos;
  - textos do instrumento sem alteração;
  - regras de navegação (`opcao_regra_finaliza`, `opcao_regra_destino_secao`) e
    encaminhamento da Seção (`secao_encaminhamento_destino`) pela **posição** da Seção de
    destino, resolvida no próprio `ConteudoVersao`.

**Justificativa**: o Dicionário é gerado da Versão imutável (FR-050), mantém a
correspondência um-para-um com Dados (FR-051) e publica as condicionais (FR-055) em
colunas tipadas, sem texto livre a interpretar.

**Alternativas consideradas**: lista de Opções numa célula com delimitador (o mesmo
problema que FR-037 evita); tabela separada de Opções (vedada pela spec). Rejeitadas.

---

## R10 — CSV: biblioteca padrão, escape universal, ZIP determinístico

**Decisão**:

- **Escrita**: `csv.writer` com `delimiter=","`, `quotechar='"'`, `doublequote=True`,
  `quoting=csv.QUOTE_MINIMAL` e `lineterminator="\r\n"`, sobre
  `io.TextIOWrapper(..., encoding="utf-8", newline="")`. Isso dá RFC 4180, UTF-8 sem BOM e
  independência de locale.
- **Escape**: em todo valor `str` das três tabelas, se o primeiro caractere ∈
  {`=`, `+`, `-`, `@`, `\t`, `\r`, `'`}, prefixar `'`.
  - Valores não textuais são formatados sem escape: `true`/`false`, dígitos, ISO 8601.
    Nenhum deles começa por `'`.
  - Os cabeçalhos são nomes técnicos.
- **Reversão universal** (publicada nas notas): em qualquer campo, se começar por `'`,
  remover um. Testada como round-trip sobre os três arquivos, sem informação de tipo.
- **Pacote**: `zipfile` em `BytesIO`, com `ZIP_DEFLATED`, três entradas na ordem
  `dados.csv`, `dicionario.csv`, `metadados.csv`, cada uma com
  `ZipInfo(date_time=(1980, 1, 1, 0, 0, 0))` e permissões fixas.
  - O mesmo snapshot produz **bytes idênticos**, embora a spec só exija igualdade
    semântica (FR-084).
  - Nenhum arquivo é gravado em disco (FR-114).

**Justificativa**:

- Biblioteca padrão, sem dependência.
- A reversão universal funciona porque todo texto iniciado por `'` também é escapado, e
  nenhum valor não textual começa por `'`. Assim o consumidor (GeN ou outro) não precisa
  do Dicionário para reverter, o que atende a clarificação.
- O ZIP determinístico elimina diferença espúria entre exportações.

**Alternativas consideradas**:

- CSV sem escape: rejeitado na clarificação.
- Escape só de texto declarado: rótulos de Opção (por exemplo, "+ de 5 salários") e
  contexto também chegam a planilhas. Rejeitada.
- Aspas como proteção: não impedem a avaliação como fórmula. Rejeitada.
- BOM para facilitar o Excel: quebra o primeiro cabeçalho em leitores automatizados, e o
  XLSX já é o formato humano. Rejeitada.

---

## R11 — XLSX: XlsxWriter para escrever; openpyxl só nos testes

**Decisão**:

- **Dependência de produção nova**: `XlsxWriter>=3.2,<4`. Ela é usada só em `formatos.py`.
- **Abertura do workbook**: `Workbook(BytesIO(), {"in_memory": True,
  "strings_to_formulas": False, "strings_to_numbers": False, "strings_to_urls": False})`.
- **Escrita**: chamadas tipadas e explícitas:
  - `write_string` para texto e para momentos (ISO);
  - `write_boolean`;
  - `write_number`;
  - `write_datetime` com formato `yyyy-mm-dd` para datas;
  - nenhuma escrita para `None`.
- **Abas**: `Dados`, `Dicionário`, `Metadados`. O cabeçalho usa um único formato negrito,
  sem nenhuma outra formatação.
- **Propriedades do arquivo**: `created` = `capturado_em` (UTC), para que o arquivo não
  carregue o momento da exportação.
- **Dependência de desenvolvimento nova**: `openpyxl>=3.1,<4`, só para os testes lerem o
  XLSX de volta.

**Justificativa**:

- `write_string` nunca produz fórmula, por construção, e as opções `strings_to_*` desligam
  toda conversão implícita. É a garantia de FR-078 sem truque de tipo de célula.
- Escrever com uma biblioteca e ler com outra torna a verificação independente: um erro
  simétrico do escritor não se esconde.
- `in_memory` evita arquivos temporários em disco (FR-114). O modo `constant_memory`
  gravaria temporários. Pelo volume estimado (R15), a memória é aceitável: células vazias
  não são escritas, e a maioria das linhas, sem Participação, tem só as 14 colunas base.

**Alternativas consideradas**:

- openpyxl para escrever: atribuir texto iniciado por `=` cria fórmula, a menos que se
  force o tipo da célula depois. É armadilha que precisaria de vigilância permanente.
  Rejeitada.
- Escrever OOXML à mão com `zipfile`: sem dependência, mas é um formato de arquivo inteiro
  para manter (estilos, datas, compatibilidade). Rejeitada.
- pandas: dependência pesada. Rejeitada.

**Consequência** (revisada no code review): **três** testes de fronteira comparavam
literalmente a lista de dependências de produção:

- `tests/interface/test_interface_fronteiras.py::test_sem_dependencia_nova_nem_script`
  (008);
- `tests/editor/test_editor_fronteiras.py::test_sem_script_recurso_externo_nem_dependencia_nova`
  (009);
- `tests/analitico/test_analitico_fronteiras.py::test_sem_dependencia_nova` (012).

Os três passam a comparar com uma lista única, `tests/dependencias.py::DEPENDENCIAS_APROVADAS`,
onde `XlsxWriter` entra uma vez, com a feature e a justificativa. Assim uma dependência
futura não exige editar três testes de features diferentes. A regra de cada feature (não acrescentar dependência) continua verdadeira para
ela. É o mesmo padrão já usado com o teste de escopo da 007.

---

## R12 — Valores não representáveis no XLSX

**Decisão**: antes de cada `write_string`, verificar o texto:

- tem mais de 32.767 caracteres (limite de célula);
- ou contém caractere fora do conjunto permitido do XML 1.0 (controles U+0000 a U+0008,
  U+000B, U+000C, U+000E a U+001F; U+FFFE, U+FFFF).

Nesses casos, `ValorNaoRepresentavel(formato="xlsx", tabela, coluna, linha)` é levantado,
sem o valor, e nada é devolvido.

Um texto que contenha literalmente o padrão `_xHHHH_`, que leitores OOXML podem decodificar
como caractere, é verificado por teste de round-trip (XlsxWriter → openpyxl):

- se não sobreviver intacto, entra na mesma verificação e no mesmo erro;
- o CSV não tem nenhum desses limites.

**Justificativa**: FR-091 proíbe truncar ou substituir silenciosamente. O XlsxWriter
trunca texto longo (retorno `-2`) e codifica controles, então a verificação precisa
acontecer antes.

**Alternativas consideradas**: remover os caracteres de controle; truncar com aviso.
Rejeitadas: ambas alteram valor.

**Decisão tomada na implementação** (padrão `_xHHHH_`; tasks T030). Round-trip
verificado com XlsxWriter 3.2.9 → openpyxl 3.1.5:

| Texto | Resultado |
|-------|-----------|
| `_x0041_`, `a_x0041_b` | intacto |
| `_x005F_x0041_` | **alterado** (volta como `_x0041_`) |
| `\x01abc` | **alterado** (volta como `_x0001_abc`) |
| 32.768 caracteres | **truncado** (`write_string` devolve `-2`) |

Como a preservação do padrão depende de detalhes internos da biblioteca, a regra adotada é
conservadora: **todo texto que contenha `_x` seguido de 4 dígitos hexadecimais e `_`**
gera `ValorNaoRepresentavel` no XLSX, assim como os caracteres de controle e o excesso de
comprimento. O valor nunca é alterado. O CSV exporta esses textos normalmente, e o padrão
é raríssimo em respostas reais.

Retorno de carro (`\r`), quebra de linha e tabulação **são** representáveis: o XlsxWriter
grava o `\r` como o escape OOXML `_x000D_`, que leitores conformes (Excel, LibreOffice)
decodificam. O leitor de teste aplica a mesma decodificação OOXML ao openpyxl, que não a
faz para todos os caracteres. Isso não é ambíguo justamente porque texto com o padrão
literal `_xHHHH_` é recusado.

---

## R13 — Ordem das linhas e reprodutibilidade

**Decisão**:

- **Ordem das linhas**: a de `linhas_do_dataset`, isto é, `conclusao_id` interno, que não
  é exportado. Os pseudônimos não ordenam, porque a ordem mudaria com a chave.
- **Ordem das colunas**: R4.
- **Reprodutibilidade**: o mesmo snapshot e a mesma chave produzem o mesmo
  `DatasetExportado` (`==`).
  - O CSV produz bytes idênticos (R10).
  - O XLSX produz conteúdo idêntico. Bytes idênticos não são exigidos (spec FR-084).

**Justificativa**: a ordem é estável sem expor identidade (FR-082), e a igualdade do dataset
lógico é o critério testável.

---

## R14 — Erros e mensagens

**Decisão** (`regras.py`):

| Exceção | Quando | Mensagem cita |
|---------|--------|---------------|
| `TypeError` | Argumento que não é `SnapshotAnalitico` | tipo recebido |
| `ExportacaoRecusada(Motivo.SNAPSHOT_NAO_GRAVADO)` | Snapshot sem `pk` ou inexistente no banco | identificador, se houver |
| `ExportacaoRecusada(Motivo.CHAVE_AUSENTE)` | Chave vazia | só o motivo |
| `ExportacaoRecusada(Motivo.CHAVE_INADEQUADA)` | Chave curta ou igual a `SECRET_KEY` | só o motivo |
| `ExportacaoInconsistente` | Versão não publicada; tipo desconhecido; forma de Resposta incompatível; Opção alheia; concluída sem percurso ou com Resposta fora dele; nome de coluna repetido | snapshot, Pergunta/Opção, motivo |
| `ValorNaoRepresentavel` (subclasse de `ExportacaoInconsistente`) | R12 | formato, tabela, coluna, número da linha |

- As exceções levantam antes de qualquer retorno, então não existe arquivo parcial.
- Não há estado nem máquina de estados.
- Nenhuma mensagem contém valor acadêmico, Resposta, identificador interno de Pessoa ou
  Conclusão, pseudônimo ou chave (spec FR-093).

**Alternativas consideradas**: código de erro numérico; exceção única com texto livre.
Rejeitadas, pelo mesmo padrão de `regras.py` da 012.

---

## R15 — Volume e consultas

**Decisão**:

- **Consultas** em número fixo por exportação, independente do número de registros:
  - Campanha;
  - conteúdo da Versão (as consultas de `conteudo_da_versao`);
  - leitura do dataset (as de `linhas_do_dataset`);
  - indicadores (1);
  - referência à Pessoa (1).
- **Memória**: o dataset lógico é materializado uma vez em tuplas, e os dois formatos o
  percorrem.
- **Estimativa**, sem garantia: cerca de 20 mil registros e cerca de 150 colunas de
  Pergunta, com uns 20% de linhas com Participação. Isso dá cerca de 0,9 milhão de células
  não vazias, ordem de centenas de MB no pior caso do XLSX em memória.
- **SC-012** (menos de 1 minuto para 20 mil registros) é verificado por um teste de volume
  marcado (`-m volume`), fora da suíte padrão, e no quickstart.

**Justificativa**: proporcionalidade (spec FR-133), sem streaming obrigatório. Ler em
blocos, ou usar `constant_memory` com diretório temporário controlado, é mudança local se a
medição real exigir.

---

## R16 — Exposição e governança

**Decisão**:

- Nenhuma view, rota, URL, template, API ou management command, e nenhuma regra nova em
  `trajetoria/governanca`.
- As funções são exercitadas por testes.
- A docstring de `trajetoria/exportacao/__init__.py` registra que:
  - quem expuser deve restringir à CPAEG ativa (spec FR-102);
  - nada é dado à CSAEG (FR-103);
  - custódia e rotação da chave são DP-1301.

**Justificativa**: spec FR-100 e FR-101, e o mesmo regime da 012 (012 R14).

---

## R17 — Testes

**Decisão**: diretório `tests/exportacao/`.

- **Cenário**: o corpo da fixture `cenario` da 012 é extraído, sem mudar comportamento,
  para `tests/analitico/construcao.py::cenario_de_referencia(inst)`.
  - As duas `conftest.py` (012 e 013) chamam essa função. Nenhuma importa de outro
    `conftest.py`, prática que o pytest desaconselha.
  - O instrumento de `tests/participacao/construcao.py` já tem os quatro tipos,
    complemento em escolha única e múltipla, regra "finaliza" e segunda Seção.
- **Nada em disco**: `tempfile.tempdir` é apontado para um `tmp_path` vazio, e as funções
  de `tempfile` falham se chamadas; o diretório deve continuar vazio depois das duas
  exportações (spec FR-114).
- **Volume**: uma Participação-molde é preenchida pelas operações; as demais são copiadas
  por `bulk_create` só no teste de volume, para medir a exportação, e não a preparação.
- **Chave**: uma fixture `autouse` define uma chave fictícia de 48 caracteres pela fixture
  `settings` do pytest-django.
- **Leitores**:
  - CSV com `zipfile` + `csv` + reversão;
  - XLSX com `openpyxl.load_workbook`.
  - Uma função de teste normaliza as células lidas para o dataset lógico (datas do
    openpyxl → `date`; momentos ISO → `datetime`) e compara.
- **Fronteiras**:
  - imports permitidos (`analitico`, `instrumento`, `django`, biblioteca padrão,
    `xlsxwriter`);
  - nenhum nome contendo `looker`, `google`, `bigquery`, `datastudio` ou `dashboard` em
    identificadores do pacote, verificado por AST, sem procurar em comentários;
  - nenhum modelo, URL ou comando.
- **Alteração simulada**: a mesma técnica da 012 (`update` direto no teste) para o caso Q e
  para `encerrada_em` retroativo (C13).

**Alternativas consideradas**: fixtures JSON; dados de demonstração. Rejeitadas: a
demonstração não muda (spec FR-141).

---

## R18 — Alterações em features anteriores

**Decisão**:

| Onde | Alteração | Semântica |
|------|-----------|-----------|
| `trajetoria/analitico/consultas.py` (012) | Campo `perguntas_do_percurso` em `LinhaDoDataset`; cálculo interno do percurso uma vez por Participação | Aditiva; `fora_do_percurso` e o resto inalterados (R6) |
| `tests/analitico/test_analitico_dataset.py` (012) | Testes do campo novo | Aditiva |
| `tests/analitico/conftest.py`, `construcao.py` (012) | Corpo de `cenario` extraído para `cenario_de_referencia(inst)` | Refatoração de teste, sem mudar comportamento |
| `tests/analitico/test_analitico_fronteiras.py` (012), `tests/interface/test_interface_fronteiras.py` (008), `tests/editor/test_editor_fronteiras.py` (009) | Lista de dependências esperada passa a incluir `XlsxWriter`, com comentário (R11) | A regra de cada feature (não acrescentar dependência) continua verdadeira para ela |
| `config/settings.py` | `TRAJETORIA_CHAVE_PSEUDONIMIZACAO` lida do ambiente, padrão vazio | Técnico |
| `pyproject.toml`, `uv.lock` | `XlsxWriter` (produção); `openpyxl` (dev); marcador `volume` registrado e excluído por padrão (`addopts` com `-m "not volume"`), exigido por `--strict-markers` | Técnico |

Nenhuma alteração de código de produção em 001 a 011, na demonstração ou na governança.
Os únicos toques em 008 e 009 são a lista de dependências esperada nos seus testes de
fronteira.
