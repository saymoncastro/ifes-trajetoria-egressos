# Validação — Feature 032, convergência visual C

## PR 1 — fundação visual e página pública (2026-10-11)

### Verificações

- `ruff check .`, `manage.py check` e `makemigrations --check --dry-run` passam.
- Suíte completa: 3353 testes aprovados, 40 ignorados (vídeo sem renderizador) e 2
  desmarcados.
- Testes novos ou revisados:
  - `tests/portal/test_fontes.py` (10): cada fonte servida com tipo, cache longo e conteúdo
    igual ao arquivo; nomes fora da lista dão 404; licenças junto dos arquivos; nenhuma
    fonte externa nem `<link>`; o instrumento e `/acesso/` sem `@font-face`; sem o Portal, a
    rota não existe.
  - `tests/portal/test_pagina_publica.py` (8), revisado conforme 032 FR-005 e FR-006:
    - ordem da página e das cinco etapas da linha;
    - chamadas, âncoras e menu da página, sem link além de `/entrar/` e das âncoras;
    - exemplos coerentes com o card;
    - finalidade do e-mail e da contribuição;
    - vocabulário vedado;
    - nenhuma consulta;
    - decoração fora da acessibilidade;
    - textos retirados dos mockups.

### Medidas da página servida

Geradas por [`evidencias/medir.py`](evidencias/medir.py), com o arnês dos protótipos.
Capturas em [`evidencias/capturas/`](evidencias/capturas/) e medidas em
[`evidencias/medidas.json`](evidencias/medidas.json).

| Critério | Resultado |
|---|---|
| Sem rolagem horizontal, 320 a 1440 px, fonte a 100% e 200% | nenhuma |
| 375×812: título, frase e "Conhecer o Portal" sem rolar | a chamada termina em 590 px |
| 1280×720: título, frase, chamada e início da linha (descontada a faixa de 50 px) | a chamada termina em 610 px e a linha começa em 692 px |
| Um h1; alvos ≥ 44 px | sim; nenhum alvo abaixo |
| Contraste dos pares novos | de 4,8:1 a 11,3:1 no texto; números grandes em `#2f9e41` (3,45:1) só em 40 px |
| Peso das fontes | 61 KB (três woff2), cache de um ano |

O Início atual, que só muda de fonte neste PR, também foi medido: sem rolagem horizontal e
sem alvo abaixo de 44 px.

### Fidelidade aos mockups C

Seguem a composição C:
- abertura com o título grande e a linha Ingresso → Adiante, com o "Hoje" em vermelho;
- três passos;
- faixa escura "Ninguém se forma sozinho" com as memórias;
- a ponte "Você concluiu → Aparece para você";
- a faixa verde-clara da contribuição com as formas numeradas;
- o card com a chamada final e o fio.

Ajustes, todos da tabela da spec:
- **Textos e marca:** sem "continua", "Comunidade", "conexão", "turma" e o padrão da marca;
  o card é o real da 021; "Conhecer o Portal" no lugar de "Entrar no meu espaço".
- **Encontro de exemplo:** entrou na faixa escura, para manter os dois exemplos da 029 FR-009.
- **Menu no celular:** abaixo de 480 px, mostra só "Entrar".

### Pendências

- DP-3201 (Bricolage) e DP-3202 (padrões da marca) com a ACS; D2 e DP-801 (textos).
- PR 2: Início, "Participação" e navegação.
- Checkpoint 1: NÃO APLICADO.

## PR 2 — área autenticada, Participação e navegação (2026-10-11)

### O que mudou

- **Início na composição C** (FR-008):
  - abertura com o título, a frase de proveniência, os números do ano (quando há), o card e
    as ações "Baixar meu card" e "Ver minha trajetória no Ifes";
  - linha das próprias formações, com "Hoje" e "Adiante" no fim;
  - "Ninguém se forma sozinho", só com um encontro pertinente (categoria Eventos da 025);
  - "Para a sua formação, agora": a formação que justifica, seta e o destaque da 025;
  - participação: contribuição com os marcos, canal de e-mail e o convite por último.
- **"Hoje" e "Adiante"** (FR-009):
  - "Hoje": "N oportunidades para a sua formação", com link à seção, ou "Nenhuma oportunidade
    divulgada agora";
  - "Adiante": "N contribuições enviadas", contando só as ativas, ou o convite para contribuir.
    Nunca "em andamento".
- **Navegação** (FR-011): Início, Minha trajetória, Oportunidades e Participação.
  - `/participacao/` reúne os blocos de participação.
  - "Participação" é o item atual em `/participacao/`, `/formacoes/`, `/meu-email/`, nas
    telas da contribuição e na confirmação.
  - O bloco da pesquisa sempre leva a `/formacoes/`; nenhuma rota mudou.
- **Demais telas** (T007): Minha trajetória, Oportunidades, contribuição e Meu e-mail ganham
  o fundo creme e os títulos na fonte e no verde profundo. Os itens de Oportunidades viram
  cartões. As folhas da 025 não mudam, porque a curadoria também as usa.

### Verificações

- `ruff check .`, `manage.py check` e `makemigrations --check --dry-run` passam.
- Suíte completa: 3365 testes aprovados, 40 ignorados (vídeo sem renderizador) e 2
  desmarcados.
