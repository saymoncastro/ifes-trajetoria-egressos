# Contrato de domínio e governança

## Governança (010) — `trajetoria/governanca/regras.py`

```text
pode_gerir_campanha(vinculos) -> bool
```

Verdadeiro se, e somente se, algum vínculo ativo tem papel CPAEG. Pura: não lê banco,
requisição, settings nem modo de demonstração. Interpretação C1 da 017, restrita à
demonstração; 004/DP-402 continua aberta. Não concede publicação, edição de instrumento,
critérios, remoção ou mobilização.

`Atuacao` (011, `trajetoria/acompanhamento/acesso.py`) ganha `gerir_campanha: bool = False`,
preenchido por `@acompanhamento` com essa regra. `@comunicacao` (016) não muda.

## Campanha (004) — `trajetoria/campanha/consultas.py`

```text
impedimentos_de_abertura(campanha, *, agora=None) -> tuple[Violacao, ...]
```

- Nada grava. Relê o estado da Versão no banco.
- Ordem: `VERSAO_NAO_PUBLICADA`; depois `PERIODO_NAO_DEFINIDO` ou `FORA_DO_PERIODO`.
- `campo` e `detalhe` idênticos aos produzidos hoje por `abrir`.
- Não trata "já aberta": quem chama decide (em `abrir`, o caso já aberto continua devolvendo
  `JA_EM_COLETA`/`JA_ENCERRADA` antes da verificação).

`operacoes.abrir` passa a usar essa função depois do bloqueio da linha; seu resultado,
rejeições e efeitos não mudam. Ela é a **única** fonte da regra de abertura: a interface
nunca reimplementa as condições. O que o GET exibe é só orientação; o POST sempre chama
`abrir`, que revalida sob bloqueio no momento da submissão. Nenhuma outra operação ou
consulta da 004 muda.

Duas outras regras saíram de dentro de operações existentes, no code review, para que a
interface as reutilize sem cópia, com o mesmo resultado:

- `operacoes.violacoes_de_periodo(inicio, fim)`: regra pura de período válido (FR-012), que
  `definir_periodo` aplica sob bloqueio. A criação a consulta quando o nome é rejeitado e
  ainda não há Campanha, para mostrar todos os erros na mesma submissão.
- `consultas.campanhas_em_coleta(agora=)`: o predicado EM_COLETA no banco, usado por
  `campanhas_em_coleta_para` e pela confirmação de abertura (aviso de sobreposição).

## Operações da 004 usadas pela interface

| Ação | Operações | Atomicidade |
| --- | --- | --- |
| Criar | `criar_campanha(nome, versao)`; se houver data, `definir_periodo(inicio, fim)` | Uma transação; qualquer rejeição desfaz tudo |
| Editar | `alterar_campanha(campanha, nome=, versao=)`; se houver data, `definir_periodo` | Idem |
| Abrir | `abrir(campanha)` | Da própria operação |
| Encerrar | `encerrar(campanha)` | Da própria operação |

Não usadas: `definir_criterios`, `remover_campanha`.

## Mapa de rejeição → interface

| Motivo | Campo | Tratamento |
| --- | --- | --- |
| `NOME_VAZIO` | nome | "Informe o nome da Campanha." |
| `PERIODO_INCOMPLETO` | início ou fim (o ausente) | "Informe as duas datas do período, ou deixe ambas em branco para definir depois." |
| `PERIODO_INVERTIDO` | início | "O início deve ser igual ou anterior ao fim." |
| `CAMPANHA_JA_ABERTA` | — | Página 409: "Esta Campanha já foi aberta e não pode mais ser alterada. Mudanças exigem nova Campanha." |
| `VERSAO_NAO_PUBLICADA`, `PERIODO_NAO_DEFINIDO`, `FORA_DO_PERIODO` | — | Impedimentos (data-model) |
| `CAMPANHA_NUNCA_ABERTA` | — | Página 409: "Esta Campanha nunca foi aberta; não há coleta para encerrar." |
| outro | — | Erro de programa: relançado |
