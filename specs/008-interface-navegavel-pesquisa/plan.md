# Implementation Plan: Interface navegável mínima da pesquisa

**Branch**: `claude/feature-008-interface-pesquisa-05dce9` | **Date**: 2026-10-01 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/008-interface-navegavel-pesquisa/spec.md`

## Summary

Primeiro vertical slice navegável do Trajetória Ifes: páginas geradas no servidor, sem
JavaScript, sobre as operações existentes. Um egresso **fictício** escolhe sua pessoa numa
entrada de demonstração, vê suas formações (007), inicia ou retoma a Participação (007 →
005), responde Seção a Seção (005), segue o percurso calculado pela 006, retoma o
rascunho e conclui (006).

Abordagem técnica (detalhes em [research.md](research.md)):

- **Dois apps sem modelos**: `trajetoria.interface` (jornada) e
  `trajetoria.demonstracao` (adaptador temporário, removível) — R1.
- **Configuração mínima**: templates, CSRF, `ALLOWED_HOSTS` local; nenhum app
  `django.contrib.*`; `DEBUG=False` fixo; nenhuma dependência nova — R2, R20.
- **Modo de demonstração** desligado por padrão; desligado, toda rota é 404 (middleware) e
  o preparo recusa — R3.
- **Pessoa em uso** num cookie assinado, revalidado a cada requisição contra a fonte
  simulada; nenhum outro estado entre requisições — R4.
- **Formulário dinâmico** (`forms.Form`) derivado de `ConteudoSecao`, campos por posição,
  todos opcionais; **gravação atômica** da Seção como uma operação da 005 por Pergunta
  alterada, com todos os erros reunidos — R6, R7.
- **Navegação só pela 006**: após salvar, pendências ou destino da Seção enviada; Seção
  atual ao entrar; redirecionamento após POST — R8.
- **Conclusão** em tela própria, chamando só `concluir` da 006 — R11.
- **Acessibilidade e responsividade** com HTML semântico e uma folha CSS inline, sem
  pipeline de estáticos — R13, R14.
- **Cenário de demonstração** por `manage.py preparar_demonstracao`, só com operações das
  001–004; cópia publicada da baseline; duas Campanhas de demonstração — R17.
- **Testes por HTTP** (cliente do Django), operações reais, relógio controlado, 17
  percursos pela interface, Versão de estrutura diferente, verificação estrutural de
  acessibilidade e de fronteiras — R18, R19.

## Technical Context

**Language/Version**: Python 3.13 (ADR 0001)

**Primary Dependencies**: Django 5.2 LTS (templates, forms, CSRF, `never_cache`,
`require_*`), psycopg 3. **Nenhuma dependência nova** (sem framework de frontend, CSS,
formulários, WhiteNoise ou freezegun).

**Storage**: PostgreSQL 16+. **Nenhuma tabela, coluna ou migração nova.** Estado de
apresentação: um cookie assinado com o `pk` da Pessoa de demonstração.

**Testing**: pytest + pytest-django; `django.test.Client` (sem JavaScript);
`html.parser` da biblioteca padrão para verificação estrutural; `ast` para fronteiras de
importação; `monkeypatch` de `django.utils.timezone.now` para o relógio.

**Target Platform**: servidor de desenvolvimento local (`manage.py runserver`) e CI
existente (GitHub Actions, Postgres 16). Navegadores atuais de desktop e celular, com ou
sem JavaScript.

**Project Type**: aplicação web monolítica server-rendered (monólito modular Django
existente).

**Performance Goals**: interação de demonstração local; cada página da jornada com
número de consultas limitado e independente da quantidade de Respostas (conteúdo da
Versão + Respostas + jornada; verificado com `django_assert_max_num_queries` nas telas de
Seção e formações).

**Constraints**: sem JavaScript como dependência; sem recursos de terceiros; sem
traceback ao usuário (`DEBUG=False`); WCAG 2.1 AA como direção; 320 px a desktop e zoom
200%; sem valores declarados em logs e URLs; modo de demonstração desligado por padrão.

**Scale/Scope**: 10 rotas, ~12 templates, 2 apps, 1 comando; baseline de 13 Seções e 54
Perguntas; 9 Pessoas fictícias materializadas.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Verificação | Princípios | Pré-Fase 0 | Pós-Fase 1 | Evidência / observação |
|---|-------------|------------|------------|------------|------------------------|
| 1 | Longitudinalidade (Pessoa → Conclusão → Participação → Respostas) | I | ✅ | ✅ | Participação só pela entrada da 007 (que usa a 005); nenhuma segunda Participação para o par; concluída não reaberta ([rotas](contracts/rotas.md#post-formacoesentrar--exige-pessoa)) |
| 2 | Pessoa versus Conclusão Acadêmica | I, XI | ✅ | ✅ | Contexto exibido é sempre o da Conclusão (`contexto_da_formacao`); a Pessoa só fornece o nome na entrada de demonstração |
| 3 | Múltiplas formações sem fusão | I, XI | ✅ | ✅ | Tela de formações reproduz a 007: seleção sem ranking; cada formação com sua Participação (E2E-3) |
| 4 | Múltiplas participações sem sobrescrita | I, VIII | ✅ | ✅ | Nenhuma escrita além de 005/006/007; concluída imutável por todas as rotas (FR-064) |
| 5 | Definição institucional de egresso | II | ✅ | ✅ | Só Conclusões incorporadas pela 001; elegibilidade só pela 004 via 007 |
| 6 | Preservação histórica | VIII, XXVII | ✅ | ✅ | Textos exatamente como na Versão; baseline continua RASCUNHO; nenhuma migração; nenhuma remoção de Participação (reinício = recriar banco local) |
| 7 | Pesquisa/Versão/Campanha/Participação distintas | VII | ✅ | ✅ | O egresso vê formação; Campanha nunca aparece; a Versão vem da Campanha da Participação |
| 8 | Proveniência proporcional | IV | ✅ | ✅ | Nenhum metadado de acesso gravado; contexto lido da Conclusão, nunca copiado |
| 9 | Institucional ≠ derivado ≠ declarado | III | ✅ | ✅ | Contexto em região própria "Sobre a sua formação", nunca `initial` de campo; Q10–Q19 sem pré-preenchimento (teste em `test_interface_secao.py`) |
| 10 | Desacoplamento de integrações | V, XV, XXV | ✅ | ✅ | Adaptador de demonstração isolado em app próprio, trocável por uma importação; nenhuma autenticação; testes sem sistema externo |
| 11 | Fronteira do NIAE | VI | ✅ | ✅ | Respondida na spec; identidade e Portal fora |
| 12 | Governança (periodicidade, publicação, competências) | IX, X | ✅ | ✅ | Nenhuma operação de Campanha ou publicação na interface; o comando de preparo publica só cópia local de demonstração (002/DP-001; 004/DP-402) |
| 13 | Escopo por unidade / visão consolidada | XII | N/A | N/A | Sem visão administrativa |
| 14 | Privacidade e minimização | XVI, XVII | ⏸ | ⏸ | Modo desligado por padrão; só fonte simulada (listagem, cookie e preparo); sem resumo de respostas; sem analytics/terceiros; `never_cache`; nada em logs/URLs (teste com `caplog`). **001/DP-009 e 005/DP-504 bloqueiam uso real** |
| 15 | Autorização | X, XII | ✅ | ✅ | Posse verificada a cada requisição (Participação ↔ Pessoa em uso); alheio = inexistente (404). Autorização real depende de 004/DP-406 e 005/DP-505 |
| 16 | Acessibilidade (WCAG 2.1 AA / eMAG) | XX | ✅ | ✅ | R13: semântica, rótulos, `fieldset/legend`, `aria-describedby`, resumo de erros, foco visível, contraste verificado; teste estrutural + roteiro manual |
| 17 | Responsividade e jornada móvel | XIV, XXI | ✅ | ✅ | R14: coluna única fluida, 320 px, zoom 200%, alvos ≥ 44px; listas longas em `<select>` (R10); uma formação pendente dispensa escolha |
| 18 | Testes proporcionais ao risco | XXV, XXVI | ✅ | ✅ | R19: E2E-1 a E2E-4 por HTTP com operações reais; 17 percursos; Versão diferente; atomicidade; fronteiras |
| 19 | Over engineering | XXII, XXIII, XXIV | ✅ | ✅ | Sem SPA, API, design system, wizard, form builder, progresso ou modelo; Django puro; uma folha CSS inline. Complexity Tracking sem violações |
| 20 | Exportabilidade | XVIII | N/A | N/A | Fora do escopo |
| 21 | Decisões pendentes explicitadas | XXIX | ✅ | ✅ | DP-801 a DP-803 e herdadas; as cinco escolhas de produto [Hipótese] confirmadas pelo solicitante e registradas em spec, Clarifications (Session 2026-10-01), sem resolver regra institucional |

**Resultado do gate**: APROVADO (pré-Fase 0 e pós-Fase 1). O item 14 permanece como
DECISÃO PENDENTE, sem violação: a interface só existe em modo de demonstração, com dados
fictícios.

**Revisão pós-implementação (2026-10-01, T047)**: gate mantido. Definition of Done
atendida:

- suíte completa: **1075 testes verdes** (916 anteriores + 159 da 008, em
  `tests/interface/`); `ruff check`, `manage.py check` e `makemigrations --check` limpos;
- **zero modelos, zero migrações**: os dois apps novos (`trajetoria/interface/`,
  `trajetoria/demonstracao/`) não têm `models.py`; continuam as mesmas 5 migrações;
- **nenhuma dependência nova**; nenhum `<script>`; nenhum recurso externo; CSS único
  incluído inline;
- `git diff origin/main` vazio nos apps de domínio e nos testes existentes, exceto o ajuste
  previsto de `test_10` da 007 (T003); fora isso, `config/settings.py`, `config/urls.py`,
  `README.md` e `.env.example`;
- testes novos além do previsto no plan: `test_interface_cenario.py` e
  `test_interface_entrada.py` (separados para paralelismo); auxiliar de teste
  `tests/interface/urls_falha.py` (view que falha, só para FR-069);
- **consultas medidas (T043, refeitas após o code review)**: tela de formações 5–6 (2 + 1
  por formação; teto 8 no teste); tela de Seção 11, igual com o percurso vazio ou completo
  (não cresce com as Respostas; teto 11 no teste) — o título e os textos vêm da Versão já
  carregada com a Participação, e o destino é a passagem seguinte do percurso, sem reler o
  conteúdo da Versão;
- **quickstart manual (T044)**, num banco `trajetoria_demo`: os três comandos funcionam; o
  preparo recusa com o modo desligado; no navegador, entrada de demonstração, tela de
  formações, S1 com texto de abertura, avanço S1 → S2 pela 006, pendências com resumo e
  título "Erro:", rótulos expostos na árvore de acessibilidade, largura de 320 px sem
  rolagem horizontal e 0 scripts. Ajuste de redação decorrente: "O que já foi preenchido
  nesta seção foi salvo." (antes: "As demais respostas foram salvas.", impreciso quando
  nada fora preenchido);
- achados baixos do `/speckit-analyze` absorvidos: C2 (importações da interface a partir
  da demonstração restritas a `pessoa_em_uso`, verificado), C3 (nenhum indicador de
  progresso, verificado), U2 (rota `""`), U3 (`empty_value=None` na escala);
- `django.request` registra no console sem `propagate=False`, para que a falha
  inesperada seja verificável (`caplog`) — sem dados declarados no registro.
- **code review (2026-10-01)**: dez achados, todos corrigidos, cada um com teste de
  regressão — conclusão rejeitada por motivo que não é pendência vira "pesquisa
  indisponível" (sem lista de motivos mantida à mão); "O que já foi preenchido… foi salvo"
  só após um envio aceito (`&salvo=1`); formulários com `action` explícito, sem herdar a
  query string; recusas de domínio no preparo viram `CommandError`; `ALLOWED_HOSTS` sem
  espaços; Pessoa em uso memorizada na requisição; conteúdo da Versão não relido nas
  telas; resumo da formação lido dos atributos, não dos rótulos; posição de Opção
  desconhecida vira erro da Pergunta sem instâncias falsas; "Trocar de pessoa" como
  ligação e um único POST de encerramento.

**Conflitos identificados**: nenhum. Tensão registrada (spec, "Tensões identificadas"):
as features 005 (FR-058), 006 (FR-054) e 007 (FR-049) vedam exposição a egressos sem
fronteira de identidade; a 008 expõe **somente** em modo de demonstração local, com
Pessoas da fonte simulada. Os comentários de `config/settings.py` são atualizados para
dizer isso; as specs anteriores não são editadas.

## Decisões Pendentes

Nenhuma é resolvida pelo plan. Tratamento provisório adotado no desenho:

- **DP-801** (identidade visual e linguagem): paleta neutra com contraste AA, textos em
  `mensagens.py` e templates, revisáveis sem mudança de comportamento (R12, R14).
- **DP-802** (acesso às próprias respostas): nenhuma rota de resumo, cópia ou comprovante.
- **DP-803** (métricas de uso): nenhum evento, nenhum script, só o logger técnico.
- **004/DP-406**, **005/DP-505**: adaptador de demonstração isolado (R1, R3, R4).
- **005/DP-504**, **002/DP-007**, **001/DP-009**: só dados fictícios; Q1 como Pergunta
  comum.
- **007/DP-701**: texto neutro para ambiguidade. **007/DP-702**: só atributos existentes.
- **003/DP-301**: rótulo de escala ausente não é exibido. **003/DP-307**: Q10–Q19 como
  Perguntas comuns.
- **006/DP-601/602/603**, **005/DP-502/503**: confirmação neutra; complemento opcional;
  sem edição pós-conclusão; sem prazo; sem limpeza de rascunhos.

## Desenho

### Camadas

```text
navegador (HTML + formulários, sem JS)
   │
   ▼
