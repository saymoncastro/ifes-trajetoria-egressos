# Data Model: Editor institucional de Pesquisa e Versão

**Feature**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md) | **Research**: [research.md](research.md)

Em resumo:

- **Entidades novas: 0.**
- **Colunas, constraints ou migrações novas: 0.**
- **Persistência de estado de interface: 0.** Não há sessão, cookie novo, prontidão,
  prévia, seleção nem aprovação.

O editor lê e escreve só as entidades da Feature 002, e escreve exclusivamente pelas
operações públicas dela (research R3). Os demais itens deste documento são **valores em
memória**, que nascem e morrem numa requisição.

## 1. Entidades consumidas (inalteradas, Feature 002)

| Entidade | Leitura pelo editor | Escrita pelo editor (operação 002) |
|----------|---------------------|-------------------------------------|
| `Pesquisa` (`nome`) | Lista; página da Pesquisa; aviso de nome repetido, por consulta de igualdade exata | `criar_pesquisa`. **Nunca** `renomear_pesquisa` |
| `Versao` (`designacao`, `estado`, `publicada_em`, `origem`, `titulo`, `texto_abertura`, `texto_encerramento`) | Lista por Pesquisa; cabeçalho; `publicada` decide se a página é editável (R12) | `criar_versao`, `criar_versao_a_partir_de`, `alterar_versao`. **Nunca** `publicar` |
| `Secao` (`posicao`, `titulo`, `texto`, `encaminhamento`) | Via `conteudo_da_versao`; queryset para próxima posição e ordem atual | `adicionar_secao`, `alterar_secao`, `definir_encaminhamento`, `reordenar_secoes`, `remover_secao` |
| `Pergunta` (`posicao`, `tipo`, `texto`, `texto_explicativo`, `obrigatoria`, `escala_*`) | Idem | `adicionar_pergunta`, `alterar_pergunta`, `mover_pergunta`, `reordenar_perguntas`, `remover_pergunta` |
| `Opcao` (`posicao`, `texto`, `complemento_textual`, `regra_destino`, `regra_finaliza`) | Idem | `adicionar_opcao`, `alterar_opcao`, `reordenar_opcoes`, `remover_opcao`, `definir_regra`, `remover_regra` |

**Não são lidas nem escritas**:

- Pessoa e Conclusão Acadêmica (001);
- Campanha (004);
- Participação e Resposta (005/006/007).

**Regras que o editor respeita e não reimplementa**: todas as de 002 FR-058, FR-059 e
FR-061 a FR-062, e a imutabilidade de FR-016. O editor só lê `Versao.publicada` para
decidir o que **exibir** e para recusar POST cedo (R12). A recusa definitiva é sempre a
da 002.

**Estados**: os de sempre, RASCUNHO → PUBLICADA. O editor **não** provoca nenhuma
transição de estado, e nenhum estado novo existe.

## 2. Mudança mínima em código de feature anterior (sem dado novo)

| Feature | Arquivo | Mudança | Efeito em dados ou contrato |
|---------|---------|---------|-----------------------------|
| 006 | `trajetoria/participacao/percurso.py` | Nova função pública e pura `secoes_nao_suportadas(conteudo) -> tuple[ConteudoSecao, ...]`, consumida por `_exigir_suporte` | Nenhum. Violações, motivo, detalhe e ordem inalterados. `__all__` acrescido |
| 002 | — | Nenhuma | — |
| 008 | `demonstracao/middleware.py` (docstring) | Cita o editor como rota coberta | Nenhum |

## 3. Valores em memória (não persistidos)

### `Localizacao` (`editor/apresentacao.py`)

| Campo | Significado |
|-------|-------------|
| `rotulo` | Texto operacional, como "Seção 4 — Situação profissional", "Pergunta 2 da Seção 4: Qual sua ocupação?" ou "Opção «Não» da Pergunta 1 da Seção 1" |
| `endereco` | Página do editor onde o elemento é corrigido |

Ela é construída por `localizador(conteudo)`, um mapa `id → Localizacao` para a Versão,
as Seções, as Perguntas e as Opções, com ordinais derivados da ordem (R7, R9).

