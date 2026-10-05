# Implementation Plan: Minha Trajetória em vídeo

**Branch**: `claude/trajetoria-video-remotion-2faa72` | **Date**: 2026-10-05 | **Spec**:
[spec.md](spec.md)

**Input**: Feature specification from `specs/022-minha-trajetoria-video/spec.md`, com a
[auditoria](../../docs/auditorias/2026-10-05-022-video-trajetoria.md) e as decisões do
solicitante de 2026-10-05 (alternativa A; execução a comparar no plan).

## Summary

Na página "Minha trajetória no Ifes", o egresso pede um **vídeo vertical de ~8 s, sem som**,
que é o card da 021 em movimento: abertura, título, linha do tempo, destaques e fecho
entram em sequência, e o vídeo termina parado no próprio card.

**Abordagem técnica:**

- **Mesma composição do card:**
  - `card.compor()` passa a expor os elementos agrupados por zona, sem mudar o SVG (R3);
  - `narrativa/composicao.py` serializa a `ComposicaoVisual` em JSON (R2).
- **Remotion só anima:** um template (`trajetoria-v1`) num projeto Node isolado em `video/`.
  Ele recebe a composição e devolve um MP4 H.264 (R1, R10, R11).
- **Fronteira única:** `video/renderizar.mjs` do lado Node; `trajetoria/video/renderizador.py`
  do lado Python (R4).
- **Execução assíncrona mínima** (R5 a R7):
  - o `POST` registra o pedido numa tabela técnica (`GeracaoDeVideo`, sem vínculo com
    Pessoa);
  - `manage.py processar_videos` renderiza um por vez;
  - o MP4 fica no banco por 2 h e é apagado depois.
- **Página:**
  - um bloco `#video` no capítulo "Seu card", com quatro estados;
  - funciona sem JavaScript;
  - prévia com suporte a `Range` para o iPhone (R8, R9).

**O spike (research R0) fixou a execução:**

- tempo de 3 a 9 s numa máquina rápida, dependente do hardware → assíncrono;
- MP4 idêntico byte a byte no mesmo ambiente;
- quadro final igual ao card, exceto o antisserrilhado dos glifos.

## Technical Context

**Language/Version**:
- Python 3.13.
- **Node ≥ 22** (novo, só para o renderizador; o spike rodou no 26).
- TypeScript/TSX só no template.

**Primary Dependencies**:
- As existentes: Django 5.2, psycopg 3, `resvg-py`.
- **Novas em `video/`:** `remotion`, `@remotion/bundler`, `@remotion/renderer` e
  `@remotion/cli` em 4.0.533 exata; `react` e `react-dom` 19. Lockfile versionado.
- **Novas de desenvolvimento (Python):** `numpy` e `Pillow`, só para comparar quadros nos
  testes (R14).
- **Runtime:** Chrome Headless Shell (provisionado), FFmpeg e ffprobe embutidos no
  Remotion.

**Storage**:
- PostgreSQL 16.
- Uma tabela técnica nova (`video_geracaodevideo`), num app novo, com migração aditiva
  `0001`.
- MP4 em `bytea` por no máximo 2 h.
- Nenhuma tabela existente muda.

**Testing**:
- pytest e pytest-django em `tests/video/` (novo) e `tests/narrativa/` (regressão do card).
- Testes de mídia com o renderizador real, pulados localmente sem ele e obrigatórios no CI.

**Target Platform**:
- Servidor Linux (CI ubuntu-latest) e macOS arm64 no desenvolvimento.
- Celulares (Safari no iOS, Chrome no Android) para reproduzir e compartilhar.

**Project Type**: aplicação web Django modular (monólito) mais um projeto Node auxiliar de
renderização, sem servidor próprio.

**Performance Goals**:
- Pedido responde na hora.
- Vídeo pronto em até 60 s na demonstração (SC-006): o spike mediu ~4,5 s de ponta a
  ponta.
- Página sem consulta adicional relevante (uma busca por chave única).

**Constraints**:
- Um render por vez por processador.
- Nenhum acesso à rede durante o render.
- Sem JavaScript obrigatório.
- Nada de domínio é escrito.
- Restrito ao modo de demonstração.

