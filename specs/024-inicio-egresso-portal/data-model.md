# Data model — Feature 024

**Nenhuma entidade, tabela, campo ou migração.** O app `portal` não tem `models.py` (FR-029;
Constituição 2.1.0, "Camada de relacionamento"). `makemigrations --check` continua limpo.

## O que é lido

| Fonte | Leitura | Para quê | Origem do dado |
|---|---|---|---|
| Sessão (018) | `pessoa_em_uso`, `declaracoes_em_uso` | Decidir entrada e destino | — |
| Pessoa → Conclusões Acadêmicas (001) + complemento (021 P2) | `narrativa.consultas.entrada_da_pessoa` → `montar` | Síntese, formações e derivados do Início | Institucional e derivado |
| Conclusões Acadêmicas | `narrativa.consultas.elegivel` (`exists`) | Regra da trajetória (FR-009) e item de navegação | Institucional |
| Campanhas, Participações (004, 005) | `participacao.entrada.situacao_de_entrada` | Convite do Início | Derivado (situação) |
| Versão da Campanha (002) | Conteúdo da Versão + `percurso.maximo_restante` | "No máximo N partes" em `/formacoes/` (FR-014) | Derivado |
| Ambiente | `renderizador.disponivel()` (022) | Atalho do vídeo | — |

**Não lidos:** Resposta, Formação Declarada (fora do redirecionamento do declarante),
Contato da Pessoa, agregados de comunidade, snapshot, exportação.

## Estruturas de apresentação (não persistidas)

- **Item de navegação.** `rotulo`, `endereco`, `atual` (contracts/navegacao.md).
- **Início.**
  - `sintese`: texto ou nada;
  - `formacoes`: linhas com `texto` e `origem`;
  - `derivados`: até 2;
  - `acoes`: itens com `rotulo` e `endereco`;
  - `convite`: `titulo`, `texto`, `acao` ou nada.

  É montado a cada requisição a partir da `TrajetoriaNarrativa` e da `SituacaoDeEntrada`, sem
  cache e sem histórico (como E3 da 021).

## Mudança de regra (sem mudança de dado)

| Função | Antes | Depois |
|---|---|---|
| `narrativa.consultas.elegivel(pessoa)` | Existe Participação concluída ancorada em Conclusão da Pessoa | `pessoa.conclusoes.exists()` (FR-009). O módulo deixa de importar `Participacao` |
