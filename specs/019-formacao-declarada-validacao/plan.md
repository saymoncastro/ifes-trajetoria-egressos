# Implementation Plan: Formação não localizada e validação posterior

**Branch**: `claude/spec-019-academic-context-d2481f` | **Date**: 2026-10-04 | **Spec**: [spec.md](spec.md)

**Input**: `specs/019-formacao-declarada-validacao/spec.md`, revisada em 2026-10-04 (68 FRs).
Constituição **2.0.0** (emenda MAJOR aplicada em 2026-10-04). Base: `main` `2f1ee86`, com
a 018 mergeada.

## Summary

*Revisado em 2026-10-04 com os cinco ajustes do solicitante: chaves por finalidade, selo
endurecido e idempotente, conflito como detectado e pendente, sem app `acervo`, e
preenchimento dos snapshots provado.*

O plano tem **um app novo**, `declaracao`. Ele contém:
- a `FormacaoDeclarada`: dado declarado, imutável, com `chave_de_criacao` única para
  criação idempotente;
- os `DadosConsultaAcervo`: CPF e data cifrados com Fernet (chave B), separáveis e
  descartáveis;
- a `ValidacaoDaFormacao`: decisão única e imutável, com
  `fora_da_abrangencia_na_validacao` congelado e `conflito_detectado_na_validacao`
  pendente até uma resolução futura;
- a trilha `AcessoAosDadosDeConsulta`;
- a `ReferenciaDeAcervo`, com o adaptador `FonteAcervoHistorico` no contrato da fronteira
  acadêmica. Assim, a Conclusão confirmada pelo acervo nasce pela incorporação normal da
  001.

O acervo **não** vira app: não tem autorização, ciclo de vida nem consumidor próprios
(R1).

A `Participacao` ganha uma âncora alternativa: `formacao_declarada`, com CHECK de
exatamente uma âncora e `conclusao` anulável. A jornada da 005, 006 e 008 é reaproveitada
sem regra nova. Só mudam a posse (sujeito da sessão) e o rótulo do contexto.

Uma única consulta, `participacoes_oficiais()`, define o que é **oficial** e a
**Conclusão efetiva**. A 007, a 011, a 012 e a 013 passam a usá-la. O snapshot da 012
congela qual Participação compõe cada registro, para que uma validação posterior nunca
altere um snapshot antigo. A exportação da 013 ganha `origem_formacao`, com contrato na
versão 2.

Entre a `NAO_CONFIRMADA` e o "Começar", CPF e data viajam em **selos transitórios**:
Fernet com a chave A, validade curta e finalidade explícita, só em POST. Nada é gravado
no banco nem na sessão antes de existir a declaração. O consumo do selo de início é
idempotente (R6).

**Migrações**:
- `declaracao/0001`;
- `participacao/000N`: âncora, aditiva;
- `analitico/000N`: dois campos, mais migração de dados com determinismo provado e aborto
  em ambiguidade (R14).

Pessoa, Conclusão, Resposta, Campanha e Versão não mudam.

## Technical Context

**Language/Version**: Python >=3.13,<3.14.

**Primary Dependencies**: Django >=5.2,<5.3.
- **Nova:** `cryptography` (PyCA), usada **só** para Fernet (R5). Justificativa: a
  biblioteca padrão não tem criptografia simétrica autenticada, e cifra própria é
  inaceitável. Entra em `tests/dependencias.py` e na ADR 0005, criada na implementação.
- **Sem JavaScript.**

**Storage**: PostgreSQL existente.
- 5 tabelas novas, todas em `declaracao`.
- 2 tabelas alteradas, de forma aditiva: `participacao_participacao` e
  `analitico_registrodosnapshot`.

**Testing**: pytest, pytest-django e ruff, como na 018. Também:
- duas transações para a serialização (padrão 005 R11);
- `caplog` e varredura do banco para vazamento (SC-007);
- relógio controlado para a validade do selo;
- o **primeiro teste de migração** do projeto (`MigrationExecutor`), para o preenchimento
  dos snapshots (R14).

**Target Platform**: execução local, `runserver` com `TRAJETORIA_DEMONSTRACAO=1`. Chaves:
- as duas da 018;
- `TRAJETORIA_CHAVE_SELO_DECLARACAO` (A);
- `TRAJETORIA_CHAVE_CONSULTA_ACERVO` (B).

Parâmetro opcional: `TRAJETORIA_SELO_DECLARACAO_VALIDADE`, padrão 30 min.

**Project Type**: monólito Django modular, HTML renderizado no servidor.

**Performance Goals**: escala da demonstração. As consultas oficiais acrescentam um JOIN
(declaração → validação). Nenhuma meta produtiva foi inventada.

