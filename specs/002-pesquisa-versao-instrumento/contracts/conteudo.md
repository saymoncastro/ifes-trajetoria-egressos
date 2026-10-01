# Contrato: leitura do conteúdo da Versão e percurso de Seções

Interface de leitura que Campanha, jornada de resposta e exportação consumirão. Módulo:
`trajetoria.instrumento.conteudo`. Atende FR-063, FR-064 e documenta FR-048 a FR-055 (sem fixar o momento de aplicação das
regras — FR-053).

## Conteúdo da Versão

```python
def conteudo_da_versao(versao: Versao) -> ConteudoVersao
```

Devolve uma árvore imutável, sem nenhum objeto do ORM. Coleções são tuplas, sempre na
ordem das posições. Ausência é `None`.

```python
@dataclass(frozen=True)
class ConteudoVersao:
    id: UUID
    pesquisa_id: UUID
    designacao: str
    estado: EstadoVersao                 # RASCUNHO | PUBLICADA
    publicada_em: datetime | None
    origem_id: UUID | None
    titulo: str | None
    texto_abertura: str | None
    texto_encerramento: str | None
    secoes: tuple[ConteudoSecao, ...]

@dataclass(frozen=True)
class ConteudoSecao:
    id: UUID
    posicao: int
    titulo: str | None
    texto: str | None
    encaminhamento_id: UUID | None       # None = fluxo padrão
    perguntas: tuple[ConteudoPergunta, ...]

@dataclass(frozen=True)
class ConteudoPergunta:
    id: UUID
    posicao: int
    tipo: TipoPergunta
    texto: str
    texto_explicativo: str | None
    obrigatoria: bool
    escala: Escala | None                # presente só em ESCALA
    opcoes: tuple[ConteudoOpcao, ...]    # vazia em TEXTO_CURTO e ESCALA

@dataclass(frozen=True)
class ConteudoOpcao:
    id: UUID
    posicao: int
    texto: str
    complemento_textual: bool
    regra: RegraNavegacao | None         # só em ESCOLHA_UNICA

@dataclass(frozen=True)
class RegraNavegacao:
    destino_secao_id: UUID | None        # None ⇔ finaliza
    finaliza: bool
```

### Garantias

- **Completo**: todo atributo e toda referência da Versão aparecem (FR-064).
- **Determinístico**: duas leituras da mesma Versão sem alteração entre elas são iguais
  (`==`). Para Versão publicada, isso vale para sempre (SC-002).
- **Fechado na Versão**: todo `encaminhamento_id` e `destino_secao_id` é `id` de uma
  `ConteudoSecao` da mesma árvore (FR-021).
- **Independente do ORM**: consumidores não precisam conhecer tabelas nem modelos.

### Lista de Versões (FR-063)

Lida diretamente pelos modelos, como na 001: `pesquisa.versoes` (ordem por
`designacao`, sem significado de domínio), com `designacao`, `estado`, `publicada_em` e
`origem`.

## Percurso de Seções

Semântica de **destino** que a futura jornada de resposta DEVE respeitar. **Nada nesta
feature a executa** (FR-056, R14). Os testes usam um auxiliar que a aplica para enumerar
os percursos de Seções possíveis e verificar SC-001, US7 e US8.

**Fora deste contrato (FR-053)**: o momento em que uma regra acionada é aplicada — logo
após a Pergunta X, ao sair da Seção que contém X ou outro — e, portanto, se as Perguntas
posteriores a X na mesma Seção são apresentadas. Também fica fora qual regra prevalece se
duas Perguntas da mesma Seção acionarem regras. A Feature 003 decide como representar
cada ramificação concreta; a feature da jornada define a execução. O contrato não tem
atributo nem enumeração de momento de aplicação.

Definições, sobre um `ConteudoVersao`:

- **Fim**: finalização do instrumento. O texto de encerramento, se houver, encerra; não
  existe Seção de fim (FR-010).
- **Seção seguinte padrão de S**: `S.encaminhamento_id`, se houver; senão, a próxima
  Seção na ordem; se S for a última, **Fim** (FR-048, FR-049).

**Início**: a primeira Seção na ordem.

**Destino depois da Seção S**, dadas as respostas às Perguntas de S:

1. Se uma Pergunta de S é `ESCOLHA_UNICA` e a Opção respondida tem regra, o destino é o
   da regra: `finaliza` → **Fim**; `destino_secao_id = Z` → Seção Z (FR-054).
2. Senão (nenhuma Opção respondida tem regra, ou a pergunta opcional ficou sem
   resposta), o destino é a **Seção seguinte padrão de S**.

Respostas a escolha múltipla, texto curto e escala nunca determinam destino (FR-050).

**Terminação**: na Versão publicada, todo destino é Seção posterior à de origem (FR-055),
e toda Seção tem ao menos uma Pergunta (FR-059). Logo, todo percurso de Seções avança na
ordem e termina em **Fim**, sem ciclos.

### Exemplo (padrões do instrumento atual, com textos fictícios)

| Seção | Perguntas | Encaminhamento | Regras |
|-------|-----------|----------------|--------|
| 1 Termos | P1 (Sim/Não) | — | P1 = Não → Fim |
| 2 Nível | P2 (A/B) | — | P2 = A → Seção 3; P2 = B → Seção 4 |
| 3 Ramo A | P3 | → Seção 5 | — |
| 4 Ramo B | P4 | — | — |
| 5 Comum | P5 | — | — |

Percursos de Seções possíveis: `1 (P1 = Não) → Fim`; `1 → 2 (P2 = A) → 3 → 5 → Fim`;
`1 → 2 (P2 = B) → 4 → 5 → Fim`.