config/urls.py ──► trajetoria.demonstracao.urls   (entrada demo: escolher / encerrar)
              └──► trajetoria.interface.urls      (formações, Seção, conclusão)
   │
   │  ModoDemonstracaoMiddleware (404 se desligado)
   │  pessoa_em_uso(request) ◄── cookie assinado (só fonte simulada)
   ▼
trajetoria.interface.views ──► apresentacao.py (contexto da formação, nomes)
                          ├──► formularios.py (FormularioDaSecao)
                          ├──► gravacao.py    (salvar_secao → 005, atômico)
                          └──► mensagens.py   (motivos → textos)
   │
   ▼  (somente estas chamadas de domínio)
007 situacao_de_entrada · entrar
006 situacao_da_jornada · concluir
005 responder_escolha_unica · responder_escolha_multipla · responder_texto ·
    responder_escala · remover_resposta
002 conteudo_da_versao (leitura) · Pergunta/Opcao (leitura)
```

### Fluxo da Seção (resumo de [rotas](contracts/rotas.md))

```text
GET  secoes/<n>  → jornada(006) → [concluída | encerrada | n∉percurso | formulário]
POST secoes/<n>  → jornada(006) → [concluída | encerrada | n∉percurso]
                 → FormularioDaSecao (forma)          → inválido: reapresenta, nada gravado
                 → salvar_secao (005, atômico)        → erro: reapresenta, nada gravado
                 → jornada(006).passagem(n)
                      pendentes → 302 secoes/<n>?pendencias=1
                      destino   → 302 secoes/<destino>
                      fim       → 302 concluir
