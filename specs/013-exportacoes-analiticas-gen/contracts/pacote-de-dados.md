# Contrato de dados analíticos — versão 1 (Feature 013)

Documento para **consumidores a jusante**: GeN, analistas, outras ferramentas. Descreve o
que um pacote exportado contém e como lê-lo, **sem acesso ao sistema** (spec FR-120). O
mecanismo de entrega ao GeN não faz parte deste contrato (DP-1302).

`contrato_versao = 1` (Metadados). Mudam a versão: colunas base, nomes técnicos, tipos,
representação, tabelas ou notas alteradas de forma incompatível (spec FR-065).

---

## O que é, e o que não é

- **É**: uma fotografia individualizada de **um** snapshot analítico de **uma** Campanha,
  com uma linha por Conclusão Acadêmica do universo do snapshot.
- **Inclui**:
  - Conclusões elegíveis sem Participação;
  - Conclusões não elegíveis no snapshot com Participação;
  - Participações não concluídas.
- **É pseudonimizado, não anônimo.** Linhas podem ser reidentificáveis por combinação de
  atributos e pela ligação entre exportações. Acesso e compartilhamento são decisões
  institucionais (DP-1301, DP-1303).
- **Não é**: mailing, lista de contatos, série histórica entre Versões, resultado oficial.
  Nenhum snapshot é oficial (012/DP-1201). Perguntas de Versões diferentes **não** são
  comparáveis por nome de coluna (002/DP-006).

---

## Tabelas

| Tabela | CSV | XLSX | Conteúdo |
|--------|-----|------|----------|
| Dados | `dados.csv` | aba `Dados` | Uma linha por registro do snapshot; 14 colunas base + colunas de Pergunta |
| Dicionário | `dicionario.csv` | aba `Dicionário` | Uma linha por coluna de Dados (mesma ordem) + valores possíveis da escolha única |
| Metadados | `metadados.csv` | aba `Metadados` | `chave`, `valor`, `tipo`: origem, contagens, versões e notas |

Estrutura completa em [data-model.md](../data-model.md).

### Colunas base de Dados

`conclusao_analitica_id`, `pessoa_analitica_id`, `elegivel_no_snapshot`, `unidade`,
`curso`, `nivel`, `modalidade`, `forma_oferta`, `ano_conclusao`, `data_conclusao`,
`possui_participacao`, `participacao_concluida`, `participacao_iniciada_em`,
`participacao_concluida_em`.

### Colunas de Pergunta

| Padrão | Significado |
|--------|-------------|
| `pergunta_<p>__aplicavel` | Pergunta no percurso calculado (verdadeiro), fora (falso), sem Participação ou percurso não determinável (vazio) |
| `pergunta_<p>` | Escolha única: texto da Opção. Texto curto: texto declarado. Escala: inteiro |
| `pergunta_<p>__opcao_<o>` | Escolha múltipla: Opção escolhida (verdadeiro) ou não (falso); vazio sem Resposta válida |
| `pergunta_<p>__complemento` | Complemento textual declarado |

`<p>` e `<o>` são identificadores da Pergunta e da Opção **dentro da Versão**, em 32
hexadecimais minúsculos. Todos os nomes usam só `[a-z0-9_]` e começam por letra.

### Como ler uma célula vazia de Pergunta

| `possui_participacao` | `__aplicavel` | Leitura |
|-----------------------|---------------|---------|
| falso | vazio | não há Participação |
| verdadeiro | vazio | percurso não determinável (contado em `participacoes_com_percurso_nao_determinavel`) |
| verdadeiro | falso | Pergunta fora do percurso |
| verdadeiro | verdadeiro | Pergunta aplicável, não respondida |

`participacao_concluida` distingue respostas finais (verdadeiro) de rascunho no
encerramento (falso).

---

## Pseudônimos analíticos

