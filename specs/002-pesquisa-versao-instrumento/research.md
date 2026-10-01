# Research: Pesquisa, versão e estrutura do instrumento

**Feature**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md) | **Date**: 2026-10-01

Critério de todas as decisões (Princípios XXII e XXIV): a opção mais simples que garante
os invariantes da spec, sobretudo a imutabilidade da Versão publicada (Princípio VIII,
NON-NEGOTIABLE), sem antecipar Campanha, Participação, Resposta ou editor.

O Technical Context não tem itens em aberto: a stack está fixada pelo
[ADR 0001](../../docs/adr/0001-stack-inicial.md). As decisões abaixo tratam da
representação do domínio.

## R1 — Stack e dependências

- **Decision**: a mesma da Feature 001 (Python 3.13, Django 5.2 LTS, PostgreSQL 16+,
  uv, pytest, pytest-django, ruff). Nenhuma dependência nova.
- **Rationale**: o ADR 0001 já está aceito. A feature é modelagem relacional com
  restrições de integridade, que a stack atende sem acréscimo.
- **Alternatives considered**: biblioteca de "form schema" ou JSON Schema. Seria um form
  builder genérico, vedado pelo Princípio XXIII.

## R2 — Fronteira do módulo

- **Decision**: novo app Django `trajetoria.instrumento`, sem nenhuma importação de
  `trajetoria.academico` nem de `trajetoria.fonte_academica`.
- **Rationale**:
  - FR-065 exige independência de Pessoa e Conclusão Acadêmica. Um app separado torna
    isso verificável (nenhum import, nenhuma FK).
  - Campanha, Participação e Resposta terão apps próprios e dependerão deste, não o
    contrário.
- **Alternatives considered**:
  - **Acrescentar ao app `academico`**: mistura domínios distintos (Princípio VII).
  - **Um app por entidade (pesquisa, versão, estrutura)**: fragmentação sem ganho; as
    entidades só fazem sentido juntas.

## R3 — Identidade dos elementos

- **Decision**: chave primária UUID gerada pelo NIAE em Pesquisa, Versão, Seção,
  Pergunta e Opção.
- **Rationale**:
  - FR-028 e FR-041 exigem identidade independente de texto e posição.
  - Respostas futuras referenciarão Pergunta e Opção; exportações futuras precisarão de
    identificadores estáveis e não previsíveis. Trocar o tipo de chave depois, com FKs
    existentes, é migração de risco (XXVII).
  - Mantém o padrão da 001 (R5 da 001).
- **Alternatives considered**:
  - **Inteiro autoincremental**: previsível e caro de trocar.
  - **Código legível por elemento (por exemplo, "Q33")**: seria atributo sem consumidor
    nesta feature (FR-033) e convidaria a reutilização entre Versões (FR-032).
  - **Texto da Opção como identidade**: vedado por FR-041.

## R4 — Representação da ordem

- **Decision**:
  - Cada Seção, Pergunta e Opção tem `posicao` inteira positiva.
  - Unicidade de (`versao`, `posicao`), (`secao`, `posicao`) e (`pergunta`, `posicao`)
    no banco, com verificação **adiada para o fim da transação** (`DEFERRABLE INITIALLY
    DEFERRED`).
  - Inclusão exige posição explícita e livre. Reordenação recebe a lista completa dos
    elementos na nova ordem e renumera 1..n.
  - Lacunas são permitidas (por exemplo, após remoção): a ordem continua total e
    inequívoca.
- **Rationale**:
  - FR-045 a FR-047: ordem explícita, independente de identificador e de criação, sem
    empate.
  - A verificação adiada permite trocar posições dentro de uma transação sem estados
    intermediários inválidos.
  - Exigir a lista completa na reordenação impede ordem parcial ou ambígua.
- **Alternatives considered**:
  - **Ordem por data de criação ou por id**: vedada (FR-046).
  - **Lista encadeada (anterior/próximo)**: consultas e integridade mais complexas.
  - **Posições fracionárias ou cadeias lexicográficas**: úteis para edição colaborativa
    intensa, que está fora do escopo.
  - **Renumerar automaticamente a cada inclusão**: esconde o efeito da operação; a spec
    pede posição explícita.

## R5 — Configuração de escala

- **Decision**: quatro colunas opcionais na própria Pergunta (`escala_inicio`,
  `escala_fim`, `escala_rotulo_inicio`, `escala_rotulo_fim`), com CHECK:
  - pergunta de escala ⇒ início e fim preenchidos e início < fim;
  - outro tipo ⇒ as quatro colunas nulas;
  - rótulos, quando presentes, não vazios.
