# Data Model: Minha Trajetória — narrativa visual personalizada

Fase 1. O modelo tem três camadas:

1. o contrato da capacidade de contexto da trajetória (P2, puro, separado da
   `FonteAcademica`);
2. a persistência (P2, app `contexto_trajetoria`);
3. a apresentação (não persistida).

Os nomes são propostos. As validações vêm da spec.

**Escopo das mudanças:**

- **P1** não cria nem altera nenhuma tabela.
- **P2** cria duas tabelas num app novo, com uma migração aditiva. Nenhuma tabela existente
  é alterada.
- **Em nenhuma fase** mudam `ConclusaoNaFonte`, `PessoaEncontrada`, `CAMPOS_DE_CONTEXTO`
  ou o protocolo `FonteAcademica` (FR-071).

---

## 1. Capacidade de contexto da trajetória (P2) — `trajetoria/fonte_academica/contexto_da_trajetoria.py`

Python puro, sem Django. Módulo separado de `contrato.py`, que não muda.

### 1.1 `ComplementoNaFonte` (congelado)

| Campo | Tipo | Regra |
|---|---|---|
| `id_externo_conclusao` | `str` | Não vazio; DEVE estar entre os ids pedidos |
| `ano_ingresso` | `int` | Obrigatório |
| `data_ingresso` | `date \| None` | Se presente, `data_ingresso.year == ano_ingresso` |

**Semântica:** o ingresso na matrícula que resultou nesta Conclusão. Reingresso e
transferência são DP-2104.

### 1.2 `MetricaAgregada` (enumeração fechada)

| Valor | Recorte | Significado (FR-053) |
|---|---|---|
| `CONCLUSOES_CURSO_UNIDADE_ANO` | curso + unidade + ano | Conclusões que a fonte reconhece daquele curso, naquela unidade, com aquele ano de conclusão |
| `CONCLUSOES_UNIDADE_ANO` | unidade + ano | Mesma regra, todos os cursos da unidade |

### 1.3 `AgregadoNaFonte` (congelado)

| Campo | Tipo | Regra |
|---|---|---|
| `metrica` | `MetricaAgregada` | — |
| `unidade` | `str` | Não vazio |
| `ano` | `int` | Ano civil de conclusão |
| `valor` | `int` | `>= 0` |
| `apurado_em` | `date` | Referência temporal da apuração, informada pela fonte |
| `curso` | `str \| None` | Obrigatório na métrica 1; `None` na métrica 2 |

### 1.4 `ContextoDaTrajetoriaNaFonte` (congelado)

| Campo | Tipo | Regra |
|---|---|---|
| `complementos` | `tuple[ComplementoNaFonte, ...]` | Sem repetir `id_externo_conclusao` |
| `agregados` | `tuple[AgregadoNaFonte, ...]` | Sem repetir a chave (métrica, curso, unidade, ano, apurado_em) |

### 1.5 `FonteDeContextoDaTrajetoria` (Protocol) e `ContextoIndisponivel`

```text
codigo: str                      # o mesmo código da fonte das Conclusões
obter_contexto(ids_externos_conclusoes: tuple[str, ...]) -> ContextoDaTrajetoriaNaFonte
    # pode lançar ContextoIndisponivel; nunca equivale a "sem complemento" ou "sem agregado"
```

- Implementação simulada: `fonte_academica/contexto_simulado.py: ContextoSimulado`.
- A `FonteSimulada` não muda.

---

## 2. Persistência (P2) — app `trajetoria/contexto_trajetoria/`

Nenhum app da 001, 018 ou 019 importa este app (FR-071; research R1 e R13).

### 2.1 `ComplementoDaConclusao`

| Campo | Tipo | Regra |
|---|---|---|
| `conclusao` | `OneToOne → academico.ConclusaoAcademica`, `PROTECT`, PK | Um por Conclusão; a fonte é a da Conclusão |
| `ano_ingresso` | `PositiveSmallIntegerField` | Obrigatório |
| `data_ingresso` | `DateField`, nulo | Coerente com o ano |
| `obtido_em` | `DateTimeField(auto_now_add)` | Proveniência |

- **Constraint:** `CheckConstraint` de coerência entre ano e data.
- **Ciclo de vida:**
  - criado por `carregar_contexto` quando ainda não existe;
  - **nunca atualizado nem removido**;
  - valor diferente gera divergência só em log (FR-048).

### 2.2 `ContextoInstitucionalAgregado`

| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID | — |
| `fonte` | `TextField` | Não vazio |
| `metrica` | `TextField(choices)` | — |
| `curso` | `TextField`, nulo | Conforme a métrica |
| `unidade` | `TextField` | Não vazio |
| `ano` | `PositiveSmallIntegerField` | — |
| `valor` | `PositiveIntegerField` | — |
| `apurado_em` | `DateField` | Informado pela fonte |
| `obtido_em` | `DateTimeField(auto_now_add)` | Proveniência |

