# Research: Interface navegável mínima da pesquisa

Fase 0 do plan da Feature 008. Cada item registra **Decisão**, **Justificativa** e
**Alternativas consideradas**. Não havia `NEEDS CLARIFICATION` no Technical Context: as
incógnitas eram de desenho e foram resolvidas abaixo, a partir da spec, da Constituição,
do ADR 0001 e do código existente das Features 001 a 007.

Referências de código lidas: `config/settings.py`, `config/urls.py`,
`trajetoria/participacao/{entrada,operacoes,consultas,percurso,regras}.py`,
`trajetoria/instrumento/conteudo.py`, `trajetoria/campanha/{consultas,operacoes}.py`,
`trajetoria/academico/incorporacao.py`, `trajetoria/fonte_academica/{simulada,cenarios}.py`,
`trajetoria/formulario_2024/materializacao.py`, `tests/participacao/construcao*.py`.

---

## R1 — Onde a interface vive: dois apps sem modelos

**Decisão**: dois apps Django novos, ambos **sem `models.py` e sem migrações**:

- `trajetoria/interface/` — a jornada do egresso: tela de formações, Seção, conclusão,
  confirmação e mensagens. Depende apenas de "qual é a Pessoa resolvida", obtida por uma
  única função importada de `trajetoria.demonstracao.entrada`.
- `trajetoria/demonstracao/` — o **adaptador temporário**: middleware do modo de
  demonstração, Pessoa de demonstração em uso (cookie), telas de escolha e encerramento,
  e o comando `preparar_demonstracao`.

**Justificativa**: FR-005 exige que a entrada de demonstração seja substituível sem mexer
nas telas da jornada. Separar em dois apps torna a fronteira física: quando a fronteira
real de identidade existir, `trajetoria.demonstracao` sai inteiro e a interface troca uma
importação. Nenhum dos dois precisa de modelo (FR-091). Os apps de domínio (`academico`,
`instrumento`, `campanha`, `participacao`) não são tocados (FR-092).

**Alternativas consideradas**:

- *Um único app* — mistura adaptador temporário e jornada; a remoção futura vira
  garimpo.
- *Código web dentro de `trajetoria/participacao/`* — acopla o domínio à apresentação e
  contraria 007 FR-050 / 006 FR-049 (domínio não produz telas).
- *Abstração "provedor de identidade" configurável por setting* — sem segundo consumidor
  (Princípio XXII; 007 FR-048). Uma função importada basta.

## R2 — Camada web mínima na configuração

**Decisão**: acrescentar a `config/settings.py` somente o necessário para páginas com
formulários:

- `INSTALLED_APPS += ["trajetoria.interface", "trajetoria.demonstracao"]` — **nenhum**
  app `django.contrib.*` (sem `admin`, `auth`, `sessions`, `contenttypes`, `messages`,
  `staticfiles`).
- `MIDDLEWARE = [SecurityMiddleware, ModoDemonstracaoMiddleware, CommonMiddleware,
  CsrfViewMiddleware, XFrameOptionsMiddleware]`.
- `TEMPLATES` com `DjangoTemplates`, `APP_DIRS=True` e um único processador de contexto
  próprio (`trajetoria.demonstracao.contexto.demonstracao`), que fornece a Pessoa em uso
  ao cabeçalho.
- `ALLOWED_HOSTS` lido de `DJANGO_ALLOWED_HOSTS`, com padrão
  `localhost,127.0.0.1,[::1]`.
- `DEBUG` continua **`False`** fixo.
- `TRAJETORIA_DEMONSTRACAO` lido de `TRAJETORIA_DEMONSTRACAO` (`"1"` ativa; qualquer outro
  valor ou ausência desativa).
- `LOGGING`: acrescentar o logger `django.request` no handler de console, nível `ERROR`,
  para que falhas inesperadas apareçam no terminal mesmo com `DEBUG=False`.
- Comentário de `INSTALLED_APPS` atualizado: as restrições de não exposição (001, 002,
  004, 005) continuam válidas para egressos; a 008 expõe somente em modo de demonstração.

**Justificativa**: sem `auth`/`sessions` não há tentação de modelar usuário (FR-006); sem
`staticfiles` não há pipeline de estáticos (R14). `DEBUG=False` garante que nenhuma
página mostre traceback (FR-068, FR-069) e que 404/500 usem templates próprios; quem
desenvolve vê o erro no console pelo logger `django.request`. Com `DEBUG=False`, o Django
exige `ALLOWED_HOSTS`; o padrão local evita erro 400 no `runserver` sem abrir hosts
arbitrários.

**Alternativas consideradas**:

- *`DEBUG` por variável de ambiente* — tentador para desenvolvimento, mas basta esquecer
  ligado numa demonstração para expor tracebacks com valores de formulário. O console
  cumpre o papel.
- *`django.contrib.sessions`* — exige tabela `django_session` (persistência nova) ou
  backend de cookie; o cookie assinado direto (R4) é menor.
