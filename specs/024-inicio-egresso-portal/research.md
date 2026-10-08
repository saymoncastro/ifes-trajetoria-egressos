# Research — Feature 024: Início do egresso e shell do Portal

Base: `main` em `8be65c0` (S0 integrada: ADR 0008, Constituição 2.1.0). Cada decisão segue o
formato decisão / justificativa / alternativas.

## R1 — Onde mora a camada do Portal

- **Decisão.** Um app Django novo, `trajetoria/portal`, só de experiência:
  - entrada do Portal;
  - identificação pelo Portal;
  - Início;
  - provedor de navegação.

  O app não tem `models.py`, migração nem gravação.
- **Justificativa.**
  - A Constituição 2.1.0 exige que o núcleo não dependa da camada e que isso seja
    verificável. Um pacote próprio permite um teste de fronteira simples: nenhum arquivo fora
    de `trajetoria/portal` importa ou referencia `trajetoria.portal`.
  - O repositório já isola capacidades em apps pequenos (`contato`, `video`).
  - O ADR 0008 deixa a granularidade para cada spec. Para a 024, um app basta.
- **Alternativas.**
  - Pôr as telas em `interface`: mistura o Portal com a jornada da pesquisa e impede o teste
    de fronteira.
  - Criar desde já `oportunidades` e `reciprocidade`: fica fora do escopo e seria YAGNI.

## R2 — Como o Portal entra (alternativa A da spec)

- **Decisão.** Entradas distintas, cada uma com destino fixo:

  | Endereço | Papel | Sem sessão | Com Pessoa | Com declarante |
  |---|---|---|---|---|
  | `/` (Portal ativo) | Entrada do Portal (divulgável) | 303 → `/entrar/` | 303 → `/inicio/` | 303 → `/declaracao/` |
  | `/entrar/` | Identificação pelo Portal | Formulário da 018 | 303 → `/inicio/` | 303 → `/declaracao/` |
  | `/inicio/` | Início | 303 → `/entrar/` (ou `/entrar/?aviso=sessao`) | 200 | 303 → `/declaracao/` |
  | `/acesso/` | Identificação pelo convite (**inalterada**) | Formulário | Formulário com "Continuar para suas formações" (023) | idem |

  O POST confirmado em `/entrar/` leva a `/inicio/`. O POST confirmado em `/acesso/`
  continua levando a `/formacoes/`.
- **Justificativa.**
  - É a escolha da spec (S4): preserva 016 FR-021/FR-022, 018 FR-053 e 023 FR-001/FR-006.
  - Nenhum parâmetro do cliente decide destino (FR-006).
  - `/entrar/` é um endereço curto e neutro.
  - A raiz não pode ser a própria identificação, porque o POST da raiz confundiria o
    comportamento da raiz sem Portal.
- **Alternativas.**
  - Destino de lista fechada (B): rejeitado na spec.
  - Identificação em `/portal/`: sem vantagem. A raiz já é a entrada espontânea (FR-005).

## R3 — Reaproveitar a identificação da 018 sem mudar seu contrato

- **Decisão.** A view `acesso.views.entrada` passa a delegar para uma função interna do
  próprio `acesso`, com dois parâmetros: o destino depois da confirmação e o endereço do
  formulário (`acao`).
  - `entrada` chama a função com `/formacoes/` e `/acesso/`, como hoje.
  - O Portal chama a mesma função com `/inicio/` e `/entrar/`, além de um rótulo de
    contexto ("Entrada do Portal do Egresso").
  - O template `acesso/entrada.html` usa `{{ acao }}` no lugar de `/acesso/` literal nos
    dois formulários (principal e painel). A ligação "Continuar para suas formações" (023
    FR-022) passa a ser um parâmetro, `continuar`. O Portal passa `continuar=None`: com
    sessão, `/entrar/` já redireciona para o Início antes de exibir o formulário.
