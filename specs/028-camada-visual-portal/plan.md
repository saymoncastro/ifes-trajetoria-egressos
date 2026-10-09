# Implementation Plan: Camada visual do Portal — direção B

**Branch**: `codex/028-camada-visual-portal` | **Date**: 2026-10-09
**Spec**: [spec.md](spec.md)

## Summary

Entregar em três etapas revisáveis: base e legenda; página pública e Início; harmonização
e validação. A direção B foi escolhida pelo solicitante. A base é `main` em `62fed3d`,
mais os protótipos em `9e4f7d5`. Nenhuma mudança de banco ou domínio.

## Technical Context

Python 3.13/uv, Django 5.2, PostgreSQL 16. HTML/CSS renderizados no servidor, sem novas
dependências. pytest/pytest-django e ruff existentes. Navegador local para a matriz
visual; capturas e medidas são evidência, não uma nova dependência da aplicação.

## Constitution Check

Verificações antes do desenho e após definir a abordagem abaixo. “OK” verifica o desenho;
os testes e medidas da implementação são registrados separadamente em `validacao.md`.

| Verificação | Pré-desenho | Pós-desenho | Evidência / aplicabilidade |
|---|---|---|---|
| Longitudinalidade | OK | OK | Nenhuma escrita ou âncora nova |
| Pessoa × Conclusão | OK | OK | Montagem existente por Pessoa, fatos por Conclusão |
| Múltiplas formações | OK | OK | Todas exibidas, sem fusão; grade quebra quando necessário |
| Múltiplas participações | OK | OK | Resolução existente; nenhuma Participação criada |
| Definição de egresso | OK | OK | Elegibilidade existente |
| Histórico e migrações | OK | OK | Nenhuma migração; revisão de specs aditiva |
| Pesquisa/Versão/Campanha/Participação | OK | OK | Instrumento e coleta intactos |
| Proveniência | OK | OK | Frases atuais e legenda por imagem efetiva |
| Institucional/derivado/declarado | OK | OK | Contrato da narrativa; Início não lê Resposta |
| Integrações e identidade | OK | OK | Nenhuma integração; identificação reaproveitada |
| Fronteira do NIAE | OK | OK | Base própria; slots neutros no núcleo, sem citar a camada |
| Governança | N/A | N/A | Nenhuma competência ou periodicidade alterada |
| Escopo por unidade | OK | OK | Curadoria e pertinência conservadas |
| Privacidade e finalidade | OK | OK | Card público versionado; sem consulta de Pessoa |
| Autorização | OK | OK | Sessão e rotas atuais; exemplo não dá acesso a dados privados |
| Acessibilidade | OK | OK | Semântica, foco, contraste, controles nativos |
| Mobile e esforço | OK | OK | Matriz 320–1440, fonte 100/200; convite independente |
| Testes | OK | OK | Regressões de raiz, legenda, acesso, fronteiras e shell |
| YAGNI | OK | OK | CSS/templates; nenhum app, modelo, fonte ou dependência nova |
| Exportações | N/A | N/A | Nenhuma alteração analítica |
| Decisões pendentes | OK | OK | Herdadas e explicitadas na spec |

**Resultado:** desenho compatível com a Constituição 2.1.0; nenhuma emenda necessária.

## Desenho técnico

### 1. Base, tokens e legenda

- `portal/base.html` estende `interface/base.html`, que permanece intacto. Inclui
  `portal/visual.css` depois da 015. Telas da camada usam essa base diretamente.
- Trajetória, e-mail e identificação usam `{% extends layout_base|default:"interface/base.html" %}`.
  O slot `layout_base` é neutro; só a camada fornece o valor fixo `portal/base.html`.
  Nenhum caminho do cliente ou nome de template informado pelo cliente é aceito.
- Blocos de estilo das telas harmonizadas incluem `block.super` para conservar a camada.
  Com o slot ausente, `block.super` é vazio e a saída antiga continua igual.