- *`django.contrib.messages`* — só para avisos pós-redirecionamento; resolvido com um
  código de aviso em lista fechada (R8).

## R3 — Modo de demonstração: desligado por padrão, 404 quando desligado

**Decisão**: `trajetoria.demonstracao.middleware.ModoDemonstracaoMiddleware` responde
`Http404` (renderizando `404.html`) para **toda** requisição quando
`settings.TRAJETORIA_DEMONSTRACAO` não é verdadeiro. A rota única do projeto
(`config/urls.py`) inclui `trajetoria.interface.urls` e `trajetoria.demonstracao.urls`
sempre; quem decide é o middleware, lido a cada requisição.

O comando `preparar_demonstracao` verifica a mesma setting e recusa (`CommandError`) se
desligada.

**Justificativa**: FR-001 e FR-016. Um único ponto de verificação, aplicado antes de
qualquer view, não depende de cada view lembrar de um decorador. Ler a setting por
requisição permite que os testes usem a fixture `settings` do pytest-django sem recarregar
`urls`. Como hoje o projeto não tem nenhuma outra rota, "toda requisição" coincide com "toda
página desta feature".

**Alternativas consideradas**:

- *`urlpatterns` condicionais em `config/urls.py`* — avaliados na importação; testes
  precisariam de `clear_url_caches` e reimportação.
- *Decorador por view* — esquecer um é falha silenciosa.
- *Detectar "produção"* — não há conceito de produção no projeto; desligado por padrão e
  documentação explícita (FR-002) são suficientes e honestos.

## R4 — Pessoa de demonstração em uso: cookie assinado, revalidado a cada requisição

**Decisão**:

- Ao escolher uma Pessoa (POST), a resposta grava o cookie
  `trajetoria_demonstracao_pessoa` com `set_signed_cookie`, valor = `pk` da Pessoa, `salt`
  próprio, `httponly=True`, `samesite="Lax"`, **sem `max_age`** (cookie de sessão do
  navegador).
- `trajetoria.demonstracao.entrada.pessoa_em_uso(request) -> Pessoa | None` lê o cookie
  com `get_signed_cookie(default=None)` e devolve a Pessoa **somente se** existir e
  `fonte == FonteSimulada.codigo` (`"simulada"`). Qualquer outro caso → `None`.
- "Trocar de pessoa" e "Encerrar demonstração" (POST) apagam o cookie e redirecionam à
  entrada de demonstração.
- Views da interface que exigem Pessoa redirecionam à entrada de demonstração quando
  `pessoa_em_uso` devolve `None` (FR-010).

**Justificativa**: FR-009 — o único estado entre requisições é a referência à Pessoa; nada
de domínio, nada no banco. A assinatura evita adulteração trivial, mas **não é** o
controle de segurança: a revalidação por fonte (FR-008) é. Cookie de sessão do navegador
casa com "demonstração": fechar o navegador encerra.

**Alternativas consideradas**:

- *Sessão Django em banco* — tabela nova, proibida pelo solicitante ("sessão em banco").
- *Sessão Django com backend `signed_cookies`* — funciona, mas traz middleware e API de
  sessão para guardar um único valor.
- *Pessoa na URL* (`/pessoas/<id>/…`) — espalha o identificador por todos os endereços e
  convida a confundir URL com identidade.

## R5 — Endereços

**Decisão**:

| Método | Caminho | Função |
|--------|---------|--------|
| GET | `/` | Redireciona: sem Pessoa → `/demonstracao/`; com Pessoa → `/formacoes/` |
| GET | `/demonstracao/` | Entrada de demonstração (lista de Pessoas) |
| POST | `/demonstracao/escolher/` | Define a Pessoa em uso |
| POST | `/demonstracao/encerrar/` | Remove a Pessoa em uso |
| GET | `/formacoes/` | Tela de formações (007, consulta) |
| POST | `/formacoes/entrar/` | Entrada (007), `formacao` opcional |
| GET | `/participacoes/<uuid>/` | Leva à Seção atual, à conclusão ou ao estado final |
| GET, POST | `/participacoes/<uuid>/secoes/<posicao>/` | Seção (posição da Seção na Versão) |
| GET, POST | `/participacoes/<uuid>/concluir/` | Tela de conclusão / ação de concluir |
| GET | `/participacoes/<uuid>/concluida/` | Confirmação |

Detalhes no [contrato de rotas](contracts/rotas.md).

**Justificativa**: FR-086 — nenhum dado pessoal, nome, curso ou resposta em endereço. O
`id` da Participação é um identificador técnico opaco, necessário para que o endereço de
uma Seção seja estável e para que duas formações tenham Participações distinguíveis; ele
nunca é mostrado como texto e **nunca autoriza**: toda view verifica que a Participação
pertence a uma formação da Pessoa em uso (FR-089), e responde 404 igual ao de inexistente
(FR-090). A Seção é endereçada pela sua `posicao` na Versão (inteiro do instrumento), não
pelo `id`, o que mantém endereços curtos e sem segundo UUID.