- **Justificativa.**
  - Uma única verificação: mesmos limites, mensagens, painel, selo do declarante e
    `Retry-After`.
  - O `acesso` não passa a conhecer o Portal: recebe valores, não importa nada.
  - Respeita o Princípio XV: nenhum mecanismo novo.
- **Alternativas.**
  - Copiar a view para o Portal: duplicaria regra de segurança.
  - Usar um parâmetro `?destino=`: é a alternativa B.

## R4 — Regra positiva da trajetória (FR-009, FR-010)

- **Decisão.** `narrativa.consultas.elegivel(pessoa)` passa a ser "a Pessoa tem ao menos uma
  Conclusão Acadêmica" (`pessoa.conclusoes.exists()`).
  - A função deixa de importar `Participacao`.
  - A docstring cita a 024 e a revisão da 021 FR-001/E2.
  - A 022 já usa a mesma função (`composicao_da_sessao`), então o vídeo acompanha sem outra
    mudança.
  - A Pessoa sem Conclusão continua indo para `/formacoes/`, onde vê a mensagem de
    `SEM_FORMACAO`.
- **Justificativa.**
  - É um único ponto. A regra fica onde a trajetória mora, independente do Portal: com o
    Portal desabilitado, a trajetória continua aberta (FR-027).
  - Formação Declarada não é Conclusão, logo fica de fora por construção (FR-012).
- **Alternativas.** Manter `elegivel` e criar uma exceção no Portal: seria a "exceção para o
  Portal" que o solicitante vetou.

## R5 — Antecipação e tamanho da pesquisa em `/formacoes/` (FR-013, FR-014)

- **Decisão.**
  - Sai `mensagens.ANTECIPACAO`.
  - Quando a formação em destaque está **disponível para iniciar**, a escolha de formações
    mostra "A pesquisa tem no máximo N partes." O valor é
    N = 1 + `maximo_restante(conteudo, primeira_secao)` sobre o conteúdo da Versão da
    Campanha. É a mesma função da 023.
  - Em `SELECAO_NECESSARIA`, a frase vai em cada formação disponível para iniciar.
  - Para retomar, vale o "onde parou" de hoje, sem a frase.
- **Justificativa.**
  - Regra de verdade (014 FR-008): o benefício já está disponível.
  - R-02 da reauditoria.
  - Nenhum cálculo novo: o grafo de Seções e a função pura já existem e são testados.
- **Alternativas.**
  - "Cerca de N minutos": vedado (008 FR-095).
  - Total exato: impossível com ramificações.

## R6 — Início: composição e leitura

- **Decisão.** A view do Início lê só o que já existe:
  1. `montar(entrada_da_pessoa(...))` (021) → seção `o_que_o_ifes_registra`, formações e
     derivados (`formacoes_registradas`, `tempo_desde_conclusao`, `primeira_formacao`),
     cada `Frase` com sua `origem`;
  2. `situacao_de_entrada(pessoa)` (007), para o convite;
  3. `renderizador.disponivel()` (022), para o atalho do vídeo.

  O contato **não** é lido. O atalho "Meu e-mail" tem rótulo fixo, e isso exige ajustar a
  spec: Key Entities e Origem dos Dados.
- **Justificativa.**
  - Uma só montagem de fatos (FR-017).
  - Minimização (XVI): o Início não precisa saber se há e-mail.
  - Falhas da narrativa omitem o bloco sem derrubar a página (edge case). É o mesmo padrão
    do bloco de vídeo da 022.
- **Alternativas.**
  - Consultar `ConclusaoAcademica` direto no Portal: seria uma segunda regra de fatos.
  - Ler o contato para variar o rótulo: dado a mais sem ganho.

## R7 — Shell e navegação sem dependência do núcleo para o Portal

