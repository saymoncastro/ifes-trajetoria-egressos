# Data Model: Minha Trajetória em vídeo

Fase 1. O modelo tem duas camadas:

1. a **apresentação**, não persistida: a `ComposicaoVisual`, derivada do card da 021;
2. o **estado técnico**, persistido só enquanto necessário: `GeracaoDeVideo`.

**Escopo das mudanças:**

- Nenhuma tabela existente muda.
- Uma tabela nova num app novo (`trajetoria/video/`), com uma migração aditiva `0001`.
- Nenhum model de domínio (Pessoa, Conclusão Acadêmica, Participação, Resposta) é lido
  pela tabela nova nem a referencia.
- `TrajetoriaNarrativa`, `Compartilhavel` e `serializar()` da 021 não mudam. O contrato da
  narrativa continua na versão 1.

---

## 1. Composição do card agrupada por zonas — `trajetoria/narrativa/card.py` (alteração interna)

### 1.1 `Elemento` (inalterado)

`tag`, `atributos`, `texto`, `interior`.

### 1.2 `Zona` (nova, congelada)

| Campo | Tipo | Regra |
|---|---|---|
| `chave` | `str` | Uma de `ZONAS` (abaixo) |
| `partes` | `tuple[tuple[Elemento, ...], ...]` | Pelo menos uma parte. Ordem de pintura preservada |

### 1.3 `Composicao` (alterada)

| Campo | Mudança |
|---|---|
| `zonas: tuple[Zona, ...]` | **Novo.** Na ordem de `ZONAS`. Só as presentes |
| `elementos: tuple[Elemento, ...]` | Mantido, **na mesma ordem de hoje**. O SVG do card não muda (research R3) |
| `exibidas`, `destaques`, `abertura` | Inalterados |

### 1.4 `ZONAS` (enumeração fechada, ordem de pintura)

| Chave | Partes | Elementos da 021 (`class`) | Presença |
|---|---|---|---|
| `fundo` | 1 | `fundo`, `faixa`, `faixa-quadro` | Sempre |
| `abertura` | 1 | `abertura` (imagem), `onda` | Sempre |
| `marca` | 1 | `marca-fundo`, `marca` | Sempre |
| `legenda` | 1 | `legenda-fundo`, `legenda` | Sempre |
| `titulo` | 1 | `titulo` | Sempre |
| `nome` | 1 | `nome` | Só com nome escolhido e disponível |
| `traco` | 1 | `traco` | Só com 2 ou mais nós |
| `nos` | 1 por formação exibida | `no`, `no-centro`, `ano`, `curso`, `detalhe` daquele nó | Sempre (≥ 1) |
| `mais` | 1 | `mais` | Só com formações omitidas |
| `destaques` | 1 por cartão | `destaque`, `filete`, `numero`, `rotulo` daquele cartão | Só com destaques no card |
| `apuracao` | 1 | `apuracao` | Só com destaques |
| `fechamento` | 1 | `fecho`, `hashtag-fundo`, `hashtag` | Sempre |
| `rodape` | 1 | `rodape` (instituição e demonstração) | Sempre |

**Invariantes (testados):**

- O conjunto de elementos de todas as partes é exatamente `Composicao.elementos`. Nada fica
  de fora, nada se repete.
- A concatenação das zonas, reordenada pelo índice original, reproduz `elementos`.
- O `card_svg` continua igual byte a byte ao de antes da mudança.

---

## 2. `ComposicaoVisual` serializada — `trajetoria/narrativa/composicao.py` (novo)

Python sem banco. `composicao_visual(compartilhavel, nome, demonstracao) -> dict` monta a
forma JSON do [contrato](contracts/composicao-visual.md).

- **Partes:** a marcação de cada parte vem de `render_to_string("narrativa/card.svg", …)`,
  sem o invólucro `<svg>`/`<title>`/`<desc>`.
- **Escape:** texto e atributos com o escape do Django; ativos (`interior`) sem escape,
  como no card.
- **Determinismo:** mesma entrada → mesmo `dict`.
- **Serialização canônica:** `json.dumps(…, ensure_ascii=False, sort_keys=True,
  separators=(",", ":"))`.