- **Constraints:**
  - `UniqueConstraint(fonte, metrica, curso, unidade, ano, apurado_em, nulls_distinct=False)`;
  - `CheckConstraint` de curso conforme a métrica;
  - textos não vazios.
- **Ciclo de vida:**
  - `get_or_create` na chave;
  - mesma chave com valor diferente é erro de fonte, só em log, sem gravar;
  - **nunca atualizado nem removido**.
- **Sem FK** para Pessoa ou Conclusão.

### 2.3 Carga (`contexto_trajetoria/carga.py`)

| Entrada | `fonte_de_contexto: FonteDeContextoDaTrajetoria`, `pessoa: Pessoa` |
|---|---|
| Saída | `ResultadoDaCarga(situacao: CARREGADO \| INDISPONIVEL \| SEM_CONCLUSOES, complementos_criados, agregados_criados, sinais)` — `sinais` (`Sinal`) registra divergências da fonte para o log, sem dados pessoais |
| Transação | A consulta à fonte acontece fora da transação. A gravação acontece numa transação própria. Os logs saem depois do commit |
| Garantias | Nunca lança `ContextoIndisponivel`; nunca altera Pessoa nem Conclusão; nunca é chamada por incorporação, acesso, declaração ou view da narrativa |

### 2.4 Migração

- `contexto_trajetoria/0001_initial.py`: `CreateModel` × 2, dependendo de
  `academico/0001`.
- É aditiva e reversível.

---

## 3. Apresentação (não persistida) — `trajetoria/narrativa/contrato.py`

A forma serializada está em [contracts/narrativa.md](contracts/narrativa.md).

### 3.1 `EntradaDaNarrativa` (construída por `narrativa/consultas.py`)

| Campo | Conteúdo |
|---|---|
| `nome` | `str \| None` (`Pessoa.nome`) |
| `formacoes` | tupla de `FatoDaFormacao`, na ordem (`ano_conclusao`, `id`) |
| `agregados` | tupla de `ContextoSelecionado` (já passou por FR-058 a FR-060) |
| `referencia` | `date` |
| `demonstracao` | `bool` |

`FatoDaFormacao` traz os sete atributos como valores e o `ingresso` opcional. Não traz `id`,
`fonte`, `id_externo` nem `incorporado_em`.

### 3.2 `TrajetoriaNarrativa`

| Campo | Conteúdo | Origem |
|---|---|---|
| `versao_contrato` | `1` | — |
| `referencia` | data dos derivados | — |
| `identidade` | nome opcional | institucional |
| `formacoes` | atributos presentes + `relacao` + `ingresso` opcionais | institucional |
| `marcos` | vazio (P3) | — |
| `derivados` | `formacoes_registradas`, `tempo_desde_conclusao`, `primeira_formacao` | derivado |
| `contextos_agregados` | métrica, recorte, valor, apuração | agregado |
| `secoes` | seções do FR-026 presentes, com frases do catálogo | — |
| `compartilhavel` | subconjunto do FR-033 com linhas quebradas, `formacoes_omitidas`, `nome_disponivel` e no máximo um par de agregados (o da primeira formação com agregado) | — |

**Regras:**

- Função pura.
- O nome não entra no `compartilhavel`. A rota o acrescenta só com `nome=1` (FR-034).
- Uma seção sem frase não existe em `secoes`.

### 3.3 Card (artefato)

- `card_svg(compartilhavel, tema=TEMA_CARD, nome=None, demonstracao=True) -> str`:
  1080 × 1920, área segura (research R10); `demonstracao` controla a indicação de dados
  fictícios (FR-037).
- `png_de(svg) -> bytes | None`: rasterização isolada (research R11).
- O PNG é o artefato principal. Nada é gravado.

---

## 4. Relações e fronteiras

```text
FonteAcademica (001, inalterada) ── obter_pessoa ──► Pessoa 1──* ConclusaoAcademica
     ▲  usada por incorporação (001), acesso (018), declaração (019)

FonteDeContextoDaTrajetoria (P2, separada) ── obter_contexto(ids) ──► carregar_contexto
     ▲  usada só pelo preparo da demonstração (e futuro gatilho, 001/DP-006)
                                        │
                                        ├──► ComplementoDaConclusao  0..1 ── 1 ConclusaoAcademica
                                        └──► ContextoInstitucionalAgregado (sem FK; mesma fonte + recorte)

narrativa ── só lê ──► Pessoa, ConclusaoAcademica, ComplementoDaConclusao,
                        ContextoInstitucionalAgregado; Participacao só como gatilho (exists)
Resposta, FormacaoDeclarada, snapshot (012), exportação (013) ── nunca lidos pela 021
```