**Constraints**:
- **CPF e data.** Nunca em claro no banco, logs, URLs, snapshots ou exportações (SC-007).
- **Falha comum da 018.** Não grava nada.
- **Validação.** Nunca altera a Participação, a declaração nem as Respostas.
- **Snapshot.** Um snapshot anterior nunca muda.
- **Ambiente.** Só modo de demonstração.
- **Visual.** Baseline 015.

**Scale/Scope**:
- 1 app novo;
- 5 modelos;
- 7 caminhos novos: 3 do egresso (`/declaracao/`, `nova/`, `comecar/`) e 4 do operador;
- ajustes em `participacao`, `interface`, `acesso`, `acompanhamento`, `analitico`,
  `exportacao`, `governanca` e `demonstracao`.

## Constitution Check

Gate executado antes da Fase 0 e repetido após a Fase 1. Constituição **2.0.0**.

| # | Verificação | Princípios | Pré-Fase 0 | Pós-Fase 1 | Evidência / observação |
| --- | --- | --- | --- | --- | --- |
| 1 | Longitudinalidade | I | ✅ Conforme | ✅ Conforme | I (2.0.0): âncora única e imutável (data-model, CHECK); oficial só com Conclusão identificada (R4); validação não altera nada (contracts/operacoes.md) |
| 2 | Pessoa versus Conclusão | I, XI | ✅ Conforme | ✅ Conforme | Declaração não cria Pessoa (FR-005); Pessoa só pela Conclusão incorporada (R11) |
| 3 | Múltiplas formações sem fusão | I, XI | ✅ Conforme | ✅ Conforme | Pessoa do acervo nunca fundida (R12; FR-084); declarações distintas por formação |
| 4 | Múltiplas participações | I, VIII | ✅ Conforme | ✅ Conforme | Conflito preserva as duas; a oficial anterior não muda (R10, R11) |
| 5 | Definição de egresso | II | ✅ Conforme | ✅ Conforme | Oficial só com Conclusão de fonte institucional (digital ou acervo) |
| 6 | Preservação histórica | VIII, XXVII | ✅ Conforme | ✅ Conforme | Migrações aditivas; snapshot congela a Participação (R14). Determinismo provado por `participacao_par_unico` desde a 0001, Participação imutável e captura só com Campanha encerrada sem reabertura. A migração aborta em ambiguidade. Teste de migração |
| 7 | Pesquisa/Versão/Campanha/Participação | VII, VIII | ✅ Conforme | ✅ Conforme | Mesma Versão; Respostas sempre na Participação |
| 8 | Proveniência | IV | ✅ Conforme | ✅ Conforme | Decisão com operador e momento; Referência de acervo com operador e momento; `origem_formacao` (R15) |
| 9 | Institucional × derivado × declarado | III | ✅ Conforme | ✅ Conforme | Declaração declarada e imutável; acervo institucional sem pré-preenchimento (FR-082); divergência derivada |
| 10 | Desacoplamento | V, XV, XXV | ✅ Conforme | ✅ Conforme | Acervo como adaptador do contrato comum (contracts/fonte-acervo.md); mecanismo da 018 intacto (FR-004) |
| 11 | Fronteira do NIAE | VI | ✅ Conforme | ✅ Conforme | Spec, "Fronteira do NIAE"; o NIAE guarda só a referência atestada |
| 12 | Governança | IX, X | ⏸ DECISÃO PENDENTE | ⏸ DECISÃO PENDENTE | O operador "registra o resultado obtido", sem atestar (FR-062). Competência: DP-1901 |
| 13 | Escopo por unidade | XII | ✅ Conforme | ✅ Conforme | E3; escopo por unidade declarada e da Conclusão; 404 indistinguível |
| 14 | Privacidade e logs | XVI, XVII | ⏸ DECISÃO PENDENTE | ⏸ DECISÃO PENDENTE | Desenho conforme: HMAC; Fernet com chaves separadas por finalidade; revelação explícita registrada; selos só em POST, com validade curta, `sensitive_post_parameters` e `no-store`. O uso real depende de DP-1902 e DP-1903 e da 018/DP-1801 a DP-1803 |
| 15 | Autorização | X, XII | ✅ Conforme | ✅ Conforme | `pode_validar_formacao`; posse pelo sujeito da sessão (R7, R19) |
| 16 | Acessibilidade | XX | ✅ Conforme | ✅ Conforme | contracts/rotas.md, "Acessibilidade" |
| 17 | Responsividade | XIV, XXI | ✅ Conforme | ✅ Conforme | Cinco campos; shell da 015; 320 px |
| 18 | Testes proporcionais | XXV, XXVI | ✅ Conforme | ✅ Conforme | R22 |
| 19 | Over engineering | XXII, XXIII, XXIV | ✅ Conforme | ✅ Conforme | Sem workflow nem estados intermediários; decisão com dois resultados; um indicador na 011; uma consulta oficial para quatro consumidores; Fernet dispensa campo de versão de chave; sessão só com UUIDs; sem catálogo novo (R20) |
| 20 | Exportabilidade | XVIII | ✅ Conforme | ✅ Conforme | `origem_formacao`; contrato v2; nada pessoal exportado |
| 21 | Decisões pendentes | XXIX | ✅ Conforme | ✅ Conforme | Spec DP-1901 a DP-1911; hipóteses E1 a E9 |