- `conclusao_analitica_id` e `pessoa_analitica_id` têm 64 hexadecimais minúsculos.
- `pseudonimizacao_esquema = hmac-sha256-v1` significa:
  - HMAC-SHA-256 sobre a mensagem UTF-8 `<domínio>:<identificador interno>`;
  - domínio `conclusao` ou `pessoa`;
  - identificador na forma canônica de UUID;
  - saída hexadecimal;
  - a chave é secreta e não acompanha o pacote.
- **Estáveis** entre exportações enquanto a mesma chave vigorar: a mesma Conclusão (ou
  Pessoa) tem o mesmo pseudônimo em snapshots e Campanhas diferentes.
- **Não comparáveis** entre exportações feitas com chaves diferentes.
- `pessoa_analitica_id` identifica o registro de Pessoa do sistema, não uma identidade
  reconciliada entre fontes (001/DP-003).

---

## CSV

| Aspecto | Regra |
|---------|-------|
| Pacote | ZIP com exatamente `dados.csv`, `dicionario.csv`, `metadados.csv` |
| Codificação | UTF-8, **sem** BOM |
| Separador / aspas | vírgula; aspas duplas, RFC 4180; quebra de linha CRLF |
| Cabeçalho | primeira linha, nomes técnicos |
| Booleano | `true` / `false` |
| Inteiro | decimal, sem separador de milhar |
| Data | `AAAA-MM-DD` |
| Momento | ISO 8601 com deslocamento (por exemplo, `2027-03-01T10:15:00-03:00`) |
| Ausência | campo vazio. O sistema nunca grava texto vazio como valor |

### Escape contra fórmula (parte do contrato; variante única)

- **Aplicação**: todo campo **textual** cujo primeiro caractere seja `=`, `+`, `-`, `@`,
  tabulação, retorno de carro ou apóstrofo recebe um apóstrofo (`'`) na frente. Isso vale
  nas três tabelas.
- **Reversão**: em qualquer campo de qualquer dos três arquivos, se o primeiro caractere
  for `'`, remova exatamente esse caractere. Não é preciso saber o tipo da coluna.
  - Campos booleanos, inteiros, de data e de momento nunca começam por `'`.
  - Todo texto original iniciado por `'` também foi escapado.
  - Por isso a reversão devolve o valor original em todos os casos.

| Valor original | No CSV | Após a reversão |
|----------------|--------|-----------------|
| `=1+1` | `'=1+1` | `=1+1` |
| `+ de 5 salários` | `'+ de 5 salários` | `+ de 5 salários` |
| `'abc` | `''abc` | `'abc` |
| `abc` | `abc` | `abc` |
| `-3` (escala, inteiro) | `-3` | `-3` |

## XLSX

| Aspecto | Regra |
|---------|-------|
| Abas | `Dados`, `Dicionário`, `Metadados`, nesta ordem; cabeçalho na linha 1 |
| Texto | célula de texto, **nunca fórmula**, **sem** escape |
| Booleano / inteiro | tipos nativos |
| Data | data nativa, exibida `yyyy-mm-dd` |
| Momento | texto ISO 8601 |
| Ausência | célula vazia |
| Proibido | fórmulas, gráficos, macros, tabelas dinâmicas, filtros, formatação condicional, células mescladas, abas ocultas; só o cabeçalho é destacado |

---

## Descrições das colunas base

Texto fixo do contrato, presente na coluna `descricao` do Dicionário.