**Scale/Scope**:
- Três rotas novas e um bloco novo na página da 021.
- Um app novo com um model e um comando.
- Um módulo novo e uma refatoração interna em `narrativa`.
- Um projeto Node com um template e um script.

## Constitution Check

*GATE: executado antes da Fase 0 e repetido depois da Fase 1.*

| # | Verificação | Princípios | Pré-Fase 0 | Pós-Fase 1 | Evidência / observação |
|---|-------------|------------|------------|------------|------------------------|
| 1 | Longitudinalidade | I | ✅ Conforme | ✅ Conforme | Só leitura do domínio. A única escrita é na tabela técnica (FR-033; data-model §3) |
| 2 | Pessoa versus Conclusão Acadêmica | I, XI | ✅ Conforme | ✅ Conforme | O vídeo replica o card, com curso e unidade por Conclusão. A tabela técnica não tem FK |
| 3 | Múltiplas formações sem fusão | I, XI | ✅ Conforme | ✅ Conforme | Mesmas formações e o mesmo "e mais N" do card (FR-012) |
| 4 | Múltiplas participações sem sobrescrita | I, VIII | ✅ Conforme | ✅ Conforme | Não toca Participação |
| 5 | Definição institucional de egresso | II | ✅ Conforme | ✅ Conforme | Elegibilidade herdada da 021 (FR-001) |
| 6 | Preservação histórica | VIII, XXVII | ✅ Conforme | ✅ Conforme | Migração aditiva num app novo. O SVG do card fica igual byte a byte (R3, teste de regressão) |
| 7 | Pesquisa / Versão / Campanha / Participação | VII, VIII | N/A | N/A | O vídeo não toca o instrumento |
| 8 | Proveniência | IV | ✅ Conforme | ✅ Conforme | A apuração dos destaques aparece como no card (zona `apuracao`) |
| 9 | Institucional × derivado × declarado | III | ✅ Conforme | ✅ Conforme | Só o conteúdo do card. Nenhum dado declarado (FR-020; teste de textos = card) |
| 10 | Desacoplamento de integrações | V, XV, XXV | ✅ Conforme | ✅ Conforme | Renderizador atrás de uma fronteira (contracts/renderizador.md). Renderizador falso nos testes de estado e rotas. Fallback C documentado (R17) |
| 11 | Fronteira do NIAE | VI | ✅ Conforme | ✅ Conforme | As cinco perguntas estão na spec. Portal pendente (DP-2108) |
| 12 | Governança institucional | IX, X | ✅ Conforme | ✅ Conforme | Licença e retenção ficam como decisões pendentes, não como regra |
| 13 | Escopo por unidade | XII | N/A | N/A | Sem tela de operador |
| 14 | Privacidade, minimização, logs | XVI, XVII | ⚠ Atenção | ✅ Conforme | Mesmo subconjunto do card; nome por escolha; sem FK; composição apagada após processar; MP4 por 2 h; chave nunca exposta; entrega recalculada pela sessão; logs sem conteúdo nem saída do Node (R6, R8, R18) |
| 15 | Autorização | X, XII | ✅ Conforme | ✅ Conforme | Sessão e elegibilidade da 021 em todas as rotas; CSRF no POST |
| 16 | Acessibilidade | XX | ✅ Conforme | ✅ Conforme | Sem autoplay; controles nativos; descrição textual do card; `aria-live`; sem `meta refresh` (R9) |
| 17 | Responsividade e jornada móvel | XIV, XXI | ✅ Conforme | ✅ Conforme | 9:16; `playsinline`; `Range` para o iOS; compartilhamento nativo progressivo |
| 18 | Testes proporcionais ao risco | XXV, XXVI | ✅ Conforme | ✅ Conforme | Matriz da spec em R14: composição pura, estado, rotas, mídia real e quadros-chave com tolerância |
| 19 | Risco de over engineering | XXII, XXIII, XXIV | ⚠ Atenção | ✅ Conforme, com justificativa | Runtime novo (Node e Chromium), tabela técnica e dependências de desenvolvimento. Ver Complexity Tracking. Um template, sem broker, sem fila em arquivos, sem entidade de vídeo, sem framework de mídia |
| 20 | Exportabilidade | XVIII | N/A | N/A | Nada da 022 entra em snapshot ou exportação (teste herdado da 021 estendido) |
| 21 | Decisões pendentes explicitadas | XXIX | ✅ Conforme | ✅ Conforme | DP-2201 (licença, codec, navegador) e DP-2202 (retenção), mais as herdadas da 021 |

