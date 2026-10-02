# Quickstart: validar a Feature 009

Este guia comprova, de ponta a ponta, que o editor atende a spec. Os pré-requisitos e o
banco são os mesmos da
[Feature 001](../001-nucleo-academico-fonte-simulada/quickstart.md#pré-requisitos): `uv` e
PostgreSQL 16+ local.

> **Ambiente não produtivo.**
>
> - O editor só responde com `TRAJETORIA_DEMONSTRACAO=1`, o modo de demonstração local
>   da 008.
> - Não há autenticação nem autorização. Ter acesso ao editor **não** confere
>   competência institucional para elaborar ou publicar o instrumento (DP-901;
>   002/DP-001).
> - O editor não publica.
> - "Sem impedimentos técnicos conhecidos" **não** é aprovação.

## Preparar

Use o mesmo banco local de demonstração da 008. O preparo cria a baseline em RASCUNHO e
uma cópia publicada, "Demonstração — cópia da referência 2024", que serve para conferir
a Versão publicada no editor.

```bash
uv sync --extra dev
```

```bash
PGDATABASE=trajetoria_demo uv run python manage.py migrate
```

```bash
PGDATABASE=trajetoria_demo TRAJETORIA_DEMONSTRACAO=1 uv run python manage.py preparar_demonstracao
```

```bash
PGDATABASE=trajetoria_demo TRAJETORIA_DEMONSTRACAO=1 uv run python manage.py runserver
```

Abra `http://localhost:8000/editor/`.

A 009 **não tem migração**:

```bash
uv run python manage.py makemigrations --check --dry-run
```

> **Baseline.**
>
> - Trabalhe sempre numa **cópia** ("Criar nova Versão a partir desta").
> - A baseline é um rascunho comum, e o editor não a protege (spec, Clarifications;
>   DP-902).
> - Se ela for alterada à mão, `preparar_demonstracao` e a materialização da 003 passam a
>   recusar por divergência. Esse é o **comportamento esperado**.
> - Para recomeçar, recrie o banco local.

## Validar automaticamente

Suíte completa, com 001 a 008 verdes e os testes existentes da 006 sem alteração:

```bash
uv run pytest
```

Só o editor:

```bash
uv run pytest tests/editor
```

Só a exposição da 006 (`secoes_nao_suportadas`):

```bash
uv run pytest tests/participacao/test_jornada_percurso.py
```

Lint e verificação do Django:

```bash
uv run ruff check .
```

```bash
uv run python manage.py check
```

O mapa dos arquivos de teste para o que cada um cobre está em
[research R14](research.md#r14--estratégia-de-testes). O mapa para os critérios de
sucesso está no [plan](plan.md#estratégia-de-testes).

## Roteiro manual

Faça os roteiros também com **JavaScript desativado** no navegador (SC-009).

### E2E-1 — Cenário principal (spec, 14 passos)

1. Abra `/editor/` e veja "Pesquisa Institucional de Egressos".
2. Abra a Pesquisa e veja as Versões:
   - a baseline, como **Rascunho**;
   - a cópia de demonstração, como **Publicada em …**;
   - a origem de cada uma.
3. Abra a baseline e confira a estrutura: 13 Seções, 54 Perguntas, tipos e
   obrigatoriedade escritos, destinos ("segue para a Seção …", "finaliza") e a Seção sem
   título.
4. Em "Criar nova Versão a partir desta", crie "Cópia de trabalho".
5. Na cópia, abra uma Seção e depois uma Pergunta. Em "Editar Pergunta", altere o texto.
6. Na Seção, use "Adicionar Pergunta" → "Escolha única", com texto e "Obrigatória".
7. Adicione as Opções "Sim" e "Não", usando "Adicionar e incluir outra".
8. Suba a nova Pergunta uma posição e inverta as Opções com "Subir" e "Descer".
9. Edite a Pergunta e alterne entre "Opcional" e "Obrigatória".
10. Veja a estrutura e a **Pré-visualização**:
    - o aviso "nada é gravado";
    - os controles por tipo;
    - as anotações de desvio;
    - a navegação pela ordem.
11. Abra o **Diagnóstico técnico**.
12. Provoque um problema e corrija-o:
    - adicione uma Pergunta de escolha sem Opções;
    - o diagnóstico A aponta "precisa de pelo menos duas Opções";
    - siga o link do problema e adicione as Opções, ou remova a Pergunta.
13. Diagnostique de novo e veja "**Sem impedimentos técnicos conhecidos**", com o texto
    que diz que isso não é aprovação e que publicar não está disponível.
14. Abra a cópia **publicada** e confira:
    - não há botões de edição, ordenação ou remoção;
    - ao reenviar um formulário antigo ou digitar uma rota de edição, a resposta é
      recusa.

Ao final, confira:

- nenhuma Versão foi publicada pelo editor;
- `preparar_demonstracao` executado de novo **não** recusa, porque a baseline está
  intacta.

### E2E-2 — Cenário de navegação

1. Na Pesquisa, crie a Versão vazia "Navegação — teste".
2. Crie as Seções A, B e C.
3. Em A, crie uma Pergunta de escolha única com "Sim" e "Não". Na Opção "Não", defina o
   desvio "ir para a Seção C".
4. Dê uma Pergunta de texto curto a B e outra a C.
5. Na estrutura e na prévia, confira:
   - "Não → Seção C";
   - "Sim" segue a ordem;
   - B segue para C;
   - C finaliza.
6. O diagnóstico mostra "Sem impedimentos técnicos conhecidos".
7. Provoque a situação (a): adicione em A outra Pergunta de escolha única com desvio. O
   diagnóstico **B** mostra "a jornada atual não consegue aplicar mais de uma Pergunta
   com desvio na mesma Seção", e a situação passa a "Estrutura válida, mas incompatível
   com a jornada atual".
8. Provoque a situação (b): suba C para antes de A. O diagnóstico **A** mostra "o destino
   precisa ser uma Seção posterior".
9. Desfaça (a) e (b) e veja de novo "Sem impedimentos técnicos conhecidos".
10. Troque o desvio de "Não" de "Seção C" para "Finalizar" numa única gravação. Não há
    estado intermediário visível.

Nenhuma tela oferece condição composta, prioridade de regras ou momento de aplicação.

### Outras situações

- **Remoção de Seção**:
  - Seção com Perguntas: a página explica e não oferece "Remover";
  - Seção destino de desvio: a página lista quem aponta para ela;
  - Seção vazia: confirmação, depois remoção.
- **Escala**: crie uma escala de 1 a 5 com rótulos e confira a explicação. Tente 5 a 1 e
  um valor não inteiro: são recusados, com erro junto ao campo e os valores mantidos.
- **Complemento**: marque "aceita complemento" em duas Opções da mesma Pergunta. A
  segunda é recusada, com a orientação de desmarcar a atual.
- **Nome repetido de Pesquisa**: criar "Pesquisa de teste" duas vezes pede confirmação
  na segunda. Confirmada, a Pesquisa é criada.
- **Modo desligado**: execute `runserver` sem `TRAJETORIA_DEMONSTRACAO=1`. Então
  `/editor/` e todas as rotas do editor respondem 404.

### Acessibilidade e responsividade (roteiro mínimo)

- Percorra E2E-1 só com teclado e confira:
  - foco visível;
  - "Pular para o conteúdo";
  - a trilha "Você está em";
  - um `h1` por página.
- Com leitor de tela, verifique:
  - "Subir" e "Descer" anunciam o elemento, por exemplo "Subir a Pergunta 3: …";
  - os estados são lidos como texto.
- Envie um formulário com erro e confira:
  - o resumo aparece no topo, sem rolagem, a 320 px;
  - cada erro está junto ao campo;
  - os valores digitados foram mantidos.
- A 320 px e com zoom de 200%, não há rolagem horizontal em nenhuma página, inclusive a
  estrutura da baseline e a prévia com lista longa (Q19).