**Resultado do gate**: APROVADO.

Os itens 12 e 14 ficam em DECISÃO PENDENTE, como na 018. O desenho é conforme com dados
fictícios, e o bloqueio do uso real está registrado.

**Conflitos identificados**, analisados nos quatro passos:

- **001 FR-030, que veda cadastro manual de Conclusão.**
  1. *A feature está incorreta?* Não.
  2. *Escopo excessivo?* Não.
  3. *Alternativa compatível?* Sim. A Conclusão do acervo nasce pela incorporação, a
     partir de uma fonte (R12). A nota de revisão na 001 registra o acervo como fonte
     institucional.
  4. Sem emenda.
- **012 ("só o que deriva é persistido; Participação referenciada na leitura").** A
  leitura por `(campanha, conclusao_id)` deixaria um snapshot antigo mudar depois de uma
  validação. A alternativa compatível é congelar a referência no registro (R14), com nota
  de revisão na 012. Sem emenda.
- **004 FR-017 ("nenhum critério inclui quem não tem Conclusão").** A população continua
  só de Conclusões (FR-023). A compatibilidade provisória decide só a **admissão** da
  Participação declarada. Nota de revisão na 004. Sem emenda.
- **018 FR-034 ("`NAO_CONFIRMADA` não altera sessão") e FR-040.** São respeitados. O selo
  de trânsito vai na página, não na sessão. A sessão do declarante guarda só UUIDs, o que
  é mais restritivo que a letra da FR-040 da 019 (R7). Nota de revisão na 018.
- **005 FR-002 e 006 FR-035.** Revistos pela emenda 2.0.0 (âncora). As notas são aplicadas
  na implementação.

## Decisões Pendentes

| ID | DECISÃO PENDENTE | Instância competente | Solução provisória (hipótese) | Como reverter |
| --- | --- | --- | --- | --- |
| DP-1901 | Quem atesta e quem registra | Proex/Proen/CPAEG + registro acadêmico | `pode_validar_formacao` para CPAEG e CSAEG, com texto de "registra o resultado obtido" | Trocar a função de regra (010) |
| DP-1902 | Quem vê dados identificados | Encarregado + CPAEG | Só a capacidade, no escopo; só dados fictícios | Restringir a regra ou o escopo |
| DP-1903 | Base legal, retenção, descarte, chaves | Encarregado + DTI | Nada é descartado; chaves locais. Rotação da chave B: `MultiFernet`, com a chave antiga mantida até todos os registros serem recifrados (R5) | Descarte = remover `DadosConsultaAcervo` (já separável) |
| DP-1904 | Evidência e forma da referência | Registro acadêmico + CPAEG | Referência em texto; sem anexo | Acrescentar campo com consumidor |
| DP-1905 | Reabertura e correção | CPAEG + registro acadêmico | Decisões e Referências imutáveis | Operação nova, com snapshot preservado |
| DP-1906 | Dados para localizar no acervo | Registro acadêmico | Cinco campos, mais CPF e data cifrados | Campo novo aditivo |
| DP-1907 | Resolução de conflito | CPAEG | A anterior prevalece; a nova fica em conflito **pendente** | Registro de resolução novo; o filtro oficial muda num único `Q` (R3, R4) |
| DP-1908 | Notificação ao egresso | Proex/CPAEG + encarregado | Nenhuma | — |
| DP-1909 | Pessoa do acervo × outra fonte; acesso futuro | DTI + registro acadêmico | Sem associação; nova rodada exige nova declaração | Reconciliação própria (001/DP-003) |
| DP-1910 | Prazo e SLA da fila | CPAEG | Nada expira | — |
| DP-1911 | Acervo digitalizado institucional | DTI + registro acadêmico | `ReferenciaDeAcervo` como fonte | Trocar o adaptador (Princípio V) |
| 001/DP-007, 010/DP-1005 | Vocabulário de unidade e nível | DTI/registro acadêmico; CPAEG | Valores existentes em Conclusões e critérios (R20) | Trocar a fonte das listas |

## Project Structure

### Documentation (this feature)

