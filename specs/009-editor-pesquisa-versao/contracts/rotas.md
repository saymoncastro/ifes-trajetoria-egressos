# Contrato: rotas do editor

Módulo: `trajetoria.editor`, montado em `config/urls.py` com
`path("editor/", include("trajetoria.editor.urls"))`. Este contrato atende spec FR-001 a
FR-112.

Nomes de views, templates e formulários são proposta do plan. As tasks podem ajustá-los
sem mudar o comportamento.

## Garantias comuns

- **Modo não produtivo**: com `TRAJETORIA_DEMONSTRACAO` diferente de `"1"`, toda rota
  abaixo responde 404 antes de qualquer view, por `ModoDemonstracaoMiddleware` da 008
  (FR-002; research R2).
- **Sem autenticação ou autorização**: nenhuma rota identifica operador. O banner de toda
  página diz que o acesso não confere competência institucional (FR-003, FR-004).
- **Métodos**:
  - `require_GET` em consultas e `require_http_methods(["GET", "POST"])` em
    formulários;
  - subir e descer são `require_POST`;
  - `never_cache` em todas.
- **Escrita**:
  - só em POST, com CSRF;
  - sempre por operações de `trajetoria.instrumento.operacoes`;
  - redirecionamento após sucesso (PRG), com `?aviso=<código>` de lista fechada e âncora
    do elemento (FR-097).