**Alternativas consideradas**:

- *Participação implícita (guardada no cookie)* — seria "Participação/contexto de
  entrada persistido" (FR-091) e quebraria duas abas com formações diferentes.
- *Formação (Conclusão) no endereço da Seção* — a mesma formação pode ter Participações
  em Campanhas diferentes; o endereço precisaria resolver Campanha, o que é papel da 007.
- *Seção pelo `id`* — funciona, mas acrescenta um UUID sem ganho.

## R6 — Formulário da Seção: `forms.Form` dinâmico derivado do conteúdo

**Decisão**: `trajetoria.interface.formularios.FormularioDaSecao`, um `forms.Form`
construído a partir de um `ConteudoSecao` (002) e das Respostas atuais (005):

- um conjunto de campos por Pergunta, nomeados pela **posição** da Pergunta na Seção:
  `p<posicao>` (valor), `p<posicao>-complemento`, `p<posicao>-remover`;
- valores de Opção = **posição** da Opção na Pergunta (inteiro), nunca `id`;
- por tipo: escolha única → `ChoiceField` (rádio, ou lista suspensa por R10); escolha
  múltipla → `MultipleChoiceField` (caixas de seleção); texto curto → `CharField` com
  `strip=False`; escala → `TypedChoiceField(coerce=int)` sobre `range(inicio, fim + 1)`
  (rádios);
- **todo campo com `required=False`**: a interface não verifica obrigatoriedade (FR-038,
  FR-051); a indicação "obrigatória" é só apresentação;
- `initial` a partir de `respostas_atuais` (via `SituacaoDaJornada.respostas`), para
  retomada (FR-039);
- mensagens de erro dos campos sobrescritas para o português simples de FR-070.

Os widgets são os do Django, renderizados por templates próprios por tipo
(`interface/perguntas/{escolha_unica,escolha_multipla,texto_curto,escala}.html`). Detalhes
no [contrato do formulário](contracts/formulario-secao.md).

**Justificativa**: Django Forms já resolvem validação de forma (opção existente, inteiro
na escala), reapresentação dos valores enviados e mensagens por campo — tudo o que FR-044
e FR-049 pedem — sem framework próprio (FR-096). Derivar os campos de `ConteudoSecao`
garante FR-034: nenhuma Pergunta tem tratamento próprio. Usar posições em vez de UUIDs
deixa o HTML sem identificadores técnicos e torna os testes legíveis.

**Alternativas consideradas**:

- *HTML manual + leitura de `request.POST`* — reimplementaria validação e
  reapresentação.
- *Um `Form` por tipo e formsets* — mais peças para o mesmo resultado.
- *Biblioteca de formulários (crispy, etc.)* — dependência sem necessidade (ADR 0001).

## R7 — Tradução para a 005: uma operação por Pergunta alterada, atômica, com todos os erros

**Decisão**: `trajetoria.interface.gravacao.salvar_secao(participacao, secao, dados)`:

1. Lê as instâncias ORM das Perguntas e Opções da Seção (`Pergunta`/`Opcao`,
   somente leitura), indexadas por posição — as operações da 005 recebem instâncias.
2. Para cada Pergunta, compara o valor limpo do formulário com a Resposta atual:
   - igual → nenhuma operação;
   - ausente (FR-041) e havia Resposta → `remover_resposta`;
   - ausente e não havia → nenhuma;
   - presente e diferente → `responder_escolha_unica` / `responder_escolha_multipla` /
     `responder_texto` / `responder_escala`, com `complemento` quando houver;
   - `p<n>-remover` marcado → `remover_resposta` (prevalece sobre o valor).
3. Tudo dentro de **um** `transaction.atomic()`. Cada operação roda com seu próprio bloco
   atômico interno (savepoint); `ParticipacaoRejeitada` é capturada **por Pergunta**,
   fora do bloco interno, e acumulada. Ao final, se houve qualquer rejeição,
   `transaction.set_rollback(True)` desfaz a submissão inteira (FR-045).
4. Motivos de rejeição são classificados:
   - **por Pergunta** (`OPCAO_DE_OUTRA_PERGUNTA`, `VALOR_INCOMPATIVEL`,
     `ESCALA_FORA_DOS_LIMITES`, `COMPLEMENTO_NAO_ADMITIDO`, `VALOR_VAZIO`,
     `PERGUNTA_DE_OUTRA_VERSAO`) → erro associado ao campo, mensagem de FR-070;
   - **globais** (`COLETA_NAO_ADMITIDA`, `PARTICIPACAO_CONCLUIDA`,
     `PARTICIPACAO_INEXISTENTE`) → resultado da submissão, que a view converte em tela
     (período encerrado, já respondida, não encontrada).

As operações são chamadas **sem `agora`**: o relógio é lido por `momento_de_referencia`,
como sempre (R18).

