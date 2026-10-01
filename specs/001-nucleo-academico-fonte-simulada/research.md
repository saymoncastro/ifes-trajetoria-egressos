# Research: Núcleo acadêmico longitudinal e fonte institucional simulada

**Feature**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md) | **Date**: 2026-09-30

Cada decisão foi tomada pelo critério da Constituição (Princípios XXII e XXIV): a opção
mais simples que implementa corretamente os invariantes da spec e sustenta as próximas
features, sem antecipá-las.

## R1 — Linguagem e framework

- **Decision**: Python 3.13 e Django 5.2 LTS. O núcleo é uma aplicação Django
  monolítica e modular, com um único projeto. **Confirmada pelo solicitante em
  2026-09-30** ([ADR 0001](../../docs/adr/0001-stack-inicial.md), aceito).
- **Rationale**:
  - **Capacidade da equipe** (XXIV): outros sistemas desenvolvidos no Ifes pelo mesmo
    desenvolvedor usam essa combinação com PostgreSQL, pytest, uv e ruff, por exemplo o
    sistema de processo seletivo do Cefor.
  - As features seguintes (jornada pública, gestão de pesquisas e campanhas, exportação
    CSV) são aplicações web com persistência relacional, que o Django atende sem
    infraestrutura adicional. Escolher agora um framework que não as atenda significaria
    reescrever.
  - O 5.2 é LTS, com suporte até abril de 2028. A migração para o próximo LTS é
    rotineira.
- **Alternatives considered**:
  - **Python puro com SQLAlchemy**: menor para a 001, mas obrigaria a montar depois o
    que o Django já entrega (migrações, configuração, camada web) e divergiria da
    prática da equipe.
  - **FastAPI**: orientado a API. A Constituição veda API pública genérica sem caso real.
  - **Java/Spring**: maior custo de estrutura e sem evidência de prática da equipe.

## R2 — Persistência

- **Decision**: PostgreSQL acessado pelo ORM do Django. Os testes também rodam em
  PostgreSQL.
- **Rationale**:
  - A idempotência (FR-031) é garantida por restrições de unicidade no banco. Isso vale
    também sob concorrência, sem depender só de verificação em código.
  - As restrições de integridade (CHECK, FK protegida) ficam no próprio esquema.
  - Rodar os testes no mesmo banco evita duas semânticas de restrição.
  - O PostgreSQL é o banco já operado pela equipe.
- **Alternatives considered**:
  - **SQLite nos testes e PostgreSQL em produção**: diferenças sutis em restrições e
    transações. Para restrições de unicidade, que são o centro desta feature, a
    economia não compensa.
  - **Fonte simulada como única "persistência"**: não atende FR-031. A identidade
    interna precisa sobreviver entre execuções.

## R3 — Forma do contrato da fronteira

- **Decision**:
  - O contrato é um `typing.Protocol` num pacote Python puro, que não importa o Django.
  - Tem **duas operações**: obter pessoa (com suas conclusões reconhecidas) e obter
    conclusão.
  - Os resultados são objetos imutáveis tipados.
  - A falha da fonte é uma **exceção** própria.
  - Detalhes em [contracts/fonte-academica.md](contracts/fonte-academica.md).
- **Rationale**:
  - FR-022 pede comportamento suficiente para localizar a pessoa, obter suas conclusões,
    obter uma conclusão e distinguir os resultados.
  - Localizar a pessoa e obter suas conclusões viram uma operação só. É o que a
    incorporação precisa, e a resposta fica coerente em uma única leitura.
  - Com a falha como exceção, ela nunca é confundida com "inexistente" ou "sem
    conclusões" por descuido de quem chama. Um retorno vazio ou nulo permitiria essa
    confusão (FR-025).
  - O `Protocol` dispensa herança, registro e framework de providers.
- **Alternatives considered**:
  - **Classe base abstrata**: equivalente, mas acopla as implementações por herança sem
    ganho.
  - **Quatro operações separadas, uma por item de FR-022**: mais superfície sem
    consumidor.
  - **Retorno `None` para inexistente**: ambíguo.
  - **Registry/configuração dinâmica de providers**: vedado pelo solicitante e sem
    necessidade, porque só existe uma fonte.

## R4 — Onde se decide "conclusão reconhecida"

