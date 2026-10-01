# Research: Jornada de resposta e conclusão da Participação

**Feature**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

Não houve `NEEDS CLARIFICATION` no Technical Context. A stack é a das Features 001 a 005
([ADR 0001](../../docs/adr/0001-stack-inicial.md)), e as quatro decisões de produto foram
confirmadas (spec, Clarifications). As decisões abaixo são de desenho.

## R1 — Onde a jornada vive

- **Decisão**: no app existente `trajetoria.participacao`, sem app novo:
  - `percurso.py` (**novo**): derivação **pura** do percurso a partir da árvore imutável
    da Versão (`ConteudoVersao`, 002) e de um mapeamento das Respostas atuais
    (`respondidas`: Pergunta → Opção escolhida ou `None`). Não acessa o ORM, não chama
    `conteudo_da_versao` nem `respostas_atuais`, não conhece Campanha, Conclusão ou
    relógio. Toda a I/O fica em `consultas.py` e `operacoes.py`, que carregam os dados e
    entregam as estruturas prontas;
  - `operacoes.py` (alterado): `concluir` e o bloqueio de escrita após a conclusão;
  - `consultas.py` (alterado): `situacao_da_jornada` e `admite_escrita` ciente da
    conclusão;
  - `regras.py` (alterado): três motivos novos.
- **Rationale**: a jornada não tem dados próprios além de `concluida_em`, que pertence à
  Participação. Escrita continua num único módulo (005, "Único caminho de escrita"), e a
  regra de navegação fica isolada numa função pura, testável sem banco.
- **Alternativas rejeitadas**:
  - app `jornada`: um app sem modelo, dependente só de `participacao`, separando a
    conclusão da escrita de respostas que ela precisa bloquear;
  - objeto `Journey`/`Jornada` com estado e métodos: o estado seria cópia derivável de
    Versão + Respostas (spec, princípio central; FR-052);
  - colocar a navegação em `instrumento`: o instrumento passaria a conhecer Respostas
    (002 FR-065).

## R2 — `concluida_em`: um campo anulável, sem enum

- **Decisão**: `Participacao.concluida_em = DateTimeField(null=True)`, gravado só por
  `concluir`. Migração `0002_participacao_concluida_em` com um único `AddField`, aditiva e
  reversível. Sem `default`, sem `auto_now`, sem índice novo.
- **Rationale**: `NULL` ⇔ rascunho; preenchido ⇔ concluída (FR-001, FR-002). O padrão é o
  mesmo de `iniciada_em` (momento de referência, não `auto_now_add`, para os testes
  controlarem o tempo) e de `Campanha.aberta_em`/`encerrada_em` da 004.
- **Alternativas rejeitadas**:
  - enum `estado` (`RASCUNHO`/`CONCLUIDA`): redundante com o momento e capaz de divergir
    dele (FR-002);
  - booleano `concluida` + momento: dois campos para um fato;
  - `CHECK concluida_em >= iniciada_em`: o momento de referência real é monotônico; com
    `agora` explícito, só um teste mal construído violaria. Sem consumidor (XXII).

## R3 — Ler a Versão pela árvore imutável da 002

- **Decisão**: a consulta e a operação leem a Versão aplicada uma vez, por
  `conteudo_da_versao` (`trajetoria.instrumento.conteudo`), e as Respostas por
  `respostas_atuais` (005), e entregam à derivação o `ConteudoVersao` e o mapeamento
  `respondidas`. A derivação reutiliza os tipos da 002 sem cópia, sem DTO novo e sem árvore
  paralela.
- **Rationale**:
  - `ConteudoVersao` já traz Seções e Perguntas em ordem, `obrigatoria`,
    `encaminhamento_id` e, por Opção, `regra` (`destino_secao_id` ou `finaliza`) — tudo de
    que a navegação precisa, sem nada a mais;
  - é imutável e comparável: o mesmo conteúdo com as mesmas respostas dá o mesmo
    resultado (FR-017);
  - número fixo de consultas ao banco (prefetch), independente do tamanho do percurso;
  - nada do instrumento é copiado nem persistido (FR-005, FR-009).
