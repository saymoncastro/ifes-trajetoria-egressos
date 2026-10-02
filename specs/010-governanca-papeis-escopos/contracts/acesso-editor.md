# Contrato: autorização do editor (`trajetoria/editor/acesso.py`)

Atende spec FR-036 a FR-046, FR-061, FR-069 a FR-071. Complementa
`specs/009-editor-pesquisa-versao/contracts/rotas.md`, que continua valendo para tudo o
que não está aqui.

## Fluxo de toda requisição ao editor

```text
requisição
  → ModoDemonstracaoMiddleware        (008: modo desligado → 404; nada abaixo roda)
  → CsrfViewMiddleware                (POST sem token → 403 da 008)
  → @exige(regra)                     (010, o decorador mais externo da view)
       1. identificador = operador_em_uso(request)          # identificação (adaptador)
       2. identificador is None        → 302 para /demonstracao/operador/ (endereço fixo)
       3. vinculos = vinculos_ativos(identificador)          # 1 consulta
       4. vinculos == []               → 403 recusa "sem atuação ativa"
       5. not regra(vinculos)          → 403 recusa "vínculo não permite"
       6. request.atuacao = Atuacao(vinculos, publicado, rascunho, elaborar)
  → require_GET / require_http_methods / require_POST   (009)
  → never_cache, _respondendo          (009)
  → view (009):
       objeto (404 se inexistente)
       [leituras por estado] _exigir_consulta(request, versao) → 403 "vínculo não permite"
       [escritas] _exigir_rascunho, formulário, operação da 002 (009, inalterados)
```

Resolução do operador (1) e autorização (3–5) ficam separadas: `acesso.py` importa
`operador_em_uso` de **um único** lugar, o adaptador de identificação. O futuro
mecanismo de identidade (DP-1001) substitui essa importação e nada mais.

## `Atuacao` (valor anexado à requisição)

| Atributo | Origem |
|----------|--------|
| `rotulos` | `rotulo_de_atuacao` de cada vínculo ativo, para o cabeçalho |
| `consultar_rascunho` | `pode_consultar_rascunho(vinculos)` |
| `elaborar` | `pode_elaborar_instrumento(vinculos)` |

(`consultar_publicado` não é guardado: quem passou do passo 4 sempre o tem.)

O identificador **não** é exposto ao template.

## `exige(regra)`

- `regra` ∈ {`pode_consultar_publicado`, `pode_consultar_rascunho`,
  `pode_elaborar_instrumento`}, as próprias funções de `governanca.regras`, passadas
  diretamente. Não há enum de capacidade, registro, nome em texto nem composição de
  regras. Qualquer outro valor é erro de programação na importação do módulo.
- Sem operador identificado: `redirect("/demonstracao/operador/")`, sem parâmetro de
  retorno, sem ler o instrumento e sem gravar. Depois da escolha, o adaptador volta a
  `/editor/`.
- Grava `exige` no objeto da view, para a verificação de cobertura.
- Nunca grava nada no banco.

## `_exigir_consulta(request, versao)` (em `views.py`)

Fica em `views.py`, ao lado de `_exigir_rascunho`, para usar o mesmo mecanismo de interrupção
(`_Resposta`) sem mover código da 009; a recusa é a de `acesso.recusa`.

- Versão PUBLICADA → retorna (já autorizada por `pode_consultar_publicado`).
- Versão RASCUNHO e `request.atuacao.consultar_rascunho` falso → interrompe com a recusa
  "vínculo não permite", variante leitura de rascunho, por `_Resposta` (009).

## Rota → regra

| # | Método | Rota | View | `@exige` | Verificação adicional |
|---|--------|------|------|----------|-----------------------|
| 1 | GET | `/editor/` | `pesquisas` | `pode_consultar_publicado` | contagem só de publicadas sem `consultar_rascunho` |
| 2 | GET | `/editor/pesquisas/<p>/` | `pesquisa` | `pode_consultar_publicado` | Versões filtradas por `estado=PUBLICADA` sem `consultar_rascunho` |
| 3 | GET | `/editor/versoes/<v>/` | `versao` | `pode_consultar_publicado` | `_exigir_consulta` |
| 4 | GET | `/editor/versoes/<v>/diagnostico/` | `diagnostico` | `pode_consultar_rascunho` | — |
| 5 | GET | `/editor/versoes/<v>/previa/` | `previa` | `pode_consultar_publicado` | `_exigir_consulta` |
| 6 | GET | `/editor/versoes/<v>/previa/secoes/<n>/` | `previa_secao` | `pode_consultar_publicado` | `_exigir_consulta` |
| 7 | GET | `/editor/secoes/<s>/` | `secao` | `pode_consultar_publicado` | `_exigir_consulta` |
| 8 | GET | `/editor/perguntas/<q>/` | `pergunta` | `pode_consultar_publicado` | `_exigir_consulta` |
| 9 | GET, POST | `/editor/pesquisas/nova/` | `pesquisa_nova` | `pode_elaborar_instrumento` | — |
| 10 | GET, POST | `/editor/pesquisas/<p>/versoes/nova/` | `versao_nova` | `pode_elaborar_instrumento` | — |
| 11 | GET, POST | `/editor/versoes/<v>/nova-a-partir/` | `versao_a_partir` | `pode_elaborar_instrumento` | — |
| 12 | GET, POST | `/editor/versoes/<v>/dados/` | `versao_dados` | `pode_elaborar_instrumento` | — |
| 13 | GET, POST | `/editor/versoes/<v>/secoes/nova/` | `secao_nova` | `pode_elaborar_instrumento` | — |
| 14 | GET, POST | `/editor/secoes/<s>/editar/` | `secao_editar` | `pode_elaborar_instrumento` | — |
| 15 | POST | `/editor/secoes/<s>/mover/` | `secao_mover` | `pode_elaborar_instrumento` | — |
| 16 | GET, POST | `/editor/secoes/<s>/remover/` | `secao_remover` | `pode_elaborar_instrumento` | — |
| 17 | GET, POST | `/editor/secoes/<s>/perguntas/nova/` | `pergunta_nova` | `pode_elaborar_instrumento` | — |
| 18 | GET, POST | `/editor/perguntas/<q>/editar/` | `pergunta_editar` | `pode_elaborar_instrumento` | — |
| 19 | POST | `/editor/perguntas/<q>/mover/` | `pergunta_mover` | `pode_elaborar_instrumento` | — |
| 20 | GET, POST | `/editor/perguntas/<q>/trocar-secao/` | `pergunta_trocar_secao` | `pode_elaborar_instrumento` | — |
| 21 | GET, POST | `/editor/perguntas/<q>/remover/` | `pergunta_remover` | `pode_elaborar_instrumento` | — |
| 22 | GET, POST | `/editor/perguntas/<q>/opcoes/nova/` | `opcao_nova` | `pode_elaborar_instrumento` | — |
| 23 | GET, POST | `/editor/opcoes/<o>/` | `opcao_editar` | `pode_elaborar_instrumento` | — |
| 24 | POST | `/editor/opcoes/<o>/mover/` | `opcao_mover` | `pode_elaborar_instrumento` | — |
| 25 | GET, POST | `/editor/opcoes/<o>/remover/` | `opcao_remover` | `pode_elaborar_instrumento` | — |

