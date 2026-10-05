# Implementation Plan: Mobilização real, Lotes e contatos do egresso

**Branch**: `claude/feature-020-audit-8056d5` | **Date**: 2026-10-05 | **Spec**:
[spec.md](spec.md)

**Input**: Feature specification from `specs/020-mobilizacao-real-lotes-contatos/spec.md`,
com o clarify de 2026-10-05 (E1 e E7 confirmadas; E2 só na demonstração; E3 a E6
mantidas).

## Summary

Uma Campanha passa a mobilizar egressos por **Lotes** reproduzíveis:

- o Lote nasce congelado a partir de uma prévia transitória;
- seus membros são Pessoas;
- cada membro guarda o contato escolhido;
- o envio por e-mail é retomável e grava situações honestas.

A Pessoa ganha **contatos de e-mail com proveniência**, registros imutáveis de duas
origens:

- importados por uma fronteira de contatos **separada** da fonte acadêmica (precedente
  021 FR-071);
- informados pelo egresso numa página opcional, anunciada como ação secundária na tela de
  conclusão.

O envio real fica **desativado**. Só os modos teste e demonstração funcionam, e o modo
real existe apenas como validação de fronteira até os Gates A e B.

**Abordagem técnica:**

- **App `trajetoria/contato/`**: model `ContatoDaPessoa`, normalização, política de
  escolha, carga e página `/meu-email/`.
- **App `trajetoria/mobilizacao/`**: models `LoteDeMobilizacao` e `MembroDoLote`,
  seleção, prévia, confirmação, envio e views do acompanhamento.
- **Fronteira de contatos**: contrato puro `fonte_academica/contatos_da_fonte.py` e
  adaptador fictício `fonte_academica/contatos_simulados.py`.
- **`comunicacao/`**: fica só com o renderer e o transporte por modos. A simulação da 016
  sai.
- **Garantia estrutural de uma abordagem por Pessoa e Campanha**: restrição única parcial
  no banco (research R6).
- **Concorrência**: confirmação serializada pelo lock da Campanha; envio com
  `select_for_update(skip_locked)` e o registro `EM_TENTATIVA` antes de cada envio.

## Technical Context

**Language/Version**: Python 3.13.

**Primary Dependencies**: as existentes (Django 5.2, psycopg 3, cryptography, resvg-py,
XlsxWriter). **Nenhuma dependência nova.** O transporte usa
`django.core.mail.EmailMultiAlternatives` e o backend SMTP do framework.

**Storage**: PostgreSQL 16. Três tabelas novas em dois apps (`contato/0001`,
`mobilizacao/0001`), com `ArrayField` e `UniqueConstraint` parcial (`condition=`).
Nenhuma tabela existente muda.

**Testing**: pytest e pytest-django.

- Novos: `tests/contato/` e `tests/mobilizacao/`. A concorrência usa
  `django_db(transaction=True)` e threads.
- Ajustes: `tests/comunicacao/`, `tests/governanca/`, `tests/acompanhamento/`,
  `tests/acesso/` (fronteiras e vazamento), `tests/analitico/`, `tests/exportacao/`,
  `tests/interface/` (conclusão) e `tests/narrativa/` (isolamento).

**Target Platform**: servidor Linux; navegador móvel e desktop sem JavaScript obrigatório.

**Project Type**: aplicação web Django modular (monólito), como nas features anteriores.

**Performance Goals**:

- prévia e confirmação na ordem de segundos para a população da demonstração;
- envio limitado a `TRAJETORIA_LOTE_ENVIO_POR_ACAO` (padrão 100) por requisição, com
  timeout SMTP de 5 s por mensagem.

**Constraints**:

- nenhum endereço em logs, URLs, sessão, cache, telas, 011, 012 e 013;
- nenhum reenvio silencioso;
- modo real inalcançável pela interface enquanto a demonstração for o único modo do
  middleware.

**Scale/Scope**: demonstração (≈12 Pessoas fictícias). O desenho tolera um piloto de um
campus por ações síncronas repetidas, sem fila. A escala real fica para depois do Gate A.

## Constitution Check