```

### Tempo e concorrência

- A interface nunca passa `agora`; cada operação lê o relógio (R18).
- A gravação da Seção é uma transação; o bloqueio da Participação, tomado pela primeira
  operação da 005, vale até o fim — conclusões concorrentes esperam ou rejeitam a escrita
  (006 FR-043).
- `entrar` e `concluir` são idempotentes na 007/006; duplo clique é inofensivo.

### Erros

Resultados previstos têm tela (data-model §4). Inesperados → `500.html` estático e log
no console. Nenhum traceback ao usuário (`DEBUG=False`).

## Project Structure

### Documentation (this feature)

```text
specs/008-interface-navegavel-pesquisa/
├── spec.md
├── plan.md              # este arquivo
├── research.md          # Fase 0 (R1–R20)
├── data-model.md        # Fase 1 (sem entidades novas; estados e telas)
├── quickstart.md        # Fase 1 (preparo, validação, roteiros manuais)
├── contracts/
│   ├── rotas.md
│   ├── formulario-secao.md
│   └── demonstracao.md
├── checklists/requirements.md
└── tasks.md             # /speckit-tasks (não criado aqui)
```

### Source Code (repository root)

```text
config/
├── settings.py                  # ALTERADO: apps, MIDDLEWARE, TEMPLATES, ALLOWED_HOSTS,
│                                #   TRAJETORIA_DEMONSTRACAO, logger django.request
└── urls.py                      # ALTERADO: inclui demonstracao.urls e interface.urls

