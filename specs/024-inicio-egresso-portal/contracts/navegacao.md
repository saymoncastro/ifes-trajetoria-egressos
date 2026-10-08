# Contrato: shell e navegação do Portal (024)

Este contrato revisa o [shell da 015](../../015-identidade-visual-jornada/contracts/shell.md)
só no que está escrito abaixo. Com o slot vazio, o HTML do shell da 015 fica idêntico.

## Pontos de extensão em `interface/base.html` (núcleo, neutros)

| Bloco | Padrão | Quem sobrescreve |
|---|---|---|
| `produto` | "Trajetória Ifes" + "Acompanhamento de egressos" (015) | Templates do Portal: "Portal do Egresso" (FR-024). O subtítulo provisório na demonstração é "Instituto Federal do Espírito Santo" |
| `navegacao` | Vazio | Templates que optam pela navegação, com `{% include "interface/_navegacao.html" %}` |
| `acao_sair` *(variável; 2026-10-08)* | `/acesso/sair/` | Provedor do Portal, nas telas com navegação: `/sair/` (FR-034) |
| `produto` no rodapé *(2026-10-08)* | "Trajetória Ifes — demonstração local…" | O mesmo `produto` do cabeçalho (FR-024) |
| `retorno` *(variável; 2026-10-08)* | Ausente: Minha trajetória mostra "Voltar às suas formações", e Meu e-mail mostra "Ver suas formações no Ifes" | Provedor do Portal, nas telas com navegação: "Voltar ao Início" → `/inicio/` (FR-035) |

O include `interface/_navegacao.html` renderiza a variável `navegacao` **só se ela existir**.
Nem o include nem o `base.html` mencionam "portal".

## Telas que optam pela navegação (FR-022)

| Tela | Template | Navegação |
|---|---|---|
| Início | `portal/inicio.html` | Sim |
| Escolha de formações | `interface/formacoes.html` | Sim |
| Confirmação de Participação | `interface/concluida.html` | Sim |
| Minha trajetória | `narrativa/minha_trajetoria.html` | Sim |
| Meu e-mail | `contato/meu_email.html` | Sim |
| Seções, concluir, avisos | `interface/secao.html`, `conclusao.html`, `aviso.html` | **Não** |
| Identificação | `acesso/entrada.html` (em `/acesso/` e `/entrar/`) | **Não** |
| Declaração (019) | `declaracao/egresso.html` | **Não** |

## Variável `navegacao` (provedor do Portal)

O provedor é `trajetoria.portal.contexto.navegacao`, registrado em `TEMPLATES[...]
["context_processors"]`. Ele devolve:

- **`{}`**:
  - com o Portal desabilitado;
  - sem Pessoa na sessão (inclusive para o declarante);
  - fora do modo de demonstração.
- **Caso contrário**, `{"navegacao": [item, …]}`, nesta ordem:

| Item | Rótulo (provisório) | Endereço | Condição |
|---|---|---|---|
| 1 | Início | `/inicio/` | Sempre |
| 2 | Minha trajetória | `/minha-trajetoria/` | `elegivel(pessoa)` (FR-009) |
| 3 | Pesquisa | `/formacoes/` | Sempre |
| 4 | Meu e-mail | `/meu-email/` | Sempre |

Cada item tem `rotulo`, `endereco` e `atual`. `atual` é verdadeiro quando o caminho da
requisição é o do item. Em `/participacoes/<id>/concluida/`, o item "Pesquisa" é o atual.

**Revisão de 2026-10-08 (avaliação por IA, A1 a A4).** Nas telas da tabela acima que têm
navegação, o provedor também devolve:
- `produto` e `produto_subtitulo` ("Portal do Egresso", FR-024);
- `acao_sair` (`/sair/`, FR-034);
- `retorno` ("Voltar ao Início", FR-035).

A decisão é por uma lista fechada de caminhos, a mesma do FR-022. Ela vale só para o
cabeçalho e para destinos fixos, nunca para endereços vindos do cliente. As demais telas
recebem só a navegação, que não exibem.

## Marcação e medidas

- **Marcação.**
  - `<nav aria-label="Portal do Egresso">` com uma lista `<ul>` de links.
  - O item atual tem `aria-current="page"` e não é sublinhado como link comum.
  - O contraste segue os tokens da 015.
- **Posição.** Logo depois do `<header>` e antes de `<main>`. O link "Pular para o
  conteúdo" continua o primeiro foco.
- **Alvos de toque.** Pelo menos 44×44 px CSS (014). Foco visível da 015 (contorno de 3 px
  com halo).
- **Largura.** Sem rolagem horizontal de 320 a 1280 px, com fonte de 100% a 200%. A 320 px,
  a lista pode quebrar em duas linhas.
- **Sem JavaScript.** Sem menu escondido.
