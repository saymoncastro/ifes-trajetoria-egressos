# Research — Feature 031, Encontros propostos por egressos

Decisões técnicas do [plan](plan.md). Cada uma diz o que foi escolhido, por quê e o que se
rejeitou. Elas partem do código na `main` em `f5c4035` e dos precedentes da 025 e da 026. Não
há `NEEDS CLARIFICATION` em aberto: as três ambiguidades de autorização e dados foram
resolvidas no clarify (spec, "Clarifications").

## R1 — Onde vive a feature

- **Decisão:** os três modelos ficam no app `trajetoria/portal`, e a lógica num subpacote
  `portal/encontros/`, no molde de `portal/oportunidades/` e `portal/contribuicao/`.
- **Por quê:** a camada continua desligável num lugar só (ADR 0008), com o mesmo teste de
  fronteira e o mesmo `TRAJETORIA_PORTAL`.
- **Rejeitado:** app novo, que duplicaria o desligamento e a fronteira (025, research R1).

## R2 — Chaves: nenhuma para o núcleo; dentro da camada, sim

- **Decisão:**
  - Encontro, Confirmação e Denúncia guardam `pessoa_id` e `conclusao_origem_id` como UUID,
    **sem chave estrangeira para o núcleo**, como a 026 (R2);
  - Confirmação e Denúncia têm **chave estrangeira para o Encontro**, com `on_delete=PROTECT`;
  - o teste `test_portal_dois_modelos_sem_fk_para_o_nucleo` passa a exigir os quatro modelos
    e a proibir só as chaves cujo destino está **fora** do app `portal`.
- **Por quê:** a regra da ADR 0008 é que o núcleo não dependa da camada e que removê-la não
  exija migração no núcleo. Uma chave **interna** não fere nenhuma das duas e dá integridade no
  banco (nenhuma confirmação órfã), o que a 026 não precisou, porque tinha um modelo só.
- **Rejeitado:** `encontro_id` como UUID solto, que deixaria a integridade só em
  `operacoes.py` sem ganho de fronteira.

## R3 — Origem do organizador copiada

- **Decisão:** no envio, o Encontro copia da Conclusão escolhida o curso, a unidade e o ano
  (`origem_curso`, `origem_unidade`, `origem_ano`), além de `conclusao_origem_id`.
- **Por quê:**
  - a moderação aprova o que vê, e o texto da fonte pode mudar numa nova carga (precedente:
    a unidade copiada na 026);
  - a página não precisa ler a Conclusão para exibir a origem;
  - a escrita verifica que a Conclusão é da Pessoa.
- **Rejeitado:** ler a Conclusão a cada exibição, que mudaria o que foi moderado sem nova
  análise.

## R4 — Data e horário

- **Decisão:** `inicio` e `termino` como data e hora com fuso, no fuso do projeto
  (`America/Sao_Paulo`). O formulário recebe data, início e término separados e os combina.
- **Por quê:** as situações derivadas (FR-010) comparam com o momento atual; o `.ics` precisa
  de instante absoluto (R11).
- **Regras** (FR-002, H-3101): mesmo dia; término depois do início; até 3 h; data entre 2 e 90
  dias depois do envio; na correção operacional (FR-008), início ainda no futuro.

## R5 — Situação derivada, sem coluna de estado

- **Decisão:** uma função pura `regras.situacao(encontro, agora)` deriva a situação dos
  momentos gravados, como `oportunidades.regras.estado`.
  - **Momentos:** `enviado_em`; `publicado_em` e `publicado_por` (a última publicação),
    `primeira_publicacao_em`; `recusado_em`, `recusado_por`, `motivo`, `complemento`;
    `retirado_em`, `retirado_por`; `cancelado_em`; `reenviado_em` e `campos_alterados`;
    `data_alterada_em`; `link_atualizado_em`;
    `publicado_por_escopo` (`institucional` ou a unidade de quem publicou), porque a
    responsabilidade calculada pelo público não diz quem decidiu quando a CPAEG age num
    encontro de unidade única.
  - **Recusa e retirada** usam o mesmo par `motivo`/`complemento`: são exclusivas, e a recusa
    de uma alteração vira retirada (FR-008).
