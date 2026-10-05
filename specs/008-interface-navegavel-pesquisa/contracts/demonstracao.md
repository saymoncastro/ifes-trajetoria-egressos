# Contrato: adaptador de demonstração

App: `trajetoria.demonstracao`. Atende FR-001 a FR-018. É um **adaptador temporário**:
quando a fronteira real de identidade existir, este app é removido e a interface passa a
obter a Pessoa resolvida de outro lugar, trocando uma importação (FR-005).

> **Nota de revisão pela Feature 018 (registrada em 2026-10-05).** A escolha de Pessoa
> fictícia por lista e o cookie `trajetoria_demonstracao_pessoa` descritos abaixo foram
> substituídos pelo acesso por CPF e data de nascimento fictícios (`/acesso/`, Feature
> 018). Hoje `/demonstracao/` só redireciona para `/acesso/`. O preparo do cenário
> (`manage.py preparar_demonstracao`) também exige as chaves de acesso da 018. A escolha do
> operador fictício (`/demonstracao/operador/`, Feature 010) continua válida.

## Setting

`TRAJETORIA_DEMONSTRACAO: bool` — verdadeiro somente se a variável de ambiente
`TRAJETORIA_DEMONSTRACAO` for exatamente `"1"`. Padrão: falso.

## `trajetoria.demonstracao.middleware.ModoDemonstracaoMiddleware`

Para toda requisição: se `settings.TRAJETORIA_DEMONSTRACAO` é falso → `Http404`.
Nenhuma outra responsabilidade.

## `trajetoria.demonstracao.entrada`

```python
COOKIE = "trajetoria_demonstracao_pessoa"

def pessoa_em_uso(request) -> Pessoa | None
    """Pessoa do cookie assinado, se existir e for da fonte simulada; senão None.
    Nunca grava, nunca levanta exceção por cookie ausente, inválido ou adulterado."""

def pessoas_de_demonstracao() -> QuerySet[Pessoa]
    """Pessoas com fonte "simulada", com Conclusões pré-carregadas, ordem (nome, pk)."""

def usar(response, pessoa: Pessoa) -> None      # grava o cookie (httponly, Lax, sem max_age)
def esquecer(response) -> None                   # apaga o cookie
```

`usar` exige `pessoa.fonte == FonteSimulada.codigo`; caso contrário, `ValueError` (erro
de programação: a view já filtrou).

Única importação da interface a partir deste app: `pessoa_em_uso` (e o processador de
contexto, pela setting `TEMPLATES`). No sentido inverso, só `demonstracao/views.py`
importa da interface, e só `trajetoria.interface.apresentacao.contexto_da_formacao`, para
montar o resumo das formações na entrada de demonstração (o mesmo texto de contexto das
demais telas). Nenhum outro módulo da interface é importado pela demonstração.

## `trajetoria.demonstracao.contexto.demonstracao(request) -> dict`

Processador de contexto. Com o modo de demonstração **desligado**, devolve `{}` sem
ler o cookie nem consultar o banco. Ligado, devolve `{"modo_demonstracao": True,
"pessoa_demonstracao": pessoa_em_uso(request)}`, que alimenta a faixa de demonstração e o
cabeçalho (nome, ligação "Trocar de pessoa" para `/demonstracao/`, botão "Encerrar
demonstração"). `pessoa_em_uso` é memorizada na requisição: view e cabeçalho fazem uma
única consulta.

As páginas de erro (`404.html`, `500.html`, `403_csrf.html`) **não** herdam o template
base e não usam essas variáveis: com o modo desligado, um 404 nunca mostra a faixa de
demonstração nem o nome de uma Pessoa, ainda que o navegador tenha um cookie válido
(FR-001).

## Faixa de demonstração (template base)

Primeiro conteúdo de `<body>` após o atalho "Pular para o conteúdo", em todas as páginas:

> **Ambiente de demonstração.** Todos os dados são fictícios. Não há autenticação: a
> escolha de uma pessoa não comprova identidade.

Região `role="note"` (não `alert`, para não ser reanunciada a cada página), texto escuro
sobre fundo amarelo-claro, identificável sem cor pelo rótulo em negrito (FR-003).

## Comando `manage.py preparar_demonstracao`

Lógica em `trajetoria.demonstracao.cenario.preparar() -> Resumo`.

### Recusas (`CommandError`; nada é alterado)

| Condição | Mensagem |
|----------|----------|
| `TRAJETORIA_DEMONSTRACAO` falso | "O modo de demonstração está desligado. Defina TRAJETORIA_DEMONSTRACAO=1 num ambiente local." |
| Existe `Pessoa` ou `ConclusaoAcademica` com `fonte != "simulada"` | "O banco contém dados que não são da fonte simulada. O cenário de demonstração só é preparado num banco local com dados fictícios." |
| Campanha de demonstração existente fora de EM COLETA | "As Campanhas de demonstração não estão mais em coleta. Recrie o banco local e execute o preparo de novo." |

### Passos (só operações existentes; FR-013)

1. `incorporar_pessoa(FonteSimulada(), id)` para cada Pessoa de
   `trajetoria.fonte_academica.cenarios.PESSOAS` (001; idempotente).
2. `materializar()` (003; idempotente; baseline continua RASCUNHO).
3. Versão de demonstração na Pesquisa da baseline, designação
   `"Demonstração — cópia da referência 2024"`: se não existir,
   `criar_versao_a_partir_de(baseline, designação)` e `publicar` (002).
4. Para cada Campanha abaixo, identificada pelo nome: se não existir, `criar_campanha`,
   `definir_periodo(hoje, hoje + 180 dias)`, `definir_criterios`, `abrir` (004).

| Nome | Critérios |
|------|-----------|
| `Demonstração — coleta ampla` | nenhum (população ampla) |
| `Demonstração — coleta sobreposta` | `unidades=["Vila Velha"]`, `niveis=["Pós-graduação"]` |

*(Revisado pela ADR 0004 — ver `docs/adr/0004-abrangencia-da-campanha-nao-e-foco-de-mobilizacao.md`.)* A "coleta ampla" não tem critério: critério de Campanha é abrangência do instrumento,
não foco de mobilização. A "coleta sobreposta" é o único cenário com abrangência restrita
(instrumento da pós-graduação de Vila Velha). Antes, a "coleta ampla" tinha `ano_minimo=2015`
e seis unidades.

5. Imprime o resumo: para cada Pessoa de demonstração, o nome e a situação de entrada
   calculada **pela 007** (`situacao_de_entrada`) — ex.: "Ana Exemplo — 1 formação com
   pesquisa pendente". Sem identificadores.

### Garantias

- Idempotente: executar de novo não duplica Pessoas, Versão ou Campanhas (FR-018).
- Recusa de operação de domínio durante o preparo (`MaterializacaoRecusada`,
  `OperacaoRejeitada`, `CampanhaRejeitada`) desfaz a transação e vira `CommandError` com a
  orientação de recriar o banco local — nunca traceback.
- Nunca cria Participação ou Resposta (FR-013).
- Nunca roda automaticamente; não é migração (FR-012).
- Reiniciar a demonstração = recriar o banco local (FR-018; 005 FR-017).