- **GET nunca escreve**, inclusive diagnóstico e prévia (FR-025).
- **Versão publicada** (research R12):
  - GET de página de formulário → 302 para a página de consulta com `?aviso=publicada`;
  - POST → **409** com `editor/aviso.html` (publicada, com link "criar nova Versão a
    partir desta"), sem chamar operação;
  - `OperacaoRejeitada(VERSAO_PUBLICADA)` por corrida → a mesma tela 409.
- **Rejeição da 002 em formulário**: 200 com o mesmo formulário, os valores preservados,
  o resumo de erros no topo e o erro no campo (FR-096). Nada é gravado.
- **Conflito** (`POSICAO_OCUPADA`, `ORDEM_INCOMPLETA` e demais da tabela do data-model
  §4): 409 com a mensagem "o conteúdo mudou desde que a página foi aberta" e um link
  para a página atual.
- **Elemento inexistente**: GET → 404 padrão; POST → 404 com `editor/aviso.html`
  ("o conteúdo mudou…").
- **`role="alert"`** só no resumo de erros de formulário, sempre com o título
  prefixado por "Erro:". Avisos (409, 404 de POST, `?aviso=`) e o diagnóstico usam
  `role="status"` ou nenhum papel.
- **Texto visível sem identificadores técnicos**: os UUIDs só aparecem em `href`,
  `action` e `value` (research R9).

## Rotas

`<p>`, `<v>`, `<s>`, `<q>` e `<o>` são UUIDs de Pesquisa, Versão, Seção, Pergunta e
Opção. `<n>` é um ordinal (1…).

### Pesquisas e Versões

| Método | Rota | View · template | Operação 002 | Sucesso |
|--------|------|-----------------|--------------|---------|
| GET | `/editor/` | `pesquisas` · `editor/pesquisas.html` | — (lista, nome e quantidade de Versões) | — |
| GET, POST | `/editor/pesquisas/nova/` | `pesquisa_nova` · `editor/formulario.html` | `criar_pesquisa(nome)` | → `/editor/pesquisas/<p>/?aviso=pesquisa-criada` |
| GET | `/editor/pesquisas/<p>/` | `pesquisa` · `editor/pesquisa.html` | — (Versões: designação, estado escrito, publicada em, origem) | — |
| GET, POST | `/editor/pesquisas/<p>/versoes/nova/` | `versao_nova` · `editor/formulario.html` | `criar_versao(pesquisa, designacao)` | → `/editor/versoes/<v>/?aviso=versao-criada` |
| GET, POST | `/editor/versoes/<v>/nova-a-partir/` | `versao_a_partir` · `editor/formulario.html` | `criar_versao_a_partir_de(origem, designacao)`. A origem pode estar em rascunho ou publicada | → `/editor/versoes/<nova>/?aviso=versao-criada` |
| GET | `/editor/versoes/<v>/` | `versao` · `editor/versao.html` | — (estrutura, R8; resumo do diagnóstico se rascunho) | — |
| GET, POST | `/editor/versoes/<v>/dados/` | `versao_dados` · `editor/formulario.html` | `alterar_versao(versao, designacao=, titulo=, texto_abertura=, texto_encerramento=)` | → `/editor/versoes/<v>/?aviso=dados-salvos` |

Detalhes de `pesquisa_nova`:

- Se já existir uma Pesquisa com o mesmo `nome`, por igualdade exata, e
  `confirmar_nome_repetido` não estiver marcado, a página volta com aviso e com a caixa
  "Criar mesmo assim". Nada é gravado.
- Confirmado, a criação ocorre. Isso não é regra de validade (spec FR-012;
  Clarifications).

### Seções

| Método | Rota | View · template | Operação 002 | Sucesso |
|--------|------|-----------------|--------------|---------|
| GET, POST | `/editor/versoes/<v>/secoes/nova/` | `secao_nova` · `editor/formulario.html` | `adicionar_secao(versao, proxima_posicao, titulo=, texto=)`; encaminhamento opcional → `definir_encaminhamento` no mesmo bloco atômico | → `/editor/secoes/<s>/?aviso=secao-criada` |
| GET | `/editor/secoes/<s>/` | `secao` · `editor/secao.html` | — (dados em leitura, destino, Perguntas com tipo, obrigatoriedade e desvio; ações se rascunho) | — |
| GET, POST | `/editor/secoes/<s>/editar/` | `secao_editar` · `editor/formulario.html` | `alterar_secao(secao, titulo=, texto=)` + `definir_encaminhamento(secao, destino ou None)`, num bloco atômico | → `/editor/secoes/<s>/?aviso=dados-salvos` |
| POST | `/editor/secoes/<s>/mover/` | `secao_mover` | `reordenar_secoes(versao, lista)`, com a lista de `acoes.mover` | → `/editor/versoes/<v>/#secao-N` |
| GET, POST | `/editor/secoes/<s>/remover/` | `secao_remover` · `editor/confirmar_remocao.html` | `remover_secao(secao)` | → `/editor/versoes/<v>/?aviso=secao-removida` |

Detalhes de `secao_mover`:

- `direcao` ∈ {`cima`, `baixo`}.
- Na ponta, nada é gravado e a resposta é 302 com `?aviso=sem-movimento`. A ação não é
  oferecida na ponta (FR-063).

Detalhes de `secao_remover`:

- O GET mostra a confirmação sem verificação prévia na interface: a regra de remoção é
  da 002 (FR-061) e não é duplicada no editor (decisão de implementação).
- No POST, as recusas `SECAO_COM_PERGUNTAS` e `SECAO_REFERENCIADA` voltam à página com a
  explicação (a segunda com a lista de `referencias_a`) e **sem** o botão "Remover".

### Perguntas

| Método | Rota | View · template | Operação 002 | Sucesso |
|--------|------|-----------------|--------------|---------|
| GET | `/editor/secoes/<s>/perguntas/nova/` | `pergunta_nova` · `editor/pergunta_tipo.html` | — (escolha entre os 4 tipos, `TipoPerguntaForm`, `method="get"`) | — |
| GET, POST | `/editor/secoes/<s>/perguntas/nova/?tipo=<T>` | `pergunta_nova` · `editor/formulario.html` | `adicionar_pergunta(secao, proxima_posicao, tipo, texto, obrigatoria=, texto_explicativo=, escala=Escala(...) se ESCALA)` | Escolha → `/editor/perguntas/<q>/?aviso=adicione-opcoes`; demais → `/editor/secoes/<s>/?aviso=pergunta-criada#pergunta-N` |
| GET | `/editor/perguntas/<q>/` | `pergunta` · `editor/pergunta.html` | — (dados, tipo fixo e explicação FR-034, escala explicada, Opções com complemento e desvio, ações) | — |
| GET, POST | `/editor/perguntas/<q>/editar/` | `pergunta_editar` · `editor/formulario.html` | `alterar_pergunta(pergunta, texto=, texto_explicativo=, obrigatoria=, escala= se ESCALA)`. **Sem** campo de tipo | → `/editor/perguntas/<q>/?aviso=dados-salvos` |
| POST | `/editor/perguntas/<q>/mover/` | `pergunta_mover` | `reordenar_perguntas(secao, lista)` | → `/editor/secoes/<s>/#pergunta-N` |
| GET, POST | `/editor/perguntas/<q>/trocar-secao/` | `pergunta_trocar_secao` · `editor/formulario.html` | `mover_pergunta(pergunta, destino, proxima_posicao(destino))` | → `/editor/perguntas/<q>/?aviso=pergunta-movida` |
| GET, POST | `/editor/perguntas/<q>/remover/` | `pergunta_remover` · `editor/confirmar_remocao.html` | `remover_pergunta(pergunta)`. A confirmação cita Opções, escala e desvios removidos junto | → `/editor/secoes/<s>/?aviso=pergunta-removida` |

Na criação de Pergunta, um `tipo` fora dos 4 volta ao passo de escolha. Esse caso nunca
chega à 002.

### Opções

| Método | Rota | View · template | Operação 002 | Sucesso |
|--------|------|-----------------|--------------|---------|
| GET, POST | `/editor/perguntas/<q>/opcoes/nova/` | `opcao_nova` · `editor/formulario.html` | `adicionar_opcao(pergunta, proxima_posicao, texto, complemento_textual=)`; desvio opcional (escolha única) → `acoes.definir_desvio`, no mesmo bloco atômico | "Adicionar" → `/editor/perguntas/<q>/#opcao-N`; "Adicionar e incluir outra" → `/editor/perguntas/<q>/opcoes/nova/?aviso=opcao-criada` |
| GET, POST | `/editor/opcoes/<o>/` | `opcao_editar` · `editor/formulario.html` | `alterar_opcao(opcao, texto=, complemento_textual=)` + `acoes.definir_desvio(pergunta, opcao, destino)`, num bloco atômico | → `/editor/perguntas/<q>/?aviso=dados-salvos#opcao-N` |
| POST | `/editor/opcoes/<o>/mover/` | `opcao_mover` | `reordenar_opcoes(pergunta, lista)` | → `/editor/perguntas/<q>/#opcao-N` |
| GET, POST | `/editor/opcoes/<o>/remover/` | `opcao_remover` · `editor/confirmar_remocao.html` | `remover_opcao(opcao)`. A confirmação cita o desvio removido junto | → `/editor/perguntas/<q>/?aviso=opcao-removida` |

As rotas de Opção só existem para Perguntas de escolha:

- Para texto curto ou escala, `opcoes/nova/` responde 404 e a página da Pergunta não
  oferece Opções (FR-041).
- O campo `desvio` só existe em escolha única (FR-051, FR-053).

### Diagnóstico e prévia

| Método | Rota | View · template | Leitura | Observação |
|--------|------|-----------------|---------|------------|
| GET | `/editor/versoes/<v>/diagnostico/` | `diagnostico` · `editor/diagnostico.html` | `diagnosticar(versao)` ([diagnostico.md](diagnostico.md)) | Versão publicada → 302 para `/editor/versoes/<v>/?aviso=publicada` (FR-075) |
| GET | `/editor/versoes/<v>/previa/` | `previa` · `editor/previa.html` | `conteudo_da_versao` | Título, abertura, índice de Seções e encerramento |
| GET | `/editor/versoes/<v>/previa/secoes/<n>/` | `previa_secao` · `editor/previa_secao.html` | `conteudo_da_versao` + `FormularioDaSecao(secao, {}).itens()` (008) | Sem `<form>` nem envio. Anotações estruturais, como "Se «X» for escolhida na aplicação real, a próxima seção será: …". Anterior e seguinte são links GET pela **ordem estrutural**. Sem cursor, sessão, respostas temporárias nem cálculo de próxima Seção pela 006 |

A prévia funciona para rascunho e publicada (FR-085). Um `<n>` fora do intervalo
responde 404.

## O que não existe (verificado em teste)

- Rota ou botão de publicar, despublicar, aprovar, homologar, enviar para aprovação.
- Rota para renomear ou excluir Pesquisa, ou excluir Versão.
- Rota de API (JSON), de exportação ou importação de definição, de Campanha, de
  Participação, de Pessoa ou de dashboard.
- Rota de troca de tipo de Pergunta.
- `<script>` em qualquer template do editor.