- **Rationale**: a escala é 1:1 com a Pergunta e tem quatro valores. CHECK no próprio
  registro garante FR-038 e FR-058 (c, d) no banco, sem junção.
- **Alternatives considered**:
  - **Tabela própria de configuração de escala**: entidade 1:1 sem ganho.
  - **Escala como Opções numeradas**: confundiria escala com escolha (FR-038 veda Opções
    em escala) e perderia o significado dos limites.
  - **JSON de configuração por tipo**: abre caminho a "configuração arbitrária" (XXII) e
    tira a integridade do banco.

## R6 — Regra de navegação condicional

- **Decision**: a regra é representada **na própria Opção** por duas colunas:
  `regra_destino` (FK opcional para Seção) e `regra_finaliza` (booleano), com CHECK
  impedindo os dois ao mesmo tempo. Sem nenhum dos dois, a Opção não tem regra.
- **Rationale**:
  - FR-052 ("no máximo uma regra por Opção") e FR-058 (f) ("Opção da própria Pergunta")
    passam a valer **por construção**: não existe forma de gravar duas regras para a
    mesma Opção nem regra com Opção de outra Pergunta.
  - FR-051 (regra associada à Pergunta e à Opção, não à Seção) é satisfeito: a Opção
    pertence à Pergunta.
  - A operação de domínio continua recebendo (Pergunta, Opção, destino), como na spec,
    e rejeita explicitamente Opção de outra Pergunta.
- **Alternatives considered**:
  - **Tabela `RegraNavegacao` (pergunta, opcao, destino)**: exigiria unicidade por Opção
    e verificação de que a Opção pertence à Pergunta, que o banco não expressa sem FK
    composta. Mais estrutura para o mesmo significado.
  - **Regra na Seção (como o Google Formulários)**: fossiliza o acidente que a spec
    contraria FR-051.
  - **Expressões de condição**: vedadas (FR-056).

## R7 — Encaminhamento de Seção

- **Decision**: FK opcional da Seção para outra Seção (`encaminhamento`). Ausente =
  fluxo padrão.
- **Rationale**: FR-049 com o mínimo de estrutura. É usado só onde a ordem não basta
  (convergência dos ramos).
- **Alternatives considered**:
  - **Condição de exibição de Seção**: paradigma diferente, vedado por FR-057.
  - **Encaminhamento obrigatório em toda Seção**: redundante com a ordem (spec, item 17
    da descrição).

## R8 — Caminho único de escrita e rejeições explícitas

- **Decision**:
  - Toda escrita passa por funções de domínio em `trajetoria/instrumento/operacoes.py`
    (contrato em [contracts/operacoes.md](contracts/operacoes.md)).
  - Cada função abre uma transação, bloqueia a linha da Versão (R12), verifica as regras
    pertinentes **àquela operação** e só então grava.
  - Violação gera a exceção `OperacaoRejeitada`, com uma tupla de `Violacao(motivo,
    elemento, detalhe)`. `Motivo` é uma enumeração fechada que corresponde a FR-058,
    FR-059 e FR-061.
  - A transação garante que nenhuma rejeição deixe alteração parcial (FR-060).
- **Rationale**:
  - FR-060 pede motivo explícito e elemento envolvido; mensagens de erro do banco não
    servem para isso.
  - Exceção (e não resultado) porque a rejeição precisa desfazer a transação e não pode
    ser ignorada por descuido de quem chama.
  - Uma enumeração fechada de motivos dá aos testes um critério objetivo (SC-004) sem
    criar framework de validação.
- **Alternatives considered**:
  - **`Model.clean()`/`full_clean()`**: não é chamado por `save()` nem por operações em
    lote; regras entre registros ficariam espalhadas.
  - **Serializers (DRF) ou forms**: camada de interface, que não existe nesta feature.
  - **Motor genérico de validação declarativa**: vedado pela spec (FR-060).
  - **Retornar resultado em vez de exceção**: exigiria que quem chama desfizesse a
    transação manualmente.

## R9 — Imutabilidade da Versão publicada garantida pela aplicação

