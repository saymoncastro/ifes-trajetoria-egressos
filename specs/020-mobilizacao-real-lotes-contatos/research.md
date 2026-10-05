# Research — Feature 020: mobilização real, Lotes e contatos do egresso

**Data**: 2026-10-05 · **Spec**: [spec.md](spec.md) ·
**Auditoria**: [2026-10-04-mobilizacao-real-lotes-contatos](../../docs/auditorias/2026-10-04-mobilizacao-real-lotes-contatos.md)

Nenhuma decisão aqui depende de dado real. O que depende da fonte real é Gate A e não foi
pesquisado.

---

## R1 — Onde mora o contato e como é identificado

**Decisão**: app novo `trajetoria/contato/`, com um model `ContatoDaPessoa`:

- FK para `Pessoa` com `PROTECT` e `related_name="+"`;
- campos `canal` (só `EMAIL`), `valor`, `origem` (`FONTE_ACADEMICA` | `EGRESSO`), `fonte` e
  `posicao` (obrigatórios só na origem fonte) e `obtido_em`.

`Pessoa` não ganha campo nem relação reversa.

**Justificativa**:

- Princípios III e IV: o contato é lateral à Pessoa.
- Segue o padrão do app `contexto_trajetoria` da 021: app próprio, que nenhum app de
  001, 018 ou 019 importa.
- `related_name="+"` evita que `pessoa.contatos` apareça em código de outras features.

**Alternativas**:

- Pôr no app `comunicacao`: mistura cadastro de contato com transporte, e a página do
  egresso passaria a importar o app de envio.
- Campo em `Pessoa`: vedado (FR-001).

## R2 — Idempotência da carga e "observação mais recente"

**Problema**: a spec pede a política "primeiro na ordem do adaptador, na observação mais
recente" (FR-008) e uma carga idempotente (FR-002). Unicidade por valor não basta:

- se a fonte reordena os mesmos e-mails, a mudança de ordem se perde;
- se a fonte informa `[antigo, novo]`, o registro novo ficaria "mais recente" que o
  antigo, contrariando a ordem declarada pelo adaptador.

**Decisão**: a carga grava uma **observação**, ou seja, a lista ordenada inteira, com um
único `obtido_em`. Isso só acontece quando a lista difere da última observação gravada para
aquela Pessoa e fonte. Os registros têm `posicao` 0..n-1.

- Unicidade: `(pessoa, fonte, obtido_em, posicao)` quando a origem é fonte.
- "Observação mais recente": os registros de `max(obtido_em)` daquela Pessoa e fonte.
- Repetir a mesma lista não grava nada (idempotência).
- Um valor pode reaparecer em observações diferentes. Isso é histórico, não duplicata.
- **Lista vazia** não grava nada e não apaga nada. A observação anterior continua
  utilizável. É hipótese: o Gate A dirá se "sumiu da fonte" deve invalidar. Fica registrado
  em DP-1601.

**Lado do egresso**: um informe igual ao seu contato `EGRESSO` mais recente, após
normalização, não grava. Um valor diferente grava. Voltar a um valor antigo grava, porque
é um novo fato.

**Precisão na spec**: FR-002 passa a dizer "mesma observação" em vez de "mesmo valor".

**Alternativas**:

- Tabela `ObservacaoDeContatos` separada: uma entidade a mais sem consumidor, porque o
  `obtido_em` comum já agrupa.
- Sobrescrever a posição: viola a imutabilidade.

## R3 — Fronteira de contatos da fonte (precedente 021 FR-071)

**Decisão**:

- **Contrato puro** em `fonte_academica/contatos_da_fonte.py`:
  - `FonteDeContatos` (Protocol) com `codigo` e
    `obter_emails(id_externo_pessoa) -> tuple[str, ...]`;
  - exceção `ContatosIndisponiveis`.
- **Simulada** em `fonte_academica/contatos_simulados.py`. Lê o mapa `EMAILS` de
  `fonte_academica/cenarios.py`, que é o mapa de `comunicacao/contatos.py` movido para lá e
  acrescido de uma Pessoa com dois e-mails.
- **Carga** em `contato/carga.py`, no padrão de `contexto_trajetoria/carga.py`:
  - consulta fora da transação;
  - indisponível não grava nada;
  - resultado tipado `CARREGADO | INDISPONIVEL | SEM_EMAIL | INALTERADO`;
  - log só com categoria e código da fonte.