- **Novo:** `tests/portal/test_inicio_convergencia.py` (12) cobre:
  - "Hoje" sem e com oportunidades;
  - "Adiante" sem contribuição, com uma e com a retirada;
  - o encontro em seção própria, sem repetir no destaque;
  - só o encontro, sem seção de oportunidades;
  - a ponte (por que ou para quem);
  - a ordem da participação, com o convite por último, e os textos retirados dos mockups;
  - a página Participação, inclusive sem Conclusão, sem sessão, com declarante e com o Portal
    desligado;
  - o download do card.
- **Revisados, com nota** (requisitos revisados da spec):
  - `test_inicio.py`: ordem, vocabulário com "Hoje" e encontro, convite sem pendência com o
    link às formações, e-mail fora das ações;
  - `test_oportunidades_inicio.py`: ordem;
  - `test_oportunidades_oraculo.py`: o encontro da Pessoa 0002 e da 0010 vai para a seção de
    encontros, e o destaque passa a ser o item seguinte;
  - `test_camada_visual.py`: a linha é uma `<ol>`;
  - `test_contribuicao_egresso.py` e `test_navegacao.py`: "Participação";
  - `tests/contato/test_meu_email.py`: o link da pesquisa vem de "Participação".

### Medidas e capturas reais

Personas da demonstração:
- **Ana:** uma formação, sem oportunidade da formação.
- **Bruno:** duas formações em Vitória, com o encontro e uma contribuição.
- **Diego:** três formações, oportunidades e uma contribuição.

| Tela | Sem rolagem horizontal, 320 a 1440 px, fonte a 100% e 200% | Um h1 | Alvos ≥ 44 px | Primeira tela |
|---|---|---|---|---|
| Início (Ana, Bruno, Diego) | sim | sim | sim | 375×812: título e primeiro fato até 488 px; 1280×720: título, fato e card |
| Participação | sim | sim | sim | — |
| Minha trajetória, Oportunidades, Contribuir, Meu e-mail | sim | sim | sim | — |

### Auditoria contra os mockups C

**Fiel:**
- abertura com o título grande e o card ao lado, inclinado;
- linha horizontal com o "Hoje" em vermelho e o "Adiante" tracejado;
- faixa escura do encontro, com o cartão creme;
- a ponte da formação à oportunidade, com o aviso de que abrir a página oficial não faz
  inscrição;
- faixa verde-clara com a contribuição e seus marcos, o canal e a pesquisa;
- botões verde-profundo e contornados.

**Divergências deliberadas:**
- **Textos:** os da tabela da spec (sem saudação, sem situação do e-mail, sem
  "Compartilhar", sem "em andamento").
- **Encontro:** só aparece quando há um pertinente (Bruno sim; Ana e Diego, não).
- **Números do ano:** continuam no Início, porque são da 028.
- **Ordem da participação:** contribuição, e-mail e pesquisa, para manter o convite por
  último (ADR 0009, decisão 8). O mockup põe a pesquisa no meio.

**Fora do alcance desta feature:** o cabeçalho é o do núcleo (assinatura e nome do produto),
com a navegação abaixo, e não na mesma linha do mockup. Mudar o cabeçalho tocaria o shell
compartilhado com o instrumento (ADR 0009, decisão 1).

**Acessibilidade:**
- sem JavaScript;
- ordem de leitura igual à visual;
- marcadores da linha com rótulo, não só cor;
- decoração com `aria-hidden`;
- contraste AA medido nos pares novos.

**Pendente:** o roteiro manual com teclado num navegador real, como o que foi feito para a
029.

### Pendências

- DP-3201 e DP-3202 (ACS); D2 e DP-801 (textos).
- Checkpoint 1: NÃO APLICADO. Recomenda-se aplicá-lo sobre esta versão.

## Code review dos PRs #60 e #61 (2026-10-11)

| Achado | Correção |
|---|---|
| "Hoje" apontava para `#oportunidades` quando só havia o encontro e a seção não existia | Sem a seção, o link vai a `/oportunidades/` (teste) |
| A escala nova do h1 também valia em `/entrar/`, que não tinha sido medido | Medido: sem rolagem horizontal; a 375×812, título, campos e "Continuar" na primeira tela. Sem mudança; a tela entrou nas medidas |
| Pessoa sem Conclusão ficava sem caminho para `/formacoes/` | `/participacao/` mostra "Ver suas formações no Ifes" quando não há convite (teste) |
| Três consultas às manifestações por Início | Uma só (`resumo_da_pessoa`), verificada em teste |
| Fonte lida do disco a cada pedido | Lida uma vez por processo |
| O redirecionamento "sem Pessoa" estava copiado em quatro views | `portal/destinos.sem_pessoa` |
| O nome do download do card era refeito no Portal | `narrativa.views.nome_do_card`, usado pela 021 e pelo Início |
| Constantes e regra de CSS sem uso | Removidas |
| Parâmetro com o mesmo nome de uma função importada | Renomeado |

Depois das correções:
- **Suíte completa:** 3366 testes aprovados, 40 ignorados e 2 desmarcados.
- **Telas medidas novamente:** pública, `/entrar/`, os três Inícios, Participação e as quatro telas internas. Todas sem rolagem horizontal, com um h1 e sem alvo abaixo de 44 px.
