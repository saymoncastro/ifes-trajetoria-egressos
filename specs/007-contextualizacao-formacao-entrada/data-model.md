# Data Model: Contextualização da formação e entrada na pesquisa

**Feature**: [spec.md](spec.md) | **Research**: [research.md](research.md)

**Nenhum modelo novo. Nenhuma migração. Nenhuma coluna, índice, CHECK ou tabela.** Os
modelos das Features 001 a 006 são lidos sem alteração; a única gravação possível é a
Participação criada por `iniciar_participacao` (005). Tudo o mais é **valor derivado**,
recalculado a cada chamada e nunca gravado (R2).

```text
academico.Pessoa (001) ──1:N── academico.ConclusaoAcademica (001)        leitura
                                        │
                                        │ campanhas_em_coleta_para(conclusao, agora)   (004)
                                        ▼
                                  0, 1 ou ≥2 campanha.Campanha                leitura
                                        │ (só com exatamente 1)
                                        ▼
                     participacao.Participacao do par, se existir (005/006)   leitura
                                        │ concluida_em (006)
                                        ▼
       Formacao ─► SituacaoDeEntrada ─► entrar() ─► iniciar_participacao (005)  única escrita
       (valores derivados, não persistidos)
```

## Modelos consumidos (inalterados)

| Modelo | Feature | O que a 007 lê | O que a 007 grava |
|--------|---------|----------------|-------------------|
| `Pessoa` | 001 | identidade (`pk`) | nada |
| `ConclusaoAcademica` | 001 | `pessoa`, `curso`, `unidade`, `nivel`, `modalidade`, `forma_oferta`, `ano_conclusao`, `data_conclusao` (`None` = não informado); ordem padrão `(ano_conclusao, id)`, sem significado | nada |
| `Campanha` | 004 | as devolvidas por `campanhas_em_coleta_para` | nada |
| `Participacao` | 005/006 | `campanha`, `conclusao`, `concluida_em` | **só via `iniciar_participacao`** |
| `Resposta`, `RespostaOpcao` | 005 | nada | nada |

## Valores derivados (não persistidos)

Imutáveis (`frozen`), no padrão de `Elegibilidade` (004) e `SituacaoDaJornada` (006). Não
são entidades nem ViewModel. Contrato completo em
[contracts/entrada.md](contracts/entrada.md).

### `SituacaoDaFormacao` (enum)

| Valor | Campanhas aplicáveis | Participação do par | `pendente` |
|-------|---------------------|---------------------|:----------:|
| `SEM_PESQUISA` | 0 | não consultada | não |
| `DISPONIVEL_PARA_INICIAR` | 1 | inexistente | **sim** |
| `DISPONIVEL_PARA_RETOMAR` | 1 | `concluida_em` nulo | **sim** |
| `JA_CONCLUIDA` | 1 | `concluida_em` preenchido | não |
| `AMBIGUIDADE_OPERACIONAL` | ≥ 2 | não consultada (nunca desempata) | não |

Propriedade `pendente` (no próprio enum): verdadeira só para as duas situações
"disponível". Pesquisa aplicável = todas menos `SEM_PESQUISA`.

### `Formacao`

| Campo | Tipo | Regra |
|-------|------|-------|
| `conclusao` | `ConclusaoAcademica` | A própria instância da 001; contexto lido dela, nunca copiado (FR-007, FR-040) |
| `situacao` | `SituacaoDaFormacao` | R5 |
| `campanhas` | `tuple[Campanha, ...]` | Campanhas aplicáveis, na ordem `(inicio, id)` da 004, sem preferência; vazia em `SEM_PESQUISA`, todas em `AMBIGUIDADE_OPERACIONAL` |
| `participacao` | `Participacao \| None` | Presente só em `DISPONIVEL_PARA_RETOMAR` e `JA_CONCLUIDA` |

Propriedade: `campanha` (a única Campanha aplicável, ou `None` fora de 1), consumida por
`entrar` para chamar a 005.

**Coerência** (garantida pela construção, verificada em teste):
`len(campanhas) == 0` ⇔ `SEM_PESQUISA`; `≥ 2` ⇔ `AMBIGUIDADE_OPERACIONAL`, com
`participacao is None`; `1` ⇔ um dos três estados da Participação.

### `ResolucaoDaEntrada` (enum)

| Valor | Condição (R5, nesta ordem) |
|-------|----------------------------|
| `SEM_FORMACAO` | zero formações |
| `ENTRADA_RESOLVIDA` | exatamente 1 formação pendente |
| `SELECAO_NECESSARIA` | 2 ou mais formações pendentes |
| `SEM_PESQUISA` | formações existem, nenhuma com Campanha aplicável |
| `SEM_ENTRADA_PENDENTE` | pesquisa aplicável existe, zero pendentes — todas concluídas, só ambíguas, concluídas e ambíguas, com ou sem outras sem pesquisa |