**Justificativa**: FR-040 (uma operação por Pergunta, só da 005), FR-045 (atômico), FR-049
(todos os erros de uma vez). Comparar antes de escrever evita escrita desnecessária e faz
com que reenviar uma Seção sem mudança seja inócuo. O bloqueio da Participação adquirido
pela primeira operação vale até o fim da transação externa, então a submissão inteira é
serializada com uma conclusão concorrente (006 FR-043). Capturar a exceção fora do bloco
atômico interno é o uso documentado do Django para seguir na transação externa.

**Validação de forma antes da 005** (FR-044): o `Form` rejeita Opção ou ponto de escala
inexistentes. Uma única verificação de interface vai além do tipo do campo: **complemento
preenchido sem a Opção que o admite marcada** — inclusive sem nenhuma Opção, caso em que a
005 não chegaria a ver o complemento (seria remoção). É a mesma regra de 005 FR-030 (a),
apresentada antes da gravação; não há caso que a 005 aceite e a interface rejeite.

**Alternativas consideradas**:

- *Parar na primeira rejeição* — mostra um erro por vez.
- *Validar tudo na interface e só então gravar* — duplicaria as regras da 005.
- *Nova operação em lote na 005* — alteraria contrato de feature anterior (FR-092) sem
  necessidade: a composição transacional resolve.

## R8 — Pendências e navegação: sempre pela 006, com redirecionamento após POST

**Decisão** (POST de `/participacoes/<id>/secoes/<n>/`):

1. `situacao_da_jornada` (006). Concluída → "já respondida". `admite_escrita` falso →
   "período encerrado". Seção `n` fora de `passagens` → redireciona à Seção atual com
   `?aviso=percurso` (FR-047).
2. Formulário inválido → reapresenta (200) com erros; nada gravado.
3. `salvar_secao` (R7). Rejeição global → tela correspondente; por Pergunta → reapresenta
   com erros.
4. `situacao_da_jornada` de novo. Localiza a `Passagem` da Seção `n`:
   - não satisfeita (`pendentes` não vazio) → **redireciona** para a mesma Seção com
     `?pendencias=1&salvo=1`;
   - destino é `UUID` de Seção → redireciona para a Seção de destino, que é a passagem
     seguinte do percurso (a 006 segue de uma Seção satisfeita para o seu destino);
   - destino é `Saida.FINALIZACAO` → redireciona para `/concluir/`.

No GET com `?pendencias=1`, a view lê de novo a jornada e mostra as pendências da Seção
**se** ela ainda for a Seção atual e tiver `pendentes`; as mensagens apontam exatamente as
Perguntas de `Passagem.pendentes` (FR-053). Sem o parâmetro, nenhuma pendência é mostrada
(primeira visita). `salvo=1` só acrescenta a frase "O que já foi preenchido nesta seção foi
salvo." e só é posto pelo redirecionamento de um envio aceito — a pendência vinda de uma
conclusão rejeitada usa só `?pendencias=1`. Os formulários têm `action` explícito, sem
query string, para que uma reapresentação com erro não repita avisos.

`?aviso=` aceita só valores de uma lista fechada (`percurso`, `situacao`); qualquer outro é
ignorado. Nunca contém dado.

GET sem Seção (`/participacoes/<id>/`) → Seção atual (`secao_atual`) ou, se
`finalizada`, `/concluir/` (FR-052).

**Justificativa**: FR-050 a FR-055 — a interface só lê `passagens`, `pendentes`,
`destino`, `secao_atual` e `finalizada`; nunca avalia regra. Redirecionar após gravação
aceita cumpre FR-048 (recarregar não reenvia). O parâmetro `pendencias` não carrega
informação: só pede que a view mostre o que a 006 calcula naquele momento.

**Alternativas consideradas**:

- *Renderizar pendências na resposta do POST* — recarregar pediria reenvio.
- *Seguir para a Seção atual (e não para o destino)* — ao revisitar uma Seção antiga, o
  egresso saltaria para longe; seguir o destino é o "próximo" que o egresso espera e é
  literalmente o que a 006 calcula para aquela Seção.
- *`contrib.messages` para o aviso* — app e middleware extras para um aviso de uma linha.

## R9 — Remover resposta sem JavaScript

**Decisão**: para Perguntas de **escolha única (em rádio) e escala** que tenham Resposta
gravada, a Seção mostra, logo abaixo das Opções, uma caixa de seleção rotulada **"Remover
minha resposta a esta pergunta"** (`p<n>-remover`). Marcada, a Resposta é removida pela
005 ao salvar, qualquer que seja a Opção marcada. Escolha múltipla (desmarcar tudo), texto
(apagar) e lista suspensa (opção vazia "Selecione…") já permitem remover pelo próprio
controle.

**Justificativa**: FR-043 — Q48 orienta "deixe em branco", e rádios não podem ser
desmarcados sem JavaScript. A caixa é um controle de formulário claramente distinto das
Opções (não é `<input type=radio>` no mesmo grupo), não é gravada como Resposta e aparece
para qualquer Pergunta respondida, obrigatória ou não — não é regra de obrigatoriedade.

**Alternativas consideradas**:

