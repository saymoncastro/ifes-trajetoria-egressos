# Feature Specification: Convergência visual C — página pública e área autenticada do Portal

**Feature Branch**: `claude/032-convergencia-visual` (PR 1); a área autenticada vai em PR próprio
**Created**: 2026-10-11
**Status**: Implementação autorizada pelo solicitante em 2026-10-11, na demonstração, em dois
PRs: (1) fundação visual e página pública; (2) Início, navegação com "Participação" e estados
vazios. Checkpoint 1 **NÃO APLICADO**.
**Input**: Solicitante, 2026-10-11: a convergência C (mockups "C · Convergência", página
pública e área autenticada, desktop 1440) é a direção visual do Portal. Decisões: Bricolage
Grotesque nos títulos e Atkinson Hyperlegible no texto, hospedadas localmente (Bricolage
provisória até a ACS); navegação com "Participação"; implementar sem nova rodada de
protótipos. Nenhum modelo, fluxo ou funcionalidade nova.

## Contexto

| Fato verificado | Fonte | Consequência |
|---|---|---|
| Os dados dos mockups já existem: formações com origem (021), oportunidades com o motivo (025), encontros como categoria "Eventos" (025), contribuição com o marco de contato (026), convite da pesquisa (007), card (021) | Código; specs 021, 025, 026 | Feature só de apresentação e navegação |
| A ADR 0009 fixava `system-ui` e h1 de 40 px | ADR 0009, decisão 4 | Revista em 2026-10-11 (fontes locais, escala) |
| Vedações de vocabulário: "turma", "conectad", "comunidade", saudação; slogan "continua" fora | ADR 0009, decisões 6 e 7; 029 | Os textos dos mockups são ajustados (tabela abaixo) |
| "Comunidade" só entra nas telas com as capacidades F ou E1 | Roadmap, revisão 12 (PR #59) | O menu público usa "Encontros" |
| O Início não lê contato; a 020 nunca mostra o e-mail guardado; o contato é imutável | 024 FR-017; 020 E5 | O bloco do e-mail é só convite, sem situação nem "remover" |
| A 026 não tem estados de atendimento | D-2601 | "1 contribuição enviada", nunca "em andamento" |
| Sem JavaScript | 015; 024 | Sem botão "Compartilhar"; o card se baixa por link |
| O celular é a referência de qualidade | ADR 0009, decisão 2 | Os mockups são de desktop: a composição do celular é definida aqui |

## Ajustes de texto em relação aos mockups

| Mockup | Implementação | Motivo |
|---|---|---|
| "Sua história com o Ifes continua." | "Sua história com o Ifes" | Slogan pendente com a ACS (D2) |
| Menu "Comunidade" | "Encontros" | Revisão 12 |
| "Sua conexão com o Ifes não precisa terminar" | "o curso terminou; a relação com o Ifes pode continuar" | "conectad" (decisão 7) |
| "a turma", "A turma." | retirados | "turma" (decisão 7) |
| "Você não se formou sozinho." | "Ninguém se forma sozinho." | Linguagem neutra |
| "Entrar no meu espaço" | "Conhecer o Portal" | 029 FR-008; 018 FR-061 |
| "Que bom ver você de novo." | retirado | Saudação (decisão 7); errado no primeiro acesso |
| "E-mail… Não informado… remover quando quiser" | convite para informar, sem situação | 024 FR-017; 020 E5; contato imutável |
| "1 contribuição em andamento" | "1 contribuição enviada" | D-2601 |
| "Compartilhar" | retirado | Sem JavaScript |
| "Suas respostas ajudam o Ifes a melhorar o curso" | "Responder é como você atualiza sua trajetória com o Ifes" | Texto vigente (024) |
| Grade de quadrados com círculo vermelho | retirada | Reproduz a marca (DP-3202) |
| Card desenhado e inclinado | card real da 021 | 029 FR-009, FR-010 |

## User Scenarios & Testing

### US1 — A página pública comunica a relação com força visual (P1, PR 1)

**Independent Test**: medir a página servida a 320, 375, 768, 1024 e 1440 px, com fonte a 100%
e 200%; capturas reais a 375, 1024 e 1440.

1. **Dado** um visitante a 375×812, **então** vê sem rolar o título, a frase e "Conhecer o
   Portal".
2. **Dado** 1280×720, **então** vê título, frase, chamada e o início da linha da trajetória.
3. **Dado** qualquer largura, **então** a linha Ingresso → Formação → Conclusão → Hoje →
   Adiante é legível (horizontal a partir de 768 px, vertical abaixo).

### US2 — O Início reúne trajetória, oportunidades, encontros e participação (P1, PR 2)

**Independent Test**: personas da demonstração com 1 e 3 formações, com e sem oportunidades,
encontro, pesquisa e contribuição.

1. **Dado** um egresso com Conclusão, **então** vê o título, a frase de proveniência, o card,
   a linha das próprias formações com "Hoje" e "Adiante".
2. **Dado** um encontro pertinente (categoria Eventos), **então** vê "Ninguém se forma
   sozinho" com esse encontro; sem encontro, a seção não existe.
3. **Dado** oportunidades pertinentes, **então** vê a principal com o motivo; sem nenhuma, a
   seção não existe e o "Hoje" diz que não há oportunidade divulgada agora.
4. **Dado** a participação, **então** vê a contribuição (ou o convite para contribuir), o
   e-mail (convite, sem situação) e, por último, o convite da pesquisa conforme a 007.
5. **Dado** uma Pessoa sem Conclusão, **então** o Início segue a 024 (sem linha, sem
   oportunidades, sem contribuição).

### US3 — Navegação com "Participação" (P1, PR 2)

1. **Dado** um egresso com Conclusão, **então** a navegação tem Início, Minha trajetória,
   Oportunidades e Participação. Sem Conclusão: Início e Participação.
2. **Dado** `/participacao/`, **então** vê os mesmos blocos de participação do Início, com
   um h1, e chega a Contribuir, Suas contribuições, Pesquisa (`/formacoes/`) e Meu e-mail.
3. **Dado** qualquer tela de contribuição, `/formacoes/`, `/meu-email/` ou a confirmação da
   participação, **então** "Participação" é o item atual. Todos os destinos atuais continuam.

### Edge Cases

- Fonte não carregada: o texto aparece em `system-ui` desde o início (`font-display: swap`).
- 320 px com fonte a 200%: títulos grandes quebram a palavra em vez de alargar a página.
- Muitas formações: a linha do Início quebra em mais de uma fileira, em ordem.
- Portal desligado: nenhuma rota nova existe; o shell da 015 não carrega fonte nenhuma.

## Requirements

**Fundação visual (PR 1)**

- **FR-001**: O Portal DEVE servir Atkinson Hyperlegible (texto) e Bricolage Grotesque
  (títulos) da própria aplicação, em woff2, por `/fontes/<arquivo>`, só com o Portal ligado,
  com cache longo e lista fechada de arquivos. As licenças OFL DEVEM ficar junto dos
  arquivos. Nenhuma requisição a terceiros.
- **FR-002**: O instrumento, `/acesso/`, a declaração e o shell sem o Portal NÃO DEVEM
  carregar as fontes nem os tokens novos (`tests/portal/referencia_shell.html` intacto).
- **FR-003**: Tokens: os atuais mais os quatro da revisão da ADR 0009. Contraste AA medido
  em todo par de texto novo; texto pequeno nunca em `#2f9e41`.
- **FR-004**: Escala: h1 até ~7,5 rem (pública) e ~5 rem (Início) a partir de 1024 px; até
  2,75 rem no celular. Títulos quebram palavra quando preciso (sem rolagem horizontal).

**Página pública (PR 1)** — revisa a ordem da 029 FR-004 e a composição da FR-011

- **FR-005**: Ordem: reconhecimento com a linha da trajetória → como funciona (3 passos) →
  encontros ("Ninguém se forma sozinho", com o encontro de exemplo) → oportunidades (a
  formação concluída → a oportunidade, com o motivo) → contribuição e participação (formas,
  pesquisa e e-mail opcionais) → o card real e a chamada final.
- **FR-006**: Menu da página: Encontros, Oportunidades e Contribuir (âncoras) e "Entrar"
  (`/entrar/`). Chamadas: "Conhecer o Portal" no topo e no fim; "Entrar para oferecer" na
  contribuição; "Ver como funciona" por âncora.
- **FR-007**: Continuam valendo da 029: FR-001 a FR-003 (só apresentação, nada consultado),
  FR-006 (finalidade do e-mail), FR-007 (vocabulário), FR-009 e FR-010 (exemplos com selo,
  mesmas formações do card, sem link real), FR-013 (acessibilidade).

**Área autenticada (PR 2)** — revisa a 024 FR-016, FR-021 a FR-023 e a 026 FR-011

- **FR-008**: Início, nesta ordem: reconhecimento (título, proveniência, números do ano
  quando houver, card e ações) → linha das formações com "Hoje" e "Adiante" → encontros
  (só com encontro pertinente) → oportunidades (só com item pertinente) → participação:
  contribuição, e-mail e, por último, o convite da pesquisa (ADR 0009, decisão 8).
- **FR-009**: "Hoje" diz quantas oportunidades há para a formação, com link, ou que não há
  nenhuma divulgada agora. "Adiante" diz quantas contribuições foram enviadas, com link a
  Suas contribuições, ou convida a contribuir. Sem "em andamento".
- **FR-010**: "Oportunidade" é admitida no Início também no "Hoje" e na seção de
  oportunidades (revisa 024 FR-021). "pesquisa" continua só no convite, na navegação e no
  cabeçalho.
- **FR-011**: Navegação: Início, Minha trajetória e Oportunidades (com Conclusão) e
  Participação. Página `/participacao/` com os blocos de participação; "Participação" é o
  item atual também nas telas da contribuição, em `/formacoes/`, `/meu-email/` e na
  confirmação da participação. Nenhuma rota atual muda.
- **FR-012**: Nada é inferido além do que as regras atuais calculam: pertinência da 025,
  situação da 007, manifestações da 026. O Início continua sem ler Resposta nem contato.

## Success Criteria

- **SC-001**: Sem rolagem horizontal de 320 a 1440 px, fonte a 100% e 200%, nas telas
  alteradas.
- **SC-002**: Primeira tela: 375×812 com título, frase e chamada (pública) ou título e
  primeiro fato (Início); 1280×720 com título, frase e chamada.
- **SC-003**: Um h1 por tela; alvos ≥ 44 px; contraste AA nos pares novos; sem JavaScript.
- **SC-004**: Nenhuma requisição externa; fontes servidas com cache longo; shell da 015
  idêntico.
- **SC-005**: Vocabulário vedado ausente; ajustes da tabela acima verificados em teste.
- **SC-006**: Suíte completa passando; testes de requisitos revisados atualizados com nota.
- **SC-007**: Capturas reais a 375, 1024 e 1440 px, comparadas com os mockups C. Passar nos
  testes não basta: a identidade precisa ficar substancialmente melhor que a 029.

## Requisitos revisados

| Origem | Revisão |
|---|---|
| ADR 0009, decisão 4 | Fontes locais e escala (revisão de 2026-10-11) |
| 029 FR-004, FR-008, FR-011 | Ordem, chamadas e composição da convergência C (FR-005, FR-006) |
| 024 FR-016 | Ordem do Início (FR-008) |
| 024 FR-021 | "Oportunidade" também no "Hoje" (FR-010) |
| 024 FR-022, FR-023; 025; 026 FR-011 | Navegação com "Participação" (FR-011) |
| 015 FR-018 | Fontes servidas só no Portal (FR-001, FR-002) |

## Decisões Pendentes

- **DP-3201 — DECISÃO PENDENTE (ACS):** Bricolage Grotesque como fonte de títulos.
  Alternativa: Open Sans.
- **DP-3202 — DECISÃO PENDENTE (ACS):** padrões decorativos derivados da marca Ifes.
- **D2, DP-801:** nome, slogan e textos definitivos.
- **Checkpoint 1:** NÃO APLICADO; recomenda-se aplicá-lo sobre esta versão.

## Out of Scope

Comunidade (030, 031, E1); novas formas de contribuição; recomendação; mudanças no
instrumento; fotografia (DP-2106); dados fictícios fora da demonstração.