- **Decision**:
  - A imutabilidade da Versão publicada e a proibição de referências entre Versões são
    garantidas **pelas operações de `operacoes.py`**, que são o único caminho de escrita
    suportado (R8): toda operação bloqueia a Versão e rejeita com `VERSAO_PUBLICADA` se
    ela estiver publicada.
  - Nenhuma operação volta uma Versão a `RASCUNHO`, muda sua Pesquisa ou a exclui; não
    há parâmetro de estado em nenhuma operação.
  - Testes de invariante cobrem, por operação, cada tentativa de alterar Versão
    publicada e seus elementos (SC-002), e a cópia independente (SC-003).
  - **Nenhum gatilho, permissão de banco ou hook de modelo** (`save()`/`delete()`
    sobrescritos, sinais).
- **Rationale**:
  - Hoje o Trajetória Ifes é o único escritor legítimo da base. Não há importação
    externa nem outro sistema gravando nas tabelas do instrumento.
  - Gatilhos espalhariam regra de domínio entre Python e SQL, complicariam migrações e
    dificultariam a evolução do modelo nas primeiras features (XXII).
  - A Constituição exige preservação histórica, não um mecanismo específico.
  - Escrita direta no PostgreSQL (`UPDATE` manual) está fora do que a 002 protege.
- **Alternatives considered**:
  - **Gatilhos PL/pgSQL como segunda barreira**: propostos no ADR 0002 e **rejeitados
    nesta fase** pelo solicitante. Podem ser reconsiderados se surgirem múltiplos
    escritores da base, operações externas ao domínio da aplicação ou requisito
    institucional de defesa em profundidade.
  - **Sobrescrever `save()`/`delete()` dos modelos**: dá falsa sensação de proteção (não
    cobre `update()` em lote) e duplica a verificação das operações.
  - **Permissões de banco por papel**: dependem de perfis inexistentes (DP-001).
  - **Congelar a Versão publicada como documento JSON**: duplicaria o conteúdo e Respostas
    futuras perderiam FK para Pergunta e Opção.
- **Registro**: [ADR 0002](../../docs/adr/0002-imutabilidade-versao-publicada.md),
  rejeitado nesta fase.

## R10 — Representação relacional em vez de documento

- **Decision**: Pesquisa, Versão, Seção, Pergunta e Opção são tabelas relacionais
  normalizadas. Não há campo JSON com estrutura do instrumento.
- **Rationale**:
  - Respostas, exportações e indicadores futuros referenciarão Pergunta e Opção com
    integridade referencial (Princípio XVIII).
  - Restrições de ordem, tipo e escala ficam no banco.
- **Alternatives considered**: documento JSON por Versão. Simplifica a cópia, mas perde
  integridade, FKs e consultas, e torna a validação um esquema genérico.

## R11 — Nova Versão a partir de existente

- **Decision**: cópia profunda, numa transação, com mapa de identidades antigas para
  novas:
  1. cria a Versão (RASCUNHO, `origem` = Versão copiada) com os textos da Versão;
  2. cria todas as Seções sem encaminhamento;
  3. cria Perguntas e Opções sem regra;
  4. preenche encaminhamentos e regras traduzindo cada destino pelo mapa.
- **Rationale**:
  - FR-020 a FR-022: elementos próprios, referências internas apontando para a nova
    Versão, origem intocada.
  - Preencher referências depois evita depender da ordem de criação.
  - `origem` atende FR-023 sem correspondência entre elementos (DP-006).
- **Alternatives considered**:
  - **Copy-on-write (compartilhar elementos até a primeira alteração)**: viola FR-021.
  - **Correspondência elemento a elemento (`copiado_de`)**: vedada até DP-006.

## R12 — Concorrência entre edição e publicação

- **Decision**: toda operação de escrita bloqueia a linha da Versão
  (`SELECT … FOR UPDATE`) antes de verificar e gravar.
- **Rationale**: impede que uma edição e a publicação da mesma Versão se cruzem, o que
  poderia publicar conteúdo não verificado ou alterar Versão recém-publicada. O custo é
  irrelevante no volume esperado. Sem gatilhos (R9), é o bloqueio que mantém a
  garantia da aplicação também sob concorrência.
- **Alternatives considered**: nível de isolamento `SERIALIZABLE` global; mais amplo que
  o necessário.

## R13 — Leitura do conteúdo

- **Decision**: a função `conteudo_da_versao(versao)` devolve uma árvore imutável de
  `dataclasses` (`ConteudoVersao` → `ConteudoSecao` → `ConteudoPergunta` →
  `ConteudoOpcao`), com todos os atributos, identidades e referências, na ordem das
  posições. Contrato em [contracts/conteudo.md](contracts/conteudo.md).
