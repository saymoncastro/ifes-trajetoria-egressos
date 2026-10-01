# Quickstart: validar a Feature 005

Guia para comprovar, de ponta a ponta, que a feature atende a spec. Pré-requisitos, banco
e variáveis são os mesmos da
[Feature 001](../001-nucleo-academico-fonte-simulada/quickstart.md#pré-requisitos):
`uv`, PostgreSQL 16+ local e nenhuma variável obrigatória.

> **Somente dados fictícios.** DP-504 (base legal e consentimento) bloqueia o uso desta
> capacidade com egressos reais. Testes e exemplos usam a fonte simulada da 001 e
> instrumentos mínimos de teste.

## Preparar

```bash
uv sync --extra dev
```

```bash
uv run python manage.py migrate
```

A migração cria só as tabelas do app `participacao` (`Participacao`, `Resposta`,
`RespostaOpcao`). Nenhuma tabela das Features 001 a 004 é alterada.

```bash
uv run python manage.py makemigrations --check --dry-run
```

## Validar

Suíte completa, incluindo 001 a 004, que devem continuar passando (o teste de escopo da
004 foi corrigido — [plan.md](plan.md#necessidade-de-voltar-à-spec-ou-às-features-anteriores)):

```bash
uv run pytest
```

Só esta feature:

```bash
uv run pytest tests/participacao
```

```bash
uv run ruff check .
```

| Arquivo de teste | O que comprova | Spec |
|------------------|----------------|------|
| `tests/participacao/test_participacao_modelo.py` | CHECKs e UNIQUEs do [modelo](data-model.md) por escrita direta no ORM; `PROTECT` em Campanha, Conclusão, Pergunta e Opção; `CASCADE` só de Resposta para RespostaOpcao; limite documentado (≥ 1 seleção não é garantido pelo banco) | FR-006, FR-018, FR-026, FR-030 |
| `tests/participacao/test_participacao_inicio.py` | Início válido; repetição devolve a existente sem alterar; repetição com Campanha encerrada devolve a existente; nova Participação em Campanha encerrada ou em preparação rejeitada; Conclusão não elegível com pendências; as duas violações juntas; nenhum convite ou token | US1, US2, FR-011–FR-016 |
| `tests/participacao/test_participacao_respostas.py` | Os quatro tipos: escolha única válida e inválida (outra Pergunta, mesmo texto, nenhuma, coleção, texto); múltipla válida, duplicata colapsada, ordem irrelevante, vazia rejeitada, Opção estranha rejeita tudo, exclusividade inexistente; texto exato, vazio rejeitado; escala nos limites, abaixo, acima, fracionária, texto, lógico; complemento válido em única e múltipla, sem Opção que o admite, vazio, substituição que o apaga | US3–US6, US8, FR-023–FR-032 |
| `tests/participacao/test_participacao_rascunho.py` | Substituir no lugar (mesmo `id`); remover; remover inexistente; obrigatória removível; navegação não aplicada (mudar resposta com regra não altera outras); atomicidade da substituição de múltipla escolha (valor anterior intacto após rejeição); Participação parcial sem conclusão | US7, FR-033–FR-038, FR-051 |
| `tests/participacao/test_participacao_coleta.py` | Leitura e escrita depois do encerramento explícito e por fim do período; último dia aceito, dia seguinte rejeitado; nada apagado; elegibilidade não reavaliada após a criação (Conclusão alterada por ORM para fora dos critérios continua editável) | US11, FR-034, FR-039–FR-041 |
| `tests/participacao/test_participacao_longitudinal.py` | Mesma Conclusão em Campanhas 2025, 2027 e 2030; alterações isoladas; nada copiado; duas Conclusões da mesma Pessoa na mesma Campanha; `participacoes_da_conclusao` | US10, FR-007–FR-009, FR-049 |
| `tests/participacao/test_participacao_versao.py` | Pergunta e Opção de outra Versão (2027 × 2028 criada a partir de 2027, textos idênticos) rejeitadas; publicação posterior não muda validação nem leitura | US12, FR-019–FR-022, SC-006, SC-010 |
| `tests/participacao/test_participacao_consulta.py` | `localizar_participacao` sem criar; `respostas_atuais` distingue não respondida; valores tipados; contexto institucional pela Conclusão; resposta de campus divergente da unidade coexiste; nenhuma escrita na Conclusão | US9, FR-042–FR-050, SC-009 |
| `tests/participacao/test_participacao_concorrencia.py` | Ramo `IntegrityError` forçado de forma determinística → `JA_EXISTENTE`, uma Participação; teste real com threads só se estável (R17); escritas repetidas na mesma Pergunta → uma Resposta | FR-006, FR-053 |
| `tests/participacao/test_participacao_aceitacao.py` | As 11 perguntas de sucesso do solicitante ponta a ponta; exatamente três modelos no app; nenhum modelo proibido; modelos das 001–004 sem colunas novas; nenhum valor declarado nas mensagens de rejeição | SC-001–SC-011 |

Resultado esperado: todos os testes passam, sem rede e sem depender do relógio real.
Toda operação temporal recebe `agora` explícito nos testes.

## Ver uma Participação no shell

```bash
uv run python manage.py shell
```

Roteiro (dados fictícios; instrumento mínimo publicado pelas operações da 002; Campanha
aberta pelas operações da 004):

1. Montar uma Versão de teste com uma pergunta de cada tipo e uma Opção "Outro:" com
   complemento; publicá-la.
2. Criar a Campanha, definir período e abrir com `agora` dentro do período.
3. Incorporar um cenário da fonte simulada e chamar `iniciar_participacao` duas vezes:
   a segunda devolve `JA_EXISTENTE`.
4. Responder cada tipo; substituir a escolha múltipla; remover o texto.
5. `respostas_atuais(participacao)`: a pergunta de texto não aparece; as demais têm o
   último valor.
6. Repetir uma escrita com `agora` depois do fim do período: `COLETA_NAO_ADMITIDA`, e a
   leitura continua igual.