- *Opção extra "Sem resposta" no grupo de rádios* — parece Opção do instrumento (vedado).
- *Botão "Limpar" de envio por Pergunta* — o primeiro botão do formulário vira o botão
  padrão do Enter; num campo de texto, Enter limparia uma resposta.
- *JavaScript* — vedado como dependência (FR-080).

## R10 — Listas longas de Opções

**Decisão**: escolha única com **mais de 10 Opções** é apresentada como lista suspensa
(`<select>`), com primeira opção vazia "Selecione…" (= sem resposta); com até 10, como
grupo de rádios. O limite é uma constante nomeada em `formularios.py`. Escolha múltipla é
sempre caixas de seleção; escala é sempre rádios.

**Justificativa**: FR-036 e Princípio XIV — S3 e S4–S7 têm listas de campi e cursos
longas; rádios com dezenas de itens pesam em celular. O critério é só a contagem, nunca a
identidade da Pergunta. `<select>` nativo é acessível por teclado e leitor de tela e não
requer JavaScript. No inventário, as Perguntas com "Outro:" (Q26, Q32, Q45) têm poucas
Opções; se uma lista suspensa tiver Opção com complemento, o campo de complemento aparece
abaixo da lista, rotulado com o texto da Opção.

**Alternativas consideradas**:

- *Sempre rádios* — fiel e simples, mas cansativo em listas de 30+ cursos.
- *Busca com autocompletar* — exige JavaScript.
- *Reproduzir "lista suspensa" do Google Formulários por Pergunta* — 002 FR-035 não
  representa a forma de apresentação; seria regra por Pergunta.

## R11 — Conclusão e confirmação

**Decisão**:

- GET `/concluir/`: jornada concluída → redireciona a `/concluida/`; não finalizada →
  Seção atual; `admite_escrita` falso → "período encerrado"; finalizada → tela com aviso
  de imutabilidade, lista de Seções do percurso (ligações para revisar) e botão
  **"Concluir pesquisa"** (POST).
- POST `/concluir/`: `concluir(participacao)` (006). `CONCLUIDA` ou `JA_CONCLUIDA` →
  redireciona a `/concluida/`. Rejeição:
  `COLETA_NAO_ADMITIDA` → "período encerrado";
  `OBRIGATORIA_PENDENTE` → Seção atual com `?pendencias=1`;
  `ESTRUTURA_NAO_SUPORTADA` ou incoerência → "pesquisa indisponível".
- GET `/concluida/`: só para Participação concluída (senão redireciona à
  `/participacoes/<id>/`); mostra "Pesquisa concluída", agradecimento, contexto da formação
  e `texto_encerramento` da Versão, quando existir, e o caminho de volta às formações.

Seções sem título na lista de revisão aparecem como "Seção <posição>" — número do próprio
instrumento, não texto inventado.

**Justificativa**: FR-056 a FR-064. A tela própria com aviso é a [Hipótese] aceita pelo
solicitante; conclusão idempotente da 006 torna duplo clique e recarga inofensivos.

## R12 — Textos ao egresso num único lugar

**Decisão**: textos fixos da interface (avisos de estado, mensagens de erro, rótulos de
ações) ficam nos templates e, os de erro de campo, num dicionário em
`trajetoria/interface/mensagens.py`, indexado por motivo da 005 e por código de erro dos
campos. Nenhum texto do instrumento é duplicado: Perguntas, Opções, rótulos e textos de
abertura/encerramento vêm sempre da Versão.

**Justificativa**: FR-067 e FR-070; DP-801 (linguagem definitiva) pode revisar os textos
sem mudar comportamento.

## R13 — Acessibilidade: padrões HTML, sem JavaScript

**Decisão**:

- `<html lang="pt-BR">`; `<title>` único por página no formato
  "`<etapa>` — Trajetória Ifes (demonstração)", prefixado com "Erro: " quando há erros ou
  pendências.
- Regiões `header`, `main`, `footer`; ligação "Pular para o conteúdo" como primeiro item
  focável.
- Hierarquia: `h1` = título da Versão (ou "Pesquisa"); `h2` = título da Seção, quando
  existir; Seção sem título não recebe `h2` inventado e as Perguntas seguem como
  `fieldset`/rótulos.
- Pergunta de escolha ou escala: `fieldset` + `legend` com o enunciado e o indicador
  "(obrigatória)" em texto; texto explicativo e erro com `id` próprio, ligados por
  `aria-describedby`; campo com erro recebe `aria-invalid="true"`.
- Texto curto: `label for` + `input`, mesmas associações.
- Rótulos de escala ("5 = Concordo totalmente") como descrição do grupo; rótulo ausente
  não é inventado (FR-033).
- Resumo de erros no topo do `main`: `role="alert"`, título "Há problemas nesta seção",
  lista de ligações `#p<n>` para cada Pergunta afetada (FR-076). Sem JavaScript, o anúncio
  vem do `role="alert"` e do `<title>` com "Erro:".
