# Quickstart — validação da Feature 020 (somente demonstração)

Roteiro inteiramente fictício. O envio real **não é habilitado** (Gates A e B; DP-2010).
Nenhuma conta real e nenhum endereço fora de `example.invalid`.

Detalhes: [data-model](data-model.md) · [rotas](contracts/rotas.md) ·
[transporte](contracts/transporte.md) · [fonte de contatos](contracts/fonte-de-contatos.md).

## 1. Preparo

```bash
createdb trajetoria_demo
```

```bash
uv sync --extra dev
```

```bash
PGDATABASE=trajetoria_demo uv run python manage.py migrate
```

Defina as chaves de demonstração da 018 e da 019, como no `.env.example`, e prepare a
demonstração:

```bash
PGDATABASE=trajetoria_demo TRAJETORIA_DEMONSTRACAO=1 uv run python manage.py preparar_demonstracao
```

Esperado: além do preparo atual, os contatos fictícios são carregados depois da
incorporação. Repetir o preparo não grava novas observações (carga idempotente).

## 2. Caixa local

```bash
env -i "$(command -v mailpit)" --listen 127.0.0.1:8025 --smtp 127.0.0.1:1025
```

Sem relay, encaminhamento ou liberação, como na 016.

## 3. Servidor

Use a mesma configuração SMTP local da 016 (`specs/016-…/quickstart.md`, §3), com
`TRAJETORIA_ENVIO_REAL` **não definida**.

## 4. Cenários manuais

1. **Prévia e confirmação.**
   - Como operador A (CPAEG), abra uma Campanha em coleta → "Lotes de mobilização".
   - Filtre por "Serra" e confira as contagens (Pessoas, com e sem contato, excluídas).
   - Mude o filtro: a prévia muda e nada é gravado.
   - Confirme com um nome.
2. **Grão Pessoa.** Uma Pessoa com duas Conclusões no recorte conta uma vez.
3. **Duplicidade.**
   - Confirme um segundo Lote sobreposto: os membros do primeiro aparecem como "já
     mobilizados nesta Campanha".
   - A Pessoa sem contato (SIM-P-0010) pode entrar de novo.
4. **Envio.**
   - Envie o Lote e confira no Mailpit:
     - uma mensagem por membro com contato;
     - texto e HTML;
     - link `/acesso/` sem identificador;
     - nenhum CPF ou id.
   - O detalhe mostra submetidos, falhas e sem contato, com o aviso de que aceite não é
     entrega.
5. **Retomada.**
   - Com `TRAJETORIA_LOTE_ENVIO_POR_ACAO=1`, cada ação envia um membro, e "Continuar envio"
     segue sem repetir ninguém.
   - Pare o Mailpit no meio: os membros seguintes ficam em falha de transporte, sem retry.
6. **Campanha em preparação ou encerrada.** Confirmar é permitido em preparação. Enviar é
   recusado nos dois casos.
7. **CSAEG (operador B, Vitória).**
   - O filtro de unidade é obrigatório e limitado a Vitória.
   - A operadora não vê Lotes institucionais nem de outras unidades.
8. **Egresso.**
   - Entre pelo `/acesso/` com uma Pessoa fictícia e conclua uma pesquisa.
   - Na conclusão, "Ver minha trajetória no Ifes" é a primeira ação, e o convite de
     e-mail vem abaixo.
   - Informe `novo@example.invalid`:
     - a página não mostra nenhum e-mail guardado;
     - um Lote confirmado **depois** usa o novo endereço;
     - um Lote confirmado **antes** mantém o antigo.
9. **Declarante (019).** A conclusão não mostra o convite.
10. **Narrativa.** `/minha-trajetoria/` e o card são iguais com e sem e-mail informado.

## 5. Suíte

```bash
uv run pytest tests/contato tests/mobilizacao tests/comunicacao tests/governanca tests/acompanhamento tests/interface tests/narrativa tests/acesso
```

```bash
uv run pytest
```

```bash
uv run ruff check .
```

```bash
uv run python manage.py makemigrations --check --dry-run
```

Esperado: tudo verde. A suíte cobre:

- concorrência entre Lotes;
- retomada após interrupção;
- idempotência da carga;
- isolamento de contatos em relação ao acesso (018) e à narrativa e ao vídeo (021/022);
- ausência de endereço em logs, sessão, cache, URLs, telas, 011, 012 e 013;
- recusa de cada exigência do modo real.

Os testes de concorrência usam transações reais (`transaction=True`).
