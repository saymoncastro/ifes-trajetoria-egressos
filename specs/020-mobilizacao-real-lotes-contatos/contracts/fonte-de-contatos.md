# Contrato — Fonte de contatos e carga

**Módulo**: `trajetoria/fonte_academica/contatos_da_fonte.py`. Python puro: não importa
Django nem fonte concreta.

## Fronteira

```text
class ContatosIndisponiveis(Exception)
    A fonte não pôde responder. Nunca equivale a "sem e-mail".

class FonteDeContatos(Protocol):
    codigo: str
    def obter_emails(self, id_externo_pessoa: str) -> tuple[str, ...]
        # Zero ou mais e-mails, na ordem de preferência que o adaptador declara.
        # Pode levantar ContatosIndisponiveis.
```

**Regras**:

- **Separação.** É distinta de `FonteAcademica`. `obter_pessoa()`, `PessoaEncontrada`,
  `ConclusaoNaFonte` e `CAMPOS_DE_CONTEXTO` não mudam.
- **Quem não importa.** `academico`, `acesso`, `declaracao`, `narrativa`, `video` e
  `contexto_trajetoria` não importam este módulo nem `contato`.
- **Responsabilidade do adaptador.** A peculiaridade da fonte real (campos, tipos,
  histórico) fica no adaptador. Ele pode ler a mesma view larga dos outros contratos.
- **Telefone.** O contrato não tem telefone (E1).

## Adaptador simulado

**Módulo**: `fonte_academica/contatos_simulados.py`, `ContatosSimulados`, com `codigo`
igual ao da `FonteSimulada`.

- Os dados vêm de `cenarios.EMAILS: dict[str, tuple[str, ...]]`, só com o domínio
  `example.invalid`:
  - SIM-P-0001…0011, como na 016;
  - SIM-P-0010 sem e-mail (tupla vazia);
  - ao menos uma Pessoa com dois e-mails, para exercitar a ordem.
- Pessoa não mapeada devolve `()`.
- O acervo histórico não tem adaptador de contatos.

## Carga

**Módulo**: `trajetoria/contato/carga.py`.

```text
carregar_contatos(fonte: FonteDeContatos, pessoa: Pessoa, *, agora) -> ResultadoDaCarga
SituacaoDaCarga = CARREGADO | INALTERADO | SEM_EMAIL | INDISPONIVEL
ResultadoDaCarga(situacao, gravados: int, ignorados_invalidos: int)
```

1. Consulta a fonte **fora** da transação. `ContatosIndisponiveis` resulta em
   `INDISPONIVEL`: não grava nada e registra log só com o código da fonte.
2. Normaliza cada valor (`contato.endereco.normalizar_email`). Os inválidos são
   descartados e contados, sem log do valor.
3. Lista resultante vazia: `SEM_EMAIL`. Não grava nada e não apaga nada.
4. Igual, em ordem, à última observação gravada daquela Pessoa e fonte: `INALTERADO`.
5. Caso contrário, grava uma observação: uma linha por posição, todas com o mesmo
   `obtido_em = agora`, numa transação. Resultado `CARREGADO`.

**Garantias**:

- A carga nunca altera `Pessoa`, nunca apaga contato e nunca é chamada por incorporação,
  acesso, declaração ou narrativa.
- O preparo da demonstração chama a carga para cada Pessoa simulada, depois de
  `_carregar_contextos`, num *savepoint* por Pessoa. Exceção é logada sem dado pessoal e
  não interrompe as demais Pessoas.

## Gate A

O adaptador real só é escrito depois do profiling da auditoria (§18) e de DP-1601.