### `Problema` (`editor/diagnostico.py`)

| Campo | Significado |
|-------|-------------|
| `origem` | `"estrutura"` (diagnóstico A, da 002) ou `"jornada"` (diagnóstico B, da 006) |
| `causa` | `Motivo` da 002, ou `Motivo.ESTRUTURA_NAO_SUPORTADA` da 006 (o motivo que a 006 já usa). É rastreável em código e em teste e **nunca** exibido |
| `elemento` | `Localizacao` |
| `texto` | Mensagem operacional acionável: **onde** (rótulo do elemento) e **o que corrigir**. Por exemplo, "A Pergunta «Qual é sua situação profissional?» (Pergunta 2 da Seção 4) precisa ter pelo menos duas Opções." |

### `Diagnostico` (`editor/diagnostico.py`)

| Campo ou propriedade | Significado |
|----------------------|-------------|
| `estrutura: tuple[Problema, ...]` | Diagnóstico **A — Estrutura válida**: um problema por `Violacao` de `verificar_completude` (002), na ordem dela |
| `jornada: tuple[Problema, ...]` | Diagnóstico **B — Compatível com a jornada atual**: um problema por Seção de `secoes_nao_suportadas` (006), na ordem |
| `estrutura_valida` | `not estrutura` |
| `compativel_com_jornada` | `not jornada` |
| `sem_impedimentos_conhecidos` | `estrutura_valida and compativel_com_jornada` |

As tuplas guardam **todos** os problemas concretos. Os booleanos são só derivados e
nunca substituem a lista exibida ao operador.

A situação apresentada é derivada no template a partir das propriedades acima:

| `estrutura_valida` | `compativel_com_jornada` | Situação exibida |
|--------------------|--------------------------|------------------|
| não | qualquer | "Com problemas de estrutura" (e as incompatibilidades, se houver) |
| sim | não | "Estrutura válida, mas incompatível com a jornada atual" |
| sim | sim | "Sem impedimentos técnicos conhecidos", com a explicação de que não é aprovação, autorização nem publicação (FR-071) |

Não existe enum de situação, campo `pronta` ou qualquer valor de aprovação.

### Formulários (`editor/formularios.py`, `forms.Form`)

| Formulário | Campos → argumento da operação |
|------------|--------------------------------|
| `PesquisaForm` | `nome` → `criar_pesquisa(nome)`. `confirmar_nome_repetido`, oculto, só controla o aviso (R11) |
| `DesignacaoForm` | `designacao` → `criar_versao` / `criar_versao_a_partir_de` |
| `DadosVersaoForm` | `designacao`, `titulo`, `texto_abertura`, `texto_encerramento` → `alterar_versao(...)`. Vazio vira `None` nos opcionais |
| `SecaoForm` | `titulo`, `texto` → `adicionar_secao` / `alterar_secao`. `encaminhamento` (UUID de outra Seção ou "seguir a ordem") → `definir_encaminhamento(secao, destino ou None)` |
| `TipoPerguntaForm` | `tipo` ∈ os 4 valores de `TipoPergunta` (GET, sem escrita) |
| `PerguntaForm(tipo)` | `texto`, `texto_explicativo`, `obrigatoria` → `adicionar_pergunta` / `alterar_pergunta`. Escala: `inicio`, `fim`, `rotulo_inicio`, `rotulo_fim` → `Escala(...)` |
| `MoverPerguntaForm` | `secao` (UUID de outra Seção da Versão) → `mover_pergunta(pergunta, secao, proxima_posicao)` |
| `OpcaoForm(tipo)` | `texto`, `complemento` → `adicionar_opcao` / `alterar_opcao`. `desvio` ("sem desvio", "finalizar" ou UUID de Seção; só escolha única) → `definir_desvio` (R6) |

Subir e descer usam só o botão (`direcao` ∈ {`cima`, `baixo`}), sem formulário de texto.

### Estado entre requisições