trajetoria/
├── demonstracao/                # NOVO — adaptador temporário (removível)
│   ├── __init__.py
│   ├── apps.py
│   ├── middleware.py            # ModoDemonstracaoMiddleware
│   ├── entrada.py               # pessoa_em_uso, pessoas_de_demonstracao, usar, esquecer
│   ├── contexto.py              # processador de contexto (faixa e cabeçalho)
│   ├── views.py                 # entrada de demonstração, escolher, encerrar
│   ├── urls.py
│   ├── cenario.py               # preparar() — só operações 001–004 (+ 007 no resumo)
│   ├── management/commands/preparar_demonstracao.py
│   └── templates/demonstracao/entrada.html
└── interface/                   # NOVO — jornada do egresso
    ├── __init__.py
    ├── apps.py
    ├── views.py                 # inicio, formacoes, entrar, participacao, secao,
    │                            #   concluir, concluida
    ├── urls.py
    ├── apresentacao.py          # contexto_da_formacao, posição ↔ Seção, título
    ├── formularios.py           # FormularioDaSecao (LIMITE_RADIOS = 10)
    ├── gravacao.py              # salvar_secao, ResultadoDaGravacao
    ├── mensagens.py             # textos de erro por motivo/código
    └── templates/
        ├── 404.html
        ├── 500.html
        ├── 403_csrf.html
        └── interface/
            ├── base.html        # lang, título, pular, faixa demo, cabeçalho, CSS inline
            ├── estilo.css       # incluída inline
            ├── formacoes.html
            ├── secao.html
            ├── perguntas/{escolha_unica,escolha_multipla,texto_curto,escala}.html
            ├── conclusao.html
            ├── concluida.html
            └── aviso.html       # já respondida | período encerrado | indisponível |
                                 #   formação não disponível