| # | Verificação | Princípios | Pré-Fase 0 | Pós-Fase 1 | Evidência / observação |
|---|-------------|------------|------------|------------|------------------------|
| 1 | Longitudinalidade | I | ✅ | ✅ | Lote e envio não criam nem alteram Participação (FR-041); data-model §4 |
| 2 | Pessoa × Conclusão | I, XI | ✅ | ✅ | O contato é da Pessoa, não da Conclusão. O filtro se aplica à Conclusão antes de chegar à Pessoa (FR-017; research R5) |
| 3 | Múltiplas formações sem fusão | I, XI | ✅ | ✅ | Grão Pessoa, sem fundir Conclusões; `UNIQUE(lote, pessoa)` |
| 4 | Múltiplas participações | I, VIII | N/A | N/A | Não lê nem altera Participação |
| 5 | Definição de egresso | II | ✅ | ✅ | Lote ⊆ abrangência da 004; não exclui ninguém (ADR 0004; SC-007) |
| 6 | Preservação histórica | VIII, XXVII | ✅ | ✅ | Contatos, Lotes e membros imutáveis; snapshots intocados; migrações só aditivas |
| 7 | Pesquisa/Versão/Campanha/Participação distintas | VII | ✅ | ✅ | O Lote referencia a Campanha sem copiar estado; o formulário da 017 não muda |
| 8 | Proveniência proporcional | IV | ✅ | ✅ | Origem, fonte, posição e `obtido_em`; o membro aponta o registro usado; operador e momento no Lote (risco do envio) |
| 9 | Institucional × derivado × declarado | III | ✅ | ✅ | `FONTE_ACADEMICA` × `EGRESSO`, sem sobrescrita; a política é derivada e explicável (data-model §1) |
| 10 | Desacoplamento de integrações | V, XV, XXV | ✅ | ✅ | `FonteDeContatos` separada; o contrato acadêmico fica intacto; transporte por modos sem fornecedor nomeado; mock com o mesmo contrato |
| 11 | Fronteira do NIAE | VI | ✅ | ✅ | Spec, "Fronteira do NIAE": só convites de Campanha; transporte substituível |
| 12 | Governança institucional | IX, X | ⏸ | ⏸ | Capacidades nomeadas e reversíveis; preparar ≠ enviar; DP-2001 e DP-1602 abertas; o modo real depende do Gate B |
| 13 | Escopo por unidade | XII | ✅ | ✅ | CSAEG limitada às suas unidades; filtro obrigatório; visibilidade por `escopo_unidades` (research R10) |
| 14 | Privacidade e minimização | XVI, XVII | ⏸ | ⏸ | Só e-mail (E1). E-mail legível **só na demonstração** com os controles C1–C7 (research R9). DP-2010 bloqueia o uso real. Base legal, retenção e opt-out são DPs |
| 15 | Autorização e menor privilégio | X, XII | ✅ | ✅ | Revalidação por requisição; o cliente não define seleção nem destino; acompanhar não concede Lote |
| 16 | Acessibilidade | XX | ✅ | ✅ | Formulários sem JS, `fieldset`/`legend`, `role="status"`, teclado; testes de acessibilidade como nas 016 e 021 |
| 17 | Responsividade | XIV, XXI | ✅ | ✅ | Página do egresso no shell da jornada, uma página e uma ação; telas de Lote de 320 px a desktop |
| 18 | Testes proporcionais | XXV, XXVI | ✅ | ✅ | Research R14: concorrência, retomada, idempotência, isolamento, vazamento, modos |
| 19 | Over engineering | XXII, XXIII, XXIV | ✅ | ✅ | Sem fila, worker, retry, rascunho, estado de Lote, score, multicanal, editor ou criptografia por analogia; nenhuma dependência nova. Complexidade mantida: abaixo |
| 20 | Exportabilidade | XVIII | N/A | N/A | Lote e contato ficam fora de 012 e 013 por desenho (FR-040) |
| 21 | Decisões pendentes explícitas | XXIX | ✅ | ✅ | DP-2001 a DP-2010 e as herdadas; o modo real fica desativado |

**Resultado do gate**: APROVADO.

- Os itens ⏸ são decisões institucionais com solução provisória reversível, não
  violações.
- Pós-Fase 1: o desenho mantém tudo.
- A restrição do research R6 exige `MembroDoLote.campanha`. É uma FK, não estado
  duplicado, e é verificada na criação.

**Conflitos identificados**: nenhum.

- A precisão de FR-002 (idempotência por observação, research R2) não muda a intenção da
  spec e foi registrada nela.
- A revisão da 021 FR-003 e da 014 FR-041 (E7) foi decidida pelo solicitante e não envolve
  princípio constitucional.