- **Decisão.**
  - **Ponto de extensão no núcleo.** `interface/base.html` ganha dois blocos neutros:
    - `{% block produto %}`, com conteúdo padrão "Trajetória Ifes / Acompanhamento de
      egressos";
    - `{% block navegacao %}`, vazio.

    Um include neutro, `interface/_navegacao.html`, renderiza a variável de contexto
    `navegacao` (lista de itens com rótulo, endereço e se é a página atual) **se ela
    existir**.
  - **Telas que optam pela navegação** (FR-022): `formacoes.html`, `concluida.html`,
    `narrativa/minha_trajetoria.html` e `contato/meu_email.html` preenchem o bloco com o
    include. Seções, concluir, aviso, entrada e declaração não preenchem.
  - **Provedor.** `trajetoria.portal.contexto.navegacao` é um *context processor*
    registrado em `settings`. Com o Portal desabilitado, devolve `{}`. Com o Portal ativo e
    Pessoa na sessão, devolve os itens do FR-023. O item "Minha trajetória" só aparece se
    `elegivel(pessoa)`.
  - **Templates do Portal** estendem `interface/base.html` e sobrescrevem `produto` com
    "Portal do Egresso".
- **Justificativa.**
  - O núcleo só conhece um slot genérico (`navegacao`), não o Portal. Sem o provedor, nada
    aparece, o que satisfaz o FR-027.
  - O teste de fronteira proíbe a string `portal` nos templates e no código do núcleo.
  - O shell da 015 não muda quando o slot está vazio, então a jornada fica idêntica
    (SC-007).
- **Alternativas.**
  - Include de `portal/...` nos templates do núcleo: cria dependência do núcleo para o
    Portal.
  - Middleware que injeta HTML: frágil e opaco.
  - Mover o shell inteiro para um app novo: mudança maior sem ganho nesta feature.

## R8 — Desabilitar o Portal (FR-027)

- **Decisão.** A configuração `TRAJETORIA_PORTAL` vem do ambiente: `"0"` desliga, e ausente
  ou qualquer outro valor liga.
  - `config/urls.py` monta as rotas por uma função `rotas(com_portal)`. As rotas do Portal
    entram **antes** de `interface.urls`, para que `""` seja a entrada do Portal. Sem
    Portal, `""` volta a ser `interface.views.inicio`, intocado.
  - O provedor de navegação verifica o valor a cada requisição.
  - Nos testes do Portal desabilitado: `override_settings(TRAJETORIA_PORTAL=False)` mais
    `pytest.mark.urls` apontando para um módulo de teste com `urlpatterns = rotas(False)`.
- **Justificativa.**
  - Ligado por padrão, porque a camada é só de demonstração: o `ModoDemonstracaoMiddleware`
    já responde 404 a tudo fora dela. Isso evita uma variável nova obrigatória no `.env` e
    no procedimento de ambiente local.
  - O `"0"` explícito torna o desligamento deliberado.
  - Desligado, o código do Portal nem é roteado, o que é a verificação mais forte da
    independência.
- **Alternativas.**
  - "Só `1` liga", como o modo de demonstração: obrigaria a atualizar `.env.example` e
    `ambiente-local.md`, e o Portal sumiria em ambientes já preparados.
  - Views do Portal que respondem 404 quando desligadas, mas continuam roteadas: a raiz
    ficaria presa ao Portal.

## R9 — Endereço do Início e sessão expirada (FR-007)

- **Decisão.**
  - Uma tela do Portal sem sujeito usa a mesma detecção da 023 (`_sessao_expirada`, já
    marcada na requisição por `pessoa_em_uso`).
  - O destino é `/entrar/?aviso=sessao` quando a sessão acabou de expirar e `/entrar/`
    quando não.
  - Em `/entrar/`, o aviso `sessao` mostra só a frase genérica da 023 FR-001. A frase do
    envio guardado (023 FR-003) é suprimida: o parâmetro `continuar` do R3 indica que o
    contexto é o Portal.
- **Justificativa.**
  - Regra de verdade: o envio guardado só volta em `/formacoes/`.
  - `aviso` já é código de lista fechada (023; `_chegada` em `acesso/views.py`) e não decide destino.
- **Alternativas.** Repetir a frase do envio: seria falsa nesse caminho.

## R10 — Visual do Início (FR-026, FR-032)