- **Preparo da demonstração**: `_carregar_contatos` roda depois de `_carregar_contextos`,
  um *savepoint* por Pessoa, e uma falha não interrompe o resto.

**Justificativa**: `obter_pessoa()` serve à 018. O contato não pode entrar no caminho da
identidade nem da incorporação.

**Alternativas**: estender `PessoaEncontrada` (versão inicial da spec) foi rejeitado; ver
a auditoria, §5.3.

## R4 — Normalização e validação do e-mail

**Decisão**: uma única função, `contato/endereco.py: normalizar_email(valor)`:

- remove espaços externos;
- recusa CR, LF, `<>,;`, espaços internos e tabulação;
- aplica `django.core.validators.validate_email`;
- põe o domínio em minúsculas e preserva a parte local;
- limita o tamanho a 254.

A mesma função serve à carga (valor inválido é ignorado e contado, sem log do valor), à
página do egresso e à política (FR-008, segunda barreira). A restrição a `example.invalid`
**não** está nela: pertence ao modo demonstração do transporte (R8).

## R5 — Lote: modelo, congelamento e concorrência

**Decisão**: app novo `trajetoria/mobilizacao/` com dois models.

`LoteDeMobilizacao`:

- `campanha` (FK `PROTECT`, `related_name="+"`) e `nome`;
- filtros `unidades` (ArrayField ou NULL), `nivel`, `ano_minimo`, `ano_maximo` e `curso`
  (NULL = sem filtro);
- escopo aplicado: `escopo_institucional` e `escopo_unidades`;
- `excluidas_por_mobilizacao`, `confirmado_em` e `operador`.

`MembroDoLote`:

- `lote` e `campanha` (cópia da FK do Lote, R6);
- `pessoa` e `contato` (FK `PROTECT`, nulo quando sem contato);
- `situacao`, `tentativa_iniciada_em` e `resultado_em`.

**Confirmação**:

- Uma transação com `select_for_update()` na linha da Campanha, que serializa as
  confirmações da mesma Campanha.
- Recalcula a seleção (FR-017), cria o Lote e cria os membros em `bulk_create`.
- Duas confirmações concorrentes da mesma Campanha são serializadas, e a segunda vê os
  membros da primeira e os exclui.

**Prévia**: GET com filtros na query string, que não contém dado pessoal. Ela usa a mesma
função de seleção, sem gravar nada.

**Alternativas**:

- Rascunho persistido: vetado pela E3.
- Lock consultivo (*advisory lock*) do PostgreSQL: equivalente, mas menos legível que
  travar a linha da Campanha, que já existe.

## R6 — Garantia de no máximo uma abordagem por Pessoa e Campanha

**Decisão**: `MembroDoLote.campanha` repete a Campanha do Lote. Essa cópia é verificada na
criação e nunca muda. Ela permite a restrição parcial:

```text
UniqueConstraint(fields=["campanha", "pessoa"],
                 condition=~Q(situacao="SEM_CONTATO"),
                 name="membro_uma_abordagem_por_campanha")
```

`SEM_CONTATO` é atribuída na criação e é final, então a condição é estável. O banco
garante FR-024 e FR-025 mesmo sob concorrência ou erro de código. *(Analyze de
2026-10-05.)* A verificação adicional antes de cada tentativa foi retirada: com a
restrição, o estado que ela procuraria não pode existir.

**Justificativa**: a duplicidade é o risco mais caro (SC-001). Uma restrição declarativa
custa uma coluna.

**Alternativa**: só a verificação em código, que deixaria o invariante sem garantia
estrutural.

## R7 — Envio retomável e "resultado incerto"

**Decisão**: `enviar_lote(lote_id, operador)` executa, nesta ordem:

1. revalida capacidade, escopo, estado `EM_COLETA`, modo de transporte e origem da base;
2. seleciona até `TRAJETORIA_LOTE_ENVIO_POR_ACAO` membros `NAO_TENTADO` (padrão 100), em
   ordem de `pk`;
3. para cada um:
   - **(a)** numa transação curta, trava o membro (`select_for_update(skip_locked=True)`),
     confirma que ainda está `NAO_TENTADO`, grava `EM_TENTATIVA` e
     `tentativa_iniciada_em`, e faz o commit;
   - **(b)** monta a mensagem e chama `send()` fora de transação;
   - **(c)** grava `SUBMETIDO_AO_TRANSPORTE` ou `FALHA_DE_TRANSPORTE` e `resultado_em`;
