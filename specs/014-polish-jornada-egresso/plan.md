# Implementation Plan: Polish consolidado da jornada do egresso

**Branch**: `claude/consolidar-auditorias-ux-5dfa52` | **Date**: 2026-10-03 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/014-polish-jornada-egresso/spec.md`

## Summary

Polish único da interface do egresso (008) que resolve os achados de interface ainda
válidos das auditorias de usabilidade, identidade e mobile-first. Tudo em template, folha
de estilo, textos fixos e pequenos ajustes nas views e na apresentação existentes: sem
modelo, migração, JavaScript ou abstração nova.

Abordagem técnica (detalhes em [research.md](research.md)):

- **"Salvar e sair"**: segundo botão de envio no mesmo formulário (`depois=sair`). Mesma
  validação, gravação e telas de estado; só o destino de um envio aceito muda, para a
  trajetória — R1.
- **Enter/"Ir"**: botão de envio padrão desabilitado e oculto como primeiro elemento do
  formulário, comportamento verificado no código do WebKit e do Blink — R2.
- **Mensagens verdadeiras**: um predicado, "há Resposta gravada nesta Seção", lido da
  jornada da 006, decide a frase de salvamento e o aviso de saída (`salvo`/`saida`);
  `&salvo=1` deixa de existir — R3.
- **Pendência × erro**: o mesmo resumo com um "tipo"; textos, prefixo do título e
  destaque visual próprios — R4.
- **Controles**: área ativável por pseudo-elemento do rótulo; escala em grade de colunas
  de 44 px que quebra alinhada; `radiogroup` só em volta das Opções — R5 a R7 (uma única
  correção, FR-018).
- **Foco no resumo**: `autofocus` + `tabindex="-1"`, mantendo `role="alert"` — R8.
- **Títulos, rodapé, trajetória e confirmação** — R9 a R12.
- **Testes por HTTP**, sem navegador automatizado; medições pelo quickstart; validação em
  aparelho real posterior — R13.

## Technical Context

**Language/Version**: Python 3.13 (ADR 0001).

**Primary Dependencies**: Django 5.2 LTS (templates, forms, CSRF, `never_cache`).
**Nenhuma dependência nova.**

**Storage**: PostgreSQL 16+. **Nenhuma tabela, coluna ou migração nova.** Nada novo é
persistido; Respostas só pelas operações da 005 (FR-042).

**Testing**: pytest + pytest-django; `django.test.Client` (sem JavaScript); construtores
existentes (`tests/participacao/construcao.py`, `tests/interface/construcao_interface.py`).
Medições de tela pelo quickstart, no painel de navegador (Chromium) com viewport emulada.

**Target Platform**: servidor local de demonstração e CI (`testes`, Postgres 16);
navegadores móveis (Safari/iOS, Chrome/Android) como alvo de uso, validados depois (FR-050).

**Project Type**: aplicação web monolítica server-rendered (monólito modular Django).

**Performance Goals**: sem meta nova. A página continua com CSS inline e sem JavaScript;
o acréscimo é de poucas regras de estilo e um botão.

**Constraints**: FR-080 e FR-091 da 008; nenhuma regressão visual no editor (009), no
acompanhamento (011) e na demonstração (FR-045); textos provisórios (DP-801); MF-03
intocado (FR-047).

**Scale/Scope**:
- Templates: cerca de 12 em `trajetoria/interface/templates`.
- Código: `views.py`, `mensagens.py`, `apresentacao.py` (uma função pequena) e
  `estilo.css`.
- Testes: um arquivo novo e cerca de 8 ajustados.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Verificação | Princípios | Pré-Fase 0 | Pós-Fase 1 | Evidência / observação |
|---|-------------|------------|------------|------------|------------------------|
| 1 | Longitudinalidade (Pessoa → Conclusão → Participação → Respostas) | I | ✅ Conforme | ✅ Conforme | Nenhuma relação alterada; "Salvar e sair" grava pela 005 na mesma Participação (research R1) |
| 2 | Pessoa versus Conclusão Acadêmica | I, XI | ✅ Conforme | ✅ Conforme | Linha da formação por Conclusão; "Você está respondendo sobre:" ancora a Participação na sua Conclusão (FR-025) |
| 3 | Múltiplas formações da mesma Pessoa sem fusão artificial | I, XI | ✅ Conforme | ✅ Conforme | Trajetória com uma entrada por Conclusão, na ordem da 007, sem desempate fabricado (FR-034, FR-035; R11) |
| 4 | Múltiplas participações sem sobrescrita | I, VIII | N/A | N/A | Nada muda em Participações; histórico de Participações fica [Dec] (ID-10) |
| 5 | Definição institucional de egresso respeitada | II | N/A | N/A | Elegibilidade e situação vêm da 004/007 sem mudança |
| 6 | Preservação histórica | VIII, XXVII | ✅ Conforme | ✅ Conforme | Textos da Versão exibidos sem alteração; título inventado proibido (FR-023, FR-046) |
| 7 | Versionamento; Pesquisa/Versão/Campanha/Participação distintas | VII, VIII | ✅ Conforme | ✅ Conforme | Nenhuma Campanha nomeada (FR-037); nenhum item [V] |
| 8 | Proveniência proporcional à finalidade e ao risco | IV | N/A | N/A | Nenhum dado novo |
| 9 | Separação entre dado institucional, derivado e declarado | III | ✅ Conforme | ✅ Conforme | Contexto só exibido; frase de entrada sem dedução nem "campus" (FR-032; R11); data-model "Origem" |
| 10 | Desacoplamento de integrações | V, XV, XXV | N/A | N/A | Nenhuma integração; adaptador de demonstração intocado |
| 11 | Fronteira do NIAE | VI | N/A | N/A | Polish de interface existente |
| 12 | Governança institucional (periodicidade, publicação) | IX, X | ✅ Conforme | ✅ Conforme | Confirmação sem promessa de contato nem periodicidade (FR-039) |
| 13 | Escopo por unidade e visão institucional | XII | N/A | N/A | Sem telas institucionais |
| 14 | Privacidade, minimização e dados pessoais em logs/exportações | XVI, XVII | ✅ Conforme | ✅ Conforme | Avisos `salvo`/`saida` só como código de lista fechada; nada pessoal no endereço (FR-012; R3) |
| 15 | Autorização | X, XII | ✅ Conforme | ✅ Conforme | Mesmas verificações de posse e CSRF da 008 para os dois botões (contrato do rodapé) |
| 16 | Acessibilidade (WCAG 2.1 AA / eMAG) | XX | ✅ Conforme | ✅ Conforme | Foco no resumo (R8); `radiogroup` correto (R7); alvos de 44 px (R5, R6); pendência sem depender de cor (R4); efeito em leitores [T] |
| 17 | Responsividade e jornada móvel | XIV, XXI | ✅ Conforme | ✅ Conforme | Escala com fonte a 200% (R6); rodapé (R10); sem rolagem horizontal (SC-008) |
| 18 | Testes proporcionais ao risco | XXV, XXVI | ✅ Conforme | ✅ Conforme | Matriz do rodapé inteira em teste HTTP; estrutura do bloqueador; medições no quickstart (R13) |
| 19 | Risco de over engineering | XXII, XXIII, XXIV | ✅ Conforme | ✅ Conforme | Sem JS, sem modelo, sem componente genérico; uma função de apresentação nova (complemento da formação); CSS restrito a `.pergunta` e classes novas (Complexity Tracking) |
| 20 | Exportabilidade e semântica das exportações | XVIII | N/A | N/A | Sem exportação |
| 21 | Decisões pendentes explicitadas; nenhuma hipótese virou regra | XXIX | ✅ Conforme | ✅ Conforme | DP-701 preservada (texto de ambiguidade); DP-702 (sem desempate); DP-801 (textos provisórios); MF-03 [T]; 480/32 px como [Hipótese] |

**Resultado do gate**: APROVADO (pré-Fase 0 e pós-Fase 1).

**Conflitos identificados**:

- **Tensão com a 008 FR-023** (textos de situação fixos). Análise:
  1. A feature está incorreta? Não: ID-11 é achado válido.
  2. O escopo é excessivo? Não.
  3. Existe alternativa compatível? Sim: omitir só "sem pesquisa" e manter o texto de
     ambiguidade (DP-701).
  4. Não precisa de emenda.

  A spec revisa a FR-023 de forma localizada.
- **Verificador de acessibilidade da 008** fixa "alerta ⇔ título `Erro:`". É um teste que
  descreve o texto antigo, não um princípio. A regra é atualizada para pendências (R4)
  sem enfraquecer a verificação.

## Decisões Pendentes

| ID | DECISÃO PENDENTE | Instância competente | Solução provisória (hipótese) | Como reverter |
|----|------------------|----------------------|-------------------------------|---------------|
| 008/DP-801 | Linguagem e identidade visual definitivas | Proex/CPAEG, comunicação, TI | Textos neutros em `mensagens.py` e nos templates; cores já documentadas | Trocar textos e cores, sem mudar comportamento |
| 007/DP-701 | Comunicação da ambiguidade operacional | Proex/CPAEG, DIREC/CSAEG | Texto atual mantido por formação | Trocar o texto em `SITUACAO_DA_FORMACAO` |
| 007/DP-702 | Distinção de formações com atributos insuficientes | CPAEG, registro acadêmico | Linha + complemento só com atributos existentes; sem desempate | Acrescentar atributo à linha quando decidido |
| MF-03 [T] | Restauração de formulário ao voltar no histórico | Validação em aparelho, depois decisão do solicitante | Nada muda (FR-047) | Feature futura, se o item 4 do roteiro indicar |

Hipóteses de produto reversíveis: 480 px (largura total dos botões) e 32 px (separação),
em `estilo.css`.

## Desenho

### Arquivos alterados

| Arquivo | Mudança | FRs |
|---|---|---|
| `trajetoria/interface/views.py` | `_salvar`: destino de "Salvar e sair" (R1) e aviso `salvo`/`saida` (R3); `secao`/`_tela_da_secao`: tipo do resumo, `ha_resposta_na_secao`, fim de `salvo=1`; `formacoes`: títulos, avisos permitidos, formação compacta (R11); `concluida`: `curso` | FR-008, 010–012, 030–036, 038 |
| `trajetoria/interface/mensagens.py` | `AVISOS["salvo"]`, `AVISOS["saida"]`; textos de pendência; `SEM_PESQUISA` sem texto por formação | FR-005–007, 012, 036 |
| `trajetoria/interface/apresentacao.py` | `complemento_da_formacao` (nível · modalidade · forma de oferta) | FR-034 |
| `templates/interface/base.html` | Prefixo do título por tipo de resumo | FR-007 |
| `templates/interface/secao.html` | `h1` da Seção; resumo por tipo com foco; bloqueador; dois botões; `div.saidas` | FR-004–016, 023, 024, 027 |
| `templates/interface/perguntas/_cabecalho.html` | Marca "Erro:" ou "Falta responder:" | FR-006 |
| `templates/interface/perguntas/escala.html`, `escolha_unica.html` | `radiogroup` só em volta das Opções; `legend` com id | FR-022 |
| `templates/interface/contexto_compacto.html` | "Você está respondendo sobre:" | FR-025 |
| `templates/interface/formacoes.html` | Trajetória (R11) e aviso | FR-002, 030–037 |
| `templates/interface/conclusao.html` | `h1`; `lista-secoes` | FR-023, 026 |
| `templates/interface/concluida.html` | Frase de registro; agradecimento condicional; rótulo da ligação | FR-030, 038–041 |
| `templates/interface/aviso.html` | Rótulo da ligação | FR-030 |
| `templates/403_csrf.html` | Instrução sem "recarregue" | FR-029 |
| `templates/interface/estilo.css` | R4 (destaque de pendência), R5, R6, R10, `lista-secoes`; tudo sob `.pergunta` ou classes novas | FR-015, 019–021, 026, 045 |

Não mudam: modelos, migrações, `formularios.py`, `gravacao.py`, `urls.py`,
`trajetoria/demonstracao`, `trajetoria/editor`, `trajetoria/acompanhamento` e qualquer
código das features 001 a 007 e 009 a 013.

### Fluxo do envio (resumo do [contrato](contracts/rodape-secao.md))

```text
POST secao ─► jornada: concluída / encerrada / fora do percurso ─► telas atuais (iguais p/ os 2 botões)
          └► formulário inválido / rejeição 005 ─► Seção com resumo "erros" (iguais p/ os 2 botões)
          └► aceito ─► jornada relida
                      ├─ depois=sair ─► /formacoes/?aviso=salvo|saida   (R3: há Resposta na Seção?)
                      └─ senão ─► pendências? ─► Seção ?pendencias=1 (resumo "pendencias", frase só se R3)
                                  └► destino da 006 (Seção seguinte ou /concluir/)
