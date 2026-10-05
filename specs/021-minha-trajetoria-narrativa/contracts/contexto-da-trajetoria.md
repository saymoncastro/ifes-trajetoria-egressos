# Contrato: capacidade de contexto da trajetória (P2)

Esta é uma fronteira **separada** da `FonteAcademica` (E5a, FR-046, FR-055, FR-071). As
estruturas estão detalhadas em
[data-model.md §1](../data-model.md#1-capacidade-de-contexto-da-trajetória-p2--trajetoriafonte_academicacontexto_da_trajetoriapy).

## Por que separada

`FonteAcademica.obter_pessoa()` e `PessoaEncontrada` servem à incorporação (001), ao
material de identidade da 018 e à validação pelo acervo da 019. O enriquecimento da
narrativa não pode:

- pesar nem falhar no caminho de identidade;
- obrigar fontes fundamentais, como o acervo histórico, a conhecer a 021.

```text
VIEW / consulta real (pode ser UMA consulta larga)
  cpf · nascimento · pessoa · conclusão · ingresso · agregados
          │
          └─ adaptador ─┬─► FonteAcademica.obter_pessoa()          → identidade + Conclusões
                        └─► FonteDeContextoDaTrajetoria.obter_contexto(ids) → complementos + agregados
```

## O que não muda (com teste)

- `trajetoria/fonte_academica/contrato.py` inteiro: `ConclusaoNaFonte`,
  `CAMPOS_DE_CONTEXTO`, `PessoaEncontrada` e o protocolo `FonteAcademica`.
- `FonteSimulada` e `FonteAcervoHistorico`.
- `incorporacao.py`, `acesso` e `declaracao`. Nenhum deles importa a capacidade, o app
  `contexto_trajetoria` nem o app `narrativa`.

## Operação

```text
FonteDeContextoDaTrajetoria
  codigo: str                                   # igual ao código da fonte das Conclusões
  obter_contexto(ids_externos_conclusoes) -> ContextoDaTrajetoriaNaFonte
      complementos: só para ids pedidos; um por id
      agregados:    recortes (curso+unidade+ano; unidade+ano) das conclusões pedidas
  lança ContextoIndisponivel quando não pode responder
```

## Obrigações de toda implementação

1. **Complemento:** o ingresso é o da matrícula que resultou naquela Conclusão.
2. **Agregado:**
   - conta Conclusões reconhecidas pela **mesma regra** da `FonteAcademica` do mesmo
     código, nunca pessoas;
   - usa o ano civil de conclusão;
   - traz o `apurado_em` real.
3. **View larga:** o adaptador separa as colunas e não repete chaves na resposta. Valores
   diferentes para a mesma chave e a mesma apuração, dentro da view, são erro do adaptador,
   que lança `ContextoIndisponivel` em vez de escolher um valor.
4. **Indisponibilidade:** nunca equivale a "sem complemento" ou "sem agregado".

## Carga (`contexto_trajetoria/carga.py: carregar_contexto`)

| Caso | Efeito |
|---|---|
| Pessoa sem Conclusões daquela fonte | `SEM_CONCLUSOES`; nenhuma chamada à fonte |
| `ContextoIndisponivel` | `INDISPONIVEL`; nada gravado; exceção não propagada; Pessoa e Conclusões intactas |
| Complemento novo | Cria `ComplementoDaConclusao` |
| Complemento igual ao gravado | Nada |
| Complemento diferente | Divergência só em log (fonte, id externo da Conclusão, campos); nada muda |
| Agregado com chave nova | Cria `ContextoInstitucionalAgregado` |
| Agregado com chave existente e mesmo valor | Nada (deduplicação) |
| Agregado com chave existente e valor diferente | Erro de fonte só em log (fonte, métrica, recorte); nada gravado |

**Quem chama:**

- o preparo da demonstração, depois da incorporação, num *savepoint* próprio por Pessoa,
  sem interromper o preparo em caso de falha;
- no futuro, o gatilho real, que segue a 001/DP-006.

**Nunca chama:** a incorporação, o acesso, a declaração nem a view da narrativa.

## Fonte simulada (`fonte_academica/contexto_simulado.py: ContextoSimulado`)

Os valores fictícios ficam em `cenarios.py` e no `cenarios-simulados.md` da 001 (FR-064):

| Dado | Valor fictício |
|---|---|
| Complemento `SIM-C-0001` (Ana, TADS) | ingresso 2019 |
| Demais conclusões | sem complemento |
| Métrica 1 | TADS · Serra · 2022 = 27, apurado em 2026-01-31 |
| Métrica 2 | Serra · 2022 = 812, apurado em 2026-01-31 |
| Demais recortes | sem agregado |

`ContextoSimulado(indisponivel=True)` serve ao teste de isolamento (SC-014). Os casos
negativos ficam só em fontes de teste parametrizadas.
