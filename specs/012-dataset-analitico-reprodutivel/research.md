# Research: Dataset analítico institucional reprodutível (Feature 012)

Fase 0 do plan. O Technical Context não tem itens `NEEDS CLARIFICATION`: a stack é a da
ADR 0001, sem dependência nova. Cada item registra **Decisão**, **Justificativa** e
**Alternativas consideradas**.

---

## R1 — O que pode derivar: verificação no código

**Decisão**: persistir somente o que a tabela abaixo marca como "Congelar". Todo o resto é
referenciado na leitura.

Verificado nas operações de domínio, que são o único caminho de escrita (ADR 0002;
`grep` de `save`/`create`/`update`/`delete` fora de `*/operacoes.py` e
`academico/incorporacao.py` não encontra escrita de produção).

| Dado | Pode mudar depois do encerramento? | Já é historicamente preservado? | Congelar? | Evidência no código |
|------|-------------------------------------|----------------------------------|-----------|---------------------|
| Critérios da Campanha (anos, unidades, níveis, modalidades, formas de oferta) | Não | Sim | **Não** | `definir_criterios` → `_bloquear_nunca_aberta` rejeita `CAMPANHA_JA_ABERTA` (`campanha/operacoes.py`) |
| Vínculo Campanha → Versão | Não | Sim | **Não** | `alterar_campanha` exige nunca aberta; `remover_campanha` idem |
| Período, nome, `aberta_em`, `encerrada_em` | Não | Sim | **Não** | `definir_periodo` exige nunca aberta; `abrir` grava `aberta_em` uma vez; `encerrar` grava `encerrada_em` uma vez |
| Estado ENCERRADA de Campanha aberta | Não volta a EM COLETA | Sim | **Não** | `estado`: `encerrada_em` fixo ou `fim` fixo desde a abertura; não há reabertura |
| Versão (estado, designação, títulos, textos) | Não, se PUBLICADA | Sim | **Não** | `alterar_versao` → `_exigir_rascunho`; `publicar` só RASCUNHO → PUBLICADA; `abrir` exige PUBLICADA |
| Seções, encaminhamentos | Não | Sim | **Não** | `adicionar/alterar/remover_secao`, `definir_encaminhamento`, `reordenar_secoes` → `_exigir_rascunho` |
| Perguntas (texto, tipo, escala, obrigatoriedade, posição) | Não | Sim | **Não** | `adicionar/alterar/mover/remover/reordenar_pergunta` → `_exigir_rascunho`; FK de Resposta é `PROTECT` |
| Opções e regras | Não | Sim | **Não** | `adicionar/alterar/remover/reordenar_opcao`, `definir/remover_regra` → `_exigir_rascunho` |
| Participação (existência, par, `iniciada_em`) | Não | Sim | **Não** | `iniciar_participacao` exige EM COLETA; nenhuma operação remove (005 FR-017); FKs `PROTECT` |
| `concluida_em` | Não | Sim | **Não** | `concluir` exige EM COLETA e grava uma vez; `JA_CONCLUIDA` não regrava |
| Respostas (valor, `opcao`, `texto`, `escala`) | Não | Sim | **Não** | `_escrever` exige não concluída **e** EM COLETA; `remover_resposta` idem |
| Opções selecionadas (`RespostaOpcao`) | Não | Sim | **Não** | Substituídas só em `_gravar`, chamado só por `_escrever` |
| Complementos | Não | Sim | **Não** | Coluna da Resposta; mesmo caminho de `_escrever` |
| Respostas fora do percurso em rascunho | Não, mas existem | Sim, como gravadas | **Não** | Removidas só por `concluir` (006 FR-032); rascunho as mantém (006 FR-033). Ver R9 |
| Pessoa | Fora do grão | — | **Não** | Não lida pela 012 |
| Nome da Pesquisa | **Sim**, a qualquer tempo | Não | **Não** | `renomear_pesquisa` sem restrição de estado; não integra a Versão (002 FR-003). Rótulo, não contexto analítico |
| Atributos de contexto da Conclusão | **Hoje não**; anunciados como mutáveis | Não por invariante | **Sim** | `incorporar_pessoa` "nunca atualiza nem remove"; é o tratamento provisório de 001/DP-005 e DP-006 |
| Pertencimento à população elegível | **Sim, hoje** | Não | **Sim** | `populacao_no_momento` é avaliada na consulta; Conclusões incorporadas depois do encerramento entram (004 FR-032) |