```

## Project Structure

### Documentation (this feature)

```text
specs/014-polish-jornada-egresso/
├── spec.md
├── plan.md              # este arquivo
├── research.md          # R1–R13
├── data-model.md        # dados de apresentação (sem entidade nova)
├── quickstart.md        # validação automatizada, em navegador e roteiro [T]
├── contracts/
│   ├── rodape-secao.md  # formulário, matriz do POST, ligações, avisos
│   └── telas.md         # conteúdo das telas alteradas
├── checklists/
│   └── requirements.md
└── tasks.md             # /speckit-tasks (não criado aqui)
```

### Source Code (repository root)

```text
trajetoria/interface/
├── views.py                      # alterado
├── mensagens.py                  # alterado
├── apresentacao.py               # alterado (+ complemento_da_formacao)
└── templates/
    ├── 403_csrf.html             # alterado
    └── interface/
        ├── base.html             # alterado
        ├── secao.html            # alterado
        ├── formacoes.html        # alterado
        ├── conclusao.html        # alterado
        ├── concluida.html        # alterado
        ├── aviso.html            # alterado
        ├── contexto_compacto.html# alterado
        ├── estilo.css            # alterado
        └── perguntas/
            ├── _cabecalho.html   # alterado
            ├── escala.html       # alterado
            └── escolha_unica.html# alterado