- **Por quê:** nenhum processo agendado; mesmo padrão da 025 (FR-009) e da 026.
- **Restrições no banco:** pares momento/operador coerentes; motivo só com recusa ou retirada;
  complemento obrigatório com "outro motivo"; tamanhos.

## R6 — Pertinência reaproveitada da 025

- **Decisão:**
  - o Encontro usa os mesmos nomes de critério da Oportunidade (`publico_unidades`,
    `publico_niveis`, `publico_cursos`, `NULL` = critério ausente);
  - a descoberta chama `oportunidades.pertinencia.satisfaz` e `explicacao`, que dependem só
    desses atributos;
  - os valores oferecidos no formulário vêm da mesma consulta da curadoria (cursos, níveis e
    unidades registrados nas Conclusões).
- **Por quê:** FR-011 e FR-012 pedem a regra da 025; reaproveitar evita uma segunda regra que
  divergiria.
- **Rejeitado:** copiar a função, ou extrair um módulo comum agora. A extração só se justifica
  se uma terceira capacidade usar a regra (XXII).

## R7 — Validação do link

- **Decisão:**
  - reaproveitar `oportunidades.regras.endereco_invalido` e `origem_do_site`;
  - "mesmo domínio" na correção operacional (FR-008) = mesmo nome de máquina, por
    `_nome_de_maquina`, sem normalização além da que ela já faz.
- **Por quê:** FR-003 pede a validação da 025; o domínio é o que a moderação viu.

## R8 — Competência e escopo da moderação

- **Decisão:** regra nomeada `pode_moderar_encontros` (CPAEG ou CSAEG ativo) e
  `responsavel(publico_unidades)` em `encontros/governanca.py`.
  - `responsavel` devolve a unidade quando o critério de unidades tem exatamente uma, ou
    "institucional" nos demais casos.
  - `modera(escopo, encontro)`: verdadeiro para escopo institucional (CPAEG age em todos,
    clarify 2), ou quando a unidade responsável está nas unidades do escopo.
- **Por quê:** o núcleo não conhece competências da camada (025, R2); H-3102 fica localizada
  num arquivo.
- **Conflito:** cada ação de moderação revalida a situação dentro de uma transação com
  `select_for_update`. Se ela mudou, a ação é recusada com página de conflito (padrão 017,
  025 FR-034).

## R9 — Limite de três ativos por organizador

- **Decisão:** verificado em `operacoes.propor`, dentro da transação, travando os encontros da
  Pessoa (`select_for_update`) antes de contar os ativos: em análise, em revisão, ou publicado
  antes do término.
- **Por quê:** clarify 3. O limite depende do relógio, por isso não cabe numa restrição de
  banco. A trava evita que dois envios simultâneos passem do limite.

## R10 — Visibilidade como função pura

- **Decisão:** `regras.o_que_ver(encontro, situacao, quem)` devolve um de três níveis:
  `conteudo`, `situacao_com_data` ou `so_situacao`. `quem` é organizador, moderação, pessoa
  com confirmação ativa (ou que a tinha no cancelamento ou no término), outra pessoa com
  Conclusão, ou sem sessão. A função implementa a tabela do FR-024a. O link (FR-021) tem
  função própria.
- **Por quê:** a regra de autorização fica testável sem banco e sem template; os templates só
  recebem o nível.
- **"Tinha confirmação ativa no cancelamento ou no término":** confirmação com
  `cancelada_em` nula, ou posterior a `cancelado_em` do Encontro ou a `termino`.

## R11 — `.ics` gerado na camada