**Justificativa**: só as duas últimas linhas derivam. A penúltima deriva por decisão
pendente anunciada (001/DP-005; 005/DP-507; 011 FR-038); a última deriva hoje, com
qualquer nova incorporação. Nenhum dado que a spec presumiu imutável se mostrou mutável de
forma relevante: o nome da Pesquisa muda, mas não é dado analítico.

**Alternativas consideradas**:

- Congelar também Participação e Respostas "por segurança": duplicaria dado imutável e
  multiplicaria a superfície de dados sensíveis (spec FR-121). Rejeitada.
- Congelar o nome da Pesquisa: sem consumidor; a identificação do instrumento é pela
  Versão. Rejeitada; a 013 decide rótulos.

---

## R2 — Onde fica o código: app `trajetoria/analitico`

**Decisão**: app novo `trajetoria.analitico`, com `models.py`, `regras.py`,
`operacoes.py`, `consultas.py` e `migrations/`, registrado em `INSTALLED_APPS`.

**Justificativa**:

- O snapshot é conceito novo e distinto da Campanha (spec FR-001); colocá-lo em
  `campanha` daria à Campanha um acessor analítico.
- A dependência vai do novo para o antigo: `analitico` importa `campanha`,
  `participacao`, `academico`, `instrumento` e `fonte_academica.contrato`. Nenhum deles
  importa `analitico`.
- `acompanhamento` (011) é app de interface e não é tocado. A 012 **não** importa dele
  (R11).
- Mesmo padrão de arquivos das features 004 e 005 (`regras.py` para o vocabulário de
  recusa; `operacoes.py` único caminho de escrita; `consultas.py` só leitura).

**Alternativas consideradas**:

- `trajetoria/campanha/snapshot.py`: acoplaria o conceito à Campanha. Rejeitada.
- App genérico `dataset`/`analytics` com abstrações reutilizáveis: framework genérico
  vedado (spec Out of Scope). Rejeitada.

---

## R3 — Modelos: dois, sem terceiro

**Decisão**: `SnapshotAnalitico` e `RegistroDoSnapshot` (campos em
[data-model.md](data-model.md)).

**Justificativa**:

- O snapshot representa só a captura: `id`, `campanha`, `capturado_em`. Título,
  descrição, status, autor, motivo, observação, número sequencial: sem consumidor (spec
  FR-061, FR-104).
- O registro carrega exatamente o que deriva (R1): pertencimento (a existência da linha),
  `elegivel_no_snapshot` e os sete atributos de contexto.
- Um terceiro modelo só se justificaria por dado mutável que não caiba nos dois. A tabela
  de R1 não tem nenhum: Participação, Respostas, seleções, Versão e estrutura são
  imutáveis depois do encerramento.

**Alternativas consideradas**:

- `SnapshotParticipacao`, `SnapshotResposta`, `SnapshotOpcao`, `SnapshotPergunta`,
  `SnapshotVersao`, `SnapshotPessoa`: nada a congelar (R1). Rejeitadas.
- Totais gravados no snapshot (elegíveis, Participações): deriváveis dos registros;
  duplicação sujeita a inconsistência. Rejeitada.
- Motivo de inelegibilidade por registro: sem consumidor (spec FR-022). Rejeitada.
- Modelo base genérico de snapshot: framework vedado. Rejeitada.

---

## R4 — Ano e data de conclusão: ambos, como atributos independentes

**Decisão**: congelar `ano_conclusao` **e** `data_conclusao`, copiados como estão.

**Justificativa** (verificado em `academico/models.py`, `fonte_academica/contrato.py` e
001 FR-011):

- ambos são colunas persistidas da Conclusão;
- a fonte pode fornecer só o ano (001 FR-011: "ano, ou data completa"), então o ano
  **não** é derivação da data;