| Coluna | `descricao` |
|--------|-------------|
| `conclusao_analitica_id` | Pseudônimo analítico da Conclusão Acadêmica (formação concluída). Estável entre exportações feitas com a mesma chave; não reversível pelo consumidor. |
| `pessoa_analitica_id` | Pseudônimo analítico do registro de Pessoa a que a Conclusão pertence. Liga Conclusões da mesma Pessoa entre exportações feitas com a mesma chave; não reversível pelo consumidor; não reconcilia registros de fontes diferentes. |
| `elegivel_no_snapshot` | Se a Conclusão pertencia à população elegível da Campanha no momento da captura do snapshot. Não é a elegibilidade atual. É o denominador das taxas. |
| `unidade` | Unidade (campus, campus avançado ou Cefor) da Conclusão, segundo a fonte institucional no momento da captura. Dado institucional, não declarado pelo egresso. Vazio = não informado. |
| `curso` | Curso da Conclusão, segundo a fonte institucional no momento da captura. Interpretar junto com a unidade: cursos homônimos de unidades diferentes são distintos. Vazio = não informado. |
| `nivel` | Nível da Conclusão, segundo a fonte institucional no momento da captura. Vazio = não informado. |
| `modalidade` | Modalidade da Conclusão, segundo a fonte institucional no momento da captura. Vazio = não informado. |
| `forma_oferta` | Forma de oferta da Conclusão, segundo a fonte institucional no momento da captura. Vazio = não informado. |
| `ano_conclusao` | Ano de conclusão, segundo a fonte institucional no momento da captura. Independente de data_conclusao: a fonte pode informar só o ano. Vazio = não informado. |
| `data_conclusao` | Data de conclusão, segundo a fonte institucional no momento da captura, quando a fonte a informa. Vazio = não informada. |
| `possui_participacao` | Se existe Participação desta Conclusão na Campanha. |
| `participacao_concluida` | Se a Participação teve conclusão registrada (inclusive por recusa em Q1). Falso = iniciada e não concluída até o encerramento. Vazio = sem Participação. |
| `participacao_iniciada_em` | Data de início da Participação, na timezone institucional (America/Sao_Paulo). Vazio = sem Participação. |
| `participacao_concluida_em` | Data da conclusão registrada da Participação, na timezone institucional. Vazio = sem Participação ou não concluída. |

## Notas fixas

Valores das chaves de nota nos Metadados. O texto é idêntico no CSV, a menos do escape, que
não se aplica porque nenhuma nota começa por caractere de gatilho, e no XLSX.

| `chave` | `valor` |
|---------|---------|
| `finalidade` | Análise institucional dos resultados do acompanhamento de egressos (PAEG, Art. 10, III). Não é lista de contatos nem base de comunicação. |
| `nota_snapshot` | Este pacote contém exatamente um snapshot analítico, escolhido por quem exportou. Nenhum snapshot é oficial ou de referência; essa designação é decisão institucional pendente. |
| `nota_privacidade` | Dados individualizados e pseudonimizados, não anônimos. Linhas podem ser reidentificáveis pela combinação de atributos e pela ligação entre exportações. Não compartilhar fora da finalidade autorizada. |
| `nota_representacao` | Célula vazia = ausência de valor (não informado, não se aplica ou sem Resposta). Booleanos como true/false; datas como AAAA-MM-DD; momentos em ISO 8601 com deslocamento; datas da Participação na timezone institucional. |
| `nota_proveniencia` | Coluna proveniencia do Dicionário: institucional = contexto da Conclusão na fonte acadêmica, congelado no snapshot; derivado = calculado por regra (elegibilidade no snapshot, pseudônimos, aplicabilidade); coleta = fato registrado pelo sistema durante a coleta (existência, início e conclusão da Participação); declarado = Resposta do egresso. |
| `nota_aplicabilidade` | Para cada Pergunta, a coluna __aplicavel indica se ela pertence ao percurso calculado da Participação (verdadeiro), está fora dele (falso) ou não tem percurso (vazio: sem Participação ou percurso não determinável). Valor preenchido só ocorre com aplicabilidade verdadeira. |
| `nota_escape_csv` | No CSV, todo campo de texto que começa por =, +, -, @, tabulação, retorno de carro ou apóstrofo recebe um apóstrofo inicial, para não ser interpretado como fórmula. Para reverter, remova o apóstrofo inicial de qualquer campo que comece por apóstrofo. No XLSX não há escape: o texto é gravado como texto. |
