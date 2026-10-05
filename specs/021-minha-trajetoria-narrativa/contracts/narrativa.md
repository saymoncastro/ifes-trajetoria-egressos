# Contrato: `TrajetoriaNarrativa` serializada (versão 1)

`TrajetoriaNarrativa` é consumida pela página, pelo card e, no futuro, pelo renderer de
vídeo da Feature 022 (FR-014). `serializar(narrativa)` produz este formato.

## Garantias

- **Determinismo:** a mesma entrada produz um JSON idêntico. As chaves são emitidas na
  ordem abaixo e as listas também têm ordem definida.
- **Origem:** cada fato traz `origem` (`institucional`, `derivado` ou `agregado`),
  conforme os Princípios III e IV.
- **Sem dados técnicos ou declarados:** não há UUID, código de fonte, id externo, CPF,
  data de nascimento, momento de incorporação, Resposta nem dado de Formação Declarada
  (FR-013).
- **Frases prontas:** o renderizador não gera frase nem aplica regra de dado. Ele só
  dispõe o que recebe.
- **Ausência:** atributo ausente é omitido. Não existe chave com valor `null` para fato
  ausente.

## Forma

```json
{
  "versao_contrato": 1,
  "referencia": "2026-10-04",
  "identidade": {"nome": "Maria Exemplo", "origem": "institucional"},
  "formacoes": [
    {
      "origem": "institucional",
      "curso": "Tecnologia em Análise e Desenvolvimento de Sistemas",
      "unidade": "Serra",
      "nivel": "Graduação",
      "modalidade": "Presencial",
      "ano_conclusao": 2022
    },
    {
      "origem": "institucional",
      "curso": "Especialização em Informática na Educação",
      "unidade": "Cefor",
      "nivel": "Pós-graduação",
      "modalidade": "A distância",
      "ano_conclusao": 2025,
      "data_conclusao": "2025-03-28",
      "relacao": {"tipo": "depois_de", "indice": 0}
    }
  ],
  "marcos": [],
  "derivados": [
    {"tipo": "formacoes_registradas", "valor": 2, "origem": "derivado",
     "regra": "contagem das Conclusões Acadêmicas da Pessoa"},
    {"tipo": "tempo_desde_conclusao", "formacao": 1, "valor": 1, "origem": "derivado",
     "regra": "anos completos entre data_conclusao e referencia"}
  ],
  "contextos_agregados": [],
  "secoes": [
    {"chave": "o_que_o_ifes_registra", "titulo": "…",
     "frases": [{"texto": "O Ifes registra 2 formações concluídas por você.",
                 "origem": "derivado"}]},
    {"chave": "trajetoria_academica", "titulo": "…", "frases": ["…"]},
    {"chave": "outras_formacoes", "titulo": "…", "frases": ["…"]}
  ],
  "compartilhavel": {
    "formacoes": [{"curso": "…", "unidade": "…", "nivel": "…", "modalidade": "…",
                   "ano_conclusao": 2022, "linhas_curso": ["…", "…"],
                   "linhas_detalhe": ["Serra · Graduação · Presencial"]}],
    "formacoes_omitidas": 0,
    "formacoes_registradas": 2,
    "contextos_agregados": [{"metrica": "conclusoes_curso_unidade_ano", "numero": 27,
                             "rotulo": ["conclusões deste curso", "na unidade Serra em 2022"]}],
    "nome_disponivel": true,
    "apuracao": "Dados institucionais apurados em 31/01/2026.",
    "unidade_da_imagem": "Serra"
  }
}
```

## Campos

| Campo | Regra |
|---|---|
| `formacoes[]` | Ordem do model (`ano_conclusao`, `id`). Só os atributos presentes. `ingresso: {"ano": …, "data": …}` só em P2, quando houver e for coerente (FR-051) |
| `formacoes[].relacao` | Só sob research R5: `depois_de` aponta para o índice da única formação do grupo de ano imediatamente anterior |
| `derivados[]` | Tipos fechados: `formacoes_registradas`, `tempo_desde_conclusao` (só com data, FR-020), `primeira_formacao` (só com menor ano único) |
| `contextos_agregados[]` | P2: `{"metrica", "recorte": {"curso"?, "unidade", "ano"}, "valor", "apurado_em", "origem": "agregado"}`. Só agregados selecionados (FR-058 a FR-060) |
| `secoes[]` | Ordem do FR-026, só as presentes (FR-027). `chave` é estável; `titulo` e `texto` vêm do catálogo |
| `compartilhavel` | Só o FR-033. **Sem nome**: a rota acrescenta o nome com `nome=1` e `nome_disponivel` (FR-034). `linhas_curso` e `linhas_detalhe` já quebradas para a linha do tempo do card (research R10, R19); o ano fica fora do detalhe, no nó (FR-077) |
| `compartilhavel.contextos_agregados[]` | *(revisão de 2026-10-05)* Destaques do card (FR-078): `metrica`, `numero` e `rotulo` de duas linhas do catálogo. No máximo um par (métricas 1 e 2), da primeira formação que tiver agregado. Se as duas apurações do par forem distintas, fica só o primeiro destaque: o rodapé tem uma apuração e nenhuma é escolhida por data (FR-059) |
| `compartilhavel.apuracao` | Texto do rodapé do card, só com destaque |
| `compartilhavel.unidade_da_imagem` | Unidade da primeira formação exibida; escolhe a imagem e a legenda da abertura (FR-076). Omitida sem unidade |

## Evolução

- A revisão de 2026-10-05 (card editorial) mudou a forma de `compartilhavel` mantendo a
  versão 1: o contrato ainda não foi publicado fora do PR #30.

- Acrescentar um campo opcional, por exemplo `marcos[]` preenchido em P3, mantém a
  versão 1.
- Mudar o significado ou remover um campo exige `versao_contrato: 2`.