- com data, o CHECK `conclusao_ano_coerente_com_data` exige ano = ano da data; sem data,
  o ano é informação própria.

Pela regra da Clarification ("se ambos forem atributos reais, congele ambos"), os dois são
congelados. Nada é derivado, reinterpretado ou corrigido na cópia.

**Alternativas consideradas**:

- Congelar só a data e derivar o ano: perderia o ano das Conclusões sem data. Rejeitada.
- Congelar só o ano: o recorte por ano funcionaria, mas a referência temporal ficaria
  incompleta para a 013 e incentivaria combinar ano congelado com data atual (spec
  FR-042). Rejeitada.
- Repetir no registro o CHECK de coerência da 001: a cópia não deve rejeitar nem
  reinterpretar o que a fonte guarda (spec FR-043). Rejeitada (R5).

---

## R5 — Contexto congelado: a tupla `CAMPOS_DE_CONTEXTO` da 001, copiada sem transformação

**Decisão**: os campos de contexto do registro são exatamente
`fonte_academica.contrato.CAMPOS_DE_CONTEXTO` (curso, unidade, nível, modalidade, forma de
oferta, ano, data), com os mesmos tipos e nulabilidade da Conclusão. A captura copia os
valores lidos, sem `strip`, normalização, preenchimento ou consulta à fonte. O registro
**não** repete os CHECKs da Conclusão.

**Justificativa**:

- A 001 declara essa tupla como a lista para "quem copia ou compara o contexto", para que
  um campo novo do contrato não seja esquecido. Um teste de fronteira compara o conjunto
  de campos de contexto do registro com a tupla: se a 001 ganhar atributo, a 012 falha e
  a decisão fica explícita (spec FR-040).
- `NULL` é a única forma de ausência na origem (CHECKs `_nao_vazio` da 001). Copiar como
  está preserva ausência como ausência e grafia como recebida.
- Repetir os CHECKs não protegeria nada (a origem já os garante) e faria a captura falhar
  se a origem um dia guardasse algo diferente, o que seria rejeitar dado institucional
  em vez de preservá-lo.

**Alternativas consideradas**:

- Subconjunto só com os seis atributos dos recortes: rejeitada (R4).
- JSON com o contexto: perderia tipos, faria o recorte depender de chaves textuais e
  dificultaria a agregação no banco. Rejeitada.

---

## R6 — Referência à Conclusão e `on_delete`

**Decisão**:

| FK | Destino | `on_delete` | `related_name` |
|----|---------|-------------|----------------|
| `SnapshotAnalitico.campanha` | `campanha.Campanha` | `PROTECT` | `"+"` |
| `RegistroDoSnapshot.snapshot` | `SnapshotAnalitico` | `CASCADE` | `"registros"` |
| `RegistroDoSnapshot.conclusao` | `academico.ConclusaoAcademica` | `PROTECT` | `"+"` |

**Justificativa**:

- **Conclusão → `PROTECT`.**
  - A 001 não tem exclusão de Conclusão; a incorporação "nunca atualiza nem remove", e
    `Participacao.conclusao` já é `PROTECT`.
  - `CASCADE` faria uma remoção futura na origem apagar em silêncio registros históricos,
    exatamente o que a Clarification proíbe (spec FR-048).
  - `SET_NULL` deixaria registro sem origem, quebraria `UNIQUE (snapshot, conclusao)` como
    garantia de grão e alteraria o snapshot em silêncio.
  - **Consequência**: se uma decisão de retenção ou eliminação (DP-1202; 001/DP-009)
    exigir remover uma Conclusão, a remoção falhará enquanto houver registro que a
    referencie. A decisão precisará tratar os snapshots explicitamente. Nenhum framework de
    retenção é criado.
- **Campanha → `PROTECT`.** Só Campanha nunca aberta pode ser removida, e só Campanha
  aberta tem snapshot; o `PROTECT` documenta a regra sem nunca ser acionado pelas
  operações.
