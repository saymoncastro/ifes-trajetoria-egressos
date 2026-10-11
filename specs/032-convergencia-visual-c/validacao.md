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
029. *(2026-10-11: executado; ver "Roteiro manual com teclado e árvore de acessibilidade"
abaixo. O leitor de tela, P4, continua pendente.)*

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

## Roteiro manual com teclado e árvore de acessibilidade (2026-10-11)

Passo 2 da sequência do roadmap (revisão 13, §13.3), antes do Checkpoint 1.

- **Navegador:** navegador embutido do aplicativo Claude 2.26454.2, Chromium 152.0.7977.130,
  em macOS.
- **Código servido:** `63b9447`, a `main` com a 032. O commit `371ec65` acima dele só muda
  documentos.
- **Ambiente:** banco próprio, recém-preparado com `preparar_demonstracao`, servidor em
  `127.0.0.1:8025` (a 8000 estava ocupada por outro processo).
- **Larguras:** 375×812 (persona Ana) e 1280×800 (persona Bruno, a única com a seção de
  encontros).
- **Teclas reais:** Tab, Shift+Tab, Enter, Espaço e setas. A cada passo, o foco foi
  conferido pelo elemento ativo e pelo estilo calculado (contorno de 3 px e halo amarelo da
  015).
- **Escritas na demonstração:** uma contribuição fictícia da Ana, com
  `verificacao-teclado@example.invalid`, enviada e depois retirada. Nos dois erros de e-mail
  testados, nada foi gravado.

**Não executado:** leitor de tela (P4). O
[roteiro para VoiceOver ou NVDA](evidencias/roteiro-leitor-de-tela.md) está pronto, sem
resultados. A árvore de acessibilidade abaixo é evidência técnica, não substitui o teste com
leitor de tela.

### Resultados por tela

| Tela | Ordem de foco (resumo) | Resultado |
|---|---|---|
| Página pública, 1280×800 | Pular → Encontros → Oportunidades → Contribuir → Entrar → Conhecer o Portal → Ver como funciona → Entrar para oferecer → Conhecer o Portal (fim) | Ordem igual à visual; foco visível em todos. "Pular" leva o foco a `main#conteudo`. Enter em "Encontros" leva a seção ao topo, e o Tab seguinte vai ao próximo elemento focável depois dela ("Entrar para oferecer"). 0 `script`, 0 formulário, 1 h1 |
| Página pública, 375×812 | Pular → Entrar → Conhecer o Portal → Ver como funciona → Entrar para oferecer → Conhecer o Portal | O menu de âncoras some abaixo de 480 px e não recebe foco. Shift+Tab volta corretamente. Sem rolagem horizontal |
| `/entrar/`, 375×812 | Pular → CPF → Data de nascimento → Continuar → "Dados fictícios para demonstração" | O painel recolhido (`details`) abre com Enter; cada botão tem nome próprio ("Usar estes dados de Ana Exemplo"). Entrada pelo teclado |
| Início, Ana, 375×812 | Pular → Sair → Início (atual) → Minha trajetória → Oportunidades → Participação → Baixar meu card → Ver minha trajetória no Ifes → "Hoje" → "Adiante" → oportunidade em destaque → Ver as 2 oportunidades → Quero contribuir → Informar e-mail → Responder | Ordem igual à visual; `aria-current="page"` em Início. O link do "Hoje" leva a `#oportunidades`, e o Tab seguinte vai ao destaque. Alvos de 44 px ou mais, exceto "Pular" (40 px, da 015) |
| Início, Bruno, 1280×800 | Pular → Sair → navegação → ações do card (coluna direita) → "Hoje" → "Adiante" → encontro → destaque → Ver as 2 oportunidades → contribuição → e-mail → pesquisa | Segue a leitura: de cima para baixo e, na participação em três colunas, da esquerda para a direita. O convite da pesquisa é o último (ADR 0009, decisão 8). Foco visível no link do encontro sobre a faixa escura |
| Participação, 375×812 | Pular → Sair → navegação (Participação atual) → Quero contribuir → Informar e-mail → Responder | Um h1; h2 para contribuição, canal e pesquisa |
| Contribuir, 375×812 | Navegação → forma (rádios) → formação (rádio marcado) → Mensagem → Continuar → Voltar ao Início | `fieldset` e `legend` nos dois grupos; as setas mudam a forma; a dica está ligada à mensagem. Sem forma: resumo com `role="alert"`, foco no primeiro rádio, `aria-describedby` no grupo. Opções de 343×60 px, com rótulo de 52 px de altura |
| Confira e envie, 375×812 | Navegação → E-mail para a resposta → Enviar contribuição → Voltar e alterar | E-mail inválido: resumo com `role="alert"`, foco no campo, `aria-invalid` e erro em `aria-describedby`, valor preservado. Envio pelo teclado |
| Sua contribuição | Navegação → Suas contribuições → Retirar esta contribuição → Voltar ao Início | Aviso "Contribuição enviada." em `role="status"` (ver A-02) |
| Retirar e Suas contribuições | Navegação → Retirar → Cancelar | Retirada pelo teclado; "Ver detalhes" tem nome acessível com a forma, a formação e a data |
| Minha trajetória, 375×812 | Navegação (Minha trajetória atual) → Incluir meu nome no card → Atualizar prévia → Baixar imagem (PNG) → Voltar ao Início | Espaço marca a caixa e Enter atualiza a prévia. Texto alternativo do card completo. A caixa nativa tem 13×13 px; o rótulo clicável, 181×44 px. O bloco de vídeo não aparece, porque o renderizador não está instalado: **vídeo não testado** |
| Oportunidades, 375×812 | Navegação (Oportunidades atual) → as duas oportunidades | Nome do link com "— site externo: oportunidades.example". h2 "Pela sua formação" e "Para todos os egressos" |
| Meu e-mail, 375×812 | Navegação (Participação atual) → E-mail → Salvar → Agora não → Ver minha trajetória no Ifes → Voltar ao Início | Ordem coerente. Erro: ver A-01 |
| `/formacoes/`, 1280×800 | Navegação (Participação atual) → Ver minha trajetória no Ifes → os dois "Iniciar a pesquisa desta formação" | Ver A-03 e A-04 |

