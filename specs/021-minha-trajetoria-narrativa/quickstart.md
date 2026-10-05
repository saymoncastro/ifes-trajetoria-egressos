# Quickstart — validar a Feature 021

Este é o roteiro de validação. Os detalhes estão em [plan.md](plan.md),
[rotas](contracts/rotas.md), [narrativa](contracts/narrativa.md),
[catálogo](contracts/catalogo.md), [card](contracts/card.md),
[contexto da trajetória](contracts/contexto-da-trajetoria.md) e [data-model](data-model.md).
Todos os dados são fictícios.

## Pré-requisitos

- O ambiente é o mesmo da [019/quickstart](../019-formacao-declarada-validacao/quickstart.md):
  Python 3.13, uv, PostgreSQL local, as chaves de acesso da 018 e as duas chaves da 019.
- A 021 **não acrescenta chave nem variável de ambiente**.
- Se a revisão aprovar o PNG (research R11), o `uv sync` instala `resvg-py`. O pacote já
  vem compilado e não depende de biblioteca do sistema.

Use um banco novo e isolado:

```bash
createdb trajetoria_demo_021
```

```bash
uv sync --extra dev && PGDATABASE=trajetoria_demo_021 uv run python manage.py migrate
```

```bash
PGDATABASE=trajetoria_demo_021 TRAJETORIA_DEMONSTRACAO=1 uv run python manage.py preparar_demonstracao
```

```bash
PGDATABASE=trajetoria_demo_021 TRAJETORIA_DEMONSTRACAO=1 uv run python manage.py runserver 127.0.0.1:8000
```

## Verificação automática

```bash
uv run pytest tests/narrativa
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

O teste de volume do SC-008 (500 respostas do mesmo recorte) fica fora da suíte padrão:

```bash
uv run pytest -m volume tests/narrativa
```

## Roteiro manual (P1)

Faça o roteiro em 320 px, 375 px e 1280 px, sem JavaScript.

1. **Maria (SIM-P-0003): o grão é a Pessoa.**
   - Entre em `/acesso/` com o CPF e a data de nascimento fictícios da Maria (a tabela
     está na própria tela de demonstração).
   - Em `/formacoes/`: título "Suas formações no Ifes" (R16) e a frase de antecipação.
     Ainda não aparece ligação para a trajetória.
   - Responda e conclua a pesquisa sobre TADS.
   - Confirmação: "Pesquisa concluída", a frase de registro e uma única ligação, "Ver
     minha trajetória no Ifes".
   - A página mostra as duas formações (TADS 2022 e a Especialização 2025), "O Ifes
     registra 2 formações concluídas por você." e a frase "Depois dessa formação…".
2. **Diego (SIM-P-0004): ordem temporal.** Três formações (2012, 2017, 2020) em ordem
   crescente, com frase de continuidade entre anos distintos.
3. **Ana (SIM-P-0001): formação única.** Uma formação. Não aparece a seção "Outras
   formações".
4. **Bruno (SIM-P-0002): granularidade da data.**
   - O técnico de 2014, só com ano, aparece como "Em 2014, você concluiu Técnico em
     Edificações na unidade Vitória.", sem contagem de anos.
   - A engenharia, com data, aparece com "Há N anos".
5. **Card para o story (de preferência num celular real, ou no modo de dispositivo do
   navegador).**
   - A prévia é a própria imagem vertical. Tocar e segurar oferece salvar.
   - Sem marcar o nome, a imagem não traz o nome.
   - Marque "Incluir meu nome no card" e "Atualizar prévia": o nome aparece na prévia e no
     arquivo baixado.
   - A imagem tem 1080 × 1920 e nenhum texto nas faixas de topo e base.
   - Confira que não há forma de oferta, data completa, brasão nem QR, e que aparece
     "Demonstração — dados fictícios".
   - "Baixar imagem" salva `minha-trajetoria-ifes.png`.
   - Num navegador com compartilhamento de arquivos (Safari no iOS, Chrome no Android),
     aparece "Compartilhar", que abre o menu do sistema com a imagem. Os destinos
     dependem do aparelho; registre quais apareceram, sem tratar a ausência do Instagram
     como falha.
   - Com JavaScript desligado, o botão não aparece e salvar continua funcionando.
   - Anexe a imagem salva a um story do Instagram (conta de teste): ela ocupa a tela sem
     recorte, e a interface do aplicativo não cobre texto.
6. **Acesso.**
   - Sem participação concluída, `/minha-trajetoria/` leva a `/formacoes/`.
   - Sem sessão, leva a `/acesso/`.
   - Com o modo de demonstração desligado, as três rotas devolvem 404.
7. **Declarante (019).** Conclua pelo caminho "Informar minha formação". A confirmação
   não muda, e nenhuma ligação leva à trajetória.

## Roteiro manual (P2)

1. **Ana: dados do complemento e dos agregados.**
   - Aparece "Sua trajetória no Ifes começou em 2019, em Tecnologia em Análise e
     Desenvolvimento de Sistemas.".
   - A seção "Naquele ano no Ifes" traz duas frases: "Em 2022, 27 conclusões de … foram
     registradas na unidade Serra, incluindo a sua." e "Em 2022, 812 conclusões foram
     registradas na unidade Serra.", com a apuração.
2. **Maria: agregados sem ingresso.**
   - Nenhuma frase de início.
   - Os mesmos agregados da Serra em 2022, vindos do mesmo registro no banco (um por
     recorte e apuração).
   - Para a Especialização no Cefor, nenhum agregado.
3. **Diego: sem agregados.** Não aparece a seção "Naquele ano no Ifes".
4. **Isolamento.** Rode o preparo com `ContextoSimulado(indisponivel=True)` (fixture do
   teste de isolamento). Login, resposta e narrativa P1 funcionam, sem a frase de início
   nem a seção de agregados.
5. **012 e 013 intactas.** Capture um snapshot e gere uma exportação. Nenhum dos dois traz
   ingresso nem agregado, e o formato é igual ao de antes.