- **Snapshot → registros `CASCADE`.** O registro não tem significado sem o seu snapshot,
  como `RespostaOpcao` em relação à Resposta. Não há operação de remoção de snapshot (spec
  FR-050). Se uma decisão futura de retenção remover um snapshot, ele desaparece inteiro,
  nunca deixando registros órfãos, coerente com "completo ou inexistente".
- `related_name="+"` nas FKs para modelos anteriores: Campanha e Conclusão não ganham
  acessor reverso, como na 005 (research R2 da 005).

**Alternativas consideradas**: copiar `fonte` e `id_externo` para não depender da FK —
vedado (spec FR-046, FR-120). Rejeitada.

---

## R7 — Universo e elegibilidade: duas consultas claras, compostas na operação

**Decisão**: o universo é formado por **duas consultas** e uma composição em memória,
dentro da operação de captura:

```text
1. elegíveis      = populacao_no_momento(campanha).values_list("pk", *CAMPOS_DE_CONTEXTO)
                    → registro com elegivel_no_snapshot = True
2. participantes  = ConclusaoAcademica.filter(pk__in=Participacao(campanha).values("conclusao_id"))
                    .values_list("pk", *CAMPOS_DE_CONTEXTO)
                    → para cada pk que não está em (1): registro com elegivel_no_snapshot = False
3. universo       = (1) ∪ (2), deduplicado por pk da Conclusão; (1) prevalece
```

**Justificativa**:

- **Contrato público da 004, sem regra paralela**: `populacao_no_momento` é a resposta da
  004 a "esta Conclusão pertence à população atual desta Campanha?" (011 Clarifications;
  011 R4). A 012 só lê o resultado. `_filtro` continua privado; nenhum critério é lido.
- **Clareza** (Clarification do plan): cada consulta diz o que é. Sem UNION,
  `CASE`, SQL manual ou query builder.
- **Elegibilidade explícita**: o valor vem da consulta de origem (`True` para (1),
  `False` para o que só aparece em (2)); nunca nulo (spec FR-021).
- **Dedução por Conclusão**: a chave é o `pk` da Conclusão. Pessoa não participa. Uma
  Conclusão elegível com Participação aparece em (1) e em (2) e gera um registro só,
  elegível.
- **Corte = o que foi lido** (spec FR-054): o contexto copiado é o lido em (1) ou, para
  participantes não elegíveis, em (2). Não há promessa de leitura isolada entre as duas
  consultas e não é preciso: os participantes não mudam depois do encerramento (R1), e uma
  Conclusão incorporada entre (1) e (2) só entraria em (2) se tivesse Participação, o que
  exigiria coleta aberta.
- **Volume**: duas consultas, independentes do número de Conclusões; nenhuma consulta por
  Conclusão.
- Equivalência verificada em teste: para cada registro, `elegivel_no_snapshot ==
  avaliar(campanha, conclusao).elegivel` (função pura da 004), e o número de elegíveis é
  igual a `populacao_no_momento(campanha).count()`.

**Alternativas consideradas**:

- Uma única instrução com combinação `|` e `Exists`: correta, mas mais difícil de ler, e
  a "consistência de uma instrução" não é requisito. Rejeitada.
- REPEATABLE READ ou SERIALIZABLE para que as duas consultas vejam o mesmo estado: sem
  cenário concreto (Clarification). Rejeitada.
- `avaliar` em Python para cada Conclusão da instituição: uma avaliação por Conclusão.
  Rejeitada.
- Copiar `_filtro` ou os critérios: regra duplicada. Vedado (spec FR-020).

---

## R8 — Captura: atomicidade, momento, verificação e volume

**Decisão**: `capturar_snapshot(campanha) -> SnapshotAnalitico`, sem parâmetro de momento,
com os passos de [contracts/operacoes.md](contracts/operacoes.md):

1. tipo do argumento (`TypeError`);
2. `transaction.atomic()`;
3. `capturado_em = momento_de_referencia(None)` (relógio do sistema, lido uma vez);
4. Campanha relida; condição de captura com esse instante (recusa: R10);
5. Versão relida e PUBLICADA (guarda de integridade);
6. universo (R7);
7. cria o `SnapshotAnalitico` e grava os registros com um `bulk_create`
   (`batch_size` constante do módulo);
