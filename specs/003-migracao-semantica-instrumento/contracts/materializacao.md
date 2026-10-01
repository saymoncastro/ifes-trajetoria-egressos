# Contrato: materialização da baseline

**Feature**: [spec.md](../spec.md) | **Research**: [R4–R7](../research.md)

Módulo `trajetoria.formulario_2024` (pacote Python, não app Django). Consumidores: testes
desta feature, a futura Feature 004 e quem opera um ambiente (via `manage.py shell -c`).
Não há comando de gestão, URL, admin nem API (research R12).

## `materializar() -> Resultado`

Garante que exista a baseline do Formulário Egresso Ifes 2024, em RASCUNHO, com o
conteúdo da declaração. Não recebe parâmetros.

### Efeito

Tudo em uma única transação (R7). Na ordem:

1. **Pesquisa** com nome exato `NOME_PESQUISA`:
   - nenhuma → criada com `criar_pesquisa`;
   - exatamente uma → usada;
   - mais de uma → levanta `PesquisaAmbigua`; nada é gravado.
2. **Versão** com designação `DESIGNACAO` nessa Pesquisa:
   - inexistente → construída pelas operações da 002 (R4); em seguida, a forma criada é
     comparada com a esperada (pós-condição, R6). Retorna `Resultado(versao, criada=True)`;
   - existente e **equivalente** → nada é gravado. Retorna `Resultado(versao,
     criada=False)`;
   - existente e **divergente** → levanta `BaselineDivergente`; nada é gravado.
3. **Nunca** chama `publicar`. A Versão criada fica em `RASCUNHO`, sem `publicada_em` e sem
   `origem`.

Uma Versão existente já publicada segue a mesma regra: equivalente → no-op; divergente →
`BaselineDivergente`. O estado não entra na comparação.

### Equivalência

Duas formas são equivalentes quando são iguais por valor (R6). Entram:

| Nível | Atributos comparados |
|-------|----------------------|
| Versão | título, texto de abertura, texto de encerramento, sequência de Seções |
| Seção | posição (pela ordem), título, texto, posição da Seção de destino do encaminhamento |
| Pergunta | posição (pela ordem), tipo, texto, texto explicativo, obrigatoriedade, escala (início, fim, rótulo inicial, rótulo final), sequência de Opções |
| Opção | posição (pela ordem), texto, complemento textual, regra (posição da Seção de destino ou "finalizar") |

Não entram: identidades (UUID), estado, momento de publicação, origem, designação, nome da
Pesquisa. Textos são comparados exatamente, sem normalização; `None` ≠ qualquer texto.

### Resultado e erros

| Situação | Retorno / exceção | Gravação |
|----------|-------------------|----------|
| Baseline criada | `Resultado(versao, criada=True)` | Pesquisa (se nova) + baseline completa |
| Baseline existente equivalente | `Resultado(versao, criada=False)` | nenhuma |
| Baseline existente divergente | `BaselineDivergente` | nenhuma |
| Pesquisa homônima repetida | `PesquisaAmbigua` | nenhuma |
| Operação da 002 rejeita algum elemento | `OperacaoRejeitada` (da 002), propagada | nenhuma |
| Baseline recém-criada difere da declaração (erro de construção) | `BaselineDivergente` | nenhuma |

- `Resultado`: `dataclass(frozen=True)` com `versao: Versao` e `criada: bool`.
- `MaterializacaoRecusada(Exception)`: base de `PesquisaAmbigua` e `BaselineDivergente`.
- `BaselineDivergente.divergencia: str`: diagnóstico da **primeira** diferença, no formato
  `"<local>: <o que difere>"`, onde `<local>` é `Versão`, `Sn`, `Sn·p` (Pergunta) ou
  `Sn·p·o` (Opção). Exemplos: `"S9·8: texto explicativo difere"`, `"S2: 7 Perguntas,
  esperadas 8"`, `"S12·3·3: regra difere"`. Não é um diff completo.
- A mensagem da exceção nunca contém dado pessoal (não há nenhum no conteúdo).

## `forma_esperada()` e `forma_da_versao(versao)`

Funções do mesmo módulo, usadas por `materializar()` e pelos testes:

- `forma_esperada()` → forma (tuplas) da declaração, sem acesso ao banco;
- `forma_da_versao(versao)` → forma (tuplas) de uma Versão existente, a partir de
  `conteudo_da_versao` da 002.

Ambas produzem a mesma estrutura (ver Equivalência). Não executam navegação.

## Invariantes

- Toda escrita passa pelas operações de `trajetoria.instrumento.operacoes`.
- Nenhum modelo, campo ou tabela é criado; nada é escrito fora das tabelas da 002.
- Nada é importado de `trajetoria.academico` nem de `trajetoria.fonte_academica`.
- Executar `materializar()` N vezes sem alterações intermediárias resulta no mesmo
  conteúdo e nas mesmas identidades da primeira execução.