- **Alternativas rejeitadas**: percorrer o ORM Seção a Seção (consultas proporcionais ao
  percurso, sem ganho); cache ou tabela de percurso (FR-005, FR-018; "Over engineering
  check" do solicitante).

## R4 — Algoritmo do percurso e precedência de destino

- **Decisão**: `percorrer(conteudo, respondidas)` começa na primeira Seção da Versão e, para
  cada Seção alcançada:
  1. **pendentes** = Perguntas obrigatórias da Seção sem Resposta;
  2. **destino** (FR-012):
     1. Pergunta com regra da Seção respondida, Opção com regra → Seção da regra ou
        finalização;
     2. Pergunta com regra obrigatória sem Resposta → **indeterminado**;
     3. senão, encaminhamento da Seção;
     4. senão, Seção seguinte na ordem;
     5. senão, finalização;
  3. registra a passagem; se há pendentes, se o destino é indeterminado ou se é a
     finalização, para; senão, segue para o destino.
- **Rationale**:
  - a unidade é a Seção: a Seção inteira entra no percurso e a regra só decide a saída
    (FR-010, FR-011). Q47 e Q48 são consideradas em S11 antes de qualquer desvio;
  - só Perguntas da própria Seção são lidas para pendências e destino. Por construção,
    uma Resposta fora do percurso nunca é lida — é exatamente a condição "inativa"
    (FR-030), sem flag;
  - pergunta com regra opcional sem resposta segue a precedência da 002 (FR-054);
  - a Versão aplicada é PUBLICADA, então todo destino é posterior (002 FR-055, FR-059 d):
    o laço termina sem detecção de ciclo (FR-015);
  - Q51 não é tratada: não tem regra, e a saída de S12 é o encaminhamento (FR-026).
- **Alternativas rejeitadas**: aplicar a regra logo após a Pergunta (contraria FR-011);
  enumerar todos os percursos possíveis (é oráculo de teste da 002/003, não execução);
  máquina de estados ou grafo (FR-052).

## R5 — Representação do percurso parcial

- **Decisão**: o resultado de `percorrer` é uma tupla de `Passagem(secao, pendentes,
  destino)`, na ordem do percurso. `destino` é o `id` de uma Seção ou um membro de
  `Saida` (`FINALIZACAO`, `INDETERMINADA`). A última passagem diz onde o percurso para:
  - satisfeita com destino `FINALIZACAO` → **jornada finalizada**;
  - com pendentes → **Seção atual**; o destino pode já estar determinado (por exemplo,
    S11 com Q46 respondida e Q47 pendente: destino S12 conhecido, mas a Seção não pode ser
    deixada);
  - destino `INDETERMINADA` → Seção atual cuja saída depende de Resposta ainda não dada.
- **Rationale**: distingue sem ambiguidade a parte determinada do ponto em que o destino
  ainda depende de resposta, e nunca inventa Seção futura. É um valor imutável de
  leitura, como `ConteudoVersao` (002) e `Elegibilidade` (004); não é entidade nem é
  persistido.
- **Alternativas rejeitadas**: devolver só a lista de Seções (perde pendências e
  destinos); incluir Seções "prováveis" além da atual (inventaria percurso).

## R6 — Estrutura não suportada: verificação da Versão inteira

- **Decisão**: antes de percorrer, `percorrer` verifica se alguma Seção da Versão tem mais
  de uma Pergunta com regra. Se tiver, rejeita com `ESTRUTURA_NAO_SUPORTADA`, uma
  violação por Seção, identificando-a. A consulta da jornada e a conclusão propagam a
  rejeição.
- **Rationale**: FR-016 refere-se à Versão aplicada, não ao trecho já percorrido.
  Verificar a Versão inteira dá o mesmo resultado para toda Participação da Campanha,
  independentemente das respostas, e não modifica nada. A 002 continua permitindo
  representar a estrutura; é limitação da execução (Clarifications).
- **Alternativas rejeitadas**: primeira ou última regra, ordem das Perguntas, combinação,
  prioridade configurável (proibidas em FR-016); verificar só ao alcançar a Seção
  (resultados diferentes por Participação para a mesma Versão).

## R7 — Respostas inativas e limpeza na conclusão

- **Decisão**:
  - **ativas** = Respostas cujas Perguntas pertencem às Seções das passagens; **fora do
    percurso** = as demais. Ambas são conjuntos de `id` de Pergunta, calculados a partir
    das passagens e de `respostas_atuais`;
  - na conclusão aceita, um único `DELETE` remove as Respostas da Participação cujas
    Perguntas não estão no percurso final (`exclude(pergunta_id__in=…)`); as seleções de
    escolha múltipla saem pelo `CASCADE` já existente de `RespostaOpcao` (005 R5).
- **Rationale**: sem coluna `ativa`, sem flag, sem tabela (FR-030). O `exclude` cobre
  também qualquer Resposta a Pergunta que nem pertença à Versão (só possível fora das
  operações): ela não está no percurso final e é removida, de modo que a Participação
  concluída contém somente o percurso final (FR-032).
- **Alternativas rejeitadas**: remover a cada troca de ramo (perderia respostas que
  voltariam a valer e exigiria saber o futuro do percurso — spec, Assumptions); marcar
  ou arquivar (histórico de ramos, proibido em FR-033); expiração de rascunhos
  (005/DP-503).

## R8 — Obrigatoriedade e pendências

- **Decisão**: pendência é uma violação `OBRIGATORIA_PENDENTE` por Pergunta obrigatória
  sem Resposta **da Seção atual**. Não há motivo "destino indeterminado": o destino só
  fica indeterminado quando a Pergunta com regra é obrigatória e não tem Resposta, e
  então ela já é pendência.
- **Rationale**: Seções anteriores do percurso estão satisfeitas por construção (senão o
  percurso teria parado nelas) e Seções posteriores ainda não são conhecidas; logo, as
  pendências da jornada são exatamente as da Seção atual (FR-019, FR-020, FR-037).
  Perguntas fora do percurso nunca são lidas.
- **Alternativa rejeitada**: listar obrigatórias de todas as Seções possíveis à frente
  (exigiria percurso não determinado).

## R9 — `concluir` no único caminho de escrita

- **Decisão**: `concluir(participacao, *, agora=None)` em `operacoes.py`:
  1. `TypeError` para argumento de classe errada; `agora` validado antes do banco;
  2. transação; bloqueia a Participação (o mesmo `_bloquear` das escritas);
  3. se `concluida_em` existe → devolve `(participacao, JA_CONCLUIDA)`, sem ler mais
     nada e sem gravar (FR-036);
  4. lê o relógio (depois do bloqueio, como nas escritas da 005);
  5. reúne violações: coleta não admitida (`estado` da 004); estrutura não suportada,
     pendências da Seção atual e incoerência das Respostas ativas (R10);
  6. com qualquer violação → `ParticipacaoRejeitada` com todas, nada gravado;
  7. remove as Respostas fora do percurso final (R7);
  8. grava `concluida_em = agora` (`update_fields`);
  9. devolve `(participacao, CONCLUIDA)`.
- **Rationale**: a conclusão escreve na Participação e remove Respostas: pertence ao
  módulo que é o único caminho de escrita (005, "Garantias comuns"). Validar antes de
  remover garante que uma rejeição não apaga nada (FR-033, FR-044); dentro da transação,
  a ordem "remover → validar" da Clarification e "validar → remover" deste plan são
  equivalentes, e validar primeiro evita escrita inútil.
- **Alternativas rejeitadas**: método `Participacao.concluir()` (lógica de domínio no
  modelo, fora do padrão do projeto); sinal ou `save()` sobrescrito; operação em módulo
  à parte (segundo caminho de escrita).

## R10 — Reusar a validação da 005 nas Respostas ativas

- **Decisão**: uma função privada nova em `operacoes.py`,
  `_verificar_resposta_gravada(resposta, pergunta)`, que **compõe os validadores
  existentes** da 005 com os valores gravados: `_opcao_da_pergunta` + `_complemento`
  (escolha única); `_opcoes_da_pergunta` + `_complemento` (múltipla);
  `_texto_declarado` (texto); `_escala_da_pergunta` (escala). Para isso, a verificação de
  escala hoje embutida em `responder_escala` é extraída para `_escala_da_pergunta`, sem
  mudar o comportamento. Cada violação encontrada é devolvida com o motivo da 005
  (`OPCAO_DE_OUTRA_PERGUNTA`, `VALOR_VAZIO`…), `campo="pergunta"` e o `id` da Pergunta no
  detalhe.
- **Rationale**: é a menor alteração que evita reescrever as regras (FR-045; pedido do
  solicitante). Nenhum motivo novo para incoerência: os da 005 já dizem o que está errado.
  Custo: algumas consultas por Resposta ativa, uma vez por conclusão (uma Participação
  tem algumas dezenas de Respostas).
- **Alternativas rejeitadas**: framework de validators ou registro por tipo
  (005 FR-054); revalidar em memória pela árvore (duplicaria as regras); omitir a
  verificação (FR-045 exige; protege contra escrita fora das operações). A verificação
  não é feita em `situacao_da_jornada`: só a conclusão consolida dados, e a incoerência só
  é possível fora das operações.

## R11 — Bloqueio de escrita após a conclusão

- **Decisão**:
  - no esqueleto `_escrever` da 005, logo depois de `_bloquear` e **antes** da coleta:
    `participacao.concluida_em is not None` → `PARTICIPACAO_CONCLUIDA`. Vale para as
    quatro `responder_*` e `remover_resposta`, em qualquer estado da Campanha (FR-038);
  - `admite_escrita` passa a exigir também `concluida_em` nulo, relido do banco (a
    instância recebida pode estar desatualizada) (FR-040);
  - `iniciar_participacao` não muda: devolve a existente, concluída ou não (FR-041).
- **Rationale**: é o ponto de extensão previsto pela 005 ("verificá-lo no passo 3 do
  esqueleto" — 005 plan, "Contrato para a 006"). Verificar antes da coleta faz a rejeição
  indicar a conclusão mesmo com a Campanha encerrada.
- **Alternativas rejeitadas**: gatilho PostgreSQL (vedado pelo solicitante; regra fora do
  caminho suportado); CHECK entre tabelas (impossível); bloquear no `save()` do modelo.

## R12 — Concorrência

- **Decisão**: o mesmo `select_for_update(of=("self",))` da Participação já usado pelas
  escritas da 005 serializa conclusão × conclusão e conclusão × escrita:
  - duas conclusões: a segunda espera o bloqueio, relê `concluida_em` preenchido e
    devolve `JA_CONCLUIDA`, sem reler respostas nem remover nada;
  - escrita esperando a conclusão: relê a Participação concluída e é rejeitada
    (`PARTICIPACAO_CONCLUIDA`);
  - conclusão esperando uma escrita: lê as Respostas já gravadas por ela.
- **Rationale**: nenhum mecanismo novo de coordenação; um `concluida_em` e nenhum
  processamento destrutivo duplicado (FR-043).
- **Testes**: determinísticos (conclusão repetida; escrita depois da conclusão) e, como
  na 005 (R17), um teste com duas threads e barreira, mantido só se estável.

## R13 — Uma consulta da jornada, sem modelo de tela

- **Decisão**: `situacao_da_jornada(participacao, *, agora=None) -> SituacaoDaJornada`,
  que lê a Participação do banco, a Versão (R3) e as Respostas uma vez e devolve um valor
  imutável com: `participacao`, `concluida_em`, `passagens`, `finalizada`,
  `secao_atual`, `respostas` (todas as atuais, da 005), `fora_do_percurso`,
  `impedimentos` (violações que impediriam concluir agora: coleta e pendências),
  `admite_escrita` e a propriedade `pode_concluir`. Estrutura não suportada é rejeição
  explícita (`ESTRUTURA_NAO_SUPORTADA`), como na conclusão.
- **Rationale**: uma função responde todas as perguntas de FR-047 sem recalcular a mesma
  coisa em funções separadas (pedido do solicitante). Para Participação concluída, o
  percurso derivado é o final, `fora_do_percurso` é vazio (R7) e `impedimentos` é vazio.
  O valor é de leitura, como `Elegibilidade` (004); não é ViewModel, não traz texto de
  tela nem progresso (FR-049).
- **Alternativas rejeitadas**: `reconstruir_percurso`, `pendencias`, `proxima_secao`
  como funções públicas independentes (recalculariam o mesmo percurso); campo
  "estrutura suportada" no resultado (o resultado não teria percurso válido para
  devolver).

## R14 — Tempo

- **Decisão**: `concluir` e `situacao_da_jornada` recebem `agora: datetime | None`,
  interpretado por `momento_de_referencia` e `estado` da 004, como na 005. Em `concluir`,
  o relógio padrão é lido depois do bloqueio. `concluida_em` recebe esse momento. Os
  testes sempre passam `agora` explícito.
- **Rationale**: sem relógio novo (pedido do solicitante); limites de período idênticos
  aos da 004 (último dia aceito, dia seguinte rejeitado).

## R15 — Testes com a baseline sem publicá-la

- **Decisão**:
  - **testes unitários sem banco** de `percorrer`, com `ConteudoVersao` construído em
    memória por um pequeno auxiliar de teste (Seções, Perguntas, Opções e regras mínimas):
    linear, regra, encaminhamento, ordem, finalização, indeterminado, estrutura não
    suportada, obrigatoriedade;
  - **testes puros sobre a baseline**: `percorrer` aplicado ao `ConteudoVersao` da
    baseline materializada numa transação desfeita (fixture `baseline` da 003; usa o banco
    só para materializar), com `respondidas` montado em memória. Cobrem os 17 percursos
    pelo oráculo `PERCURSOS` de `tests/instrumento/formulario_2024_esperado.py`,
    transcrito da spec da 003, consumido só por testes;
  - **testes de ponta a ponta** com uma cópia da baseline criada por
    `criar_versao_a_partir_de` e publicada **só no banco de teste**, aplicada a uma
    Campanha aberta. A baseline continua RASCUNHO; a cópia é descartada com a transação
    do teste. Um auxiliar preenche as obrigatórias de um percurso escolhido (Q1, Q14,
    Q33, Q46).
- **Rationale**: o oráculo dos 17 percursos já existe e é independente da declaração
  (003 FR-039); os testes puros são rápidos e não dependem de Campanha; os de ponta a
  ponta exercitam conclusão, limpeza e bloqueio na estrutura real da baseline. Publicar
  uma cópia em teste não é publicação institucional (002/DP-001).
- **Alternativa rejeitada**: publicar a própria baseline em teste (a 003 garante que ela
  nunca é publicada; a cópia preserva essa garantia mesmo em teste).

## R16 — Testes de fronteira da 005 que proíbem a conclusão

- **Decisão**: três asserções de testes da 005 descrevem a fronteira "a 005 não conclui"
  e precisam refletir o ponto de extensão previsto por 005 FR-056:
  - `test_participacao_aceitacao.py::test_10_nenhuma_jornada_ou_conclusao_antecipada`:
    retirar `"concluir"`, `"concluida"` e o atributo `"concluida_em"` das listas
    proibidas; manter `"submet"`, `"progresso"`, `"proxima"`, `"obrigat"`, `"naveg"`,
    `"estado"`, `"submetida_em"`;
  - `test_participacao_aceitacao.py::test_campos_dos_modelos_novos`: `Participacao` passa
    a ter `[..., "iniciada_em", "concluida_em"]`;
  - `test_participacao_rascunho.py::test_participacao_parcial_ou_completa_nao_e_conclusao`:
    o conjunto de campos inclui `concluida_em`, e a asserção passa a ser que escrever
    respostas (zero, algumas, todas) deixa `concluida_em` nulo;
  - **(encontrada na implementação)**
    `test_participacao_inicio.py::test_nao_existe_reinicio_nem_tentativa`: exigia que
    `operacoes.__all__` fosse exatamente a lista da 005. A igualdade exata foi mantida,
    com os três nomes da 006 acrescentados (`concluir`, `SituacaoConclusao`,
    `ResultadoConclusao`); continua provando que não há reinício nem tentativa.
- **Rationale**: não é mudança de requisito da 005: a 005 previu exatamente esses três
  acréscimos (FR-056) e proíbe apenas que ela própria conclua. A intenção dos testes
  (nada de conclusão por quantidade de respostas, nada de progresso, submissão ou
  próxima pergunta) é preservada.
- **Alternativa rejeitada**: colocar `concluir` fora de `operacoes.py` só para não tocar
  o teste (criaria um segundo caminho de escrita — R9).

## R17 — Privacidade nos rastros

- **Decisão**: nenhuma das novas funções registra log. `Violacao.detalhe` dos motivos
  novos cita Seção e Pergunta por `id` técnico, nunca valor declarado; a reembalagem das
  violações da 005 (R10) mantém os detalhes da 005, que já não contêm valores (005
  FR-059).
- **Rationale**: FR-046; Constituição, Observabilidade.

## R18 — Leitura histórica sem gate temporal

- **Decisão**: o estado temporal da Campanha (004) é verificado só em criação de
  Participação (005), escrita de Resposta (005) e conclusão em rascunho (006). Ele nunca
  condiciona leitura:
  - `situacao_da_jornada`, `respostas_atuais` e `percorrer` funcionam com a Campanha em
    qualquer estado e em qualquer data;
  - para Participação concluída, `situacao_da_jornada` não chama `estado`:
    `admite_escrita` é falso e `impedimentos` é vazio por causa da conclusão;
  - `concluir` em Participação concluída devolve `JA_CONCLUIDA` antes de consultar a
    Campanha (R9, passo 3);
  - para rascunho, `agora` só afeta `admite_escrita` e o impedimento
    `COLETA_NAO_ADMITIDA`, nunca passagens, pendências ou `fora_do_percurso`.
- **Rationale**: a observação concluída é histórica (Princípio VIII): daqui a anos, a
  mesma Versão e as mesmas Respostas devem reconstruir o mesmo percurso final. A data
  atual não reinterpreta o que foi observado. `percorrer` é puro e não recebe tempo, o
  que torna isso uma propriedade estrutural.
- **Teste**: Participação concluída durante a coleta; consulta com `agora` anos depois do
  encerramento → mesmas passagens, mesmo `concluida_em`, mesmas Respostas; escrita
  continua rejeitada (`PARTICIPACAO_CONCLUIDA`).
- **Alternativa rejeitada**: reaproveitar `admite_escrita` como pré-condição da consulta
  (tornaria a leitura dependente da data).