Capturas do foco: [`teclado-foco-inicio-hoje-375.jpg`](evidencias/capturas/teclado-foco-inicio-hoje-375.jpg)
(link do "Hoje", Ana) e [`teclado-foco-encontro-1280.png`](evidencias/capturas/teclado-foco-encontro-1280.png)
(link do encontro, Bruno).

**Árvore de acessibilidade (Início do Bruno, 1280×800):** `banner`, `navigation` "Portal do
Egresso" com quatro itens em lista, `main`, `contentinfo`. Os títulos seguem h1 → h2. A
linha da trajetória é uma lista nomeada ("Sua trajetória com o Ifes"), com "Hoje" e "Adiante"
como texto, não só cor. A região "Participação" tem nome. O card tem texto alternativo
completo, e a decoração não aparece na árvore.

### Achados

Nenhum achado impede uma tarefa do Checkpoint 1 ou do Checkpoint 2. Nenhum foi corrigido:
mudanças de código dependem de autorização.

| # | Tela | Achado | Origem | Efeito nos checkpoints | Correção possível |
|---|---|---|---|---|---|
| A-01 | `/meu-email/` | Depois do erro do servidor, o foco fica no início da página, e não no campo nem no erro. O valor digitado não volta ao campo. O erro está ligado por `aria-describedby` e `aria-invalid` | 020 (anterior à C) | Nenhum: as tarefas só pedem encontrar a tela, sem preencher | `autofocus` no campo com erro, como na contribuição (026) |
| A-02 | Sua contribuição; Suas contribuições | Os avisos "Contribuição enviada." e "Contribuição retirada." usam `role="status"`, mas já vêm no carregamento da página, e o foco não vai até eles. Leitores de tela costumam não anunciar regiões vivas presentes no carregamento | 026 | A confirmar no teste com leitor de tela (P4). R5 e R7 do Checkpoint 2 dependem de a pessoa perceber o envio e a retirada | Aviso focável (`tabindex="-1"` e `autofocus`), como em `/acesso/` |
| A-03 | `/formacoes/` | O link "Ver minha trajetória no Ifes" tem 194×19 px, abaixo dos 44 px da 014 | Instrumento, anterior à C | Nenhum: não está no caminho das tarefas | Alvo mínimo no link isolado |
| A-04 | `/formacoes/` | Com duas formações, os dois botões se chamam "Iniciar a pesquisa desta formação". O contexto está no mesmo item da lista, mas quem navega por botões ouve nomes iguais | Instrumento (007/008), anterior à C | A confirmar com leitor de tela; SC-012 passa por essa tela | Nome acessível com o curso, sem mudar o texto visível |

**Observação de conteúdo, não de acessibilidade.** O "Hoje" conta também as oportunidades
abertas a todos os egressos e os encontros. Na Ana e no Bruno, ele diz "2 oportunidades para
a sua formação", e uma delas é "Aberta a todos os egressos do Ifes". Pode pesar no CP2-C1
("por que aparece") e fica para a observação do Checkpoint 2.

### Não coberto

- leitor de tela real (P4);
- vídeo da Minha trajetória;
- compartilhamento por JavaScript da Minha trajetória;
- toque e teclado virtual num celular real;
- zoom do sistema a 200% com teclado (a ausência de rolagem horizontal a 200% já está medida
  acima);
- personas Maria e Diego, só no oráculo e nas medidas.
