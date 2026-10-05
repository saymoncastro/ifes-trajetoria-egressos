# Catálogo: cenários da fonte simulada

Conjunto canônico e determinístico da fonte simulada (FR-026 a FR-029). Fica em
`trajetoria/fonte_academica/cenarios.py`, com código de fonte `simulada`. Esse código é o
que identifica, na proveniência, que os dados vieram da fonte simulada.

**Todos os dados são fictícios.** O sobrenome "Exemplo" e o prefixo `SIM-` marcam isso
de forma visível. Unidades e cursos são plausíveis no Ifes (as listas do instrumento
atual servem de referência). Isso não declara quais valores existem na fonte real
(DP-004, DP-007).

## Situação acadêmica interna da fonte simulada

Cada registro declara uma situação. Só `concluida` é reconhecida como conclusão (R4).
As demais são exemplos de vocabulário de fonte e não são vocabulário do NIAE.

| Situação declarada | Reconhecida? |
|--------------------|--------------|
| `concluida` | sim |
| `matricula_ativa` | não |
| `evasao` | não |
| `transferencia` | não |
| valor não mapeado (`"situacao_legada_x"`) | não (desconhecida) |
| ausente (`None`) | não (não informada) |

## Pessoas e registros

Legenda: Téc. = Técnico; Grad. = Graduação; Pós = Pós-graduação; Pres. = Presencial;
EaD = A distância; "—" = `None` (não informado pela fonte).

| Cen. | Pessoa | Nome | Registro | Situação | Curso | Unidade | Nível | Modal. | Oferta | Conclusão |
|------|--------|------|----------|----------|-------|---------|-------|--------|--------|-----------|
| A | SIM-P-0001 | Ana Exemplo | SIM-C-0001 | concluida | Tecnologia em Análise e Desenvolvimento de Sistemas | Serra | Grad. | Pres. | — | 2022-12-16 |
| B | SIM-P-0002 | Bruno Exemplo | SIM-C-0002 | concluida | Técnico em Edificações | Vitória | Téc. | Pres. | Integrado | 2014 (só ano) |
| B | SIM-P-0002 | | SIM-C-0003 | concluida | Bacharelado em Engenharia Civil | Vitória | Grad. | Pres. | — | 2020-07-10 |
| C | SIM-P-0003 | Maria Exemplo | SIM-C-0004 | concluida | Tecnologia em Análise e Desenvolvimento de Sistemas | Serra | Grad. | Pres. | — | 2022 (só ano) |
| C | SIM-P-0003 | | SIM-C-0005 | concluida | Especialização em Informática na Educação | Cefor | Pós | EaD | — | 2025-03-28 |
| D | SIM-P-0004 | Diego Exemplo | SIM-C-0006 | concluida | Técnico em Química | Vila Velha | Téc. | Pres. | Integrado | 2012 (só ano) |
| D | SIM-P-0004 | | SIM-C-0007 | concluida | Licenciatura em Química | Vila Velha | Grad. | Pres. | — | 2017 (só ano) |
| D | SIM-P-0004 | | SIM-C-0008 | concluida | Mestrado Profissional em Química | Vila Velha | Pós | Pres. | — | 2020 (só ano) |
| E | SIM-P-0005 | Elisa Exemplo | SIM-C-0009 | concluida | Técnico em Agropecuária | Alegre | Téc. | Pres. | Integrado | 2019 (só ano) |
| F1 | SIM-P-0006 | João Exemplo | SIM-C-0901 | matricula_ativa | Bacharelado em Sistemas de Informação | Cachoeiro de Itapemirim | Grad. | Pres. | — | — |
| F2 | SIM-P-0007 | Fernanda Exemplo | SIM-C-0010 | concluida | Técnico em Mecânica | Cariacica | Téc. | Pres. | Subsequente | 2018 (só ano) |
| F2 | SIM-P-0007 | | SIM-C-0902 | matricula_ativa | Bacharelado em Engenharia Mecânica | Cariacica | Grad. | Pres. | — | — |
| F3 | SIM-P-0008 | Gustavo Exemplo | SIM-C-0903 | evasao | Técnico em Logística | Viana | Téc. | Pres. | Concomitante | — |
| F3 | SIM-P-0008 | | SIM-C-0904 | transferencia | Licenciatura em Matemática | Cachoeiro de Itapemirim | Grad. | Pres. | — | — |
| F3 | SIM-P-0008 | | SIM-C-0905 | situacao_legada_x | Técnico em Informática | Colatina | Téc. | Pres. | Subsequente | — |
| F3 | SIM-P-0008 | | SIM-C-0906 | (ausente) | Tecnologia em Logística | Cariacica | Grad. | Pres. | — | — |
| Sem nome | SIM-P-0009 | — | SIM-C-0011 | concluida | Técnico em Informática | Colatina | Téc. | Pres. | Subsequente | 2021 (só ano) |
| Homônimos | SIM-P-0010 | Carla Exemplo | SIM-C-0012 | concluida | Licenciatura em Pedagogia | Vitória | Grad. | Pres. | — | 2016 (só ano) |
| Homônimos | SIM-P-0011 | Carla Exemplo | SIM-C-0013 | concluida | Tecnologia em Redes de Computadores | Serra | Grad. | Pres. | — | 2023 (só ano) |