tests/interface/
├── test_interface_rodape.py      # novo
├── test_interface_secao.py       # ajustado
├── test_interface_navegacao.py   # ajustado
├── test_interface_aceitacao.py   # ajustado
├── test_interface_gravacao.py    # ajustado
├── test_interface_formacoes.py   # ajustado
├── test_interface_encerramento.py# ajustado
├── test_interface_conclusao.py   # ajustado
└── test_interface_acessibilidade.py # ajustado (R4; novos estados)
tests/editor/test_editor_previa.py   # ajustado só se a marcação de R7 exigir
```

**Structure Decision**: monólito modular existente (ADR 0001), só o app
`trajetoria.interface`. Nenhum app, módulo ou pasta nova.

## Estratégia de testes

Detalhada em [research R13](research.md#r13--estratégia-de-testes).

| SC | Como é verificado |
|----|-------------------|
| SC-001 | `test_interface_secao.py`, `test_interface_gravacao.py`: textos, prefixo do título, marca por Pergunta nos dois tipos |
| SC-002 | `test_interface_rodape.py`: estados "incompleto", "sem Resposta", "Seção opcional vazia", "Respostas removidas", na reapresentação e no aviso de saída |
| SC-003, SC-004, SC-015 | `test_interface_rodape.py`: matriz inteira (8 estados × 2 envios; destino das 2 ligações; ligações presentes na reapresentação com erro), com `retrato()` antes e depois |
| SC-005 | Estrutura em `test_interface_rodape.py` (primeiro botão de envio desabilitado; nenhum outro antes); comportamento no quickstart 2.1 |
| SC-006 a SC-010 | Quickstart 2.2 a 2.5 (viewport emulada, fonte raiz alterada) |
| SC-011 | `test_interface_formacoes.py`, `test_interface_encerramento.py`: ordem comparada com `situacao_de_entrada`; textos |
| SC-012 | `test_interface_conclusao.py`: Versão com e sem `texto_encerramento`; curso ausente |
| SC-013 | `makemigrations --check`; varredura de `<script>`; E2E e verificador da 008 |
| SC-014 | Suítes da 009, 011 e demonstração; quickstart 2.6 |

## Complexity Tracking

Nenhuma violação da Constituição. Escolhas registradas para revisão:

| Escolha | Por que é necessária | Alternativa mais simples rejeitada porque |
|---------|----------------------|-------------------------------------------|
| Botão oculto e desabilitado no formulário | Único meio sem JavaScript de bloquear o envio implícito (R2) | Sem ele, Enter envia a Seção (MF-02); JS é proibido |
| Dois códigos de aviso (`salvo`, `saida`) em vez de um | Mensagem verdadeira com e sem Resposta gravada (FR-008) | Um único texto ou sugeriria salvamento falso ou seria vago |
| `complemento_da_formacao` em `apresentacao.py` | Linha complementar sem desempate (D10, DP-702) | Mostrar a ficha completa anula ID-03/ID-14; omitir nível/modalidade fere a 008 FR-025 |
| Invólucro `radiogroup` em escolha única | Tirar a caixa de remoção do grupo exclusivo (UX-19) sem perder `aria-required` | Tirar `role` do `fieldset` deixaria `aria-required` inválido; mover a caixa para fora desliga-a da Pergunta |

**Não adotado**: navegador automatizado no CI (decisão da 008 mantida; medições pelo
quickstart); sessão para mensagens; assinatura do código de aviso.

## Necessidade de voltar à spec ou às features anteriores

- **Spec da 014**: nenhuma mudança.
- **Documentos da 008**: na implementação, anotar na spec da 008 os FRs revisados pela 014
  (FR-020, 021, 023, 032, 049, 050, 062, 071, 076, 077) com "*(Revisado pela 014)*", e
  atualizar a seção da Seção em `contracts/rotas.md` (`h1`, rodapé, fim de `&salvo=1`),
  como fez o polish `226ca93`. Nenhum contrato de domínio muda.
- **Testes existentes que fixam o texto ou o endereço antigo**: são ajustados, não
  removidos.
  - Redirecionamento `?pendencias=1&salvo=1` → `?pendencias=1`
    (`test_interface_aceitacao.py`, `test_interface_navegacao.py`).
  - "Há problemas", "Sobre a sua formação", "Obrigado", "Sobre qual formação", "Suas
    outras formações", "Sem pesquisa disponível" e "não está disponível neste momento"
    (este último continua presente).
  - Regra de título do verificador de acessibilidade (R4).
- **Features 001 a 007 e 009 a 013**: nenhuma mudança de código ou contrato. A prévia da
  009 muda de marcação por reutilizar os controles de Pergunta, o que a FR-045 prevê.