| O quê | Onde | Persistência |
|-------|------|--------------|
| Elemento atual | Caminho da URL (UUID) | Nenhuma |
| Aviso pós-gravação | `?aviso=<código>` de lista fechada (`mensagens.AVISOS`) | Nenhuma |
| Retorno ao elemento | Âncora `#secao-N`, `#pergunta-N`, `#opcao-N` | Nenhuma |
| Confirmação de nome repetido | Campo oculto do próprio formulário | Nenhuma |

## 4. Mapeamento de rejeições → mensagens e campos

Os textos estão em `editor/mensagens.py`. Os mapeamentos são **locais**: no
diagnóstico, os 5 motivos de completude; em cada view, os motivos que sua operação pode
devolver (research R10). O sentido segue spec FR-095.

| Origem | Causa | Campo associado (quando houver) | Mensagem (sentido) |
|--------|-------|---------------------------------|--------------------|
| 002 | `VERSAO_PUBLICADA` | — (tela 409) | Publicada; crie nova Versão a partir dela |
| 002 | `DESIGNACAO_REPETIDA` | `designacao` | Já existe Versão com esta designação nesta Pesquisa |
| 002 | `TEXTO_VAZIO` | o texto obrigatório do formulário | Informe o texto |
| 002 | `OPCAO_REPETIDA` | `texto` | Já existe Opção com este texto nesta Pergunta |
| 002 | `COMPLEMENTO_REPETIDO` | `complemento` | Só uma Opção por Pergunta aceita complemento; desmarque a atual antes |
| 002 | `ESCALA_INVALIDA` | `inicio` | Limite inicial inteiro e menor que o final |
| 002 | `SECAO_COM_PERGUNTAS` | — (confirmação de remoção) | Remova ou mova as Perguntas antes |
| 002 | `SECAO_REFERENCIADA` | — (confirmação de remoção) | É destino de …, com a lista de `referencias_a` |
| 002 | `POSICAO_OCUPADA`, `ORDEM_INCOMPLETA`, mapeados só nas ações de inclusão, mudança de Seção e reordenação | — | O conteúdo mudou desde que a página foi aberta |
| 002 | Qualquer motivo **não mapeado** pela ação, como `TIPO_NAO_SUPORTADO`, `REGRA_EM_TIPO_INCOMPATIVEL`, `POSICAO_INVALIDA` ou `REFERENCIA_OUTRA_VERSAO` numa escrita | — | **Não é traduzido**: propaga como erro (500, com log). A interface não oferece ação que o provoque; se ocorrer, é erro de programa, não validação |
| 002 (diagnóstico A) | `SEM_SECOES` | Versão | A Versão não tem Seções |
| 002 (diagnóstico A) | `SECAO_SEM_PERGUNTAS` | Seção | Esta Seção não tem Perguntas |
| 002 (diagnóstico A) | `OPCOES_INSUFICIENTES` | Pergunta | Precisa de pelo menos duas Opções |
| 002 (diagnóstico A) | `DESTINO_NAO_POSTERIOR` | Seção (encaminhamento) ou Opção (desvio) | O destino precisa ser uma Seção posterior |
| 002 (diagnóstico A) | `REFERENCIA_OUTRA_VERSAO` | idem | Destino fora desta Versão. Só ocorre por escrita fora das operações |
| 006 (diagnóstico B) | Seção em `secoes_nao_suportadas` | Seção | A jornada atual não consegue aplicar mais de uma Pergunta com desvio na mesma Seção |
| — | Elemento inexistente (POST) | — (tela 404 do editor) | O conteúdo mudou desde que a página foi aberta |
| — | Falha inesperada | — (500 da 008) | Continua sendo erro: página 500 da 008, sem detalhe técnico ao usuário e registrada no log. Nunca é mascarada como erro de formulário |

## 5. Origem dos dados apresentados

Todo dado exibido é **configuração do instrumento** (002), ou diagnóstico **derivado**
dela pelas capacidades da 002 e da 006. Nenhum dado pessoal, institucional de Conclusão
ou declarado é lido ou exibido (spec, "Origem dos Dados"; Constituição III e XVI).