Não há valor global de ambiguidade nem valores para distinguir as combinações de
`SEM_ENTRADA_PENDENTE`: o detalhe está em cada `Formacao`.

### `SituacaoDeEntrada`

| Campo | Tipo | Regra |
|-------|------|-------|
| `formacoes` | `tuple[Formacao, ...]` | **Todas** as Conclusões da Pessoa, na ordem da 001, qualquer que seja a situação (FR-017) |
| `resolucao` | `ResolucaoDaEntrada` | Derivada só de `formacoes` |

Propriedade: `pendentes` (formações pendentes, na mesma ordem). Em `ENTRADA_RESOLVIDA`, a
formação resolvida é `pendentes[0]`; em `SELECAO_NECESSARIA`, `pendentes` são as
alternativas.

### `Entrada`

| Campo | Tipo | Regra |
|-------|------|-------|
| `situacao` | `SituacaoDeEntrada` | Reavaliada no momento da entrada (FR-032) |
| `participacao` | `Participacao \| None` | A Participação do par; `None` ⇔ nada a iniciar ou retomar |
| `criada` | `bool` | Verdadeiro só quando a 005 devolveu `CRIADA` |

Indicação exigida por FR-034, sem enum próprio:

| Indicação | Condição |
|-----------|----------|
| iniciada | `criada` |
| em rascunho | `participacao` presente, não `criada`, `concluida_em` nulo |
| concluída | `participacao.concluida_em` preenchido |
| não realizada | `participacao is None`; o motivo está em `situacao.resolucao` (sem formação informada) ou na situação da formação informada |

### `FormacaoDeOutraPessoa` (exceção)

Rejeição de domínio: a formação informada não é Conclusão da Pessoa — de outra Pessoa ou
inexistente, casos indistinguíveis de propósito. Lançada antes de qualquer chamada à
005. Sem atributos nem identificadores da Conclusão ou da
Pessoa alheia na mensagem (FR-044, FR-045).

### Simplificações por YAGNI (em relação ao primeiro desenho do plan)

| Removido | Por quê |
|----------|---------|
| `DesfechoDaEntrada` (enum de 4 valores) | `EM_RASCUNHO`/`CONCLUIDA` repetiam `participacao.concluida_em`; `NAO_REALIZADA` repetia `participacao is None`. Resta só o que não é derivável: `criada` |
| `Entrada.formacao` | A formação usada é `situacao.pendentes[0]` (resolvida) ou a que o chamador informou; a Participação já aponta a Conclusão |
| `SituacaoDeEntrada.pessoa` e `.momento` | O chamador já os tem; nenhum consumidor |
| `SituacaoDeEntrada.resolvida` | É `pendentes[0]` em `ENTRADA_RESOLVIDA` |
| `Formacao.entrada_pendente` | Depende só da situação: virou `SituacaoDaFormacao.pendente` |

## Invariantes e onde são garantidos

| Invariante | Garantia |
|------------|----------|
| Contexto é sempre uma Conclusão (Princípio I) | `Formacao.conclusao`; a entrada usa a Conclusão da formação |
| Só Conclusões da Pessoa | Consulta filtra por `pessoa`; formação alheia → `FormacaoDeOutraPessoa` |
| Pessoa sem campus/curso | Nada lido nem gravado na Pessoa além do `pk` |
| Elegibilidade e estado vêm da 004 | Só `campanhas_em_coleta_para`; nenhum filtro copiado |
| Participação vem da 005 | Escrita só por `iniciar_participacao` |
| Jornada vem da 006 | `entrada.py` não usa `percurso` nem `situacao_da_jornada` (regra de desenho, conferida na revisão — T025); por comportamento: nenhuma Resposta nem `concluida_em` gravados pela entrada (T013, T023) |
| Concluída não é alternativa | R5: só `SituacaoDaFormacao.pendente` conta |
| Ambiguidade não é desempatada nem global | R11: Participação não consultada; não entra na contagem |
| Sem prioridade | Ordem é a da 001/004; nenhuma ordenação nova |
| Institucional ≠ declarado | Nenhuma `Resposta` criada; nada copiado |
| Nada persistido | Zero modelos e migrações; consulta sem escrita |

## Fora do modelo (deliberadamente)

EntrySession, ContextSession, Context, Selection, EnrollmentChoice, EnrollmentOption,
EligibleFormation, EligibleCampaignMembership, CampaignAssignment, PortalUser, Usuario,
Conta, Credential, Login, Identity, IdentityProvider, AuthenticationProvider,
PersonResolver, IdentityResolver, PersonMatcher, workflow; colunas de "Campanha
escolhida", "formação atual", "situação de entrada" ou rótulo de formação; cache,
snapshot ou tabela auxiliar de aplicabilidade.
