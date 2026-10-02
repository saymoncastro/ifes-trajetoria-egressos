# Contrato: rotas do acompanhamento da coleta (Feature 011)

As rotas só existem com o modo de demonstração ligado. Desligado, o
`ModoDemonstracaoMiddleware` (008) responde 404 antes de resolver qualquer rota (spec
FR-157). Todas são **GET**; outro método → 405.

| Rota | View | Página |
|------|------|--------|
| `/acompanhamento/` | `campanhas` | Lista de Campanhas do acompanhamento |
| `/acompanhamento/campanhas/<uuid:campanha>/` | `campanha` | Detalhe operacional, com `?recorte=<valor>` opcional |

Nenhuma outra rota. Não há rota de escrita, exportação, API, drill-down nem configuração.

## Ordem de verificação (decorador `@acompanhamento`, o mais externo)

| Passo | Condição | Resposta |
|-------|----------|----------|
| 1 | Sem operador identificado | **302** → `/demonstracao/operador/?destino=acompanhamento` |
| 2 | Operador sem vínculo ativo | **403**, recusa "sem atuação" |
| 3 | `escopo_de_acompanhamento(vinculos) is None` | **403**, recusa "sem atuação" |
| 4 | (detalhe) Campanha inexistente | **404** |
| 5 | (detalhe) Campanha não visível para o escopo | **403**, recusa "fora do escopo", sem dado da Campanha |
| 6 | (detalhe) `recorte` presente e fora do vocabulário | **404** |
| 7 | — | **200** |

Detalhes:

- Os passos 4 a 6 vêm depois de 1 a 3. Sem vínculo ativo, nunca há 404 de Campanha.
- O passo 5 usa `campanhas_visiveis(escopo)`, a mesma função da lista.

## Recusas (403)

Mesma natureza das recusas da 010 (010 FR-043, FR-044): título "Acesso não permitido",
texto operacional e links "Voltar ao acompanhamento" (se houver atuação) e "Trocar
operador fictício".

| Variante | Texto (revisável em `apresentacao.py`) |
|----------|-------------------------------------|
| Sem atuação | "Não há vínculo institucional ativo para este operador. Sem vínculo ativo, o acompanhamento da coleta não pode ser usado." |
| Fora do escopo | "Esta Campanha não está no escopo de acompanhamento da sua atuação." |

A recusa **não** contém nome, período, instrumento, critério, unidade ou número da
Campanha, nem lista de vínculos.

## `?recorte=`

Valores: `unidade`, `curso`, `nivel`, `modalidade`, `forma-oferta`, `ano-conclusao`.

| Situação | Resultado |
|----------|-----------|
| Ausente | `unidade` se oferecido; senão `curso` |
| Valor da lista | Esse recorte. `unidade` é atendido mesmo quando não oferecido (CSAEG de unidade única): só contém dados do escopo |
| Valor fora da lista, repetido ou combinado | **404** |

Recortes oferecidos (FR-057):

- todos os seis no escopo institucional ou com mais de uma unidade;
- sem `unidade` quando o escopo tem uma única unidade.

## Lista — conteúdo (FR-040, FR-041)

Por Campanha visível:

| Coluna | Conteúdo |
|--------|----------|
| Nome | Link para o detalhe |
| Instrumento | Ver research R11 |
| Período | "dd/mm/aaaa a dd/mm/aaaa" ou "Período não definido" |
| Situação | EM PREPARAÇÃO, EM COLETA ou ENCERRADA, por extenso |
| Elegíveis atuais | No escopo |
| Participações iniciadas | No escopo |
| Participações concluídas | No escopo |

Demais regras:

- Ordem: `(inicio desc, nulos por último; nome; id)`. A ordem é determinística e sem
  significado de prioridade.
- Texto permanente: "Números calculados no momento da consulta. Elegíveis atuais é a
  população elegível atual, não o número de pessoas: cada formação concluída conta
  separadamente."
- Lista vazia: "Nenhuma Campanha no escopo da sua atuação."
- Sem taxas na lista.

## Detalhe — conteúdo (FR-043 a FR-046, FR-050 a FR-061)

1. Trilha: Acompanhamento da coleta › <nome>.
2. `h1` com o nome. Dados: instrumento; período; situação; aberta em (se houve);
   encerrada em e forma (antecipada ou fim do período), se houve.
3. Aviso do estado (research R10).
4. **Resumo**, na ordem abaixo:

   | Indicador | Definição curta |
   |-----------|-----------------|
   | Elegíveis atuais | "Formações concluídas que atendem hoje aos critérios da Campanha (população elegível atual)." |
   | Participações iniciadas | "Participações existentes nesta Campanha, inclusive as ainda sem respostas." |
   | Participações concluídas | "Participações com conclusão registrada." |
   | Em andamento / Iniciadas e não concluídas | "Participações iniciadas sem conclusão registrada." |
   | Taxa de início | "Participações iniciadas ÷ elegíveis atuais." |
   | Taxa de conclusão | "Participações concluídas ÷ elegíveis atuais." |

5. **Recorte**: `nav` com os recortes oferecidos e a tabela do recorte ativo.
   - Colunas: dimensão (no curso: Unidade e Curso; a coluna Unidade é omitida quando o
     escopo tem uma única unidade), Elegíveis atuais, Iniciadas, Concluídas, Taxa de
     conclusão.
   - Legenda: "<Recorte> — dados do registro acadêmico institucional".
   - Linha final de total, igual ao resumo.
6. Rodapé: momento da consulta (data e hora locais), não gravado.

Termos ausentes de toda página: "dashboard", "KPI", "funil", "abandono", "desistência",
"ranking", "melhor", "pior", "questionários integralmente respondidos", "role",
"permission", "scope".

## Página de escolha de operador (010, ajuste de demonstração)

| Rota | Mudança |
|------|---------|
| `GET /demonstracao/operador/?destino=acompanhamento` | Repassa `destino` num campo oculto do formulário de escolha. Mostra links "Editor do instrumento" e "Acompanhamento da coleta" para o operador em uso |
| `POST /demonstracao/operador/escolher/` | Redireciona para `/acompanhamento/` se `destino == "acompanhamento"`; qualquer outro valor ou ausência → `/editor/` (comportamento atual) |

Não há URL arbitrária nem `next`.