- **Rationale**:
  - FR-064 pede o conteúdo completo, suficiente para deduzir os percursos.
  - Igualdade estrutural de dataclasses dá aos testes um critério direto de
    "integralmente idêntico" (SC-002, SC-003).
  - É a forma que Campanha, jornada e exportação consumirão, sem conhecer as tabelas.
  - A lista de Versões de uma Pesquisa (FR-063) é lida diretamente pelos modelos, como
    na 001.
- **Alternatives considered**:
  - **Ler sempre pelos modelos**: comparações frágeis e consultas espalhadas.
  - **Serialização para JSON**: formato de interface, sem consumidor nesta feature.

## R14 — Percurso de Seções: semântica de destino documentada, não executada

- **Decision**:
  - O contrato documenta só o **destino** depois de cada Seção (regra acionada,
    encaminhamento ou fluxo padrão), em
    [contracts/conteudo.md](contracts/conteudo.md#percurso-de-seções).
  - O **momento** de aplicação da regra dentro da Seção não é modelado: nenhum
    atributo, enumeração ou estratégia (FR-053).
  - Não há função de produção que execute a navegação. Os testes têm um auxiliar que
    enumera os percursos de Seções de uma Versão para verificar SC-001, US7 e US8, e que
    só aceita Versões com no máximo uma pergunta com regras por Seção (como o instrumento
    atual), já que a prevalência entre duas regras na mesma Seção depende do momento de
    aplicação.
- **Rationale**:
  - A spec veda executar a navegação (FR-056) e deixa o momento de aplicação para a
    Feature 003 (representação de cada ramificação) e para a jornada (execução).
  - Modelar o destino no nível da Seção basta para deduzir todos os percursos de Seções
    do instrumento atual sem decidir o caso Q46–Q48.
- **Alternatives considered**:
  - **Efeito imediato após a pergunta**: proposto na primeira versão da spec e
    rejeitado pelo solicitante, porque presumiria uma intenção metodológica não
    confirmada (Q47 e Q48 sumiriam do percurso).
  - **Efeito ao sair da Seção**: fossilizaria a limitação do Google Formulários.
  - **Atributo configurável de momento** (`AFTER_QUESTION`, `END_OF_SECTION`): abstração
    sem decisão que a sustente; vedada por FR-053.
  - **Função `proximo_passo()` em produção**: código sem consumidor que anteciparia a
    jornada.

## R15 — Verificação de "destino posterior"

- **Decision**: na publicação, cada encaminhamento e cada regra com destino é verificado
  comparando a posição da Seção de destino com a da Seção de origem. Nenhuma análise de
  grafo.
- **Rationale**: FR-055 e FR-059 (d). Com todos os destinos posteriores, todo percurso
  avança e termina, o que torna desnecessária a detecção de ciclos.
- **Alternatives considered**:
  - **Detecção de ciclos e de alcançabilidade**: mais complexa e não exigida pela spec.
  - **Verificar na própria edição**: impediria reordenações temporárias legítimas em
    rascunho (spec, Edge Cases).

## R16 — Textos e ausência

- **Decision**:
  - Textos em `TextField`, preservados **exatamente** como recebidos (sem `strip`, sem
    normalização de grafia).
  - Ausência = `NULL`; cadeia vazia proibida por CHECK (como R8 da 001).
  - As operações rejeitam texto obrigatório vazio ou só com espaços (FR-058 k).
  - Unicidade de texto de Opção por Pergunta é comparação exata.
- **Rationale**: FR-039 e Edge Cases ("Corcordo totalmente" preservado). Normalizar seria
  alterar o instrumento.
- **Alternatives considered**: normalizar espaços e maiúsculas na comparação de
  unicidade. Seria regra de equivalência textual não pedida.

## R17 — Componentes não adotados

- **Decision**: nenhuma interface, admin, comando de gestão, endpoint ou API. O app não é
  registrado no admin. `INSTALLED_APPS` ganha apenas `trajetoria.instrumento`.
- **Rationale**: a spec exclui editor e CRUD, e a publicação não deve ser exposta antes
  de DP-001 (spec, "Tensões").
- **Alternatives considered**: admin do Django como editor provisório. Exporia a
  publicação e a edição a quem tiver acesso técnico (Princípio X).

## R18 — Nome da Pesquisa sem unicidade

- **Decision**: o nome administrativo da Pesquisa não tem restrição de unicidade.
- **Rationale**: a spec não define essa regra. A identidade é o UUID, e o nome pode ser
  renomeado livremente (FR-003).
- **Alternatives considered**: nome único. Seria regra administrativa não pedida.
