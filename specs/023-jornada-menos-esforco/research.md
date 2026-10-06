# Research — Feature 023

## R1 — Onde guardar o envio pendente

- **Decision**: um registro próprio no armazenamento de sessões do Django (outra
  `session_key` criada com o `SessionStore` do engine configurado), com `set_expiry` de 30
  minutos. A sessão do navegador guarda só a chave desse registro, sob `pendente.envio`.
- **Rationale**: (a) o registro expira em 30 min no banco, e o `clearsessions` diário,
  já previsto na implantação, remove o que sobrar: a retenção máxima fica em 30 min mais o
  intervalo da limpeza (FR-004), mesmo se a pessoa confirmar e for embora sem enviar;
  (b) a sessão do sujeito não carrega Participação nem valores (018 FR-040); (c) não há
  tabela nova (FR-034); (d) é a mesma infraestrutura que já protege a sessão (banco,
  HttpOnly, SameSite).
- **Alternatives considered**: guardar dentro da sessão do navegador (rejeitado: depois da
  confirmação, a linha vive até `SESSION_COOKIE_AGE`, 2 semanas, e mistura Participação com
  o sujeito); cache `LocMemCache` (rejeitado: um cache por processo não sobrevive a vários
  workers); cookie assinado (rejeitado: respostas sensíveis no cliente, legíveis em base64,
  e limite de 4 KB); modelo novo (rejeitado: FR-034).

## R2 — Conteúdo e limites do envio pendente

- **Decision**: `{"participacao": uuid, "posicao": int, "dados": {campo: [valores]},
  "em": iso8601}`. Só campos `p<n>`, `p<n>-complemento` e `p<n>-remover` das Perguntas
  daquela Seção, no máximo 2 000 caracteres por valor. Sem `depois`, CSRF, CPF ou data. Há
  no máximo um por navegador: um novo envio apaga o registro anterior.
- **Rationale**: é o mínimo para reconstruir o formulário (FR-002, FR-009). O limite por
  valor evita usar o registro como depósito.
- **Alternatives considered**: guardar o POST inteiro (rejeitado: minimização).

## R3 — Como a chave atravessa a confirmação e a saída

- **Decision**: `acesso/sessao.estabelecer` e `declaracao/sessao.estabelecer_declarante`
  preservam só a chave `pendente.envio` ao fazer `cycle_key` + `clear`. `encerrar` ("Sair")
  apaga o registro apontado. A reconciliação (descartar se o sujeito não é o dono) acontece
  na primeira tela do sujeito depois da confirmação: `/formacoes/` para a Pessoa,
  `/declaracao/` (POST) para o declarante.
- **Rationale**: a 018 continua sem conhecer a interface (ela só preserva uma chave cujo
  nome ela mesma exporta). A posse da Participação é verificada onde já se verifica hoje.
- **Alternatives considered**: redirecionar direto para a Seção na resposta da confirmação
  (rejeitado: a 018 precisaria conhecer Participação e interface; um redirecionamento a
  mais, invisível, resolve).

## R4 — Sinal de sessão expirada

- **Decision**: `pessoa_em_uso` e `declaracoes_em_uso` marcam `request._sessao_expirada =
  True` quando descartam uma sessão que existia. O `_pessoa` da interface redireciona para
  `/acesso/?aviso=sessao` quando há esse sinal ou quando guardou um envio pendente; sem
  ele, `/acesso/` como hoje. A entrada mostra o aviso por código de lista fechada e
  acrescenta a frase do envio guardado só se o registro existir e for válido (FR-003).
- **Rationale**: endereço sem dado pessoal (FR-001), mesmo padrão dos avisos da 014
  (`?aviso=salvo`), e regra de verdade (FR-003).
- **Alternatives considered**: guardar o aviso na sessão (rejeitado: a sessão acabou de ser
  descartada; o código no endereço é inofensivo).

## R5 — "(opcional)" sem perder o anúncio de obrigatória

- **Decision**: obrigatórias levam `<span class="visualmente-oculto"> (obrigatória)</span>`
  no enunciado; opcionais, "(opcional)" visível. Mantém `aria-required` onde já existe.