- **Decision**: na implementação de cada fonte. O contrato só transporta conclusões
  reconhecidas na operação de pessoa. A operação de conclusão devolve um resultado
  próprio, "registro não reconhecido como conclusão", para os demais registros.
- **Rationale**:
  - O mapeamento de situação acadêmica para conclusão é peculiaridade da fonte
    (Princípio V) e depende de critério institucional (DP-008).
  - O domínio nunca recebe um registro não concluído com forma de conclusão. Por isso
    não há como materializá-lo como egresso por engano (FR-018, FR-019).
- **Alternatives considered**: transportar a situação acadêmica e filtrar no domínio.
  Isso exigiria vocabulário canônico de situações (inexistente; DP-007/008) e poria
  regra acadêmica no núcleo, contra FR-020.

## R5 — Identidade interna

- **Decision**: chave primária UUID gerada pelo NIAE para Pessoa e para Conclusão
  Acadêmica.
- **Rationale**:
  - É estável (FR-008), não deriva de identificador de fonte (FR-001, FR-006) e não é
    sequencial.
  - As próximas features tendem a expor identificadores em links da jornada, e trocar o
    tipo de chave depois, com chaves estrangeiras já existentes, é migração de risco
    (XXVII).
- **Alternatives considered**: inteiro autoincremental, que é simples mas previsível e
  caro de trocar depois.

## R6 — Referência de origem

- **Decision**: colunas `fonte` e `id_externo` na própria tabela de Pessoa e na de
  Conclusão Acadêmica, com unicidade em (`fonte`, `id_externo`). A fonte simulada é
  identificada pelo próprio código de fonte (`simulada`). Não há atributo de domínio
  indicando "mock".
- **Rationale**:
  - Nesta feature cada registro tem exatamente uma referência, e uma tabela separada
    seria abstração para múltiplas fontes que ainda não existem.
  - FR-006 ("não impedir várias referências no futuro") continua atendido: a identidade
    é o UUID, não a referência. Quando houver segunda fonte, mover a referência para
    tabela própria é migração aditiva (criar tabela, copiar, remover colunas).
- **Alternatives considered**:
  - **Tabela `ReferenciaOrigem` 1:N desde já**: rejeitada por YAGNI.
  - **Coluna booleana `fonte_simulada`**: rejeitada após revisão do plan. Mistura uma
    característica do ambiente de desenvolvimento com o modelo institucional, fica
    inútil com a fonte real e é redundante com `fonte`.
  - Se for preciso impedir a fonte simulada em produção, isso é configuração de
    ambiente, não modelo de domínio. Não há ambiente de produção nesta feature.

## R7 — Referência temporal da proveniência

- **Decision**: um único campo, `incorporado_em`: o momento em que o registro foi
  incorporado pela primeira vez.
- **Rationale**:
  - Atende FR-035 com o mínimo.
  - Registrar "última obtenção" exigiria uma escrita a cada leitura idempotente e
    começaria uma trilha que FR-037 veda.
- **Alternatives considered**: `ultima_obtencao_em` e histórico de obtenções. Ficam
  rejeitados até DP-006.

## R8 — Atributo "não informado pela fonte"

- **Decision**:
  - Atributo ausente é `NULL` no banco e `None` no contrato, com semântica documentada
    "não informado pela fonte".
  - Cadeia vazia é proibida por restrição CHECK, para que não exista segunda forma de
    ausência.
  - Nenhum valor padrão.
- **Rationale**: atende FR-010 sem tipo especial e sem valor sentinela.
- **Alternatives considered**: um marcador textual ("não informado") gravado no campo.
  Mistura ausência com valor e contamina buscas e exportações futuras.

## R9 — Referência temporal da conclusão

- **Decision**:
  - Dois campos opcionais: `ano_conclusao` e `data_conclusao`.
  - Uma restrição CHECK garante que, havendo data, o ano é o ano da data.
  - Só ano preenchido indica granularidade anual.
- **Rationale**: preserva a granularidade da fonte sem fabricar precisão (FR-011) e
  continua consultável por ano.
- **Alternatives considered**:
  - **Data com dia/mês fictícios**: viola FR-011.
  - **Texto livre**: perde a consulta por período.

## R10 — Curso, unidade, nível, modalidade, forma de oferta

- **Decision**: texto livre, como entregue pela fonte, sem lista fechada nem código de
  fonte.
- **Rationale**:
  - O vocabulário canônico é DP-007, e códigos de fonte são peculiaridade do adaptador
    (Princípio V).
  - Texto atende os cenários e a "experiência esperada".