- Foco visível: `:focus-visible` com anel em duas cores (contorno escuro + halo amarelo),
  perceptível sobre fundo claro e sobre botões escuros.
- Estado nunca só por cor: "(obrigatória)", "Erro:", "Pesquisa já respondida" são texto.
- Paleta com contraste AA (verificado com a fórmula WCAG): texto `#1b1b1b` sobre `#ffffff`
  (≈17:1); botão primário texto `#ffffff` sobre `#1a4480` (≈9.6:1); erro `#b50909` sobre
  `#ffffff` (≈7:1); faixa de demonstração texto `#1b1b1b` sobre `#fff1d2` (≈15.4:1); bordas de
  campos `#565c65` sobre branco (≈6.7:1, acima dos 3:1 exigidos para componentes).

**Justificativa**: FR-071 a FR-078 com HTML e CSS apenas. A verificação automatizada
(R19) é estrutural; o roteiro manual está no [quickstart](quickstart.md).

**Alternativas consideradas**: *axe-core via navegador automatizado (Playwright)* —
traria navegador e dependência de teste pesada só para isso; fica como evolução se a
interface crescer (registrado em Complexity Tracking como não adotado).

## R14 — Estilo: uma folha CSS inline, sem `staticfiles`

**Decisão**: uma única folha `trajetoria/interface/templates/interface/estilo.css`
(~150 linhas), incluída **inline** no `<head>` do template base por `{% include %}`.
Layout de coluna única, `max-width: 40rem` para o texto, fluido abaixo disso, fonte do
sistema (`system-ui`), `1rem` = 16px mínimo, alvos de toque ≥ 44px, sem animações, sem
`@import`, sem fontes externas. Unidades relativas para suportar zoom de 200% e largura de
320px sem rolagem horizontal (FR-077).

**Justificativa**: com `DEBUG=False`, o `runserver` não serve estáticos; habilitá-los
exigiria `staticfiles` + `--insecure` ou WhiteNoise. Uma folha pequena inline elimina o
problema, não tem pipeline (FR-079) e não carrega nada de terceiros (FR-082). Visual
neutro e sóbrio, sem identidade institucional presumida (FR-081; DP-801).

**Alternativas consideradas**: *`staticfiles` + WhiteNoise* — dependência nova; *framework
CSS (Bootstrap, etc.)* — design system de terceiros, vedado; *estilos por atributo* —
ilegível.

## R15 — Segurança de formulário

**Decisão**:

- `CsrfViewMiddleware` + `{% csrf_token %}` em todos os formulários POST; template
  `403_csrf.html` em português simples (a view padrão de falha de CSRF o usa).
- `require_GET` / `require_POST` / `require_http_methods(["GET", "POST"])` em cada view;
  método errado → 405.
- `never_cache` em todas as views de `/participacoes/…` e `/formacoes/` (FR-088).
- Autoescape padrão dos templates; textos multilinha do instrumento com o filtro
  `linebreaks` (que escapa antes de converter).
- Nenhum campo oculto decide Pessoa, Participação, Campanha ou percurso (FR-046): a
  Pessoa vem do cookie revalidado; a Participação do endereço, verificada contra a Pessoa;
  a Seção do endereço, verificada contra `passagens`; o único campo oculto é `formacao`
  na seleção, validado pela 007 (`FormacaoDeOutraPessoa`).
- `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff` e `Referrer-Policy:
  same-origin` pelos padrões do Django.

**Justificativa**: FR-083, FR-084, FR-089, FR-090. Tudo nativo do Django; nada de
framework próprio.

## R16 — Erros inesperados, 404 e 500

**Decisão**: templates `404.html`, `500.html` e `403_csrf.html` na raiz de
`trajetoria/interface/templates/`, **autônomos**: não herdam `interface/base.html`, não
mostram faixa de demonstração nem cabeçalho de Pessoa e trazem só a mensagem, a ligação
para `/` e a folha de estilo incluída. `500.html` é estático (o Django o renderiza sem
contexto). O processador de contexto da demonstração devolve `{}` com o modo desligado,
sem ler o cookie nem consultar o banco. Assim, o 404 do modo desligado não revela que a
demonstração existe nem o nome da Pessoa de um cookie antigo (FR-001). Resultados previstos (situações da 007, rejeições
da 005/006, `FormacaoDeOutraPessoa`) nunca chegam a 500: cada um tem tela (FR-068).
Participação ou formação alheia → `Http404`, indistinguível de inexistente (FR-090).

## R17 — Cenário de demonstração: comando `preparar_demonstracao`

**Decisão**: `manage.py preparar_demonstracao` (em `trajetoria/demonstracao/management/
commands/`), com a lógica em `trajetoria/demonstracao/cenario.py`:

1. **Recusas** (`CommandError`, nada alterado): modo de demonstração desligado (FR-016);
   existe `Pessoa` ou `ConclusaoAcademica` com `fonte != "simulada"` (FR-017).
