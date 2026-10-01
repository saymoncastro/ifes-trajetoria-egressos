# Data Model: Migração semântica do instrumento institucional vigente

**Feature**: [spec.md](spec.md) | **Research**: [research.md](research.md)

## Persistência: nenhuma mudança

Esta feature **não cria, altera nem remove** modelo, campo, restrição ou migração. O que
ela persiste é apenas uma instância das entidades da Feature 002
([002 data-model](../002-pesquisa-versao-instrumento/data-model.md)):

| Entidade (002) | Linhas criadas pela baseline |
|----------------|------------------------------|
| `Pesquisa` | 0 ou 1 ("Pesquisa Institucional de Egressos"; reutilizada se já existir uma) |
| `Versao` | 1 (designação "Formulário Egresso Ifes 2024 — referência migrada"; `RASCUNHO`; `publicada_em` e `origem` nulos) |
| `Secao` | 13 (7 com `encaminhamento`) |
| `Pergunta` | 54 (38 `ESCOLHA_UNICA`, 3 `ESCOLHA_MULTIPLA`, 2 `TEXTO_CURTO`, 11 `ESCALA`) |
| `Opcao` | 385 (3 com `complemento_textual`; 9 com `regra_destino`; 1 com `regra_finaliza`) |

Nada é gravado em `trajetoria.academico` (Pessoa, Conclusão Acadêmica) nem em qualquer
outra tabela. Q1–Q54, S1–S13, categorias da Matriz e E-xx não existem no banco (FR-012,
FR-036).

## Declaração em código (não persistida)

`trajetoria/formulario_2024/declaracao.py`. Estruturas imutáveis, locais ao pacote, que
descrevem a baseline para a materialização e para os testes ([research R3](research.md#r3--forma-da-declaração)).

### `SecaoDeclarada`

| Campo | Tipo | Mapeia para (002) |
|-------|------|-------------------|
| `chave` | `"S1"`…`"S13"` | — (só rastreabilidade); a posição é a ordem na declaração |
| `titulo` | texto ou `None` | `Secao.titulo` |
| `texto` | texto ou `None` | `Secao.texto` |
| `perguntas` | tupla de `PerguntaDeclarada` | `Pergunta` na ordem (posição = ordem) |
| `encaminhamento` | chave de Seção ou `None` | `Secao.encaminhamento` |

### `PerguntaDeclarada`

| Campo | Tipo | Mapeia para (002) |
|-------|------|-------------------|
| `chave` | `"Q1"`…`"Q54"` | — (só rastreabilidade) |
| `tipo` | `TipoPergunta` da 002 | `Pergunta.tipo` |
| `texto` | texto | `Pergunta.texto` |
| `obrigatoria` | booleano | `Pergunta.obrigatoria` |
| `texto_explicativo` | texto ou `None` | `Pergunta.texto_explicativo` |
| `opcoes` | tupla de textos (vazia em texto curto e escala) | `Opcao.texto`, posição = ordem |
| `complemento` | texto de uma das `opcoes` ou `None` | `Opcao.complemento_textual` |
| `escala` | `Escala` da 002 ou `None` | colunas `escala_*` da `Pergunta` |
| `regras` | tupla de (texto da Opção, chave da Seção ou `FINALIZAR`) | `Opcao.regra_destino` / `Opcao.regra_finaliza` |

### Constantes de módulo

| Constante | Conteúdo |
|-----------|----------|
| `NOME_PESQUISA` | "Pesquisa Institucional de Egressos" (FR-002) |
| `DESIGNACAO` | "Formulário Egresso Ifes 2024 — referência migrada" (FR-004) |
| `TITULO`, `TEXTO_ABERTURA`, `TEXTO_ENCERRAMENTO` | Textos da Versão (FR-016) |
| `TEXTO_TERMOS` | Texto introdutório de S1 (FR-017) |
| `LISTA_C`, `LISTA_E`, `LISTA_15`, `LISTA_17`, `LISTA_18`, `LISTA_19` | Listas do inventário, um item por linha, na ordem original |
| `SECOES` | As 13 `SecaoDeclarada`, na ordem S1–S13 |

### Coerência exigida da declaração

Verificada pelos testes ([plan, Estratégia de testes](plan.md#estratégia-de-testes)),
não por código de produção além do que as operações da 002 já rejeitam:

- chaves `S1`…`S13` e `Q1`…`Q54` únicas, em ordem;
- `complemento` e textos de `regras` pertencem às `opcoes` da própria pergunta;
- destinos de regras e encaminhamentos são chaves de Seções posteriores;
- `escala` só em `ESCALA`; `opcoes` só em escolha.

## Baseline esperada

O conteúdo exato está na spec: [Representação da baseline](spec.md#representação-da-baseline)
(textos, Seções, navegação, percursos, escalas) e [Matriz de Migração](spec.md#matriz-de-migração-q1q54).
Estados e transições são os da 002; esta feature termina com a Versão em `RASCUNHO` e
nunca chama `publicar`.