8. verificação de integridade, na mesma transação: nenhuma Participação da Campanha sem
   registro;
9. devolve o snapshot.

**Justificativa**:

- **Atomicidade** (spec FR-052): significa "o snapshot e todos os seus registros são
  gravados, ou nada é". Tudo numa transação; qualquer exceção desfaz cabeçalho e
  registros. Nenhum estado "processando" ou "falhou". **Não** significa leitura isolada
  de todas as tabelas (Clarification do plan): nenhum nível de isolamento, lock global ou
  advisory lock.
- **Momento definido pela operação** (spec FR-016): a operação lê o relógio. Isso desvia
  conscientemente do padrão `agora=` das operações da 004 e da 005 (research R6 da 004),
  porque aqui o instante **é** o dado gravado e não pode ser escolhido pelo chamador.
  `capturado_em` é o **momento técnico** em que a captura foi produzida, não o instante de
  uma leitura isolada. Os testes não precisam controlar o relógio: as Campanhas de teste
  são abertas e encerradas com `agora=` no passado (operações da 004), e a captura ocorre
  "agora". O teste verifica `antes ≤ capturado_em ≤ depois`.
- **Verificações** (spec FR-053): (a) e (b) antes de gravar; (c) pela deduplicação de R7 e
  pelo `UNIQUE (snapshot, conclusao)`; (e) pela origem do valor e pela coluna não nula; (f)
  por construção, porque os elegíveis gravados são exatamente os lidos em (1); (d)
  verificada depois do `bulk_create`. O total não é verificado à parte: o `bulk_create`
  grava todos ou levanta, e o `UNIQUE` impede duplicata (revisão de código). Falha →
  `CapturaInconsistente`, transação desfeita.
- **Escrita concorrente no limite do encerramento**: uma Participação cuja transação
  começou antes do encerramento e confirmou depois da consulta (2) faz a verificação (d)
  falhar. A captura é desfeita inteira e pode ser repetida. É o tratamento suficiente
  (Clarification do plan); nenhuma infraestrutura de concorrência.
- **Volume** (spec FR-110): duas consultas de leitura e um `bulk_create`, sem consulta
  nem `INSERT` por Conclusão. A lista do universo é do tamanho do universo da Campanha
  (dezenas de milhares no máximo previsto), não da instituição. Sem iterador de servidor,
  sem framework de lotes.

**Alternativas consideradas**:

- Parâmetro `agora` como nas outras operações: permitiria fabricar data histórica.
  Vedado. Rejeitada.
- Iterador de servidor com lotes manuais: otimização sem evidência de volume. Rejeitada.
- Estado "em andamento" no cabeçalho: vedado (spec FR-052). Rejeitada.

---

## R9 — Participação em rascunho e Respostas fora do percurso (Achado A1)

**Decisão**: o dataset (R12) classifica cada linha com Participação:

- **concluída** (`concluida_em` não nulo): todas as Respostas são do percurso final. A 006
  já removeu as demais ao concluir (006 FR-032). Nenhum recálculo, nenhuma limpeza.
  `fora_do_percurso = ∅`.
- **não concluída**: `fora_do_percurso` é calculado com as **funções puras da 006**, na
  mesma composição de `situacao_da_jornada`: `frozenset(respostas) −
  perguntas_do_percurso(percorrer(conteudo, respondidas(respostas)))`. O conteúdo da
  Versão é carregado **uma vez** (`conteudo_da_versao`). As Respostas fora do percurso são
  entregues, distinguíveis, e **nunca** como de Participação concluída.