```text
specs/019-formacao-declarada-validacao/
├── spec.md
├── plan.md              # este arquivo
├── research.md          # R1–R22
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── rotas.md
│   ├── operacoes.md
│   ├── fonte-acervo.md
│   └── dados-oficiais.md
├── checklists/requirements.md
└── tasks.md             # /speckit-tasks — NÃO criado agora
```

### Source Code (repository root)

```text
trajetoria/
├── declaracao/                 # novo
│   ├── models.py               # FormacaoDeclarada, DadosConsultaAcervo, ValidacaoDaFormacao,
│   │                           # AcessoAosDadosDeConsulta, ReferenciaDeAcervo
│   ├── selo.py                 # Fernet: chave A (selos de trânsito e de início) e
│   │                           # chave B (consulta) (R5, R6)
│   ├── acervo.py               # FonteAcervoHistorico (contrato FonteAcademica) e
│   │                           # registrar_referencia (R12)
│   ├── operacoes.py            # iniciar_participacao_declarada, registrar_validacao,
│   │                           # revelar_dados, campanhas_compativeis
│   ├── consultas.py            # fila, candidatas, outras do mesmo CPF, divergência
│   ├── views_egresso.py        # /declaracao/…
│   ├── views_validacao.py      # /validacoes-formacao/…
│   ├── formularios.py, mensagens.py, urls.py, templates/, migrations/
├── participacao/               # models (âncora), operacoes (bloqueio + FR-092),
│                               # consultas (participacoes_oficiais), entrada (R18)
├── interface/                  # views (posse por sujeito), apresentacao (rótulo declarado)
├── acesso/                     # transito (selo de NAO_CONFIRMADA, chave A), views +
│                               # template (botão), demonstracao (painel); não importa a 019
├── acompanhamento/             # consultas (oficiais, atributo efetivo), indicador da fila
├── analitico/                  # models (2 campos), migração de dados (R14), operacoes
│                               # (universo oficial), consultas
├── exportacao/                 # contrato (coluna, v2), dataset
├── governanca/regras.py        # pode_validar_formacao
├── demonstracao/               # base (admite acervo), cenario (Pessoa não importada)
└── fonte_academica/cenarios.py # pares fictícios de declaração; Pessoa não importada
tests/
├── declaracao/                 # novo; inclui o teste de migração dos snapshots (R14)
└── participacao/ interface/ acesso/ acompanhamento/ analitico/ exportacao/ governanca/
                                # ajustes + fronteiras
docs/adr/0005-criptografia-dados-consulta-acervo.md   # na implementação
```

**Structure Decision**: um app novo (`declaracao`) e ajustes localizados nos existentes
(R1). `fonte_academica` continua Python puro. Nenhum módulo genérico, nenhuma camada de
serviço nova.

### Ordem sugerida para as tasks (fatias independentes)

1. **Âncora e oficialidade.** Modelos de `declaracao` e alteração da Participação, mais
   `participacoes_oficiais`. Ajustes de 007, 011, 012 e 013 com declaradas criadas em
   teste. Garante a quarentena antes de existir interface.
2. **Caminho do egresso.** Selo, sessão do declarante, telas e jornada (US1, US7).
3. **Validação pela fonte digital.** Fila, revelação e trilha, candidatas, conflito e
   abrangência (US3, US5).
4. **Acervo histórico.** `ReferenciaDeAcervo`, adaptador e validação pelo acervo (US4).
5. **Demonstração, ADR 0005 e notas de revisão** nas specs 001, 004, 005, 006, 007, 008,
   011, 012, 013, 018 e na ADR 0004.

## Complexity Tracking

Nenhuma violação de princípio. Para revisão, registram-se os acréscimos que aumentam
superfície e por que o mais simples não serviu:

| Acréscimo | Por quê | Alternativa mais simples rejeitada |
| --- | --- | --- |
| Dependência `cryptography` | CPF e data precisam ser legíveis ao validador (decisão 10), e a biblioteca padrão não cifra | Só HMAC: irreversível, não serve à busca no acervo |
| Adaptador de fonte dentro de `declaracao` | Sem autorização, ciclo de vida ou consumidor próprios, não justifica app (R1). O núcleo só conhece o contrato (V) | App `acervo`: um app por feature. Dentro de `fonte_academica`: quebra o "Python puro" da 001 |
| Duas chaves Fernet | Finalidades, vida e rotação diferentes (R5) | Uma chave: rotacionar o selo exigiria recifrar dados persistidos |
| `chave_de_criacao` única | Consumo idempotente do selo (R6) | Tabela de tokens consumidos: infraestrutura sem ganho |
| `participacao` no registro do snapshot | Reprodutibilidade depois de validações (FR-103) | Leitura por `(campanha, conclusao_id)`: muda snapshot antigo |
| Selos transitórios no formulário | Nada persistido em falhas da 018 | Sessão no banco: persistiria a cada falha |