- O contexto da camada fornece o slot somente nas telas harmonizadas; a identificação
  recebe-o do chamador `/entrar/`. `/acesso/`, formações e Participações ficam fora.
- `imagens.legenda()` identifica a unidade da imagem, nunca atribui a imagem genérica à
  unidade da formação. Essa correção tem regressões para genérica, própria e divergente.

### 2. Página pública e Início

- `entrada()` continua resolvendo Pessoa/declarante, mas renderiza `portal/publico.html`
  quando não há sujeito. Mantém `never_cache` e destinos fixos.
- Card público: SVG de exemplo gerado em tempo de execução por `portal/exemplo.py`, com o código da
  021; incluído inline com nome acessível e selo explícito. Nenhum dado de banco.
- O Início reaproveita uma montagem sem nome para síntese, formações, agregados,
  apurações e descrição da prévia. O `src` da prévia aponta ao endpoint existente do card (PNG quando há rasterização, como na Minha trajetória),
  sem parâmetro de nome; não cria endpoint, arquivo pessoal nem cache persistente.
- Linha do tempo horizontal no desktop com várias formações; grade permite linhas
  adicionais. Agregados ficam ao lado quando presentes. Reconhecimento tem espaçamento
  mais compacto que o protótipo para corrigir o achado da Ana.
- Ações e prévia compartilham seção; Oportunidades e convite seguem no fluxo normal,
  sem `order` ou coluna que antecipe a pesquisa.

### 3. Harmonização

- `/entrar/`: slot neutro para recolher o painel fictício com `details/summary`;
  identificação, CSRF, mensagens e limites inalterados. `/acesso/` conserva o painel.
- Trajetória e contato conservam conteúdo e fluxos. Só a base e estilos da camada mudam.
- Oportunidades conserva grupos, campos, links e explicação. Curadoria não é harmonizada.
- Formulários continuam com largura de leitura; o container mais largo não estica campos
  nem parágrafos. Navegação quebra em linhas, sem menu dependente de JavaScript.

## Project Structure

`trajetoria/portal/templates/portal/{base.html,visual.css,publico.html,inicio.html}` e `trajetoria/portal/exemplo.py`;
`portal/{contexto.py,views.py,inicio.py}`; extensão neutra nos três templates compartilhados;
correção de legenda em `narrativa/imagens.py`. Testes nas pastas existentes `portal` e
`narrativa`; documentação em `specs/028-camada-visual-portal/`.

## Validação e entrega

Seguir [ambiente-local.md](../../docs/desenvolvimento/ambiente-local.md), sem alterar código
para subir ambiente. Banco novo `trajetoria_028` para preservar bancos já preparados com
outras chaves. Cada comando `manage.py` começa com `source .env &&`.

1. Linha de base com as quatro verificações do CI antes da mudança de aplicação.
2. Testes relevantes de raiz pública, painel, legenda, reconhecimento, fronteiras,
   navegação e Portal desligado; depois as quatro verificações completas.
3. Navegar no ambiente de demonstração com Ana e Diego, sem JavaScript; medir 320, 375,
   768, 1024, 1280 e 1440 px com fonte 100/200. As medidas usam viewport real ou iframe
   de largura exata; documentar o desconto da faixa na primeira tela.
4. Capturas 375, 1024 e 1440, primeiras telas 375×812, 1280×720 e 1440×900, e passagem
   para o instrumento. Comparar com protótipos B; guardar medidas e contraste.
5. Registrar validação, riscos e tarefas efetivamente concluídas. Não declarar
   Checkpoint 1 aplicado por medidas automáticas ou escolha da direção.

## Complexity Tracking

Sem desvio constitucional. Dois slots neutros de apresentação permitem conservar o
núcleo independente e o shell antigo; duplicar lógica de identificação ou views da
narrativa seria mais complexo. Nenhum mecanismo genérico de temas é criado.

## Decisões Pendentes

As da spec; tratamento provisório limitado à demonstração. A reversão remove a base
da camada e os valores dos slots; o núcleo e a coleta continuam funcionando.
