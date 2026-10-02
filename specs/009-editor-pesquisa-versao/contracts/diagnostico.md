# Contrato: diagnóstico técnico, exposição da 006 e auxiliares de ação

Este contrato atende spec FR-021, FR-052, FR-061, FR-066 a FR-075 e FR-109, e a decisão 4
das Clarifications. Detalhes em research R4 a R7.

## 1. Feature 006: `secoes_nao_suportadas` (única alteração em feature anterior)

Módulo: `trajetoria.participacao.percurso`.

```text
secoes_nao_suportadas(conteudo: ConteudoVersao) -> tuple[ConteudoSecao, ...]
```

- **Pura**: sem ORM, sem relógio, sem Participação e sem Campanha, como o resto do
  módulo.
- **Resultado**: as Seções de `conteudo.secoes`, na ordem, que contêm mais de uma
  Pergunta com alguma Opção com regra de navegação (006 FR-016; DP-604).
- **Quando vazio**: `()` se a Versão está dentro da capacidade de execução da jornada.
- **Não depende do estado**: o resultado não depende de a Versão estar publicada.
- **Exportação**: entra no `__all__`.

`_exigir_suporte(conteudo)` passa a ser escrita em termos dela, **sem mudança
observável**:

- uma `Violacao(Motivo.ESTRUTURA_NAO_SUPORTADA, "secao", "Seção <id> tem <n> Perguntas com regra de navegação")`
  por Seção devolvida, na mesma ordem;
- `ParticipacaoRejeitada` se houver ao menos uma.

O que continua igual:

- `percorrer`, `situacao_da_jornada` e `concluir`;
- os testes existentes da 006 e da 008, que passam sem alteração.

Teste novo da 006 (`tests/participacao/test_jornada_percurso.py`):

- a Versão suportada dá `()`;
- duas Seções não suportadas são devolvidas na ordem;
- as Seções devolvidas correspondem, uma a uma, às violações levantadas por `percorrer`
  sobre o mesmo conteúdo.

## 2. Editor: `diagnosticar`

Módulo: `trajetoria.editor.diagnostico`.

```text
diagnosticar(versao: Versao) -> Diagnostico
```

Pré-condição: a Versão está em RASCUNHO. A view não chama o diagnóstico para Versão
publicada (FR-075).

Passos:

1. `conteudo = conteudo_da_versao(versao)` (002), uma leitura;
2. `localizar = localizador(conteudo)` (`editor/apresentacao.py`);
3. diagnóstico **A**: para cada `Violacao` de `verificar_completude(versao)` (002, na
   ordem dela), criar `Problema(origem="estrutura", causa=v.motivo,
   elemento=localizar[v.elemento], texto=<o que corrigir, composto com o rótulo>)`, com
   o mapa local dos 5 motivos de completude;
4. diagnóstico **B**: para cada `secao` de `secoes_nao_suportadas(conteudo)` (006),
   criar `Problema(origem="jornada", causa=participacao.regras.Motivo.ESTRUTURA_NAO_SUPORTADA,
   elemento=localizar[secao.id], texto=mensagens.INCOMPATIVEL_COM_A_JORNADA)`;
5. devolver `Diagnostico(estrutura=..., jornada=...)`.

Garantias:

- **Problemas concretos preservados**: `estrutura` tem **um `Problema` por `Violacao`**
  devolvida pela 002, e `jornada` tem **um `Problema` por Seção** devolvida pela 006.
  Nenhum é agrupado, descartado ou resumido a booleano. Os booleanos são propriedades
  derivadas.
- **Acionável**: cada `texto` diz onde está o problema e o que corrigir, sem correção
  automática. Por exemplo: "A Pergunta «Qual é sua situação profissional?» (Pergunta 2 da
  Seção 4) precisa ter pelo menos duas Opções."
- **Mesma capacidade, estado real**: alterar o rascunho por operações reais (adicionar a
  Opção que faltava, remover o segundo desvio) muda o diagnóstico seguinte. Isso é
  verificado em teste, sem réplica de `verificar_completude`.
- **Nenhuma escrita**: verificável por retrato antes e depois e por contagem de queries
  sem INSERT, UPDATE ou DELETE.
- **Sem terceira fonte**: nenhum problema vem de outro lugar (FR-069).
- **Ordem determinística**: A antes de B; dentro de cada um, a ordem da fonte.
- **Tudo de uma vez**: B é calculado mesmo quando A tem problemas (FR-066).
- **Valor em memória**: nada é gravado (FR-072).
- **Coerência com a publicação**: `sem_impedimentos_conhecidos` ⇒ `publicar(versao)`
  aceita sem `OperacaoRejeitada`, e `secoes_nao_suportadas(conteudo) == ()` (FR-073).
  Isso é verificado em teste, sobre cópia, com `publicar` chamado **apenas** no teste.

Apresentação (`editor/diagnostico.html` e o resumo em `editor/versao.html`):

- seção "Estrutura válida" (A), com a lista ou "nenhum problema de estrutura";
- seção "Compatível com a jornada atual" (B), com a lista ou "nenhuma
  incompatibilidade", e a explicação da semântica atual (FR-056; 006/DP-604);
- situação derivada (data-model §3). Em "Sem impedimentos técnicos conhecidos", a página
  diz que isso não é aprovação, homologação, autorização nem publicação, e que publicar
  não está disponível no editor (FR-071, FR-076);
- cada problema traz `elemento.rotulo`, um link para `elemento.endereco` e o `texto`;
- `causa` não é exibida.

Sinalização por elemento (FR-074): `versao.html`, `secao.html` e `pergunta.html` marcam
com texto ("Problema: …") os elementos cujo `id` aparece no diagnóstico. Eles usam o mesmo
`Diagnostico`, sem cálculo próprio.

## 3. Editor: auxiliares de ação (`trajetoria.editor.acoes`)

Os auxiliares são pequenos e cada um tem um consumidor concreto. Não há service layer
nem UnitOfWork.

### `proxima_posicao`

```text
proxima_posicao(conjunto: QuerySet) -> int
```

- Devolve `(max(posicao) or 0) + 1`. Só lê.
- Concorrência: `POSICAO_OCUPADA` na operação seguinte vira a mensagem de conflito.

### `mover`

```text
mover(em_ordem: list, elemento, direcao: "cima" | "baixo") -> list | None
```

- Devolve a lista com `elemento` trocado com o vizinho, ou `None` na ponta.
- A view passa a lista a `reordenar_secoes`, `reordenar_perguntas` ou
  `reordenar_opcoes` (002).

### `definir_desvio`

```text
definir_desvio(pergunta: Pergunta, opcao: Opcao, destino: Secao | FINALIZAR | None) -> None
```

| Regra atual da Opção | `destino` | Operações 002 |
|----------------------|-----------|---------------|
| igual a `destino` | — | nenhuma |
| qualquer | `None` | `remover_regra` |
| nenhuma | Seção ou `FINALIZAR` | `definir_regra` |
| outra | Seção ou `FINALIZAR` | `remover_regra`, depois `definir_regra` |

- Executa dentro de `transaction.atomic()`, chamado pela view no mesmo bloco de
  `alterar_opcao` ou `adicionar_opcao`.
- Qualquer `OperacaoRejeitada` desfaz tudo, e a Opção mantém o texto, o complemento e o
  desvio anteriores (FR-052, FR-023).
- Teste: falha injetada em `definir_regra` depois de `remover_regra` → o desvio original
  continua no retrato.
