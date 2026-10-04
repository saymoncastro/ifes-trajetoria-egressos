# Quickstart — validar a Feature 019

Roteiro de validação. Detalhes em [plan.md](plan.md), [rotas](contracts/rotas.md),
[operações](contracts/operacoes.md), [fonte de acervo](contracts/fonte-acervo.md),
[dados oficiais](contracts/dados-oficiais.md) e [data-model](data-model.md). Só dados
fictícios.

## Pré-requisitos

Use o mesmo ambiente da [018/quickstart](../018-identificacao-acesso-egresso/quickstart.md):
Python 3.13, uv, PostgreSQL local e as duas chaves de acesso exportadas. As chaves do
preparo e as do servidor precisam ser as mesmas.

**Duas chaves novas, uma por finalidade (R5).** São chaves Fernet, sem valor padrão,
geradas localmente e nunca versionadas. Precisam ser diferentes entre si e das demais.

A chave A serve aos selos transitórios:

```bash
export TRAJETORIA_CHAVE_SELO_DECLARACAO="$(uv run python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')"
```

A chave B serve aos dados para consulta ao acervo:

```bash
export TRAJETORIA_CHAVE_CONSULTA_ACERVO="$(uv run python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')"
```

**Banco novo e isolado.**

```bash
createdb trajetoria_demo_019
```

```bash
uv sync --extra dev && PGDATABASE=trajetoria_demo_019 uv run python manage.py migrate
```

```bash
PGDATABASE=trajetoria_demo_019 TRAJETORIA_DEMONSTRACAO=1 uv run python manage.py preparar_demonstracao
```

```bash
PGDATABASE=trajetoria_demo_019 TRAJETORIA_DEMONSTRACAO=1 uv run python manage.py runserver 127.0.0.1:8000
```

## Verificação automática

```bash
uv run pytest tests/declaracao
```

```bash
uv run pytest
```

```bash
uv run ruff check .
```

## Roteiro manual

As credenciais fictícias aparecem no painel da demonstração em `/acesso/`.

### 1. Declarar e responder (US1, US2)

1. Em `/acesso/`, informe o **par inexistente** do painel. Deve aparecer "Conferir os
   dados" e, depois dele, "Informar minha formação".
2. Escolha "Informar minha formação". Informe nome, unidade, nível, curso e ano e
   continue. Deve aparecer "Formação informada por você: …".
3. Comece e conclua a pesquisa. Ao final deve aparecer "Sua resposta foi registrada. A
   formação informada passará por verificação institucional."
4. No banco:
   - nenhuma Pessoa ou Conclusão nova;
   - nenhum CPF nem data em claro;
   - `DadosConsultaAcervo` com um token.
5. Repita o passo 1 com outro par e desista na tela de formação. Nada deve ter sido
   gravado.

### 2. Quarentena (US2)

Como operador A (CPAEG), abra o acompanhamento da Campanha.
- As taxas não mudaram.
- Aparece "Validações de formação: 1 na fila".

### 3. Validar pela fonte digital (US3)

1. Declare usando o par da **Pessoa sem data de nascimento** (018). Para isso, escolha
   uma data qualquer e conclua.
2. Em `/validacoes-formacao/`, abra a declaração. A Conclusão da Pessoa aparece como
   **candidata**.
3. Acione "Mostrar dados para consulta ao acervo". CPF e data aparecem, e uma linha de
   acesso é registrada.
4. Confirme pela candidata. A situação passa a `DECLARADA_VALIDADA`.
5. Encerre a Campanha, capture um snapshot e exporte. A linha tem
   `origem_formacao = declarada_validada_fonte_digital`.
6. Declare com o par da **Pessoa presente na fonte e não importada**. Confirme pela
   referência na fonte. A Pessoa e a Conclusão são incorporadas e vinculadas.

### 4. Validar pelo acervo (US4)

1. Declare uma formação antiga com o par inexistente.
2. Na validação, escolha "acervo histórico". Os campos aparecem vazios, com o declarado ao
   lado.
3. Registre a referência "Livro 3, folha 12" com curso e ano **diferentes** do declarado.
4. Confira:
   - a Conclusão tem `fonte = acervo_historico`;
   - a tela mostra "confirmada com dados diferentes";
   - a declaração continua intacta.

### 5. Não confirmar, fora da abrangência e conflito (US5)

1. Registre "Formação não confirmada" numa declaração. Ela continua preservada e fora dos
   dados oficiais.
2. Na "coleta sobreposta" (pós-graduação, Vila Velha), declare uma pós-graduação em Vila
   Velha. Valide pelo acervo como graduação. O resultado é `DECLARADA_FORA_DA_ABRANGENCIA`.
3. Com uma Pessoa importada que já respondeu na Campanha, declare com a data errada e
   valide pela candidata.
   - O aviso de conflito aparece antes do registro.
   - Depois do registro, o resultado é `DECLARADA_EM_CONFLITO`.
   - A Participação institucional não mudou.

### 6. Escopo e chave (FR-063, FR-117)

1. Como operador B (CSAEG Vitória):
   - só aparecem declarações de Vitória;
   - abrir uma de Serra pela URL resulta em 404.
2. O operador C, sem vínculo, é recusado.
3. Reinicie o servidor sem `TRAJETORIA_CHAVE_CONSULTA_ACERVO`.
   - "Começar" leva à indisponibilidade técnica e nada é gravado.
   - Na fila, a revelação aparece como indisponível.
4. Reinicie com as duas chaves iguais. O caminho de declaração fica indisponível.

### 6b. Selo e idempotência (R6)

1. Na tela de confirmação, clique duas vezes em "Começar", ou atualize a página depois.
   Deve existir uma única declaração, e você chega à mesma Participação.
2. Espere passar a validade do selo, ou use `TRAJETORIA_SELO_DECLARACAO_VALIDADE=1`, e
   envie. Você volta a `/acesso/` sem detalhe.
3. Confira nos logs do servidor e na barra de endereço: nenhum selo, CPF ou data.

### 7. Retomada (US7)

1. Declare, responda uma Seção e feche o navegador.
2. Volte com o mesmo par. A formação informada aparece com "Continuar".
3. Volte com o mesmo CPF e outra data. A declaração anterior não aparece. Se você declarar
   de novo, a fila mostra as duas como "outras declarações com o mesmo CPF".