- **`chave_da_composicao(dict) -> str`:** SHA-256 hexadecimal da serialização canônica. Uso
  interno; nunca exposta.
- **`TEMPLATE_DE_VIDEO = "trajetoria-v1"`:** constante única. Vai no JSON e entra na chave
  (FR-019).

**Proibições (testadas):** nenhuma chave nem texto com id interno, CPF, data de nascimento,
contato, Resposta, forma de oferta, data completa, tempo decorrido ou ingresso. Nenhuma
referência a model.

---

## 3. Estado técnico — `trajetoria/video/models.py: GeracaoDeVideo`

Não é entidade de domínio (FR-028). Existe para que o egresso possa consultar o estado de
um processamento que não cabe na requisição (FR-030, FR-031; research R5, R6).

| Campo | Tipo | Regra |
|---|---|---|
| `id` | `BigAutoField` | — |
| `chave` | `CharField(64)` | SHA-256 da composição canônica. **Única** |
| `template` | `CharField(40)` | `TEMPLATE_DE_VIDEO` no momento do pedido |
| `estado` | `CharField(12)`, choices | `SOLICITADO`, `PROCESSANDO`, `PRONTO`, `FALHOU` |
| `composicao` | `JSONField(null=True)` | Preenchida no pedido. **Apagada** ao sair de `PROCESSANDO` |
| `video` | `BinaryField(null=True)` | Só em `PRONTO` |
| `tamanho` | `PositiveIntegerField(null=True)` | Bytes do vídeo |
| `motivo` | `CharField(40, blank=True)` | Só em `FALHOU`; código técnico (`tempo_esgotado`, `sem_processador`, `saida_invalida`, `indisponivel`, `codigo_<n>`) |
| `solicitado_em` | `DateTimeField` | — |
| `iniciado_em` | `DateTimeField(null=True)` | Ao entrar em `PROCESSANDO` |
| `concluido_em` | `DateTimeField(null=True)` | Ao entrar em `PRONTO` ou `FALHOU` |
| `expira_em` | `DateTimeField()` (**obrigatório**) | Sempre definido, em toda transição, como `momento da transição + TRAJETORIA_VIDEO_RETENCAO`: `solicitado_em` (`SOLICITADO`), `iniciado_em` (`PROCESSANDO`), `concluido_em` (`PRONTO`, `FALHOU`). Nenhuma linha existe sem prazo de descarte (FR-029; analyze P1) |

**Restrições no banco:**

- `UniqueConstraint(chave)`.
- `CheckConstraint`s:
  - `PRONTO` ⇒ `video` não nulo;
  - `FALHOU` ⇒ `motivo` não vazio;
  - `SOLICITADO` ⇒ `composicao` não nula.
- Índice em (`estado`, `solicitado_em`), usado pelo processador, e índice em `expira_em`, usado pela limpeza.

**Sem FK.** Nenhum campo identifica a Pessoa.

### 3.1 Transições

```text
                 solicitar (POST)
   (ausente) ───────────────────────► SOLICITADO
       ▲                                  │ processador toma (select_for_update skip_locked)
       │ limpeza (expira_em < agora)      ▼
       │                              PROCESSANDO
       │                     sucesso ╱          ╲ falha / tempo esgotado / > 5 min
       │                            ▼            ▼
       └──────────────────────── PRONTO        FALHOU ── "Tentar novamente" (POST) ──► SOLICITADO
                                                  │
                                                  └── limpeza (expira_em < agora) ──► (ausente)
```

