# Implementation Plan: Foundations e validação da identidade visual da jornada do egresso

**Branch**: `claude/feature-015-identidade-visual` | **Date**: 2026-10-03 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/015-identidade-visual-jornada/spec.md`

## Summary

Primeira versão real — código de produção — das foundations e da identidade visual da
jornada do egresso, validada por um gate em quatro situações antes do merge. Tudo em
folhas de estilo, templates da jornada, um template SVG da assinatura oficial e um mapa
fixo de variantes de aviso; sem modelo, migração, JavaScript, dependência ou recurso
externo.

Abordagem técnica (detalhes em [research.md](research.md)):

- **Duas camadas de estilo** (R1): `estilo.css` (compartilhada) ganha só os tokens no
  `:root` e as mudanças escopadas em `.pergunta` (jornada + prévia do editor);
  `jornada.css` (nova) é incluída **só** por `interface/base.html` e leva o shell e os
  refinamentos da jornada. Editor e acompanhamento não carregam a camada da jornada —
  fronteira por construção, sem condicional nem duplicação.
- **Tokens e A/B** (R2): propriedades personalizadas; a Direção é definida por duas
  linhas (`--cor-acao`, `--cor-acao-forte`); mergeado em **B**; A gerada só durante a
  validação.
- **Assinatura** (R3): o ZIP oficial da marca sistêmica (`marca-ifes.zip`) foi baixado
  com autorização e **não contém SVG** (só EPS, JPG e PNG). A inclusão da assinatura está
  **bloqueada por D-03** até a ACS fornecer o SVG oficial; quando vier, entra como
  template SVG inline pelo mesmo mecanismo da folha de estilo. Sem a assinatura, a 015
  não passa no gate (SC-001).
- **Shell** (R4): faixa de demonstração recebe os controles de demonstração; cabeçalho
  branco com fio de marca, assinatura e nome do produto em texto; rodapé mínimo.
- **403/404/500 fora** (R5): handlers globais do Django, usados também pelo editor e pelo
  acompanhamento; ficam para a propagação transversal (D8).
- **Questionário** (R6), **feedback** (R7), **trajetória e contexto** (R8): regras visuais
  da spec, com duas mudanças mínimas de marcação (situação da formação; destaque da linha
  na frase de entrada) e um mapa código de aviso → variante.
- **Testes por HTTP** (R9) e **registro de validação** do gate (R10, R11).

## Technical Context

**Language/Version**: Python 3.13 (ADR 0001).

**Primary Dependencies**: Django 5.2 LTS (templates, `{% include %}`). **Nenhuma
dependência nova** — nem de execução, nem de desenvolvimento.

**Storage**: PostgreSQL 16+. **Nenhuma tabela, coluna ou migração.**

**Testing**: pytest + pytest-django; `django.test.Client` (sem JavaScript); leitor de
cascata do IV-03, movido para `tests/interface/construcao_interface.py`. Medições e
capturas do gate no painel de navegador (Chromium) com viewport emulada (quickstart).

**Target Platform**: servidor local de demonstração e CI (`testes`, Postgres 16);
navegadores móveis e desktop atuais. Recursos CSS usados: propriedades personalizadas,
`accent-color`, `:has()` (degradação aceitável sem `:has`: resta o controle marcado).

**Project Type**: aplicação web monolítica server-rendered (monólito modular Django).

**Performance Goals**: sem meta nova. Acréscimo por página da jornada: `jornada.css`
inline (alvo ≤ 6 KB) + SVG da assinatura inline (alvo ≤ 30 KB), medidos no registro.

**Constraints**: 008 R14 e FR-082 (sem `staticfiles`, sem recurso externo); 014 FR-045
(editor/acompanhamento sem mudança); FR-012 (sem alternância em execução); FR-036 (nada
funcional muda); Manual da Marca IF.

**Scale/Scope**:
- Folhas: `interface/estilo.css` (alterada), `interface/jornada.css` (nova).
- Templates da jornada: `base.html`, `formacoes.html`, `formacao.html`, `secao.html`,
  `concluida.html`, novo `assinatura.svg` (`conclusao.html` muda só por CSS).
- Código: `mensagens.py` (mapa de variantes), `views.py` (variante do aviso; frase de
  entrada separada em prefixo/linha/sufixo, mesmo texto).
- Testes: um arquivo novo; ajustes pontuais onde a marcação muda de propósito.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Verificação | Princípios | Pré-Fase 0 | Pós-Fase 1 | Evidência / observação |
|---|-------------|------------|------------|------------|------------------------|
| 1 | Longitudinalidade (Pessoa → Conclusão → Participação → Respostas) | I | N/A | N/A | Nenhuma relação, gravação ou fluxo alterado (FR-036, FR-037) |
| 2 | Pessoa versus Conclusão Acadêmica | I, XI | ✅ Conforme | ✅ Conforme | Contexto e ficha continuam por Conclusão; só mudam fio e fundo (contracts/telas.md) |
| 3 | Múltiplas formações da mesma Pessoa sem fusão artificial | I, XI | ✅ Conforme | ✅ Conforme | Itens, ordem e situações da 014 inalterados; só hierarquia visual (R8) |
| 4 | Múltiplas participações sem sobrescrita | I, VIII | N/A | N/A | Sem mudança em Participações |
| 5 | Definição institucional de egresso respeitada | II | N/A | N/A | Sem elegibilidade nova |
| 6 | Preservação histórica | VIII, XXVII | ✅ Conforme | ✅ Conforme | Textos da Versão exibidos sem alteração (FR-023, FR-036); sem migração |
| 7 | Versionamento; Pesquisa/Versão/Campanha/Participação distintas | VII, VIII | N/A | N/A | Sem mudança de domínio |
| 8 | Proveniência proporcional à finalidade e ao risco | IV | N/A | N/A | Nenhum dado novo; origem da assinatura registrada no registro de validação (R3) |
| 9 | Separação entre dado institucional, derivado e declarado | III | ✅ Conforme | ✅ Conforme | Destaque da formação é só apresentação; nada pré-preenchido (R8; data-model) |
| 10 | Desacoplamento de integrações | V, XV, XXV | N/A | N/A | Sem integração; demonstração só muda de lugar os controles (R4) |
| 11 | Fronteira do NIAE | VI | N/A | N/A | Apresentação da jornada existente |
| 12 | Governança institucional | IX, X | ⏸ DECISÃO PENDENTE | ⏸ DECISÃO PENDENTE | DP-801, D-02, D-03 abertas; tratamento provisório reversível (Direção B; uso local da assinatura); propagação depende de decisão (FR-045) |
| 13 | Escopo por unidade e visão institucional | XII | N/A | N/A | Sem telas institucionais; marca sistêmica por ser multicampi (R3) |
| 14 | Privacidade, minimização e dados pessoais | XVI, XVII | ✅ Conforme | ✅ Conforme | Nenhum recurso de terceiros (assinatura inline; sem fonte externa — R3, FR-018); nenhum dado pessoal novo |
| 15 | Autorização | X, XII | N/A | N/A | Rotas, posse e CSRF inalterados; formulário de encerramento só muda de posição (R4) |
| 16 | Acessibilidade (WCAG 2.1 AA / eMAG) | XX | ✅ Conforme | ✅ Conforme | Tokens com contraste documentado (contracts/tokens.md); foco inalterado + resumo focado visível (R7); estado selecionado além do controle; verde da marca só gráfico; pendência × erro sem depender de cor; nome acessível da assinatura |
| 17 | Responsividade e jornada móvel | XIV, XXI | ✅ Conforme | ✅ Conforme | Limites de cabeçalho a 375 px; escala com fonte a 200% (R6); ações em largura total; gate a 375/390/430/1280 |
| 18 | Testes proporcionais ao risco | XXV, XXVI | ✅ Conforme | ✅ Conforme | Testes HTTP das fronteiras e papéis de cor (R9); gate com medições e capturas (R10) |
| 19 | Risco de over engineering | XXII, XXIII, XXIV | ✅ Conforme | ✅ Conforme | Sem design system, biblioteca, framework, fonte, ícones ou mecanismo A/B; uma folha nova só por fronteira (R1); um mapa fixo de variantes (Complexity Tracking) |
| 20 | Exportabilidade e semântica das exportações | XVIII | N/A | N/A | Sem exportação |
| 21 | Decisões pendentes explicitadas; nenhuma hipótese virou regra | XXIX | ✅ Conforme | ✅ Conforme | Direção B como tratamento provisório de D-02; raio, divisor, limites de px e ícones como [Hipótese] decididas no gate (R11); 403/404/500 adiadas (R5) |

**Resultado do gate**: APROVADO (pré-Fase 0 e pós-Fase 1), com a linha 12 em decisão
pendente e tratamento provisório reversível.

**Conflitos identificados**:

- **FR-040 ("a prévia DEVE refletir ritmo") × tela do editor.** A prévia intercala uma
  lista de anotações do editor depois de cada Pergunta e tem regra própria
  (`.previa .pergunta { margin-bottom: 0.5rem }`, 009). Análise:
  1. A feature está incorreta? Não: a prévia deve mostrar a Pergunta como o egresso vê.
  2. O escopo é excessivo? Sim, se "ritmo" incluir o espaço **entre** Perguntas: isso
     mudaria a composição da tela do editor, vedada pela mesma FR-040.
  3. Alternativa compatível: a prévia herda tipografia, estados e o espaço interno
     (enunciado → resposta); o espaço entre Perguntas continua o do editor (R6).
  4. Sem emenda. **Resolvido (solicitante, 2026-10-03):** FR-040 e US6 cenário 2
     reescritos — a prévia reflete tipografia, estados e tratamento visual interno dos
     controles e da Pergunta, sem herdar espaçamento entre Perguntas, shell, ritmo de
     página ou regras exclusivas da jornada.
- **D-03 (assinatura) bloqueante.** O ZIP oficial não tem SVG (R3). Sem o SVG, SC-001
  não passa e a 015 não fecha o gate; o resto da feature segue.
- **D8 resolvida pela inspeção (R5).** 403/404/500 são globais e inseparáveis sem lógica
  nova; ficam fora da 015, conforme a regra condicional da spec (FR-020). Não há conflito;
  registro para a propagação.
- **014 SC-014 ("entrada e operador da demonstração sem diferença visual").** Superado de
  propósito por D7 da 015: essas telas estendem o template da jornada e acompanham o
  shell. Não é regressão.

## Decisões Pendentes

| ID | DECISÃO PENDENTE | Instância competente | Solução provisória (hipótese) | Como reverter |
|----|------------------|----------------------|-------------------------------|---------------|
| 008/DP-801 | Identidade visual e linguagem definitivas | Proex/CPAEG, ACS, TI | Direção da auditoria implementada como código de produção na jornada; propagação depende da decisão | Alterar tokens e `jornada.css`; nada funcional depende delas |
| Aud. D-02 | Aplicação do Padrão Digital de Governo ao Trajetória; margem para a identidade do Ifes; barra gov.br/VLibras | Proex/CPAEG, TI, ACS | **Direção B** mergeada; A comparada no gate | Trocar duas linhas de token |
| Aud. D-03 | (a) **Formato digital oficial (SVG) da assinatura sistêmica** — o ZIP oficial não tem SVG; (b) uso em publicação e produção | ACS | (a) **Bloqueia** a tarefa da assinatura e o fechamento do gate (SC-001); pedido do SVG à ACS pelo solicitante; nada substituto no cabeçalho. (b) Uso local, interno e não publicado, respeitando o Manual | (a) Incluir o SVG quando recebido; (b) remover o include ou trocar o arquivo |

Hipóteses de produto reversíveis: limites de 64/80/120 px, 48 px entre Perguntas, raio,
divisor, ausência de ícones — todas em tokens ou numa regra de `jornada.css`.

## Desenho

### Arquivos alterados

| Arquivo | Mudança | FRs |
|---|---|---|
| `trajetoria/interface/templates/interface/estilo.css` | `:root` com tokens e contraste; regras de `.pergunta`/`.escala`/`.opcoes` (ritmo, tipografia, `accent-color`, selecionado, hover, células); `.com-pendencia`/`.resumo-pendencias`/resumo em tokens; foco do resumo | FR-001–010, 022–025, 027, 028 |
| `trajetoria/interface/templates/interface/jornada.css` (novo) | Shell (faixa, cabeçalho, rodapé); `a`, `button.primario`/`.secundario` da jornada; avisos com variantes; item de formação; contexto e ficha; confirmação; ação em largura total; divisores suaves | FR-004, 015–021, 026, 029, 031–035 |
| `trajetoria/interface/templates/interface/assinatura.svg` (novo, **bloqueado por D-03**) | Assinatura sistêmica oficial em SVG, exatamente como fornecida pela ACS (R3) | FR-017, FR-018 |
| `trajetoria/interface/templates/interface/base.html` | Inclui `jornada.css`; controles de demonstração na faixa; cabeçalho e rodapé novos | FR-015–021 |
| `trajetoria/interface/templates/interface/formacoes.html`, `formacao.html` | Classe de variante do aviso; `<strong>` na linha da frase de entrada; `span.situacao` | FR-026, 031, 032 |
| `trajetoria/interface/templates/interface/secao.html` | Classe de variante do aviso de percurso | FR-026 |
| `trajetoria/interface/templates/interface/concluida.html` | Bloco do topo com acento de sucesso (wrapper, se necessário) | FR-029 |
| `trajetoria/interface/mensagens.py` | `VARIANTE_DO_AVISO` (mapa fixo código → `sucesso`/`informacao`) | FR-026 |
| `trajetoria/interface/views.py` | Passa a variante com o aviso; frase de entrada em prefixo/linha/sufixo de `ENTRADA_FATO` (texto final idêntico) | FR-026, FR-032 |
| `tests/interface/construcao_interface.py` | Recebe o leitor de cascata do IV-03 | — |
| `tests/interface/test_interface_secao.py` | Usa o leitor movido | — |
| `tests/interface/test_interface_identidade.py` (novo) | Testes de R9 | FR-046 |
| `specs/015-identidade-visual-jornada/validacao.md` (novo, só texto) | Registro do gate; capturas anexadas ao PR ou externas, não versionadas (R10) | FR-042–044 |

**Não alterados:** `editor/*`, `acompanhamento/*`, `403_csrf.html`, `404.html`,
`500.html`, modelos, migrações, rotas. `demonstracao/*` herda o shell pela base; se D7
exigir edição ali, só o mínimo para mover os controles para a faixa, sem mudança funcional.

### Ordem de implementação sugerida

1. Pré-requisito: SVG oficial da assinatura (R3; **bloqueado por D-03** — o resto segue em paralelo).
2. Tokens no `:root` (sem efeito visual) + teste da troca A/B restrita aos dois tokens de ação.
3. `jornada.css` + shell em `base.html` + teste de inclusão por página.
4. Questionário (`.pergunta`) e feedback.
5. Trajetória, contexto, confirmação.
6. Testes restantes de R9; suíte completa.
7. Rodada 1 do gate (registro); A × B; raio; divisor; correções; novas rodadas até aprovar.

## Project Structure

### Documentation (this feature)

```text
specs/015-identidade-visual-jornada/
├── spec.md
├── plan.md                      # este arquivo
├── research.md                  # R1–R11
├── data-model.md                # sem entidades; mapa de variantes; modelo visual
├── quickstart.md                # execução do gate
├── contracts/
│   ├── tokens.md
│   ├── shell.md
│   ├── telas.md
│   └── registro-validacao.md
├── checklists/requirements.md
├── validacao.md                 # criado na implementação (gate; só texto)
└── tasks.md                     # /speckit-tasks (não criado aqui)
```

### Source Code (repository root)

```text
trajetoria/interface/
├── mensagens.py                 # + VARIANTE_DO_AVISO
├── views.py                     # variante do aviso; frase de entrada separada
└── templates/interface/
    ├── estilo.css               # tokens + .pergunta (compartilhada)
    ├── jornada.css              # novo: só a jornada
    ├── assinatura.svg           # novo: marca sistêmica oficial
    ├── base.html                # shell
    ├── formacoes.html
    ├── formacao.html
    ├── secao.html
    └── concluida.html

tests/interface/
├── construcao_interface.py      # + leitor de cascata
├── test_interface_secao.py      # usa o leitor movido
└── test_interface_identidade.py # novo
```

**Structure Decision**: monólito modular Django existente; tudo dentro do app
`trajetoria.interface`, sem app, pacote ou camada nova.

## Estratégia de testes

Ver [research R9](research.md#r9--estratégia-de-testes). Automatizado por HTTP:
fronteiras de inclusão das folhas, troca A/B só nos dois tokens de ação, verde da marca só gráfico, seletores
administrativos sem tokens, papéis de cor, assinatura com nome acessível, ausência de
recurso externo, textos inalterados. Medido no gate (quickstart): alturas, contraste
renderizado, reflow e 200%, SCs mobile da 014, escala de cinza, capturas A × B e regressão
administrativa.

## Complexity Tracking

| Item | Por que é necessário | Alternativa mais simples rejeitada porque |
|---|---|---|
| Segunda folha (`jornada.css`) | Fronteira jornada × administração por construção (FR-040), sem condicional nem duplicação | Uma folha só obrigaria a alterar regras globais usadas pelo editor/acompanhamento, ou a prefixar dezenas de seletores |
| Mapa `VARIANTE_DO_AVISO` | Variante visual derivada do código já existente, num só lugar | Decidir a variante no template repetiria a lista de códigos em cada tela |
| Template SVG da assinatura | Marca oficial sem `staticfiles` nem requisição externa | `<img>` com estáticos exigiria infraestrutura nova só pela marca (008 R14) |

## Necessidade de voltar à spec ou às features anteriores

- **Spec 015, FR-040 / US6 cenário 2**: redação aprovada e aplicada (2026-10-03).
- **Spec 015, FR-042**: capturas identificadas no registro e anexadas ao PR, não
  versionadas (R10; decisão do solicitante).
- **Spec 015, D8**: resolvida por R5 (403/404/500 fora); registrar no fechamento.
- **Gate, rodada 1** ([validacao.md](validacao.md)): critérios objetivos sem a assinatura
  aprovados após uma correção (títulos com palavra longa, SC-005); raio 4 px nos controles;
  sem divisor; **SC-001 impossível sem o SVG oficial (D-03)** — gate não aprovado.
- **014**: nenhum requisito revisado; SC-014 da 014 quanto à entrada e ao operador da
  demonstração é superado por D7 (registrado acima).