**Resultado do gate**: APROVADO. A linha 19 depende da Complexity Tracking aceita em
revisão.

**Conflitos identificados:**

- **FR-018 (determinismo) × arquivo binário:** a spec exige mesmo conteúdo visual. O spike
  mostrou bytes idênticos no mesmo ambiente.
  - **Encaminhamento:** o teste exige bytes iguais no mesmo ambiente e tolerância visual
    entre ambientes (R13). Sem conflito com a Constituição.
- **Linha de apuração antes dos destaques**, achado do spike: zona `apuracao` separada do
  rodapé (R10). A spec não muda: o rodapé de demonstração continua visível o tempo todo.

## Decisões Pendentes

| ID | DECISÃO PENDENTE | Instância competente | Solução provisória (hipótese) | Como reverter |
|----|------------------|----------------------|-------------------------------|---------------|
| DP-2201 | Aceite da licença e dos termos do Remotion, de licenças de codec H.264 e da operação do Chromium no servidor | DTI, com a assessoria jurídica | Só na demonstração; versão 4 fixada | Trocar `video/` e `renderizador.py` pela alternativa C (R17) sem tocar composição, estado nem rotas |
| DP-2202 | Retenção de arquivo temporário com dado pessoal em ambiente real | Encarregado de dados, com a DTI | 2 h (`TRAJETORIA_VIDEO_RETENCAO`, máximo 24 h) | Configuração |
| DP-2101 | Compartilhamento de representação com o nome do Ifes (herdada) | CPAEG/Proex, ACS, encarregado | Download e menu do dispositivo, só na demonstração | Remover o bloco `#video` |
| DP-2102 | Marca do Ifes em peça compartilhável (herdada) | ACS | Mesma assinatura do card | Herda a decisão do card |
| DP-2103 | Nome civil × nome social (herdada) | Registro acadêmico | Mesma escolha do card | Herda |
| DP-2105, DP-2106, DP-2110 | Agregados, imagens, fecho e hashtag (herdadas) | Conforme a 021 | Mesmos do card | Herda |

## Project Structure

### Documentation (this feature)

```text
specs/022-minha-trajetoria-video/
├── spec.md
├── plan.md                    # este arquivo
├── research.md                # Fase 0, com o spike (R0)
├── data-model.md              # Fase 1
├── quickstart.md              # Fase 1
├── contracts/
│   ├── composicao-visual.md   # entrada do template (JSON v1)
│   ├── renderizador.md        # fronteira Python ↔ Node
│   ├── template-video.md      # tempo e movimento de trajetoria-v1
│   └── rotas.md               # rotas e bloco #video
├── checklists/requirements.md
├── evidencias/                # spike: quadros-chave, quadro final × card, mapa de diferenças
└── tasks.md                   # /speckit-tasks (ainda não criado)
```

### Source Code (repository root)