## Controles do e-mail legível e revisão antes do uso real (E2, DP-2010)

**Por que legível é aceitável aqui.** O e-mail não é fator de verificação (a 018 usa CPF e
data). A 020 não cria link mágico nem token. O pior efeito de um vazamento na demonstração
é nulo, porque os dados são fictícios em `example.invalid`.

**Controles obrigatórios** (detalhe e verificação no research R9):

| # | Controle |
| --- | --- |
| C1 | Leitura de `valor` só na confirmação, no envio e na gravação |
| C2 | Nenhuma tela exibe endereço |
| C3 | Nenhum endereço em logs, erros, URLs, sessão e cache |
| C4 | Nenhum endereço em 011, 012 e 013 |
| C5 | Nenhum app de identidade, acadêmico, declaração, narrativa, vídeo, participação, analítico ou exportação importa `contato` |
| C6 | Fora do admin e de serializações |
| C7 | Somente dados fictícios na demonstração |

**Revisão obrigatória antes do uso real.** A DP-2010 é item do Gate B e condição de FR-033.
A DTI e o encarregado registram a decisão sobre proteção em repouso. Se for cifrar, o ponto
de troca é localizado: Fernet no `valor` e HMAC para a idempotência do egresso, sem mudança
fora de `contato/` e das duas operações de C1.

## Impacto compartilhado na tela de conclusão (E7)

A independência funcional de 021 e 022 continua:

- a narrativa não depende de contato;
- o contato não depende da narrativa;
- `narrativa`, `video` e `contexto_trajetoria` não importam `contato` nem `mobilizacao`.

Isso **não** elimina o impacto compartilhado. `interface/templates/interface/concluida.html`
é definida por 014 (FR-041), 021 (FR-003) e 020 (FR-009):

- "Ver minha trajetória no Ifes" continua a primeira e principal ação;
- o convite de e-mail é um parágrafo secundário logo abaixo;
- a ramificação declarada não muda.

**Notas de revisão** aplicadas na implementação:

- 021 FR-003: "única ação" → "ação principal";
- 014 FR-041;
- docstring de `interface/views.py: concluida`;
- documentação institucional.

Um teste verifica a ordem das ações e a ausência do convite para declarante, na página da
narrativa, no card e no vídeo.

## Decisões Pendentes

| ID | DECISÃO PENDENTE | Instância competente | Solução provisória (hipótese) | Como reverter |
|----|------------------|----------------------|-------------------------------|---------------|
| DP-2001 | Quem prepara e envia em produção | CPAEG/Proex, DIREC, CSAEGs | `pode_preparar_lote`/`pode_enviar_lote` = CPAEG\|CSAEG no escopo, só na demonstração | Alterar duas funções em `governanca/regras.py` |
| DP-2002 | Remetente institucional | DTI, comunicação | Remetente fictício; o modo real exige `TRAJETORIA_REMETENTE_INSTITUCIONAL` | Configuração |
| DP-2003 | Textos do convite real e da página do egresso | Proex, comunicação, encarregado | Templates provisórios marcados | Trocar templates |
| DP-2004 | Confirmação do e-mail | CPAEG, encarregado | Sem confirmação | Registro próprio futuro, aditivo |
| DP-2005 | Reenvio deliberado | Instância da DP-2001 | Nenhum (restrição R6) | Nova ação e relaxar a condição da restrição |
| DP-2006 | Retenção | Encarregado, CPAEG | Nada é apagado | Rotina de expurgo futura |
| DP-2007 | Suporte | DIREC, CSAEGs | Nenhum | — |
| DP-2008 | Observabilidade do envio real | DTI | Logs só por categoria | Acrescentar métricas sem dado pessoal |
| DP-2009 | Telefone/WhatsApp | Instância de 004/DP-407 | Não coletado | Novo valor de `canal` e nova fronteira |
| DP-2010 | Proteção em repouso para uso real | DTI, encarregado | Legível só na demonstração (C1–C7) | Cifrar `valor` (research R9) |
| DP-1601 | Fonte real de contatos e o que significa "sumiu da fonte" | DTI, responsáveis pela fonte | Adaptador fictício; lista vazia não invalida (research R2) | Adaptador real após o Gate A |
| DP-1603, DP-1604, DP-1606 | Base legal, provedor, opt-out | Encarregado, DTI, CPAEG | Modo real desativado | Gate B |

## Project Structure

### Documentation (this feature)