- **Rationale**: grupos de caixas (escolha múltipla) não têm `aria-required` válido; o
  texto oculto preserva o anúncio para todos os tipos (Const. XX).
- **Alternatives considered**: só `aria-required` (rejeitado: não cobre caixas).

## R6 — Complemento condicionado sem JavaScript

- **Decision**: em `jornada.css` (só a jornada; a prévia do editor continua mostrando
  tudo):

  ```css
  @supports selector(:has(*)) {
    .pergunta .complemento:not(.sempre-visivel) { display: none; }
    .pergunta:has(.opcao-com-complemento input:checked) .complemento,
    .pergunta:has(option.opcao-com-complemento:checked) .complemento { display: block; }
  }
  ```

  A Opção que admite complemento leva a classe `opcao-com-complemento`. O campo leva
  `sempre-visivel` quando tem valor, o que cobre o erro (texto com a Opção desmarcada) e a
  restauração.
- **Rationale**: FR-018 a FR-020 sem JS; `display: none` tira o campo da ordem de foco; sem
  suporte a `:has`, o `@supports` falha e nada é escondido.
- **Alternatives considered**: `<details>` por Opção (rejeitado: muda a interação);
  JavaScript (rejeitado: FR-035).

## R7 — Opções lado a lado

- **Decision**: o item ganha `lado_a_lado` quando o modo é rádio, há exatamente 2 Opções e
  cada texto tem no máximo 15 caracteres. CSS: `display: grid; grid-template-columns:
  repeat(auto-fit, minmax(min(100%, 8rem), 1fr))`. Em `rem`, o limite cresce com a fonte e
  as Opções voltam a empilhar quando não cabem.
- **Rationale**: FR-024; regra só de forma (008 FR-034). Na baseline, atinge as 14
  perguntas Sim/Não e Q12.

## R8 — Máximo de partes restantes

- **Decision**: `maximo_restante(conteudo, secao_id) -> int` em `participacao/percurso.py`.
  As arestas de uma Seção são: para cada Opção com regra da pergunta com regra, o destino
  (finaliza → fim); mais o destino padrão (encaminhamento, Seção seguinte ou fim) quando
  não há pergunta com regra, quando ela é opcional ou quando alguma Opção não tem regra. O
  resultado é o maior número de Seções depois da exibida, por recursão com memória (o
  grafo de uma Versão publicada não tem ciclo: 006 FR-015). A parte é o índice da passagem
  + 1.
- **Rationale**: FR-013 e FR-014. Não depende de Resposta, logo nunca subestima. É
  determinística e pura, como `percorrer`.
- **Alternatives considered**: usar as Respostas da Seção atual (rejeitado na spec: pode
  subestimar enquanto a pessoa não deixa a Seção).

## R9 — Restaurar sem mostrar erros

- **Decision**: `FormularioDaSecao.itens(..., com_erros=False)` para a restauração: valores
  do formulário ligado aos dados pendentes, sem lista de erros. O primeiro envio de
  verdade valida como sempre.
- **Rationale**: FR-007 (conferir e salvar) e caso-limite "erro aparece no novo envio".

## R10 — "Corrigir" na declaração

- **Decision**: a confirmação recebe também o selo de trânsito (o mesmo que permitiu chegar
  ao formulário) e os valores, como campos ocultos de um formulário "Corrigir" para
  `/declaracao/nova/` com `corrigir=1`. A view devolve o formulário ligado a esses valores.
- **Rationale**: FR-032 sem nova confirmação, dentro da validade do selo; os valores são os
  que a própria pessoa acabou de ver na tela.

## R11 — Próxima formação na confirmação

- **Decision**: `situacao_de_entrada(pessoa).pendentes`, na ordem da 007, sem a formação
  recém-concluída (ela já não é pendente). Primeiro item com um botão de envio para
  `/formacoes/entrar/` (`formacao=<pk>`); com mais de um, também a ligação para
  `/formacoes/`.
- **Rationale**: FR-011 e FR-012 reutilizando a entrada, que reavalia a situação no próprio
  momento (007).