```text
video/                                   # NOVO: projeto Node isolado (fora do pacote Python)
├── package.json                         # engines node>=22; versões exatas
├── package-lock.json
├── tsconfig.json
├── renderizar.mjs                       # único ponto de entrada (contracts/renderizador.md)
├── src/
│   ├── index.ts                         # registerRoot
│   ├── Root.tsx                         # Composition "trajetoria-v1", calculateMetadata
│   └── TrajetoriaV1.tsx                 # zonas no tempo (contracts/template-video.md)
└── README.md                            # instalação, provisionamento e licença (DP-2201)

trajetoria/narrativa/
├── card.py                              # ALTERADO: Zona; Composicao.zonas; SVG inalterado
├── composicao.py                        # NOVO: composicao_visual(), serialização canônica, chave
└── templates/narrativa/
    └── minha_trajetoria.html            # ALTERADO: inclui o bloco #video no capítulo "Seu card"

trajetoria/narrativa/views.py            # ALTERADO: contexto do bloco #video (via trajetoria.video)

trajetoria/video/                        # NOVO app
├── __init__.py
├── apps.py
├── models.py                            # GeracaoDeVideo (técnico, sem FK)
├── migrations/0001_initial.py
├── renderizador.py                      # único módulo que chama o Node
├── operacoes.py                         # solicitar, estado_para, processar_proximo, limpar
├── mensagens.py                         # textos do bloco #video
├── views.py                             # POST solicitar; GET video.mp4 (Range); GET estado
├── urls.py
├── templates/video/bloco.html           # incluído pela página da 021
└── management/commands/processar_videos.py

config/settings.py                       # ALTERADO: app e TRAJETORIA_VIDEO_*
config/urls.py                           # ALTERADO: inclui trajetoria.video.urls
pyproject.toml                           # ALTERADO: numpy e Pillow em dev
.gitignore                               # ALTERADO: video/node_modules/
.github/workflows/ci.yml                 # ALTERADO: setup-node, npm ci, browser ensure
docs/adr/0007-renderizacao-do-video.md   # NOVO (proposto nesta fase)

tests/video/                             # NOVO
├── conftest.py                          # renderizador falso; marcador de "precisa do renderizador"
├── construcao.py                        # casos da matriz (reusa tests/narrativa/construcao.py)
├── test_composicao.py                   # zonas, textos = card, vedados, escape, chave
├── test_estado.py                       # transições, duplicata, retenção, travado, sem processador
├── test_processador.py                  # processar_videos --uma-vez com renderizador falso
├── test_rotas.py                        # sessão, CSRF, Range, 404, estado, sem JS, isolamento
├── test_fronteira.py                    # só renderizador.py chama node; logs sem conteúdo
├── test_midia.py                        # MP4 real: ffprobe, duração, bytes iguais
└── test_quadros.py                      # quadros-chave × card e referências, rodapé, estabilidade
tests/narrativa/test_card_zonas.py       # NOVO: regressão byte a byte do SVG e invariantes das zonas
```

**Structure Decision**:

- **App `video` separado de `narrativa`:**
  - mantém a narrativa sem models, como a 021 definiu;
  - isola o derivado opcional, que pode ser removido por inteiro sem tocar a devolutiva.
- **Projeto Node na raiz:** fica fora do wheel Python e torna a fronteira visível.
- **Dependência num só sentido:** `video` depende de `narrativa` (composição);
  `narrativa.views` consulta `video.operacoes` só para montar o bloco.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Runtime novo: Node, Chromium (Chrome Headless Shell) e ~600 MB de dependências | Decisão do solicitante (E1): o vídeo é a fundação da camada de vídeo, e o Remotion resolve animação, tempo e codificação sem motor próprio | **C (resvg + FFmpeg em Python):** começaria um motor de animação próprio, que cresce com o segundo template. Fica como fallback (R17). **Serviço externo:** envio de dado pessoal |
| Tabela técnica `GeracaoDeVideo` e processo `processar_videos` | O render leva de 3 a 30 s conforme o hardware (R0, R5). Não cabe numa requisição de tempo previsível, e o FR-032 exige limitar a concorrência | **Síncrono:** imprevisível e sem limite natural. **Pasta de pedidos:** fila ad hoc em arquivos, rejeitada pelo solicitante. **Celery/broker:** infraestrutura sem caso |
| MP4 em `bytea` | Web e processador compartilham o resultado sem diretório de mídia, com limpeza por `DELETE` | **Disco:** exige diretório compartilhado entre processos e varredura de órfãos |
| `numpy` e `Pillow` (só desenvolvimento) | Comparar quadros com tolerância (SSIM, regiões) sem inspeção humana (spec, matriz) | **Pixel-perfect com `hashlib`:** frágil entre ambientes. **SSIM em Python puro:** lento demais para ~40 quadros |
| Suporte manual a `Range` (~30 linhas) | O Safari no iOS não reproduz `<video>` sem `206` | **`FileResponse`:** o Django não trata `Range` |