4. devolve os totais.

- Erro inesperado entre (a) e (c), inclusive a morte do processo, deixa o membro em
  `EM_TENTATIVA`. Ele é apresentado como "resultado incerto" e nunca volta a
  `NAO_TENTADO`.
- Duas ações concorrentes sobre o mesmo Lote não pegam o mesmo membro (`skip_locked` e a
  checagem de estado).
- "Continuar envio" é a mesma ação.

**Justificativa**: o registro antes do envio é o único jeito honesto de não reenviar sem
saber (FR-028). O limite por ação mantém a requisição curta sem fila (FR-029).

**Alternativas**:

- Gravar só depois do envio: uma queda reenviaria.
- Fila ou worker: vetado (FR-029).

## R8 — Fronteira de transporte e modos

**Decisão**: `comunicacao/transporte.py` substitui `TransporteLocal` por
`transporte_de_envio()`, que devolve um objeto com `modo` e `conexao()`.

| Modo | Condição exclusiva | Barreiras |
| --- | --- | --- |
| `teste` | `TRAJETORIA_COMUNICACAO_TESTE is True` e backend locmem | Iguais às da 016. |
| `demonstracao` | `TRAJETORIA_DEMONSTRACAO` ligado, `TRAJETORIA_ENVIO_REAL` desligado, SMTP em loopback:1025 sem credenciais nem TLS | As barreiras da 016: remetente, destinatários e URL. |
| `real` | `TRAJETORIA_ENVIO_REAL == "1"`, `TRAJETORIA_DEMONSTRACAO` desligado | SMTP com `EMAIL_USE_TLS` ou `EMAIL_USE_SSL`, usuário e senha não vazios, `TRAJETORIA_REMETENTE_INSTITUCIONAL` válido, `TRAJETORIA_URL_ENTRADA` em `https` sem query nem fragmento, `base_somente_simulada()` falso. |

- Qualquer outra combinação recusa com uma categoria e nenhuma conexão.
- **Consequência estrutural honesta**: com a demonstração desligada,
  `ModoDemonstracaoMiddleware` responde 404 a tudo. O modo real **não é alcançável pela
  interface** nesta base. Ele existe só como validação na fronteira, coberta por testes
  com `override_settings`.
- Torná-lo alcançável exige operadores reais (010/DP-1001) e o Gate B. Isso é intencional
  e cumpre "capacidade desativada".

**Renderer**:

