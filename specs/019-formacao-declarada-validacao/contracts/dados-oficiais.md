# Contrato: efeito nos dados oficiais (007, 011, 012, 013)

Todas as superfícies usam `participacoes_oficiais()` (R4). Nenhuma reimplementa o filtro.

```text
oficial = âncora institucional
        OU declarada + CONFIRMADA + NOT fora_da_abrangencia_na_validacao + NOT conflito pendente
```

Na 019, "conflito pendente" equivale a `conflito_detectado_na_validacao`, porque ainda não
existe resolução (DP-1907).

## 007 — entrada da Pessoa

A Participação do par `(Campanha, Conclusão)` é a oficial com essa Conclusão efetiva:
- uma declarada **validada** conta como "já respondida" ou "em andamento";
- pendente, não confirmada, fora da abrangência e em conflito **nunca** aparecem
  (FR-036).

## 011 — acompanhamento

| Indicador | Antes | Depois |
| --- | --- | --- |
| Elegíveis atuais | População da 004 | Inalterado (FR-023) |
| Iniciadas, concluídas, em andamento, taxas | Todas as Participações da Campanha | Só as oficiais |
| Escopo de unidade e recortes | `conclusao__<campo>` | `atributo_efetivo(<campo>)` |
| **Validações de formação: N na fila** | — | Agregado, no escopo pela unidade declarada, com link para a fila (FR-101) |

Nada nominal é exibido na 011. As FR-080 a FR-084 da 011 continuam valendo.

## 012 — snapshot

**Universo.** População elegível no momento ∪ Conclusões efetivas das Participações
oficiais.

**Registro.** Ganha `participacao` e `origem_formacao`, congelados na captura (R14).

**Integridade (FR-053 d).** Toda Participação **oficial** da Campanha tem registro, e
nenhuma não oficial tem.

**Leitura.** `linhas_do_dataset` e os indicadores passam a usar `registro.participacao`.
Nunca procuram a Participação por `(campanha, conclusao_id)` depois da captura.

**Reprodutibilidade.**
- Um snapshot anterior a uma validação permanece idêntico (FR-103).
- A captura seguinte inclui a declarada validada.

**Pendências.** Nunca entram em snapshot.

## 013 — exportação

**Coluna base nova `origem_formacao`.**

| Atributo | Valor |
| --- | --- |
| Proveniência | `derivado` |
| Tipo | `texto` |
| Valores | `institucional`, `declarada_validada_fonte_digital`, `declarada_validada_acervo`; vazio quando não há Participação |
| Dicionário | "Como a Participação chegou à Conclusão Acadêmica: âncora institucional ou declaração do egresso validada depois pela fonte digital ou pelo acervo histórico. O contexto acadêmico desta linha é sempre o da Conclusão, dado institucional." |

**Contrato.** `VERSAO_CONTRATO` passa de 1 a 2 (013 FR-065).

**Leitura de FR-021.** A coluna varia por construção. Ser constante numa Campanha sem
declarações não a torna coluna constante no sentido de FR-021.

**Nunca exportados.** Nome declarado, valores da declaração, HMACs, CPF, data, dados da
decisão (operador, momento) e a trilha de acesso (FR-106).

**Metadados.** As contagens continuam iguais às da 012 (013 FR-013).