| Ação | Pré-condição | Efeito |
|---|---|---|
| `solicitar(composicao)` | Linha ausente | Cria `SOLICITADO` com `composicao`, `solicitado_em` e `expira_em` |
| `solicitar(composicao)` | `SOLICITADO`, `PROCESSANDO` ou `PRONTO` não vencido | **Nada** (FR-032) |
| `solicitar(composicao)` | `FALHOU`, ou qualquer linha vencida | Volta a `SOLICITADO`: nova `composicao`, limpa `motivo`, `video`, `iniciado_em` e `concluido_em`; novos `solicitado_em` e `expira_em` |
| `processar_proximo()` | Existe `SOLICITADO` | Numa transação curta: → `PROCESSANDO` com `iniciado_em` e `expira_em`, guardando o `iniciado_em` lido. Render **fora** da transação. Gravação final **condicionada** (abaixo) |
| Gravação final do processador | `UPDATE … WHERE id = :id AND estado = 'PROCESSANDO' AND iniciado_em = :iniciado_em_lido` | Afetou 1 linha: → `PRONTO` (`video`, `tamanho`, `concluido_em`, `expira_em`) ou `FALHOU(motivo)`, com `composicao := null`. Afetou 0 linhas (a linha foi apagada, reiniciada por "Tentar novamente" ou marcada como travada durante o render): o resultado é **descartado**, com log técnico `"video: resultado descartado"` (analyze U2) |
| `limpar()` | `expira_em < agora`, qualquer estado | `DELETE` |
| `limpar()` | `PROCESSANDO` com `iniciado_em` há mais que o prazo de travado: `max(5 min, TRAJETORIA_VIDEO_TEMPO_MAXIMO + 1 min)` | → `FALHOU(tempo_esgotado)`, `composicao := null`, novos `concluido_em` e `expira_em` |
| `limpar()` | `SOLICITADO` com `solicitado_em` há mais de 10 min (processador ausente ou fila parada) | → `FALHOU(sem_processador)`, `composicao := null`, novos `concluido_em` e `expira_em`. Sem processador, a composição com o nome vive no máximo 10 min (analyze P1) |

**Quem chama `limpar()`:** o laço do processador, `solicitar()` e, no máximo a cada 30 s
por processo, `estado_para()` e `video_pronto()`. A limpeza não depende de o processador
estar rodando: o acesso à página descarta o que venceu (analyze P1). O limite de 30 s evita
que cada consulta de estado ou pedido `Range` vire três escritas (code review).

**Prazos dos estados intermediários (code review):** `expira_em` nunca vence antes da
janela do estado.
- `SOLICITADO`: `max(retenção, 11 min)`, pois vira `FALHOU` aos 10 min.
- `PROCESSANDO`: `max(retenção, travado + 1 min)`.

Uma retenção curta ou um render longo nunca apagam nem dão como travado um pedido em
curso.

### 3.2 Leitura do estado pelo egresso (`estado_para(chave)`)

| Situação no banco | Estado exibido |
|---|---|
| Ausente ou vencida | `nenhum` (oferece "Gerar vídeo") |
| `SOLICITADO` ou `PROCESSANDO` | `preparando` |
| `PRONTO` não vencido | `pronto` |
| `FALHOU` (inclusive `sem_processador`, aplicado pela limpeza que antecede a leitura) | `falhou` |

Os quatro estados da spec (FR-031) são os do banco. A página agrupa `SOLICITADO` e
`PROCESSANDO` numa única mensagem.

---

## 4. Configuração — `config/settings.py`

Todas com padrão de desenvolvimento. Nenhum segredo.

| Variável | Padrão | Uso |
|---|---|---|
| `TRAJETORIA_VIDEO_PROJETO` | `BASE_DIR / "video"` | Diretório do projeto Node |
| `TRAJETORIA_VIDEO_NODE` | `shutil.which("node")` | Executável do Node |
| `TRAJETORIA_VIDEO_NAVEGADOR` | vazio | Executável do Chrome, opcional (research R12) |
| `TRAJETORIA_VIDEO_TEMPO_MAXIMO` | 120 s | Limite de um render |
| `TRAJETORIA_VIDEO_CONCORRENCIA` | 2 | Abas do Chrome por render |
| `TRAJETORIA_VIDEO_RETENCAO` (ambiente: `TRAJETORIA_VIDEO_RETENCAO_MINUTOS`) | 2 h | Retenção de pronto ou falho (DP-2202; máximo de 24 h validado na carga) |

---

## 5. Origem dos dados (resumo)

Tudo o que aparece no vídeo vem da composição do card (spec, "Origem dos Dados"). A tabela
técnica guarda conteúdo derivado e temporário, nunca dado de domínio.
