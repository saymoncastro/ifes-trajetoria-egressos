# Implementation Plan: Editor institucional de Pesquisa e Versão

**Branch**: `claude/feature-009-research-editor-0de597` | **Date**: 2026-10-01 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/009-editor-pesquisa-versao/spec.md`

## Summary

O plan entrega a interface administrativa mais simples possível sobre a Feature 002:
páginas geradas no servidor, sem JavaScript, para compor e editar uma Versão em rascunho
sem editar código. O operador pode:

- listar e criar Pesquisas;
- listar Versões, criar Versão vazia ou a partir de outra;
- estruturar Seções, Perguntas dos quatro tipos e Opções;
- configurar escala, complemento, encaminhamento e desvio;
- obter um **diagnóstico técnico** derivado;
- pré-visualizar.

Versão publicada é só consultada. O editor não publica.

Abordagem técnica (detalhes em [research.md](research.md)):

- **Um app novo sem modelos**, `trajetoria/editor`. Ele é exigido pelas fronteiras
  existentes: a 007 proíbe views nos apps de domínio, e a 008 proíbe a jornada do egresso
  de importar operações de escrita do instrumento (R1).
- **Mesma entrada não produtiva da 008**: o `ModoDemonstracaoMiddleware` já devolve 404
  em toda requisição quando o modo está desligado, inclusive em `/editor/`. Não há
  autenticação nem autorização (R2).
- **Toda escrita por `trajetoria.instrumento.operacoes`**, num mapa ação → operação
  completo. **Nenhuma alteração na 002** (R3).
- **Uma extração mínima na 006**: `secoes_nao_suportadas(conteudo)`, pública e pura,
  consumida pela própria `_exigir_suporte` (R4).
- **Diagnóstico técnico** = A (`verificar_completude`, 002) + B (`secoes_nao_suportadas`,
  006), compostos em memória. As três situações são derivadas, e a favorável é "sem
  impedimentos técnicos conhecidos". Não há persistência nem enum de aprovação (R5).
- **Três auxiliares pequenos**, cada um com consumidor concreto: `definir_desvio`
  (troca de desvio tudo-ou-nada), `mover` (subir e descer pela reordenação completa) e
  `proxima_posicao` (R6, R7).
- **Páginas em níveis**:
  - páginas de lista não têm campos de texto;
  - páginas de formulário têm um único envio (R8);
  - rótulos operacionais por ordinal e nenhum identificador técnico visível (R9);
  - mensagens num único módulo (R10);
  - `forms.Form` por ação, sem reimplementar regras da 002 (R11).
- **Publicada**: os templates não mostram controles, GET de formulário redireciona e
  POST responde 409 antes de qualquer operação. A 002 continua sendo a recusa definitiva
  (R12).
- **Prévia**: uma Seção por página, reaproveitando a apresentação por tipo da 008
  (`FormularioDaSecao(secao, {}).itens()` e os templates por tipo), sem `<form>` (R13).
  - É leitura, não jornada: anterior e próxima são links GET na ordem estrutural.
  - Não há cursor, sessão ou respostas temporárias, e a 006 não calcula a próxima
    Seção.
  - Os desvios são anotações estruturais.
- **Testes por HTTP** em `tests/editor/` e um teste novo da 006 (R14).

## Technical Context

**Language/Version**: Python 3.13 (ADR 0001).

**Primary Dependencies**: Django 5.2 LTS (views, `forms.Form`, templates, CSRF,
`never_cache`, `require_*`) e psycopg 3. **Nenhuma dependência nova**: não há framework
de frontend, biblioteca de ordenação, CSS framework nem `django.contrib.*`.

**Storage**: PostgreSQL 16+. **Nenhuma tabela, coluna ou migração nova.** Nenhum estado
de interface é persistido: não há sessão, cookie novo, prontidão, prévia nem seleção.

**Testing**:

- pytest + pytest-django e `django.test.Client`, que não executa JavaScript;
- `html.parser` da biblioteca padrão, reaproveitando
  `tests/interface/test_interface_acessibilidade.py::verificar`;
- `ast` para as fronteiras de importação;
- `django_assert_max_num_queries` nas páginas de estrutura e diagnóstico.

**Target Platform**: servidor de desenvolvimento local (`manage.py runserver`), com
`TRAJETORIA_DEMONSTRACAO=1`, e o CI existente (GitHub Actions, Postgres 16). Navegadores
atuais, com ou sem JavaScript.

**Project Type**: aplicação web monolítica server-rendered (monólito modular Django
existente).

**Performance Goals**: uso local por operador. As páginas de estrutura e diagnóstico de
uma Versão do tamanho da baseline (13 Seções, 54 Perguntas, 385 Opções) têm número de
consultas limitado e independente do número de Perguntas: uma leitura de
`conteudo_da_versao` e uma de `verificar_completude`.

**Constraints**:

- sem JavaScript como dependência e sem recursos de terceiros;
- `DEBUG=False`: sem traceback ao usuário;
- sem identificador técnico no texto visível;
- WCAG 2.1 AA como direção, de 320 px a desktop, com zoom de 200%;
- modo não produtivo desligado por padrão.

**Scale/Scope**:

- 25 rotas e 25 views;
- 8 formulários;
- cerca de 21 templates (15 páginas + base + 5 partials) mais 1 CSS. Esses números não são meta (consolidações em tasks.md);
- 1 app novo sem modelos;
- 1 função pública nova na 006;
- 0 alterações na 002.

## Constitution Check

*GATE: aprovado antes da Fase 0 e reavaliado depois da Fase 1.*

| # | Verificação | Princípios | Pré-Fase 0 | Pós-Fase 1 | Evidência / observação |
|---|-------------|------------|------------|------------|------------------------|
| 1 | Longitudinalidade (Pessoa → Conclusão → Participação → Respostas) | I | N/A | N/A | O editor não lê nem escreve Pessoa, Conclusão, Participação ou Resposta (spec FR-005, FR-090; data-model §1). A fronteira de importação é testada (R14) |
| 2 | Pessoa versus Conclusão Acadêmica | I, XI | N/A | N/A | Idem: nenhuma Pessoa nem Conclusão é usada. O `editor/base.html` não mostra Pessoa fictícia (R15) |
| 3 | Múltiplas formações sem fusão artificial | I, XI | N/A | N/A | Fora do alcance do editor |
| 4 | Múltiplas participações sem sobrescrita | I, VIII | N/A | N/A | Nenhuma Participação é criada. A prévia usa `FormularioDaSecao(secao, {})`, sem Resposta (R13) |
| 5 | Definição institucional de egresso | II | N/A | N/A | Fora do alcance |
| 6 | Preservação histórica | VIII, XXVII | ✅ | ✅ | **Publicada**: a interface não mostra controles, GET de formulário redireciona, POST responde 409 sem chamar operação e a recusa definitiva é a da 002 (R12; [rotas](contracts/rotas.md#garantias-comuns)). **Evolução**: só por `criar_versao_a_partir_de` (R3). **Baseline**: não é escrita pelos testes; equivalência verificada ao final (R14). Sem despublicar nem corrigir no lugar (002/DP-003). Sem migração |
| 7 | Versionamento; Pesquisa, Versão, Campanha e Participação distintas | VII, VIII | ✅ | ✅ | O editor trata só Pesquisa e Versão. Sem rota, leitura ou exibição de Campanha ou Participação; sem Campanha nem Participação de prévia (R13; rotas, "O que não existe") |
| 8 | Proveniência proporcional | IV | N/A | N/A | O conteúdo é configuração do instrumento. A autoria e o histórico de rascunhos ficam como DP-903, sem trilha nova |
| 9 | Separação institucional, derivado e declarado | III | ✅ | ✅ | Q10–Q19 não são tocadas automaticamente (spec FR-101); não há fontes nem regras por Pergunta (teste de fontes, R14). O diagnóstico é derivado da configuração, não dado de egresso |
| 10 | Desacoplamento de integrações | V, XV, XXV | ✅ | ✅ | Nenhuma integração. O acesso pela entrada existente é substituível pela 010, sem mecanismo novo (R2) |
| 11 | Fronteira do NIAE | VI | ✅ | ✅ | Spec, "Fronteira do NIAE": o editor é interface sobre Pesquisa e Versão, que pertencem ao domínio. Não há importação ou exportação de definição |
| 12 | Governança institucional (publicação, competências) | IX, X | ✅ | ✅ | **Não publica**: nenhuma chamada a `publicar`, verificada por `ast` (R14). **Sem estados intermediários**: não há estado novo, enum de aprovação ou prontidão gravada. **Situação favorável**: "sem impedimentos técnicos conhecidos", com o texto que diz que não é aprovação (R5; FR-071). **Acesso não produtivo**: declarado como não sendo governança (R2; DP-901) |
| 13 | Escopo por unidade e visão consolidada | XII | ⏸ | ⏸ | Sem escopo por unidade nem ACL de Pesquisa. Competência de elaboração e escopo: DP-901 → Feature 010 |
| 14 | Privacidade e minimização | XVI, XVII | ✅ | ✅ | Não há dado pessoal no editor; logs só de falha técnica (008 R2). Modo desligado por padrão. Q1 não vira consentimento (FR-102) |
| 15 | Autorização (menor privilégio; técnica ≠ normativa) | X, XII | ⏸ | ⏸ | Não há autorização: proibido inventá-la (FR-004). O banner permanente diz que o acesso não confere competência (FR-003). O editor só existe no modo não produtivo. DP-901 e 002/DP-001 continuam abertas |
| 16 | Acessibilidade | XX | ✅ | ✅ | `verificar` da 008 em todas as telas; nomes acessíveis de subir, descer e remover; resumo de erros no topo; estados em texto (R15) |
| 17 | Responsividade e jornada móvel | XIV, XXI | ✅ | ✅ | Folha sem larguras fixas acima de 320 px; roteiro de 320 px e zoom de 200% (quickstart). A jornada do egresso não muda |
| 18 | Testes proporcionais ao risco | XXV, XXVI | ✅ | ✅ | `tests/editor/` (15 arquivos) e o teste novo da 006 cobrem toda a lista pedida (R14). Os testes existentes da 006 e da 008 continuam sem alteração |
| 19 | Over engineering (YAGNI; sem form builder) | XXII, XXIII, XXIV | ✅ | ✅ | Ver a tabela "Sinais de over engineering" abaixo: nenhum presente |
| 20 | Exportabilidade | XVIII | N/A | N/A | A feature não exporta. Exportação ou importação de definição está fora do escopo (FR-106) |
| 21 | Decisões pendentes explícitas; hipóteses não viram regra | XXIX | ✅ | ✅ | As [Hipóteses] da spec estão implementadas como reversíveis (posição ao final, subir e descer, aviso de nome repetido, campo vazio = ausente). A semântica de navegação é explicada como "atual" (006/DP-604). A tabela "Decisões Pendentes" vem abaixo |

**Resultado do gate**: APROVADO antes da Fase 0 e depois da Fase 1. Nenhuma violação.
Os itens ⏸ são decisões institucionais pendentes, com tratamento provisório
reversível, e não violações.

**Conflitos identificados**: nenhum. A única alteração fora do app novo é a promoção, na
006, de uma função privada a pública, sem mudança observável (R4). Ela é a alternativa
compatível ao "segundo validador" que a spec proíbe.

**Sinais de over engineering** (checagem pedida pelo solicitante):

| Sinal | Presente? | Observação |
|-------|-----------|------------|
| App novo sem necessidade | Não | O app existe por bloqueio concreto: 007 test_10 e a fronteira de importação da 008 (R1) |
| Model novo | Não | 0 modelos |
| Workflow, approval, PublicationRequest | Não | Sem rota nem estado de publicação ou aprovação |
| Form builder genérico | Não | 8 `forms.Form` fixos, 4 tipos fixos |
| RuleEngine | Não | O desvio continua sendo "Opção → Seção ou finalizar" (002). A exposição da 006 é uma função de uma linha de lógica |
| API, SPA, component library | Não | Só páginas server-rendered; sem `<script>` |
| Autosave | Não | Cada POST é uma ação explícita |
| Editor visual de grafo | Não | Destinos aparecem como texto |
| Diff de versões, histórico de edição | Não | Só a origem da Versão (002 FR-023); DP-903 |

## Decisões Pendentes

| ID | DECISÃO PENDENTE | Instância competente (se conhecida) | Solução provisória (hipótese) | Como reverter |
|----|------------------|-------------------------------------|-------------------------------|---------------|
| DP-901 | Quem pode elaborar e editar rascunhos, e com que escopo | Proex/CPAEG; Feature 010 | Editor só no modo não produtivo, sem autenticação, com banner (R2) | A 010 adiciona autorização às rotas de `trajetoria/editor`; o domínio não muda |
| DP-902 | Estatuto da baseline migrada (proteger, publicar ou manter rascunho comum) | CPAEG (+ 002/DP-001) | Rascunho comum, sem exceção por nome; testes não a editam; recomendação genérica de trabalhar em cópia; recusa da 003 por divergência é esperada | Decisão futura aplicada por spec própria, sem dado do editor a migrar |
| DP-903 | Autoria e histórico de alterações de rascunhos | CPAEG/Proex; Feature 010 | Nenhum histórico; a última operação aceita prevalece | Acréscimo futuro, aditivo |
| 002/DP-001 | Quem pode publicar | Proex/CPAEG | O editor não publica, nem como botão desabilitado | A 010 decide se e como expor `publicar` |
| 002/DP-002 | Fluxo de elaboração e aprovação | CPAEG | Só RASCUNHO e PUBLICADA; diagnóstico derivado, nunca estado | Spec futura |
| 002/DP-003 | Correção editorial pós-publicação | CPAEG | Imutabilidade total; caminho é nova Versão | Spec futura |
| 002/DP-004 | Melhorias metodológicas | CPAEG | O editor não aplica nem sugere nenhuma | — |
| 002/DP-005 | Tipos e capacidades futuras | CPAEG + spec | Exatamente os 4 tipos e as capacidades da 002 | Spec própria |
| 002/DP-006 | Comparabilidade entre Versões | CPAEG | Só a origem da Versão; sem diff nem identidade global | Spec futura |
| 002/DP-007 | Consentimento | A identificar | Q1 é conteúdo comum | Spec futura |
| 003/DP-307 | Q10–Q19 como contexto institucional | CPAEG + dono da fonte | Nenhuma alteração automática | Spec futura |
| 006/DP-604 | Semântica futura de navegação | CPAEG | Explicada como semântica **atual**; incompatibilidade aparece no diagnóstico B | Mudança na 006 muda `secoes_nao_suportadas`, e o editor acompanha sem alteração |
| 008/DP-801 | Identidade visual e linguagem | Proex/comunicação | Padrão neutro da 008; textos em `editor/mensagens.py` | Revisão de textos sem mudar comportamento |

## Desenho

### Camadas

```text
templates/editor/*.html ── leem valores de apresentação (rótulos, situação, flags)
        ▲
views.py ──────────────── HTTP: método, CSRF, _exigir_rascunho, PRG, 409/404
   │  └─ formularios.py ── conversão de entrada (sem regras do domínio)
   │  └─ acoes.py ──────── proxima_posicao, mover, definir_desvio
   │  └─ diagnostico.py ── diagnosticar = A (002) + B (006)
   │  └─ apresentacao.py ─ rótulos, tipos, escala, destinos, localizador, referências
   │  └─ mensagens.py ──── textos operacionais (todo Motivo coberto)
   ▼
trajetoria.instrumento.operacoes   (002: única escrita)
trajetoria.instrumento.conteudo    (002: leitura)
trajetoria.instrumento.regras      (002: verificar_completude, Motivo, OperacaoRejeitada)
trajetoria.participacao.percurso   (006: secoes_nao_suportadas — leitura pura)
trajetoria.participacao.regras     (006: Motivo.ESTRUTURA_NAO_SUPORTADA, só como causa)
trajetoria.interface.formularios   (008: FormularioDaSecao, só na prévia)
```

Importações permitidas para `trajetoria/editor` (verificadas por `ast`):

| Módulo | Nomes |
|--------|-------|
| `trajetoria.instrumento.operacoes` | as operações do mapa de R3 e `FINALIZAR`; **não** `publicar` nem `renomear_pesquisa` |
| `trajetoria.instrumento.conteudo` | qualquer |
| `trajetoria.instrumento.regras` | `Motivo`, `OperacaoRejeitada`, `verificar_completude` |
| `trajetoria.instrumento.models` | `Pesquisa`, `Versao`, `Secao`, `Pergunta`, `Opcao`, `TipoPergunta` (leitura) |
| `trajetoria.participacao.percurso` | `secoes_nao_suportadas` |
| `trajetoria.participacao.regras` | `Motivo` |
| `trajetoria.interface.formularios` | `FormularioDaSecao` |

Nada de `campanha`, `academico`, `formulario_2024`, `demonstracao`,
`participacao.operacoes`, `participacao.consultas`, `participacao.entrada` nem
`participacao.models`.

### Fluxo de uma escrita (padrão)

```text
POST → objeto (404 se inexistente: aviso "conteúdo mudou")
     → _exigir_rascunho(versao)            # publicada → 409, nenhuma operação
     → formulário.is_valid()               # só conversão (número inteiro, vazio → None)
     → with transaction.atomic(): operação(ões) 002   [+ acoes.definir_desvio]
          OperacaoRejeitada → mapa Motivo→campo → 200 com erros (ou 409 conflito/publicada)
     → 302 para a página de consulta ?aviso=…#âncora
```

### Diagnóstico (resumo de [diagnostico.md](contracts/diagnostico.md))

- `diagnosticar(versao)` é chamado:
  - no GET de `/editor/versoes/<v>/diagnostico/`;
  - no GET da estrutura de rascunho, para o resumo e as marcas por elemento;
  - nas páginas de Seção e Pergunta, para marcar o elemento.
- O resultado guarda todos os problemas concretos (A: um por `Violacao` da 002; B: um
  por Seção da 006). Os booleanos e a situação são apenas derivados, nunca estado.

### Concorrência

- A serialização por Versão e a atomicidade são da 002.
- O editor converte `POSICAO_OCUPADA`, `ORDEM_INCOMPLETA`, elemento inexistente e Versão
  publicada entre o GET e o POST em mensagens operacionais. Não há bloqueio nem sessão de
  edição.

### Erros

- 404 e 500 seguem as páginas autônomas da 008.
- 409 e o 404 de POST usam `editor/aviso.html`.
- Nenhum `detalhe` de `Violacao` vai para o HTML.

## Project Structure

### Documentation (this feature)

```text
specs/009-editor-pesquisa-versao/
├── spec.md
├── plan.md              # este arquivo
├── research.md          # Fase 0 (R1–R16)
├── data-model.md        # Fase 1 (0 entidades; valores em memória; mapa de rejeições)
├── quickstart.md        # Fase 1 (preparo, validação, roteiros E2E-1 e E2E-2)
├── contracts/
│   ├── rotas.md         # rotas, garantias, ação → operação 002
│   └── diagnostico.md   # secoes_nao_suportadas (006), diagnosticar, auxiliares de ação
├── checklists/requirements.md
└── tasks.md             # /speckit-tasks (não criado aqui)
```

### Source Code (repository root)

```text
config/
├── settings.py                  # ALTERADO: INSTALLED_APPS += "trajetoria.editor";
│                                #   comentário do modo de demonstração cita o editor
└── urls.py                      # ALTERADO: path("editor/", include("trajetoria.editor.urls"))

trajetoria/
├── editor/                      # NOVO — app sem modelos
│   ├── __init__.py
│   ├── apps.py
│   ├── urls.py                  # 25 rotas (contracts/rotas.md)
│   ├── views.py                 # pesquisas, pesquisa_nova, pesquisa, versao_nova,
│   │                            #   versao_a_partir, versao, versao_dados, secao_nova,
│   │                            #   secao, secao_editar, secao_mover, secao_remover,
│   │                            #   pergunta_nova, pergunta, pergunta_editar,
│   │                            #   pergunta_mover, pergunta_trocar_secao,
│   │                            #   pergunta_remover, opcao_nova, opcao_editar,
│   │                            #   opcao_mover, opcao_remover, diagnostico, previa,
│   │                            #   previa_secao
│   ├── formularios.py           # PesquisaForm, DesignacaoForm, DadosVersaoForm,
│   │                            #   SecaoForm, TipoPerguntaForm, PerguntaForm,
│   │                            #   MoverPerguntaForm, OpcaoForm
│   ├── acoes.py                 # proxima_posicao, mover, definir_desvio
│   ├── diagnostico.py           # Problema, Diagnostico, diagnosticar
│   ├── apresentacao.py          # rótulos, TIPOS, descrever_escala, destinos,
│   │                            #   localizador, referencias_a
│   ├── mensagens.py             # textos: o que corrigir, INCOMPATIVEL_COM_A_JORNADA,
│   │                            #   AVISOS, explicações fixas, banner (mapas são locais)
│   └── templates/editor/
│       ├── base.html            # lang, título, pular, banner não produtivo, trilha,
│       │                        #   CSS inline (interface/estilo.css + editor/estilo.css)
│       ├── estilo.css
│       ├── _trilha.html         # partial: "Você está em"
│       ├── _erros.html          # partial: resumo de erros no topo
│       ├── _campo.html          # partial: rótulo + campo + ajuda + erro associado
│       ├── _ordem.html          # partial: Subir/Descer (Seções, Perguntas, Opções)
│       ├── _diagnostico.html    # partial: A, B e situação (estrutura e diagnóstico)
│       ├── formulario.html      # páginas de formulário simples: nova Pesquisa (com
│       │                        #   aviso de nome repetido), nova Versão, nova a partir
│       │                        #   de, dados da Versão, mover Pergunta para outra Seção
│       ├── pesquisas.html
│       ├── pesquisa.html
│       ├── versao.html          # estrutura (rascunho | publicada)
│       ├── secao.html
│       ├── pergunta_tipo.html
│       ├── pergunta.html        # formulários de Seção, Pergunta e Opção usam
│       │                        #   formulario.html (consolidação no implement)
│       ├── confirmar_remocao.html
│       ├── diagnostico.html
│       ├── previa.html
│       ├── previa_secao.html    # inclui interface/perguntas/*.html (008)
│       └── aviso.html           # 409 publicada | conflito | 404 de POST
├── participacao/percurso.py     # ALTERADO (006): secoes_nao_suportadas pública;
│                                #   _exigir_suporte a consome; __all__
└── demonstracao/middleware.py   # ALTERADO: só docstring (cita o editor)

tests/editor/                    # NOVO (sem __init__.py)
├── conftest.py                  # modo ligado; fixtures de Pesquisa/Versão/baseline/cópia
├── construcao_editor.py         # retrato, texto_visivel, auxiliares de POST
├── test_editor_acesso.py
├── test_editor_pesquisas.py
├── test_editor_versoes.py
├── test_editor_publicada.py
├── test_editor_secoes.py
├── test_editor_perguntas.py
├── test_editor_opcoes.py
├── test_editor_escala.py
├── test_editor_navegacao.py
├── test_editor_diagnostico.py
├── test_editor_previa.py
├── test_editor_aceitacao.py
├── test_editor_baseline.py
├── test_editor_acessibilidade.py
└── test_editor_fronteiras.py

tests/participacao/test_jornada_percurso.py   # ACRESCIDO: teste de secoes_nao_suportadas
                                              #   (testes existentes intactos)

README.md                        # ALTERADO: uma linha para o quickstart da 009
```

**Structure Decision**: monólito modular existente (ADR 0001), com um app novo **sem
modelos**, como a 008 fez com `interface` e `demonstracao`.

- **Não mudam**: os apps de domínio `instrumento` (002), `formulario_2024` (003),
  `campanha` (004) e `academico`, e a 008 (`interface`, `demonstracao`), exceto a
  docstring.
- **Muda**: `participacao`, só em `percurso.py` (R4).
- **Nenhum teste existente é alterado.**

## Estratégia de testes

Detalhada em [research R14](research.md#r14--estratégia-de-testes). Pontos de controle
para os critérios de sucesso:

| SC | Como é verificado |
|----|-------------------|
| SC-001 | `test_editor_aceitacao.py::test_cenario_principal`: os 14 passos por HTTP, e ao final a baseline equivalente, 0 Campanhas novas e 0 Versões publicadas pelo editor |
| SC-002 | `test_editor_aceitacao.py::test_cenario_navegacao` e `test_editor_navegacao.py` |
| SC-003 | `test_editor_publicada.py`: varredura das páginas sem controles; POST em cada rota de escrita → 409; retrato idêntico |
| SC-004 | `test_editor_diagnostico.py`: um caso de cada condição da 002 e da 006; A e B separados; as três situações |
| SC-005 | `test_editor_diagnostico.py`: "sem impedimentos" ⇒ `publicar` aceita (só no teste, sobre cópia) e `secoes_nao_suportadas == ()`; ausência de "pronta", "aprovada", "homologada" |
| SC-006 | `test_editor_diagnostico.py` e `test_editor_previa.py`: retrato e contagens de Participação, Campanha e Resposta antes e depois |
| SC-007 | `test_editor_fronteiras.py`: `texto_visivel` sem UUID, nomes de `Motivo` da 002 e da 006, `Traceback`, códigos `FR-`. Motivo não mapeado propaga como erro |
| SC-008 | `test_editor_baseline.py`: `materializar()` devolve `criada=False` sem recusa |
| SC-009 | Por construção: cliente sem JS e nenhum `<script>` (`test_editor_fronteiras.py`) |
| SC-010 | `test_editor_perguntas.py` (4 tipos), `test_editor_navegacao.py` (3 destinos), `test_editor_fronteiras.py` (sem `publicar`, sem `models.py`, `makemigrations --check`) |
| SC-011 | `test_editor_aceitacao.py`: da estrutura da baseline, toda Pergunta está a 2 links (Seção → Pergunta) |
| SC-012 | `test_editor_acessibilidade.py` com `verificar` da 008 em todas as telas, mais o roteiro manual de 320 px |
| SC-013 | `test_editor_acesso.py`: um único teste percorre todas as rotas de `editor.urls` (GET e POST) → 404 com o modo desligado. O gate é central, no middleware; o controle com o modo ligado usa uma rota por família |

Testes de regressão existentes que provam "nenhuma outra feature mudou semanticamente":

- `tests/participacao/test_jornada_percurso.py` e `test_jornada_conclusao.py` (006);
- `tests/interface/*` (008);
- `tests/instrumento/*` (002 e 003).

Todos rodam sem alteração.

## Complexity Tracking

**Vazio.** Não há violação da Constituição a justificar.

Escolhas registradas para revisão, sem violação:

- o app novo `trajetoria/editor`, exigido pelas fronteiras da 007 e da 008 (R1);
- a promoção de `secoes_nao_suportadas` na 006, a alternativa ao segundo validador (R4);
- a transação externa em `definir_desvio`, o mesmo padrão aceito na 008 (R6).

**Não adotado** (pode ser reavaliado com necessidade concreta):

- posição explícita como alternativa a subir e descer (é PODE na spec);
- prévia com todas as Seções numa página;
- verificação de acessibilidade com navegador automatizado.

## Necessidade de voltar à spec ou às features anteriores

- **Spec da 009**: nenhuma mudança necessária. As quatro decisões pré-plan já estão na
  seção *Clarifications*.
- **002**: nenhuma mudança. Todas as ações têm operação pública. `verificar_completude`
  já é pública em `regras.py`.
- **006**: só `secoes_nao_suportadas`, pública e pura, sem mudança observável. Os testes
  existentes passam sem alteração.
- **008**: nenhuma mudança de comportamento. O editor reutiliza `FormularioDaSecao` e os
  templates por tipo, em leitura. Os testes de fronteira da 008 continuam verdes, porque
  `interface` e `demonstracao` não importam nada do editor.
- **001, 003, 004, 005, 007**: nada muda.