**Leituras declaradas** (8): rotas 1–8. **Toda** outra rota exige
`pode_elaborar_instrumento`. A verificação automatizada de cobertura falha se uma rota
nova não tiver `exige`, ou se uma rota fora da lista de leituras não exigir elaborar.

## Respostas

| Situação | Status | Corpo |
|----------|--------|-------|
| Modo desligado | 404 | página 404 da 008 |
| Modo ligado, nenhum operador escolhido (GET ou POST) | 302 | `Location: /demonstracao/operador/` |
| Sem vínculo ativo | 403 | `editor/recusa.html`, variante `sem_atuacao` |
| Regra falsa ou rascunho sem `consultar_rascunho` | 403 | variante `vinculo_nao_permite` (leitura de rascunho ou elaboração) |
| Elemento inexistente, autorizado | 404 | como na 009 |
| Elemento inexistente, não autorizado | 403 | recusa (precede a busca) |
| Escrita em publicada, CPAEG | 302 (GET de formulário) / 409 (POST) | como na 009 |
| Escrita em publicada, sem elaborar | 403 | recusa |

## `editor/recusa.html`

- Estende `editor/base.html`, com o banner e sem trilha.
- `<h1>` "Acesso não permitido", parágrafo da variante e ligações:

| Variante | Texto (em `mensagens.py`) | Ligações |
|----------|---------------------------|----------|
| `sem_atuacao` | "Não há vínculo institucional ativo para este operador. Sem vínculo ativo, o editor não pode ser usado." | "Trocar operador fictício" → `/demonstracao/operador/` |
| `vinculo_nao_permite` (leitura de rascunho ou diagnóstico) | "Seu vínculo institucional atual não permite consultar Versões em rascunho. Ele permite consultar o instrumento publicado." | "Voltar às Pesquisas" → `/editor/`; "Trocar operador fictício" |
| `vinculo_nao_permite` (elaboração) | "Seu vínculo institucional atual não permite editar este instrumento. Ele permite consultar o instrumento publicado." | "Voltar às Pesquisas" → `/editor/`; "Trocar operador fictício" |

- Linguagem operacional. O texto principal **não** cita número de artigo da PAEG; a
  fundamentação (Art. 21, VI; Art. 22, IV) fica na spec, nas docstrings de
  `governanca/regras.py` e nos testes.
- Nada de identificador, valor técnico do papel, nome de regra, código de rejeição, UUID,
  lista de vínculos ou detalhe interno.
- Sem `role="alert"`: não é erro de formulário (padrão da 009).
- Passa em `verificar` da 008 (acessibilidade) e em `padroes_tecnicos` da 009.

## Cabeçalho do editor (`editor/base.html`)

- **Banner** (`mensagens.BANNER`, spec FR-061): "Ambiente não produtivo de demonstração: a
  identificação é simulada por operador fictício, e os vínculos fictícios não
  representam designação institucional real. Este editor não está disponível para uso
  produtivo."
- **Atuação**: "Atuação: {rótulos separados por ponto e vírgula}" quando há
  `request.atuacao`; nada na recusa sem atuação.
- **Ligação**: "Trocar operador fictício" → `/demonstracao/operador/`.

## Ações condicionadas (apresentação; a proteção é o servidor)

| Ação na página | Aparece se |
|----------------|-----------|
| Nova Pesquisa, Nova Versão | `atuacao.elaborar` |
| Nova Versão a partir desta (publicada) | `atuacao.elaborar` |
| Recomendação de trabalhar em cópia (009 FR-100) | só em rascunho; já restrito a CPAEG |
| Aviso "Somente Versões publicadas são exibidas para a sua atuação" | `not atuacao.consultar_rascunho` |

## O que não existe

Rota, ação ou botão de publicar, aprovar ou pedir aprovação; tela de vínculos; escolha
de "papel ativo"; identificador de operador aceito por parâmetro, cabeçalho ou campo de
formulário.
