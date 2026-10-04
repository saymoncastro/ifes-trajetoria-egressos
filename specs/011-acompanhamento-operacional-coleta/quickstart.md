# Quickstart: validar a Feature 011

Este guia mostra, de ponta a ponta, que o acompanhamento operacional da coleta atende a
spec. Pré-requisitos e banco são os da
[Feature 001](../001-nucleo-academico-fonte-simulada/quickstart.md#pré-requisitos); o
ambiente de demonstração e os operadores fictícios são os da
[Feature 010](../010-governanca-papeis-escopos/quickstart.md).

> **Leitura operacional, agregada e atual.**
>
> - Os números são calculados no momento da consulta. Nada é gravado.
> - "Elegíveis atuais" é a população elegível **atual**, não um denominador histórico
>   (004/DP-408).
> - Nenhum dado individual aparece. Nenhuma ação de Campanha existe.
> - Só existe no modo de demonstração (010/DP-1001).

## Preparar

O banco local é o da Feature 010. O preparo é idempotente: num banco já preparado, ele
só acrescenta a Campanha fictícia de acompanhamento (research R14). Os operadores
fictícios **não mudam**.

```bash
uv sync --extra dev
```

```bash
PGDATABASE=trajetoria_demo uv run python manage.py migrate
```

```bash
PGDATABASE=trajetoria_demo TRAJETORIA_DEMONSTRACAO=1 uv run python manage.py preparar_demonstracao
```

```bash
PGDATABASE=trajetoria_demo TRAJETORIA_DEMONSTRACAO=1 uv run python manage.py runserver
```

| Operador fictício | Vínculo |
|-------------------|---------|
| A | CPAEG, ativo |
| B | CSAEG, unidade Vitória, ativo |
| C | nenhum |

| Campanha fictícia | Estado | Critério de unidades | Versão |
|-------------------|--------|----------------------|--------|
| Demonstração — coleta ampla (008) | EM COLETA | nenhum (população ampla) | cópia publicada |
| Demonstração — coleta sobreposta (008) | EM COLETA | Vila Velha (Pós-graduação) | cópia publicada |
| **Demonstração — rodada em preparação** (011) | EM PREPARAÇÃO, nunca aberta, sem período | nenhum | baseline em RASCUNHO |

*(Revisado pela ADR 0004 — ver `docs/adr/0004-abrangencia-da-campanha-nao-e-foco-de-mobilizacao.md`.)* Critério de Campanha é abrangência do instrumento, não foco de mobilização. A Campanha
nunca aberta se chamava "Demonstração — acompanhamento Serra e Vitória" e era restrita a
essas unidades; a "coleta ampla" tinha ano ≥ 2015 e seis unidades. Os números do roteiro
abaixo já refletem o cenário revisado.

Confirme que não há migração nova:

```bash
uv run python manage.py makemigrations --check --dry-run
```

Resultado esperado: "No changes detected".

## Validar automaticamente

```bash
uv run pytest
```

```bash
uv run pytest tests/acompanhamento tests/governanca
```

```bash
uv run pytest tests/interface/test_demonstracao_operador.py tests/campanha
```

Resultado esperado: tudo verde. As suítes do editor (009/010), da jornada (005–008) e da
Campanha (004) continuam passando sem mudança de comportamento.

## Roteiro manual

Abra `http://localhost:8000/acompanhamento/`.

| # | Ação | Resultado esperado | Caso / SC |
|---|------|--------------------|-----------|
| 1 | Abrir sem operador | Encaminhado à escolha de operador fictício. Depois de escolher, volta ao acompanhamento | US5.4 |
| 2 | Escolher **C** | Recusa "sem vínculo institucional ativo", sem conteúdo | US5.3 |
| 3 | Escolher **A** (CPAEG) | Lista com as três Campanhas, cada uma com situação, elegíveis atuais, iniciadas e concluídas. Sem taxas, cores ou ordenação por número | A, C; US1 |
| 4 | Abrir "coleta ampla" | Resumo com os seis indicadores e suas definições; taxas 0,0%; aviso "momento da consulta"; 13 elegíveis atuais; recorte por unidade com as sete unidades que têm Conclusões (Serra 3, Vitória 3, Vila Velha 3, Cefor 1, Alegre 1, Cariacica 1, Colatina 1), soma igual ao total | A, B, H; US2, US7 |
| 5 | Trocar para recorte por curso, nível, modalidade, forma de oferta e ano | Uma tabela por vez, troca por link, "não informado" onde faltar atributo (forma de oferta das graduações), soma igual ao total, ano em ordem crescente, rótulo "Ano de conclusão" | M; US8, US9 |
| 6 | Editar o endereço para `?recorte=coorte` | 404 | FR-059 |
| 7 | Abrir "rodada em preparação" como A | "A coleta ainda não começou"; 13 elegíveis atuais; instrumento identificado (baseline em rascunho), com link para o editor | US11; FR-042 |
| 8 | Escolher **B** (CSAEG Vitória) | Lista com "rodada em preparação" e "coleta ampla" (sem critério de unidades); "coleta sobreposta" ausente | D, E; US3 |
| 9 | Abrir essa Campanha como B | 3 elegíveis atuais (só Vitória; nenhum valor de Serra); "Instrumento ainda não publicado", sem nome nem link; sem opção de recorte por unidade; recorte por curso sem coluna Unidade | D; US4; US11.2 |
| 10 | Colar o endereço de "coleta sobreposta" como B | Recusa "fora do escopo", sem nome nem números da Campanha | N; US5.1 |
| 11 | Em outra aba, escolher a Pessoa fictícia Ana Exemplo (Serra, 2022) em `/demonstracao/` e iniciar a pesquisa; como A, atualizar "coleta ampla" | Participações iniciadas 1; em andamento 1; taxa de início 7,7% | J; US6.2 |
| 12 | Concluir a Participação da Ana pela jornada e atualizar | Concluídas 1; em andamento 0; taxa de conclusão 7,7%. Concluir só com "Não" na Q1 também conta como concluída | K; FR-033 |
| 13 | Como A, ver o recorte por curso da "coleta ampla" | "Tecnologia em Análise e Desenvolvimento de Sistemas" na linha de Serra, com 2 elegíveis, 1 iniciada e 1 concluída. Nenhum nome de Pessoa em nenhuma página | SC-005 |
| 14 | Navegar só por teclado; 320 px; zoom 200%; JavaScript desligado | Tudo operável; só a tabela rola horizontalmente; "—" anunciado como "não se aplica" | US13; SC-011 |
| 15 | Desligar o modo (`TRAJETORIA_DEMONSTRACAO` ausente) | `/acompanhamento/` responde 404 | FR-157 |

Os casos F (dois CSAEG), G (CPAEG + CSAEG), I (elegíveis = 0), L (encerrada) e as
contagens não nulas de Participações no escopo CSAEG dependem de vínculos, datas ou
Participações que o cenário fictício não fixa. Eles são cobertos pelos testes
automatizados (plan, "Estratégia de testes"). O cenário não cria Campanha EM COLETA
relevante para Vitória, para não alterar a jornada consolidada da 007/008.