- **Versão com estrutura não suportada** (006 FR-016): verificada **uma vez** por leitura,
  com `secoes_nao_suportadas(conteudo)`; `fora_do_percurso = None` ("percurso não
  determinável") para os rascunhos. Nada é descartado. Isso só pode ocorrer em rascunho,
  porque a conclusão rejeitaria a estrutura.
- **Respostas que a 006 rejeita** ao percorrer (Opção ausente ou alheia na Pergunta com
  regra; só por escrita fora das operações): `fora_do_percurso = None` só para aquela
  Participação; a leitura das demais linhas continua (revisão de código).

**Justificativa**:

- Reutiliza a 006 sem segunda implementação da jornada: `percorrer`, `respondidas` e
  `perguntas_do_percurso` são públicas e puras. Teste de equivalência: para cada
  rascunho, `fora_do_percurso == situacao_da_jornada(p).fora_do_percurso`.
- `situacao_da_jornada` não é chamada por linha porque relê a Versão e bloqueia a linha da
  Participação a cada chamada (várias consultas por Participação).
- Nenhuma Resposta de rascunho vira resposta final; nenhuma categoria "abandono" ou
  "recusa" (spec FR-075).

**Alternativas consideradas**:

- Descartar as Respostas fora do percurso do dataset: perderia dado preservado e
  anteciparia 005/DP-503. Rejeitada.
- Gravar a classificação: é derivada e determinística (006 FR-030). Rejeitada.
- Recalcular o percurso também das concluídas: desnecessário (006 FR-032). Rejeitada.

---

## R10 — Condição de captura e vocabulário de recusa

**Decisão**: `regras.py` com `Motivo` e `SnapshotRecusado`, no padrão de
`campanha/regras.py`:

| Ordem | Condição (instante = `capturado_em`) | Motivo |
|-------|--------------------------------------|--------|
| 1 | `campanha.aberta_em is None` (inclusive ENCERRADA pelo fim do período) | `CAMPANHA_NUNCA_ABERTA` |
| 2 | `estado(campanha, agora=capturado_em) is not ENCERRADA` | `COLETA_NAO_ENCERRADA` |

Inconsistências (Versão não publicada; verificações do passo 8 de R8) levantam
`CapturaInconsistente`, distinta de recusa de domínio, sem estado de validação.

**Justificativa**: a 004 é a dona do estado (`estado`) e do fato de abertura
(`aberta_em`; 004 FR-040: "`aberta_em` diz se houve coleta"). A ordem garante que Campanha
nunca aberta e expirada receba o motivo certo (spec FR-012). Nenhum estado novo.

**Alternativas consideradas**: usar `encerramento()` da 004 — devolve forma e momento,
mas não distingue nunca aberta. Desnecessário para a decisão. Rejeitada.

---

## R11 — Reprodução de indicadores e recortes, sem a Conclusão atual

**Decisão**: `consultas.py` agrega **somente** sobre `RegistroDoSnapshot` do snapshot
recebido, com dois `Exists` sobre `Participacao` filtrados pela Campanha do snapshot e por
`conclusao_id = OuterRef("conclusao_id")`: com Participação; com conclusão registrada.
Cada `Exists` aparece **uma vez** no SQL: a consulta agrupa também por
`elegivel_no_snapshot`, e a separação elegíveis × não elegíveis é feita em memória sobre
as linhas agrupadas (revisão de código: filtros repetidos avaliavam quatro subconsultas
correlacionadas por registro). Uma consulta para os totais e uma por recorte, com o mesmo
auxiliar.

O recorte é um `Enum` próprio da 012, fechado, com os mesmos seis recortes e os mesmos
campos da 011 (`unidade`; `unidade, curso`; `nivel`; `modalidade`; `forma_oferta`;
`ano_conclusao`), agora sobre os campos congelados.

**Justificativa**:

- **Nunca a Conclusão atual** (spec FR-080): a consulta só junta `RegistroDoSnapshot` com
  `Participacao` por `conclusao_id`. Nenhuma tabela da 001 aparece no SQL, o que é
  verificado em teste capturando as consultas executadas.
- **Nenhuma Resposta lida** (spec FR-112): idem, nenhuma tabela de Resposta no SQL.
- **Participação é imutável** depois do encerramento (R1), então juntar com ela não
  introduz deriva.
- **Definições da 011** (spec FR-082, FR-083): iniciadas = Participação existente;
  concluídas = conclusão registrada; denominador = registros elegíveis; numerador = todas
  as Participações, inclusive de registros não elegíveis; sem teto.
- **Enum próprio**: a 012 é núcleo de domínio e não importa o app de interface da 011. A
  lista é fechada, de seis itens, e um teste compara seus campos com os da 011 para não
  divergirem.
- Indicadores em objeto de valor imutável, com contagens separadas por elegibilidade e
  taxas `Decimal | None` (como na 011 R9; `None` com denominador zero). Nenhum
  arredondamento: apresentação é da 013.

**Alternativas consideradas**:

- Reutilizar `acompanhamento.consultas.Recorte` e `Indicadores`: acoplaria o núcleo
  analítico ao app de interface. Rejeitada.
- Gravar agregados por snapshot: cache disfarçado (spec FR-111). Rejeitada.
- Ler a Participação pelo registro com junção à Conclusão: poria a tabela da 001 no SQL.
  Rejeitada.

---

## R12 — Fronteira de leitura do dataset

**Decisão**: `linhas_do_dataset(snapshot)` devolve um **iterador** de `LinhaDoDataset`,
objeto de valor imutável (campos em [data-model.md](data-model.md)):

- referência técnica interna à Conclusão e elegibilidade no snapshot;
- `ContextoCongelado` (os sete atributos, nunca a instância do registro, para que nenhum
  acesso leve à Conclusão atual);
- `ParticipacaoNoDataset` ou `None` (identificador técnico, `iniciada_em`, `concluida_em`;
  nunca a instância, que alcançaria Conclusão e Pessoa);
- `respostas`: as Respostas preservadas, por `id` da Pergunta, como `RespostaNoDataset`
  (Pergunta da Versão aplicada, `opcao_id`, Opção, Opções selecionadas, texto, escala,
  complemento). **Nunca** a instância de `Resposta`, porque `resposta.participacao`
  alcançaria Participação, Conclusão atual e Pessoa (spec FR-076). `Pergunta` e `Opcao`
  podem ser entregues: são do instrumento imutável e não têm acessor reverso para
  Resposta (`related_name="+"` na 005);
- `fora_do_percurso` (R9).

Leitura simples e sem N+1: os registros do snapshot são lidos em ordem de `conclusao_id`
(só determinismo); uma consulta de Participações da Campanha; uma de Respostas dessas
Participações com `select_related` de Pergunta e Opção e `prefetch_related` das Opções
selecionadas; o conteúdo da Versão carregado uma vez. Nenhuma consulta por linha. Se o
volume real um dia exigir leitura em blocos, a mudança é local à função; a docstring de
`linhas_do_dataset` registra isso.

**Mínima, não é a 013** (Clarification do plan): os objetos de valor representam só o
necessário — contexto congelado, elegibilidade, estado da Participação, Respostas na
semântica existente e a classificação de rascunho. Nenhum schema, definição de colunas,
serializador, achatamento, nome externo, CSV ou adaptação ao GeN.

**Justificativa**:

- Combina registro, Campanha/Versão, Participação e Respostas **sem persistir** a
  combinação (spec FR-070, FR-071).
- Número de consultas independente do número de Conclusões (spec FR-110).
- Não achata Perguntas em colunas e não serializa escolha múltipla: as Respostas vêm na
  estrutura semântica existente (spec FR-074). A 013 decide formato, colunas e nomes.
- A referência à Conclusão e à Participação é técnica e interna. A docstring e o
  contrato declaram que não são identificadores exportáveis (spec FR-047); a exposição é
  da 013, sob 005/DP-505.
- Recebe o snapshot explicitamente; nenhuma função escolhe snapshot (spec FR-064).

**Alternativas consideradas**:

- Modelo `Dataset` ou visão materializada: persistência por conveniência. Vedado.
  Rejeitada.
- Serializador genérico (dict/JSON) com nomes de campo finais: anteciparia a 013.
  Rejeitada.
- Entregar instâncias de `Participacao`, `RegistroDoSnapshot` ou `Resposta`: o acesso
  preguiçoso a `.conclusao`, `.pessoa` ou `.participacao` permitiria ler o estado atual ou
  PII. Rejeitada.

---

## R13 — Vários snapshots e concorrência

**Decisão**:

- Nenhuma unicidade por Campanha; cada snapshot tem seus registros, e o
  `UNIQUE (snapshot, conclusao)` é por snapshot.
- `snapshots_da_campanha(campanha)` devolve **todos**, em ordem `(capturado_em, id)`, com
  a docstring "ordem administrativa, sem autoridade".
- **Nenhuma** função `snapshot_atual`, `snapshot_vigente`, `ultimo_snapshot` ou
  equivalente. Um teste de fronteira verifica que o `__all__` de `consultas` não oferece
  nada além do contrato.
- Nenhum lock: duas capturas simultâneas são duas transações independentes. Cada uma lê
  e grava seus próprios registros, sem chave compartilhada; cada uma é atômica (R8). A Campanha não é bloqueada: nada nela muda depois do encerramento (R1) e
  ela não pode ser removida (só nunca aberta é removível; `PROTECT`).

**Justificativa**: Clarifications de 2026-10-02; spec FR-060 a FR-064.

**Alternativas consideradas**:

- `select_for_update` na Campanha: serializaria capturas sem necessidade (Clarification:
  "não impedir isso com lock"). Rejeitada.
- Deduplicar capturas equivalentes: elegeria um snapshot implicitamente. Vedado (FR-061).
  Rejeitada.

---

## R14 — Governança, interface e disparo

**Decisão**:

- A operação de domínio existe; nenhuma UI, rota, view, endpoint ou management command a
  chama nesta feature.
- Nenhuma regra nova em `governanca` (`pode_criar_snapshot` ou similar não é criada).
- O plan registra que, quando houver exposição institucional, a competência (CPAEG,
  Interpretação B2; spec FR-102) precisará ser aplicada por quem expuser.
- O quickstart exercita a feature por testes automatizados. Management command não é
  criado: não há consumidor concreto (o cenário de demonstração não tem Campanha
  encerrada com Participações, e acrescentá-la está vedado pela spec FR-131).

**Justificativa**: Clarifications de 2026-10-02; spec FR-100 a FR-104; YAGNI.

**Alternativas consideradas**:

- Management command `capturar_snapshot`: sem consumidor (nem demonstração, nem
  operação técnica real com dados fictícios persistentes). Rejeitada; pode surgir com a
  013.
- Regra `pode_capturar_snapshot` por simetria: sem consumidor. Rejeitada.

---

## R15 — Demonstração e dados de teste

**Decisão**: nenhuma mudança em `trajetoria/demonstracao`. Fixtures isoladas em
`tests/analitico/`, reutilizando as construções existentes (`tests/acompanhamento/
construcao.py` para Conclusões fictícias e `tests/participacao/construcao.py` para
preencher o instrumento). Campanhas de teste com período no passado, abertas e encerradas
com `agora=` passado, pelas operações da 004; Participações e Respostas pelas operações
da 005/006.

Alteração acadêmica simulada (casos G, J, K): `ConclusaoAcademica.objects.filter(…)
.update(…)` **dentro do teste**, documentado como simulação de 001/DP-005. Nenhuma
operação de correção é criada.

**Justificativa**: spec FR-130 a FR-132; Clarification "fixtures isoladas resolvem".

**Alternativas consideradas**: acrescentar Campanha encerrada com Participações ao preparo
da demonstração — contrariaria "o preparo nunca cria Participação nem Resposta" e FR-131.
Rejeitada.

---

## R16 — Privacidade

**Decisão**:

- Campos do registro: só referência interna, elegibilidade e os sete atributos de
  contexto. Teste de fronteira compara o conjunto exato de campos dos dois modelos.
- Nenhuma cópia de nome, CPF, e-mail, telefone, matrícula, endereço, `fonte`,
  `id_externo`, Resposta, Pergunta, Opção ou texto.
- Sem hash, pseudônimo ou identificador analítico.
- Mensagens de recusa e de inconsistência citam motivo, `id` da Campanha e do snapshot e
  contagens; nunca valores acadêmicos ou conteúdo de Resposta. Nenhum log novo.
- Nenhuma supressão de grupos pequenos na captura (011/DP-1101).

**Justificativa**: spec FR-120 a FR-125; Const. XVI.

**Alternativas consideradas**: nenhuma.