```text
specs/020-mobilizacao-real-lotes-contatos/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── fonte-de-contatos.md
│   ├── rotas.md
│   └── transporte.md
├── checklists/requirements.md
└── tasks.md             # /speckit-tasks
```

### Source Code (repository root)

```text
trajetoria/
├── fonte_academica/
│   ├── cenarios.py                 # + EMAILS (movido de comunicacao/contatos.py)
│   ├── contatos_da_fonte.py        # novo: FonteDeContatos, ContatosIndisponiveis
│   └── contatos_simulados.py       # novo: ContatosSimulados
├── contato/                        # novo app
│   ├── apps.py, models.py          # ContatoDaPessoa
│   ├── endereco.py                 # normalizar_email
│   ├── politica.py                 # contato_utilizavel(pessoa, t)
│   ├── carga.py                    # carregar_contatos
│   ├── operacoes.py                # informar_email (egresso)
│   ├── views.py, urls.py           # /meu-email/
│   ├── templates/contato/meu_email.html
│   └── migrations/0001_initial.py
├── mobilizacao/                    # novo app
│   ├── apps.py, models.py          # LoteDeMobilizacao, MembroDoLote
│   ├── selecao.py                  # seleção FR-017 (prévia e confirmação)
│   ├── operacoes.py                # confirmar_lote, enviar_lote
│   ├── acesso.py                   # @lotes, visibilidade
│   ├── views.py                    # lista/prévia, confirmar, detalhe, enviar
│   ├── templates/mobilizacao/{lotes,lote}.html
│   └── migrations/0001_initial.py
├── comunicacao/
│   ├── convite.py                  # renderer com modo
│   ├── seguranca.py                # validações (destino por modo)
│   ├── transporte.py               # novo: transporte_de_envio()
│   └── templates/comunicacao/{convite,convite_real}.{txt,html}
│   # removidos: views.py, consultas.py, contatos.py, acesso.py, operacoes.py,
│   #            templates preparar.html e resultado.html
├── governanca/regras.py            # + pode_consultar_lotes/preparar/enviar; − pode_simular_comunicacao
├── acompanhamento/urls.py          # rotas de Lote; − comunicacao/
├── acompanhamento/templates/acompanhamento/campanha.html   # link "Lotes de mobilização"
├── interface/templates/interface/concluida.html            # convite secundário (E7)
├── interface/views.py              # docstring de concluida (021 FR-003 revista)
└── demonstracao/cenario.py         # _carregar_contatos após _carregar_contextos
config/settings.py, config/urls.py, .env.example             # apps, rota /meu-email/, 4 configurações

tests/
├── contato/                        # modelo, normalização, política, carga, página, isolamento
├── mobilizacao/                    # seleção, prévia, confirmação, duplicidade, concorrência,
│                                   # envio, retomada, modos, governança, acessibilidade, vazamento
└── (ajustes) comunicacao/, governanca/, acompanhamento/, acesso/, analitico/,
    exportacao/, interface/, narrativa/, demonstracao
```

**Structure Decision**: dois apps novos, no padrão dos apps por capacidade (como
`contexto_trajetoria` e `declaracao`):

- `contato` não depende de `mobilizacao`;
- `mobilizacao` depende de `contato`, `campanha`, `governanca`, `acompanhamento` (escopo e
  visibilidade) e `comunicacao` (renderer e transporte);
- `comunicacao` deixa de depender de `campanha` e `acompanhamento`.

Notas de revisão de specs anteriores (001, 004/ADR 0004, 010, 014, 016, 021) e a
documentação institucional são atualizadas na implementação.

## Complexity Tracking

Não há violação. Três pontos de complexidade ficam registrados por transparência (Princípio
XXII):

| Elemento | Por que é necessário | Alternativa mais simples rejeitada porque |
|----------|----------------------|-------------------------------------------|
| `MembroDoLote.campanha` + restrição única parcial | Garante no banco no máximo uma abordagem por Pessoa e Campanha (SC-001) | Só a verificação em código não protege contra concorrência nem contra erro futuro |
| Situação `EM_TENTATIVA` | Evita reenvio silencioso após queda entre o envio e o registro (FR-028) | Registrar só depois reenviaria sem saber |
| Observação de contatos por `obtido_em` + `posicao` | Mantém a ordem do adaptador e a idempotência sem tabela extra (research R2) | A unicidade por valor perde reordenação e contraria a ordem declarada |