- **Alternatives considered**:
  - **Enumerações**: cristalizariam a hipótese de vocabulário (XXIX).
  - **Tabelas de domínio (Curso, Unidade)**: entidades sem consumidor.

## R11 — Divergência entre leituras da mesma fonte

- **Decision**:
  - A incorporação compara o que a fonte devolve com o que já foi incorporado.
  - Diferenças viram itens `Divergencia` no **resultado** da incorporação.
  - Os dados incorporados não são alterados nem removidos.
  - Um aviso de log registra tipo, fonte e identificador externo, sem nome.
  - Nada é persistido sobre a divergência.
- **Rationale**: é exatamente o mínimo de FR-033 (não duplicar, não sobrescrever, não
  destruir, sinalizar). O tratamento definitivo é DP-005/DP-006.
- **Alternatives considered**: tabela de inconsistências, fila, painel, aprovação
  humana, event sourcing. Todas foram vedadas pelo solicitante e pela spec.

## R12 — Fonte simulada

- **Decision**:
  - A fonte simulada é uma classe que implementa o contrato sobre registros declarados
    num módulo Python versionado (`cenarios.py`). Cada registro declara explicitamente
    sua situação acadêmica.
  - A classe aceita, opcionalmente, outro conjunto de registros. Os testes usam isso
    para simular mudanças da fonte, sem alterar o conjunto canônico.
  - A falha (Cenário H) é provocada por um parâmetro explícito de construção.
- **Rationale**:
  - Dados como código tipado dispensam formato, parser e validação de esquema e
    continuam revisáveis (SC-009).
  - A fonte simulada contém um mapeamento real de situação para reconhecimento,
    exatamente como fará um adaptador real (R4).
- **Alternatives considered**:
  - **JSON/YAML**: exige carregador e validação.
  - **Banco com dados simulados**: acopla a fonte simulada à persistência do núcleo.
  - **Identificador "mágico" para provocar falha**: comportamento escondido nos dados.

## R13 — Verificação de substituibilidade

- **Decision**:
  - Uma suíte de contrato é parametrizada sobre duas implementações: a fonte simulada e
    uma segunda implementação mínima, **escrita só nos testes**, com outro conjunto
    fictício e estrutura interna diferente.
  - Os testes de incorporação também rodam com as duas.
- **Rationale**: demonstra FR-024 e SC-006 sem criar em produção uma segunda fonte que
  ninguém usa.
- **Alternatives considered**:
  - **Usar só a fonte simulada**: não prova independência da implementação.
  - **Segunda fonte em produção**: código sem consumidor.

## R14 — Disparo da incorporação e acesso pelos consumidores

- **Decision**:
  - A incorporação é uma função de serviço que recebe a fonte como argumento.
  - Não há comando, endpoint, job ou agendamento.
  - Os consumidores leem Pessoa e Conclusões pelos modelos e suas relações.
- **Rationale**:
  - O disparo é DP-006.
  - Receber a fonte como argumento basta para substituí-la, sem container de injeção.
  - Uma camada de consultas ou repositórios genéricos seria indireção sem ganho num
    projeto Django.
- **Alternatives considered**:
  - **Comando de gestão**: sem consumidor. O quickstart usa testes e shell.
  - **Repository pattern**: vedado sem necessidade.
  - **API**: vedada.

## R15 — Componentes Django não usados

- **Decision**: `INSTALLED_APPS` contém apenas o app do núcleo acadêmico. Ficam de fora
  admin, auth, sessions, DRF, Celery e cache.
- **Rationale**:
  - Sem interface, sem autenticação e sem CRUD nesta feature (FR-030 e Out of Scope).
  - Não registrar os modelos no admin evita a edição manual que FR-030 proíbe.
- **Alternatives considered**: o projeto-padrão do `startproject`. Ele traz componentes
  sem uso, que as features que precisarem deles acrescentam.

## R16 — Ferramentas

- **Decision**: `uv` (ambiente e lock), `ruff` (lint/format), `pytest` com
  `pytest-django`, `psycopg` 3. Sem outras dependências de execução.
- **Rationale**: prática da equipe (R1), dependências mínimas e lock reprodutível.
- **Alternatives considered**: pip/requirements e unittest. Funcionam, mas divergem do
  padrão da equipe sem vantagem.