| Declaração 019 | SIM-P-0012 | Helena Exemplo | SIM-C-0014 | concluida | Técnico em Informática | Serra | Téc. | Pres. | Subsequente | 2004 (só ano) |

## Cenários sem registro próprio

| Cen. | Como é provocado | Resultado esperado |
|------|------------------|--------------------|
| G | `obter_pessoa("SIM-P-9999")`, `obter_conclusao("SIM-C-9999")` | `PessoaInexistente`, `ConclusaoInexistente` |
| H | fonte simulada construída com `indisponivel=True` | `FonteAcademicaIndisponivel` em qualquer operação |
| Repetição | incorporar o conjunto canônico 3× em ordens diferentes | mesmas linhas e mesmos UUIDs |
| Divergência | fonte simulada construída com **variante** do conjunto canônico, mesmo código de fonte, só nos testes: (i) curso de SIM-C-0001 alterado; (ii) SIM-C-0003 ausente; (iii) SIM-C-0002 atribuída a SIM-P-0001; (iv) nome de SIM-P-0009 passa a existir | divergências `ATRIBUTOS_DIFERENTES`, `AUSENTE_NA_FONTE`, `CONCLUSAO_DE_OUTRA_PESSOA`, `ATRIBUTOS_DIFERENTES`; nada alterado |

## Cobertura exigida pela spec

| Requisito | Atendido por |
|-----------|--------------|
| A, B, C, D, E (FR-027) | linhas A a E |
| Pessoa com ≥ 3 conclusões | SIM-P-0004 |
| Atributo "não informado" | forma de oferta das graduações e pós; SIM-P-0009 sem nome |
| Datas só com ano e data completa | B, C, D, E (ano) e A, B, C (data) |
| "Experiência esperada" | SIM-P-0003 |
| F: matrícula ativa, evasão, transferência, desconhecida, não informada | F1, F2, F3 |
| F: pessoa só com registros não concluídos | F1, F3 |
| F: pessoa com conclusão e registro não concluído | F2 |
| G, H | tabela acima |

> Observação: "—" em forma de oferta de graduação e pós significa "não informado pela
> fonte", e não "não se aplica". Se a fonte real precisar distinguir os dois casos, isso
> será resolvido no vocabulário canônico (DP-007).

## Dados de verificação — fictícios

Dados artificiais da 018; CPFs gerados com dígitos verificadores válidos, sem dados reais.

| Pessoa | CPF | Nascimento | Caso |
| --- | --- | --- | --- |
| SIM-P-0001 Ana | 000.000.001-91 | 1998-04-12 | Uma formação |
| SIM-P-0002 Bruno | 111.444.777-35 | 1990-09-03 | Duas formações |
| SIM-P-0003 Maria | 000.000.002-72 | 1997-11-25 | Unidades diferentes |
| SIM-P-0004 Diego | 000.000.003-53 | 1994-02-08 | Três formações |
| SIM-P-0005 Elisa | — | 2001-06-30 | Sem CPF |
| SIM-P-0006 João | 000.000.004-34 | 2003-03-14 | Sem conclusão |
| SIM-P-0007 Fernanda | 000.000.005-15 | 1999-08-21 | Conclusão e matrícula ativa |
| SIM-P-0008 Gustavo | 000.000.006-04 | 2000-01-17 | Nenhum concluído |
| SIM-P-0009 sem nome | 000.000.007-87 | — | Sem data |
| SIM-P-0010 Carla | 000.000.008-68 | 1992-05-05 | CPF compartilhado |
| SIM-P-0011 Carla | 000.000.008-68 | 1995-10-19 | CPF compartilhado |

| SIM-P-0012 Helena | 000.000.010-82 | 1980-06-30 | Fonte digital, excluída do preparo (019) |

O par 000.000.009-49 / 2001-06-30 é fictício e inexistente na fonte, para testar declaração.


## Nota de revisão pela Feature 021 (2026-10-04)

### Contexto da trajetória (021)

Os valores são fictícios. Ficam em `cenarios.py` (`COMPLEMENTOS`, `AGREGADOS`) e são
servidos por `ContextoSimulado`, que é separado da `FonteSimulada`. Não afirmam que a fonte
real fornece ingresso ou agregados (021 FR-064).

| Dado | Valor fictício |
|---|---|
| Complemento `SIM-C-0001` (Ana, TADS) | ingresso 2019 |
| Demais conclusões | sem complemento |
| Conclusões de TADS na unidade Serra em 2022 | 27, apurado em 2026-01-31 |
| Conclusões da unidade Serra em 2022 | 812, apurado em 2026-01-31 |
| Demais recortes (Vila Velha, Cefor, …) | sem agregado |

Os dois agregados são coerentes com as conclusões simuladas do recorte: valor maior ou
igual ao número delas (021 FR-060).

Referência: [021 — Minha Trajetória: narrativa visual personalizada](../../021-minha-trajetoria-narrativa/spec.md).