- `renderizar_convite` ganha o parâmetro `modo`, que escolhe entre dois pares de templates
  fixos: `convite.txt/html` (demonstração, inalterado) e `convite_real.txt/html`
  (provisório, com o marcador visível "Texto provisório — pendente de aprovação
  institucional", DP-2003).
- `validar_conteudo` recebe a URL permitida do modo.

**Alternativas**:

- Integração com API de provedor: depende do Gate B.
- Configuração genérica de "canais": vetada.

## R9 — Controles de proteção do e-mail legível (E2, só demonstração)

**Decisão**: armazenar `valor` em texto, com estes controles, cada um verificável:

| # | Controle | Verificação |
| --- | --- | --- |
| C1 | Só duas operações leem `valor`: a confirmação do Lote, para escolher a referência, e o envio, para endereçar. Mais a gravação (carga e página do egresso). | Teste AST: nenhum módulo fora de `contato/` e `mobilizacao/operacoes.py` referencia `.valor` de `ContatoDaPessoa`. |
| C2 | Nenhuma tela administrativa ou do egresso exibe endereço. | Testes de resposta HTML com marcador de endereço fictício. |
| C3 | Nenhum endereço em logs, mensagens de erro, URLs, sessão e cache. | Extensão de `tests/acesso/test_vazamento.py` (*caplog*, requisições, sessão, cache). |
| C4 | Nenhum endereço em 011, 012 e 013. | Extensão dos testes de fronteira de `analitico`, `exportacao` e `acompanhamento`. |
| C5 | O app `contato` não é importado por `academico`, `acesso`, `declaracao`, `narrativa`, `video`, `participacao`, `analitico` nem `exportacao`. | Teste AST de dependência. |
| C6 | `ContatoDaPessoa` e `MembroDoLote` fora do admin e de qualquer serialização. | Inspeção e teste de ausência de registro no admin; o projeto não tem admin. |
| C7 | Dados só fictícios: na demonstração, a carga e a página recusam base não simulada, e o transporte só aceita `example.invalid`. | Testes de origem e de transporte. |

**Revisão obrigatória antes do uso real (DP-2010)**: a decisão é registrada pela DTI e pelo
encarregado antes de ativar o modo real. Se a escolha for criptografia de aplicação, o
ponto de troca é localizado:

- `valor` passa a ser cifrado com Fernet (padrão da ADR 0005), com chave própria;
- a leitura fica concentrada nas duas operações de C1;
- a idempotência do egresso (R2) passa a usar HMAC do valor normalizado.

Nenhum outro módulo muda. O plan **não** implementa isso agora.

## R10 — Governança e rotas

**Decisão**:

- **Regras novas** em `governanca/regras.py`, todas `CPAEG|CSAEG` na demonstração:
  `pode_consultar_lotes`, `pode_preparar_lote` e `pode_enviar_lote`.
- `pode_simular_comunicacao` é removida, e o teste de enumeração das regras é atualizado.
- O escopo reutiliza `escopo_de_acompanhamento`.
- **Visibilidade**: a CPAEG vê todos. A CSAEG vê Lotes com `escopo_institucional=False` e
  `escopo_unidades ⊆` suas unidades.
- **Lote preparado por CSAEG**: o filtro de unidades é obrigatório e contido no escopo; o
  servidor recusa o contrário.

**Rotas** em `acompanhamento/urls.py`, com o marcador `lotes` no decorator `@lotes`:

| Método | Rota | Ação |
| --- | --- | --- |
| GET | `campanhas/<uuid>/lotes/` | Lista e prévia (filtros na query) |
| POST | `campanhas/<uuid>/lotes/confirmar/` | Confirma o Lote |
| GET | `campanhas/<uuid>/lotes/<uuid>/` | Detalhe e contagens |
| POST | `campanhas/<uuid>/lotes/<uuid>/enviar/` | Envia e continua o envio |

- As rotas `comunicacao/` e `comunicacao/simular/` saem.
- `test_toda_rota_exige_o_gate_de_acompanhamento` passa a esperar `lotes` para caminhos
  com `/lotes/`.

Cada operação revalida no seu próprio momento (como a 016 FR-024).

## R11 — Página do egresso e tela de conclusão (impacto compartilhado)

**Decisão**:

- **Rotas**: `contato/urls.py` com `GET/POST /meu-email/` (`@never_cache`, CSRF). Usa
  `acesso.sessao.pessoa_em_uso`.
  - O teste de fronteira da 018, que hoje só permite `interface/views.py`, passa a permitir
    também `contato/views.py`, apenas `pessoa_em_uso`.
  - Sem Pessoa na sessão, inclusive o declarante, redireciona para `/acesso/`.
- **`concluida.html`**:
  - na ramificação não declarada, mantém `<p><a href="/minha-trajetoria/">Ver minha
    trajetória no Ifes</a></p>` como primeira ação;
  - acrescenta abaixo um parágrafo secundário, com classe de menor destaque, e o link
    "Quer manter seu e-mail atualizado com o Ifes?" para `/meu-email/`;
  - a ramificação declarada não muda.
- **Notas de revisão a aplicar na implementação**:
  - 021 FR-003 ("única ação" → "ação principal") e o docstring de `interface/views.py:
    concluida`;
  - 014 FR-041;
  - teste existente da 021 que verifique "única ação", se houver, ajustado para "primeira
    ação".
- **Depois de salvar ou recusar**:
  - links para `/minha-trajetoria/`, quando `narrativa.consultas.elegivel(pessoa)` for
    verdadeiro, e para `/formacoes/`;
  - `contato` importa só essa função pública da 021;
  - a 021 não importa `contato` (FR-009).
- **Shell**: `interface/base.html`.

## R12 — Retirada da 016

Saem:

- `comunicacao/views.py` e `comunicacao/consultas.py` (público atual);
- `comunicacao/contatos.py`, que vai para `cenarios.EMAILS`;
- `comunicacao/acesso.py` (o decorator `@comunicacao`);
- `operacoes.simular_comunicacao` e os templates `preparar.html` e `resultado.html`;
- o link "Comunicação simulada" do detalhe da Campanha.

Ficam e evoluem: `convite.py` (renderer), `seguranca.py` (validações, separando o que é
da demonstração) e `transporte.py`.

Testes de `tests/comunicacao/`:

| Teste | Destino |
| --- | --- |
| `test_convite*.py`, `test_seguranca.py`, `test_configuracao.py`, `test_falhas.py` | Adaptados ao transporte por modo |
| `test_publico*.py`, `test_preview.py`, `test_simulacao*.py`, `test_acesso.py`, `test_origem.py`, `test_demonstracao.py` | Substituídos por equivalentes em `tests/mobilizacao/` |
| `test_contatos.py` | Vai para `tests/contato/` |

`tests/acesso/test_vazamento.py` passa a confirmar e enviar um Lote no lugar de
`simular_comunicacao`.

## R13 — Interface do Lote

Usa o shell administrativo do acompanhamento.

- **Lista**:
  - Lotes da Campanha visíveis, com nome, confirmado em, por quem (rótulo do operador
    fictício) e situação derivada;
  - formulário GET de filtros: unidades (checkbox a partir das unidades existentes nas
    Conclusões do escopo), nível, ano mínimo e máximo, curso (texto);
  - prévia com Conclusões, Pessoas, com contato, sem contato e excluídas;
  - campo nome e botão "Confirmar Lote" (POST, que envia só os filtros);
  - sem filtros e com escopo institucional, uma caixa de confirmação explícita "Confirmo
    que este Lote abrange N Pessoas" é obrigatória.
- **Detalhe**: filtros, momento, contagens por situação (sem contato, não tentados,
  submetidos, falhas, incertos), os textos de FR-042 e o botão "Enviar"/"Continuar envio"
  quando houver não tentados e a Campanha estiver `EM_COLETA`. Fora disso, explicação
  textual.
- Sem JavaScript, com `<fieldset>`/`<legend>`, mensagens com texto e `role="status"`.

## R14 — Validações solicitadas

| Pedido | Onde |
| --- | --- |
| Concorrência entre Lotes | `tests/mobilizacao/test_concorrencia.py`, `pytest.mark.django_db(transaction=True)` e duas threads: confirmação simultânea de dois Lotes sobrepostos (o segundo exclui), envio simultâneo do mesmo Lote (nenhum membro duas vezes), membro de dois Lotes (o banco recusa) e envio de Lotes diferentes com a mesma Pessoa (impossível pela restrição; verificação explícita) |
| Retomada após interrupção | `tests/mobilizacao/test_retomada.py`: transporte de teste que levanta exceção inesperada no k-ésimo envio; estado `EM_TENTATIVA` simulado; nova ação processa só não tentados; incerto nunca é retentado; o limite por ação gera "continuar envio" |
| Idempotência da carga | `tests/contato/test_carga.py`: mesma lista (nada), reordenada (nova observação), valor novo, lista vazia (nada), indisponível (nada, situação distinta), valor inválido ignorado, falha numa Pessoa não afeta as outras |
| Isolamento em relação ao acesso | `tests/contato/test_isolamento.py`: AST (`academico`, `acesso`, `declaracao` e `fonte_academica/contrato.py` não importam `contato` nem `contatos_da_fonte`); acesso por CPF e data e incorporação funcionam com fonte de contatos indisponível |
| Isolamento em relação à narrativa e ao vídeo | AST (`narrativa`, `video`, `contexto_trajetoria` não importam `contato` nem `mobilizacao`); a página `/minha-trajetoria/` e o card idênticos com e sem contato; a tela de conclusão tem "Ver minha trajetória no Ifes" como primeira ação |

## R15 — Configurações novas

Nenhuma tem padrão permissivo:

- `TRAJETORIA_ENVIO_REAL`: só `"1"` liga. Padrão desligado.
- `TRAJETORIA_REMETENTE_INSTITUCIONAL`: vazio por padrão. Exigido só no modo real.
- `TRAJETORIA_URL_ENTRADA`: vazio por padrão. Exigido só no modo real. A demonstração
  continua com `TRAJETORIA_URL_ENTRADA_DEMONSTRACAO`.
- `TRAJETORIA_LOTE_ENVIO_POR_ACAO`: inteiro, padrão 100.

`.env.example` documenta as quatro com aviso de Gate B.