- **Decisão:** `encontros/calendario.py` gera o arquivo à mão, com a biblioteca padrão.
  - **Conteúdo:** RFC 5545, CRLF, dobra em 75 octetos, `DTSTART`/`DTEND` em UTC, `UID`
    estável (`<id>@portal-do-egresso.demonstracao`), `URL` absoluta da página e descrição com o aviso.
  - **`SEQUENCE`:** cresce com a data alterada e com o cancelamento; é derivada, e não gravada
    (0, +1 com data alterada, +1 cancelado).
  - **Rota:** `/encontros/<id>/calendario.ics`, só para quem confirmou e para o organizador,
    `Content-Disposition: attachment`.
- **Por quê:** FR-027; sem dependência nova (`tests/dependencias.py`). A forma foi validada no
  protótipo (`prototipo/exemplo.ics`).
- **Rejeitado:** biblioteca `icalendar`, uma dependência nova para três campos.

## R12 — Destino preservado depois da identificação

- **Decisão:**
  - sem sessão, `/encontros/<id>/` mostra a página neutra (FR-022). O link "Confirme seus
    dados para ver" aponta para `/entrar/?encontro=<id>`;
  - `entrar` aceita só esse parâmetro: um UUID de Encontro existente. Ele monta o destino
    `/encontros/<id>/` e o repassa a `identificar(destino=…, acao="/entrar/?encontro=<id>")`;
  - qualquer outro valor é ignorado, e o destino volta a ser `/inicio/`;
  - `destinos.sem_pessoa` ganha o mesmo caso.
- **Por quê:** ADR 0008, item 5, admite destino preservado por **lista fechada**. Aqui a lista
  tem um padrão de rota e identificadores que existem; nunca URL livre, e nunca dado de
  identidade no endereço.
- **Testes:** URL externa, caminho arbitrário, UUID inexistente e UUID válido.
  `identificar` não muda, porque já recebe o destino de quem chama.

## R13 — Início, navegação e vocabulário

- **Decisão:**
  - `inicio._encontro` passa a devolver o par (próximo F pertinente, primeiro A pertinente);
    a seção "Ninguém se forma sozinho." existe se houver ao menos um;
  - `ENCONTROS_TEXTO` muda (spec, "Requisitos revisados");
  - a navegação ganha "Encontros" entre "Oportunidades" e "Participação" (H-3105);
  - as telas `/encontros/...` marcam "Encontros" como item atual.
- **Medidas:** cinco itens de navegação já foram medidos na 025 (R10); repetir a 320 px com
  fonte a 200%.
- **Vocabulário:** "comunidade" só na página Encontros e na seção do Início. Os testes de
  vocabulário da 024, 028, 029 e 032 são revistos com nota.

## R14 — Moderação nas telas de operação

- **Decisão:** rotas sob `/curadoria/encontros/`, com a base da curadoria da 025 e a escolha
  de operador fictício (destino registrável `curadoria`).
  - Lista: em análise, em nova análise, publicados com denúncias; e o estado vazio.
  - Telas de análise, recusa e retirada.
- **Por quê:** FR-019; reaproveita o shell e o padrão de conflito. O protótipo (m1 a m6) já
  segue essa forma.

## R15 — Demonstração

- **Decisão:** o sinal `cenario_preparado` cria encontros fictícios:
  - publicado, para Diego, por curso;
  - aberto a todos;
  - em análise, de unidade única **Vitória**, para a CSAEG do operador fictício B (a
    demonstração só tem CSAEG Vitória e CPAEG; o protótipo usa Serra só como ilustração);
  - em nova análise;
  - recusado;
  - encerrado.

  Cria também confirmações e uma denúncia, para a lista da moderação e "Seus encontros" terem
  conteúdo (precedente 025 R4 e 026 R13). As personas e os textos são os do protótipo.
- **Por quê:** sem conteúdo, nem a moderação nem o percurso do Checkpoint 2 têm o que mostrar.

## R16 — O que não muda

Nenhuma alteração em Pessoa, Conclusão, Contato, Campanha, Versão, Participação, Resposta,
snapshot, exportação analítica, mobilização ou instrumento. Nenhuma dependência nova, nenhum
JavaScript, nenhuma notificação.