2. **Pessoas**: `incorporar_pessoa(FonteSimulada(), id)` para cada Pessoa de
   `cenarios.PESSOAS` (001). Pessoas sem conclusão elegível (SIM-P-0006, SIM-P-0008) não
   são materializadas, como na 001.
3. **Instrumento**: `materializar()` (003, idempotente; baseline em RASCUNHO); se não
   existir Versão com designação `"Demonstração — cópia da referência 2024"` na Pesquisa
   da baseline, `criar_versao_a_partir_de(baseline, designação)` + `publicar` (002).
4. **Campanhas** (004), identificadas pelo nome; criadas, configuradas e abertas só se não
   existirem; período de **hoje a hoje + 180 dias**:
   - `"Demonstração — coleta ampla"`: critérios `ano_minimo=2015`,
     `unidades=["Serra", "Cefor", "Vila Velha", "Alegre", "Cariacica", "Colatina"]`;
   - `"Demonstração — coleta sobreposta"`: `unidades=["Vila Velha"]`,
     `niveis=["Pós-graduação"]`.
   Se uma Campanha de demonstração existir e não estiver EM COLETA, o comando recusa com a
   orientação de recriar o banco (FR-018).
5. **Resumo** no terminal: nome de cada Pessoa e a situação que ela demonstra — sem
   identificadores (os nomes são fictícios).

Situações resultantes (calculadas pela 007, não pelo comando):

| Pessoa (fictícia) | Formações | Situação de entrada |
|-------------------|-----------|---------------------|
| Ana Exemplo | ADS Serra 2022 | entrada resolvida (iniciar) — **jornada principal** |
| Maria Exemplo | ADS Serra 2022; Especialização Cefor 2025 | seleção necessária |
| Diego Exemplo | Téc. Química 2012; Lic. Química 2017; Mestrado 2020 (Vila Velha) | entrada resolvida (Lic.), Mestrado em ambiguidade, Téc. sem pesquisa |
| Bruno Exemplo | Téc. Edificações 2014; Eng. Civil 2020 (Vitória) | sem pesquisa disponível |
| Carla Exemplo (Pedagogia, Vitória 2016) | 1 | sem pesquisa disponível |
| Carla Exemplo (Redes, Serra 2023) | 1 | entrada resolvida — **jornada Q1 = Não** |
| Elisa, Fernanda, Pessoa sem nome | 1 cada | entrada resolvida (reserva para novas demonstrações) |

"Disponível para retomar" e "já concluída" surgem do uso da interface (FR-015).
Nenhuma Participação ou Resposta é criada pelo comando (FR-013).

**Justificativa**: FR-012 a FR-018 — comando explícito, fora de migrações, só operações
existentes. Os critérios usam apenas valores presentes na fonte simulada (igualdade exata
da 004). Duas Campanhas sobrepostas só em Vila Velha/Pós-graduação produzem exatamente uma
formação ambígua (caso O da 007) sem contaminar as demais. Período relativo a hoje mantém
as Campanhas EM COLETA na demonstração; vencido, recria-se o banco (não há operação para
reabrir — 004/DP-405 — nem para remover Participações — 005 FR-017).

**Alternativas consideradas**:

- *Fixture JSON / `loaddata`* — gravaria Pessoas fora da fonte simulada (001 FR-030) e
  Versões sem as operações da 002.
- *Migração de dados* — vedada (FR-012).
- *Opção `--reiniciar` que apaga dados* — exigiria remover Participações (005 FR-017).

## R18 — Tempo

**Decisão**: a interface nunca passa `agora`; as operações leem o relógio por
`momento_de_referencia` (004), como definido. Nos testes, a fixture `relogio` substitui
`django.utils.timezone.now` (via `monkeypatch`) por um instante fixo e controlável
(`c.NO_PERIODO`, `c.ULTIMO_DIA`, `c.DEPOIS_DO_FIM`); a mudança de instante entre duas
requisições simula o encerramento por data. O encerramento explícito usa `encerrar` da
004.

**Justificativa**: preserva o ponto único de leitura do relógio (004/007 R9) e o princípio
de que nenhum teste depende do relógio real, sem nova dependência (freezegun).

## R19 — Estratégia de testes

**Decisão**: pytest + pytest-django, `client` do Django (sem JavaScript), banco real,
operações reais das 001–007, sem dublês de domínio (FR-097). Diretório
`tests/interface/` (sem `__init__.py`, como `tests/participacao/`), módulos com prefixo
`test_interface_` (nomes de módulo de teste precisam ser únicos; já existe
`tests/test_aceitacao.py`), auxiliares em `tests/interface/construcao_interface.py` que reutilizam
`tests/participacao/construcao.py` (`baseline_publicada`, `campanha_aberta`, `momento`,
`secoes_esperadas`, `escolhas_baseline`) e `construcao_entrada.incorporar`.