tests/interface/                 # NOVO (sem __init__.py, como tests/participacao/)
├── conftest.py                  # modo ligado, relógio, cliente com Pessoa
├── construcao_interface.py      # auxiliares (reutiliza tests/participacao/construcao*)
├── test_interface_demonstracao.py
├── test_interface_cenario.py      # comando preparar_demonstracao
├── test_interface_entrada.py      # POST /formacoes/entrar/ e /participacoes/<id>/
├── test_interface_formacoes.py
├── test_interface_secao.py
├── test_interface_gravacao.py
├── test_interface_navegacao.py
├── test_interface_conclusao.py
├── test_interface_encerramento.py
├── test_interface_aceitacao.py
├── test_interface_acessibilidade.py
└── test_interface_fronteiras.py

tests/participacao/test_entrada_aceitacao.py   # AJUSTADO: test_10 restrito aos apps de
                                               #   domínio (ver "Necessidade de voltar…")

README.md                        # ALTERADO: uma linha para o quickstart da 008
.env.example                     # ALTERADO: TRAJETORIA_DEMONSTRACAO, DJANGO_ALLOWED_HOSTS
```

**Structure Decision**: monólito modular existente (ADR 0001). Dois apps novos sem
modelos; apps de domínio (`academico`, `instrumento`, `campanha`, `participacao`,
`fonte_academica`, `formulario_2024`) **não são alterados** (FR-092). Testes novos em
`tests/interface/`, com prefixo `test_interface_` (os nomes de módulo de teste precisam ser
únicos: já existe `tests/test_aceitacao.py` e não há `__init__.py` nos diretórios de
teste). Um único teste existente é ajustado (abaixo).

## Estratégia de testes

Detalhada em [research R19](research.md#r19--estratégia-de-testes). Pontos de controle
para os critérios de sucesso:

| SC | Como é verificado |
|----|-------------------|
| SC-001 | Quickstart: `migrate`, `preparar_demonstracao`, `runserver`; `test_interface_demonstracao.py` executa `call_command("preparar_demonstracao")` |
| SC-002, SC-003 | `test_interface_aceitacao.py` (E2E-1, E2E-2 e variante) |
| SC-004 | `test_interface_navegacao.py`, parametrizado nas 17 combinações, com o oráculo `secoes_esperadas` da 006 |
| SC-005 | `test_interface_navegacao.py` com `construcao.instrumento()` da 005 (estrutura diferente) |
| SC-006, SC-007 | `test_interface_fronteiras.py` (importações via `ast`; textos da `declaracao.py` ausentes dos fontes; nenhum `save/create/update/delete` de modelo nos apps novos) e testes de comportamento |
| SC-008 | `test_interface_secao.py` (valores restaurados nos quatro tipos e complemento) |
| SC-009 | `test_interface_gravacao.py` (retrato antes/depois com `retrato()` da 005) |
| SC-010 | `test_interface_conclusao.py` (todas as rotas após concluir) |
| SC-011 | `test_interface_encerramento.py` (relógio em `ULTIMO_DIA` e `DEPOIS_DO_FIM`; `encerrar` explícito) |
| SC-012 | `test_interface_demonstracao.py` (modo desligado em todas as rotas; Pessoa de outra fonte; recusas do comando) |
| SC-013 | varredura do texto renderizado de todas as telas por UUID, `SIM-`, nomes de Campanha, nomes de `Motivo` |
| SC-014 | `test_interface_acessibilidade.py` + roteiro manual do quickstart |
| SC-015 | roteiro manual do quickstart (320 px, zoom 200%); CSS sem larguras fixas em `px` acima de 320 |
| SC-016 | `test_interface_fronteiras.py` com `caplog` e inspeção dos `Location` dos redirecionamentos |
| SC-017 | `makemigrations --check`; apps novos sem `models.py`; `pyproject.toml` sem dependência nova; nenhum `<script>` nos templates |

Reutilização: `tests/participacao/construcao.py` (`baseline_publicada`, `campanha_aberta`,
`instrumento`, `momento`, `NO_PERIODO`, `ULTIMO_DIA`, `DEPOIS_DO_FIM`, `secoes_esperadas`,
`escolhas_baseline`, `retrato`) e `construcao_entrada.incorporar` — sem alterá-los. A
interface é testada com Pessoas da **fonte simulada**, porque é a única aceita.

## Complexity Tracking

Nenhuma violação da Constituição a justificar. Escolhas que poderiam parecer
complexidade, registradas para revisão:

| Escolha | Por que é necessária | Alternativa mais simples rejeitada porque |
|---------|----------------------|-------------------------------------------|
| Dois apps em vez de um | Fronteira física do adaptador de demonstração substituível (FR-005) | Um app misturaria código temporário e permanente |
| Transação externa sobre várias operações da 005 | Atomicidade da Seção (FR-045) sem alterar contrato da 005 | Parar na primeira rejeição gravaria parte da Seção ou mostraria um erro por vez |
| Verificação de complemento antes da 005 | Complemento sem nenhuma Opção não chega à 005 (vira remoção) e seria perdido em silêncio | Ignorar o complemento descartaria texto digitado sem aviso |
| Lista suspensa acima de 10 Opções | Listas de 30+ cursos em celular (XIV, XXI) | Só rádios: fiel, mas cansativo; autocompletar exige JS |

**Não adotado** (pode ser reavaliado com necessidade concreta): verificação de
acessibilidade com navegador automatizado (axe-core/Playwright); `staticfiles`/WhiteNoise;
sessões Django.

## Necessidade de voltar à spec ou às features anteriores

- **Spec da 008**: nenhuma mudança necessária. As [Hipóteses] foram mantidas como
  desenhadas.
- **Teste existente da 007**: `tests/participacao/test_entrada_aceitacao.py::test_10_nenhum_mecanismo_de_autenticacao`
  verifica, além da ausência de autenticação e sessão (que continua verdadeira), que
  **nenhum** app de `trajetoria/` tem `urls.py`, `views.py`, `forms.py` ou `middleware.py`.
  Essa parte expressava "a 007 não cria interface" e passa a falhar quando a 008 cria
  `trajetoria/interface/` e `trajetoria/demonstracao/`. Ajuste mínimo: restringir a
  verificação de arquivos aos apps de domínio (`academico`, `instrumento`, `campanha`,
  `participacao`, `fonte_academica`, `formulario_2024`), mantendo intactas as demais
  asserções (sem `auth`/`sessions`, middleware sem "session"/"auth", nenhuma rota de
  `trajetoria.participacao`, `__all__` sem nomes proibidos). Não muda contrato nem
  comportamento da 007; é a atualização do teste que descrevia o estado do projeto antes
  da primeira interface.
- **Features 001–007**: nenhum contrato precisa mudar (FR-092). As operações recebem
  instâncias ORM; a interface lê `Pergunta`/`Opcao` para chamá-las (somente leitura). A
  jornada não devolve o `ConteudoVersao` completo; a interface chama
  `conteudo_da_versao` uma vez por página para título e textos de abertura/encerramento —
  custo pequeno e sem alteração da 006.
