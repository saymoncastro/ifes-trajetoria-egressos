# Contrato: pertinência, explicação e oráculo da demonstração (025)

## Regra (FR-011, FR-012, FR-014, FR-016)

`pertinentes(oportunidades_em_divulgacao, conclusoes)` → lista de itens:

1. Sem nenhuma Conclusão, a lista é vazia (FR-011, FR-024).
2. Uma oportunidade **sem público** entra no grupo `todos`.
3. Uma oportunidade **com público** entra no grupo `formacao` se, e só se, **alguma Conclusão,
   sozinha,** satisfaz **todos** os critérios definidos:
   - `curso in publico_cursos`, se definido;
   - `nivel in publico_niveis`, se definido;
   - `unidade in publico_unidades`, se definido;
   - por igualdade exata. `NULL` na Conclusão não satisfaz.
4. **Formações citadas:** todas as Conclusões que satisfazem, na ordem da 007.
5. **Ordem:** grupo `formacao` antes de `todos`; dentro do grupo, `inicio` decrescente, depois
   `titulo`, depois `id`.
6. A função é pura: a mesma entrada dá a mesma saída. Ela não lê o relógio nem grava.

## Explicação (FR-013; textos provisórios)

| Caso | Modelo | Exemplo |
|---|---|---|
| Sem público | "Aberta a todos os egressos do Ifes." | — |
| Critério de curso (com ou sem outros) | "Aparece porque você concluiu {formações}." Cada formação é "{curso} ({unidade}, {ano})" | "Aparece porque você concluiu Tecnologia em Redes de Computadores (Serra, 2023)." |
| Sem curso, com nível e/ou unidade | "Aparece porque você concluiu uma formação{ de {nível}}{ na unidade {unidade}}: {formações}." Cada formação é "{curso} ({ano})", com a unidade entre parênteses quando não houver critério de unidade | "Aparece porque você concluiu uma formação de Pós-graduação: Mestrado Profissional em Química (Vila Velha, 2020)." |
| Várias formações | Unidas por vírgula e "e", na ordem da 007 | "… na unidade Vitória: Técnico em Edificações (2014) e Bacharelado em Engenharia Civil (2020)." |
| Dado ausente na formação | O fragmento ausente é omitido, sem "não informado" | "… Técnico em Química (2012)." |

**Linha de origem**, que acompanha todo item:
- "Oferecida pela unidade {unidade_responsavel}", ou "Oferecida pelo Ifes" quando
  institucional;
- seguida de "· site do Ifes: {domínio}" ou "· site externo: {domínio}".

Com vários valores num critério, cita-se só o valor satisfeito pela formação.

## Catálogo fictício da demonstração (FR-042)

`D` é a data local em que o `preparar_demonstracao` roda. O domínio é reservado para
exemplos (`oportunidades.example`). Todos os itens são fictícios.

| # | Título | Categoria | Unidade responsável | Público | Período | Situação | Publicada por |
|---|---|---|---|---|---|---|---|
| O1 | Curso de extensão a distância em Ciência de Dados | Cursos e formação continuada | Ifes (institucional) | — (todos) | D−7 a D+60 | Publicada | operador A (CPAEG) |
| O2 | Especialização em Segurança da Informação | Cursos e formação continuada | Serra | cursos = {Tecnologia em Redes de Computadores, Tecnologia em Análise e Desenvolvimento de Sistemas} | D−3 a D+45 | Publicada | operador A |
| O3 | Mestrado Profissional em Educação: seleção aberta | Cursos e formação continuada | Vitória | níveis = {Pós-graduação} | D−5 a D+30 | Publicada | operador B (CSAEG Vitória) — público além da própria unidade (DP-2502) |
| O4 | Encontro de egressos das engenharias e edificações | Eventos | Vitória | unidades = {Vitória} | D−2 a D+20 | Publicada | operador B |
| O5 | Programa de mentoria em pesquisa aplicada | Pesquisa e extensão | Serra | níveis = {Pós-graduação} **e** unidades = {Serra} | D−6 a D+40 | Publicada | operador A |
| O6 | Programa de estágio em laboratórios parceiros | Carreira e empregabilidade | Vila Velha | níveis = {Técnico} **e** unidades = {Vila Velha} | D−4 a D+25 | Publicada | operador A |
| O7 | Feira de empreendedorismo e inovação | Empreendedorismo | Ifes (institucional) | — | D+10 a D+40 | Publicada (Agendada) | operador A |
| O8 | Ciclo de palestras de carreira 2026 | Carreira e empregabilidade | Ifes (institucional) | — | D−40 a D−1 | Publicada (Encerrada) | operador A |
| O9 | Curso livre de fotografia | Outras iniciativas | Vitória | — | D−10 a D+10 | Publicada e retirada | operador B |
| O10 | Oficina de currículo (rascunho) | Carreira e empregabilidade | Vitória | — | D−1 a D+30 | Rascunho | — |

O5 existe para provar que os critérios não se combinam entre formações diferentes. Maria
tem uma Pós-graduação (Cefor) e uma Graduação na Serra, mas nenhuma formação dela é, ao
mesmo tempo, Pós-graduação e da Serra.

## Oráculo por persona em D (025 SC-002; escrito antes da implementação)

| Persona | "Pela sua formação" (em ordem) | "Para todos os egressos" | Destaque no Início | Não pode aparecer |
|---|---|---|---|---|
| Ana (SIM-P-0001) | O2: "…você concluiu Tecnologia em Análise e Desenvolvimento de Sistemas (Serra, 2022)." | O1 | O2 | O3–O10 |
| Bruno (SIM-P-0002) | O4: "…uma formação na unidade Vitória: Técnico em Edificações (2014) e Bacharelado em Engenharia Civil (2020)." | O1 | O4 | O2, O3, O5–O10 |
| Maria (SIM-P-0003) | O2 (TADS, Serra, 2022); O3: "…uma formação de Pós-graduação: Especialização em Informática na Educação (Cefor, 2025)." | O1 | O2 | **O5**, O4, O6–O10 |
| Diego (SIM-P-0004) | O6: "…uma formação de Técnico na unidade Vila Velha: Técnico em Química (2012)."; O3: "…de Pós-graduação: Mestrado Profissional em Química (Vila Velha, 2020)." | O1 | O6 | O2, O4, O5, O7–O10 |
| Fernanda (SIM-P-0007) | — | O1 | O1 | O2–O10 |
| Carla (SIM-P-0010) | O4: "…na unidade Vitória: Licenciatura em Pedagogia (2016)." | O1 | O4 | demais |
| Carla (SIM-P-0011) | O2: "…Tecnologia em Redes de Computadores (Serra, 2023)." | O1 | O2 | demais |
| Pessoa sem Conclusão (teste) | — | — | sem bloco | todas |

- **Ordem dentro do grupo.** Por `inicio` decrescente: O4 (D−2) > O2 (D−3) > O6 (D−4) > O3 (D−5).
- **Em D+11.** O7 entra em "todos" para todas as personas com Conclusão.
- **Em D+61.** O1 sai.
- **O8, O9 e O10** nunca aparecem.