| Arquivo | Cobre |
|---------|-------|
| `test_interface_demonstracao.py` | modo desligado → 404 em todas as rotas, sem revelar Pessoa nem faixa; fonte simulada apenas; cookie revalidado; trocar/encerrar; nenhum identificador técnico no HTML |
| `test_interface_cenario.py` | comando `preparar_demonstracao`: recusas, idempotência, situações da tabela R17, nenhuma Participação ou Resposta |
| `test_interface_entrada.py` | `POST /formacoes/entrar/` e `GET /participacoes/<id>/` |
| `test_interface_formacoes.py` | cinco situações globais da 007; textos por situação da formação; entrada com/sem formação; formação alheia → 404; `entrar` só por POST; GET não cria Participação |
| `test_interface_secao.py` | renderização dos quatro tipos, complemento, obrigatoriedade, lista suspensa > 10; valores restaurados; texto de abertura na primeira Seção; Q10–Q19 sem pré-preenchimento |
| `test_interface_gravacao.py` | tradução para a 005 (registrar, substituir, remover, sem mudança); atomicidade com erro em uma Pergunta; todos os erros de uma vez; complemento sem Opção; campos alheios ignorados; Seção fora do percurso; recarga sem regravação |
| `test_interface_navegacao.py` | destino da 006 após salvar; pendências; voltar; Seção fora do percurso → atual; **17 percursos da baseline** pela interface (SC-004); **Versão de estrutura diferente** (SC-005) |
| `test_interface_conclusao.py` | tela de conclusão só com jornada finalizada; concluir; idempotência; rejeições → telas; confirmação sem respostas; concluída imutável por todas as rotas |
| `test_interface_encerramento.py` | E2E-4: encerramento por data entre requisições e explícito; último dia aceito |
| `test_interface_aceitacao.py` | E2E-1, E2E-2 (com variante), E2E-3 |
| `test_interface_acessibilidade.py` | verificação estrutural do HTML de todas as telas com `html.parser` da biblioteca padrão: `lang`, `<title>` único, um `h1`, todo controle com rótulo, `fieldset`+`legend` nos grupos, `aria-describedby` apontando para `id` existente, resumo de erros com ligações válidas, "Erro:" no título quando há erros |
| `test_interface_fronteiras.py` | importações dos apps novos restritas ao permitido (via `ast`); nenhum texto de Pergunta/Opção da baseline (`declaracao.py`) nos fontes e templates da interface; 0 modelos nos apps novos; CSRF aplicado (`Client(enforce_csrf_checks=True)`); métodos; `Cache-Control` nas páginas com respostas; logs e URLs sem valores declarados (`caplog`) |

**Importações permitidas** (verificadas em `test_interface_fronteiras.py`): na `interface`,
`participacao.entrada` (`situacao_de_entrada`, `entrar`, tipos),
`participacao.operacoes` (`responder_*`, `remover_resposta`, `concluir`),
`participacao.consultas` (`situacao_da_jornada`), `participacao.percurso` (só `Saida`,
para interpretar destino), `participacao.regras` (`Motivo`, `ParticipacaoRejeitada`),
`participacao.models` (`Participacao`, leitura), `instrumento.conteudo`,
`instrumento.models` (`Pergunta`, `Opcao`, `TipoPergunta`, leitura),
`academico.models` (leitura). **Proibidas** na `interface`: `campanha.*`,
`fonte_academica.*`, `instrumento.operacoes`, `participacao.operacoes.iniciar_participacao`.
A `demonstracao` pode importar `fonte_academica.simulada` (o código da fonte, em
`entrada.py`), `trajetoria.interface.apresentacao` (`contexto_da_formacao`, para o resumo
das formações, **só** em `views.py`) e, **só** em `cenario.py`, também `campanha.operacoes`,
`instrumento.operacoes`, `formulario_2024`, `academico.incorporacao`,
`fonte_academica.cenarios` e `participacao.entrada` (para o resumo).

**Justificativa**: SC-002 a SC-017. A Versão de estrutura diferente (reaproveitando
`construcao.instrumento()` da 005, com regra de finalização e duas Seções) é a prova
comportamental de que não há navegação codificada; a verificação de importações e de
textos é a prova estrutural, barata e sem inspeção frágil de lógica.

## R20 — Documentação e o que não muda

**Decisão**:

- `README.md`: uma linha apontando para o quickstart da 008.
- `.env.example`: `TRAJETORIA_DEMONSTRACAO` e `DJANGO_ALLOWED_HOSTS`, com o aviso de que o
  modo é só para ambiente local com dados fictícios.
- Specs das 001–007 **não são editadas**: as restrições de exposição continuam valendo para
  egressos; a compatibilidade está registrada na spec da 008 ("Tensões").
- `pyproject.toml`: **nenhuma dependência nova**.
- **Um teste existente é ajustado**: `tests/participacao/test_entrada_aceitacao.py::test_10`
  proíbe `urls.py`/`views.py`/`forms.py`/`middleware.py` em **qualquer** app de
  `trajetoria/`. A verificação de arquivos passa a valer só para os apps de domínio; as
  asserções sobre autenticação, sessão e rotas da `participacao` ficam como estão (ver
  plan, "Necessidade de voltar…").