- **Decisão.**
  - **Composição.** Uma coluna, a mesma da 021:
    1. abertura com a ilustração vetorial do catálogo e legenda "· ilustração";
    2. `h1` "Sua história com o Ifes";
    3. a frase-síntese da seção `o_que_o_ifes_registra`;
    4. a lista de formações (padrão `formacao.html`), cada uma com o selo de texto
       "Registro do Ifes";
    5. a nota de proveniência;
    6. a lista de ações (trajetória, retrato e vídeo, e-mail);
    7. o convite.
  - **Visual.** Tokens da 015, sem novos. Nada de grade de cartões nem hero com saudação. A
    reabertura do veto vale só para a abertura ilustrada, que já existe na 021.
  - **Navegação.** Lista horizontal de links que quebra linha, abaixo do cabeçalho, com
    alvos de 44 px e `aria-current="page"`. Sem menu escondido, sem JavaScript.
- **Justificativa.**
  - É o mínimo perceptível: a primeira tela fala da pessoa, não da pesquisa.
  - Reaproveita componentes já auditados.
  - Com no máximo 4 itens curtos, a lista cabe em uma ou duas linhas a 320 px.
- **Alternativas.**
  - Barra fixa no rodapé, como o "dock" do mockup: exige cuidado com sobreposição e foco e
    não traz ganho para 4 itens.
  - Menu hambúrguer: precisaria de JavaScript ou `details`, e esconde os destinos que o
    Checkpoint 1 quer que sejam encontrados.

## R11 — Textos (microcopy provisória)

- **Decisão.** Os textos ficam centralizados em `trajetoria/portal/mensagens.py`, com
  verificação de vocabulário vedado em teste:
  - proibidos: "minutos", "%", "turma", "geração", "conectados", "Olá";
  - "pesquisa" só no bloco do convite.

  Lista provisória em [contracts/inicio.md](contracts/inicio.md).
- **Justificativa.** Segue o padrão `mensagens.py` dos apps de interface e permite testar a
  regra de verdade.

## R12 — Testes

- **Decisão.** Os testes ficam em `tests/portal/`:
  - `test_entradas.py`: caminhos A e B, declarante, parâmetros ignorados (FR-001 a FR-008,
    FR-033 1–5 e 9);
  - `test_inicio.py`: ordem do documento, proveniência, convite por situação, Pessoa sem
    Conclusão, falha de narrativa;
  - `test_navegacao.py`: telas com e sem navegação, item da trajetória condicional,
    `aria-current`;
  - `test_desabilitado.py`: FR-027, SC-005;
  - `test_fronteiras.py`: nenhuma importação ou referência a `portal` fora do app, ausência
    de `models.py` e migrações, nenhuma gravação (contagens antes e depois).

  Também mudam testes existentes:
  - `tests/narrativa/test_rotas.py::test_sem_participacao_concluida_vai_para_formacoes`
    passa a "sem Conclusão vai para formações", e entra o caso "com Conclusão e sem
    Participação vê a página";
  - o teste de antecipação em `tests/interface/test_interface_formacoes.py` e a lista de
    fontes em `tests/narrativa/test_catalogo.py`;
  - os testes do vídeo que exigem Participação concluída, se houver.

  As medidas (SC-002, SC-004, SC-007) são feitas com o navegador a 375×812, como na
  reauditoria.
- **Justificativa.** Cada caso do FR-033 tem um teste nomeado. Os requisitos revisados
  aparecem como testes atualizados, com a referência da revisão.

## R13 — Dados da demonstração

- **Decisão.** Não muda nada em `preparar_demonstracao`.
  - Pessoas com Conclusão e sem Participação já existem: todas, antes de responder.
  - O caso "Pessoa sem Conclusão" não existe na demonstração: a incorporação ignora quem
    não tem conclusão (`test_interface_cenario`). Ele é coberto só por teste, com uma Pessoa
    criada pela construção de testes.
- **Justificativa.** Sem dado novo, sem migração.
