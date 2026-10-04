# Quickstart: validar a Feature 010

Este guia comprova, de ponta a ponta, que a autorização institucional do editor atende a
spec. Pré-requisitos e banco são os da
[Feature 001](../001-nucleo-academico-fonte-simulada/quickstart.md#pré-requisitos) e o
ambiente de demonstração é o da [Feature 009](../009-editor-pesquisa-versao/quickstart.md).

> **Autorização, não autenticação.**
>
> - A 010 decide **o que** um operador já identificado pode fazer. Ela não identifica
>   ninguém de forma confiável.
> - A identificação só existe no modo de demonstração, por **operador fictício**. Os
>   vínculos fictícios não representam designação institucional real.
> - O editor **não** está disponível para uso produtivo enquanto DP-1001 estiver aberta.
> - Ninguém publica pelo sistema (002/DP-001).

## Preparar

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

O preparo garante, além do cenário da 008:

| Operador fictício | Vínculo |
|-------------------|---------|
| Operador fictício A | CPAEG, ativo |
| Operador fictício B | CSAEG, unidade Vitória, ativo |
| Operador fictício C | nenhum |

A partir da Feature 011, o preparo também cria a Campanha fictícia "Demonstração — rodada
em preparação" (nunca aberta, sem período, sem critério, Versão de referência em rascunho),
para o acompanhamento da coleta. *(Revisado pela ADR 0004 — ver `docs/adr/0004-abrangencia-da-campanha-nao-e-foco-de-mobilizacao.md`.)* Os operadores acima não mudam, e a Campanha não
admite Participação ([quickstart da 011](../011-acompanhamento-operacional-coleta/quickstart.md)).

A única migração nova é `governanca/0001_initial`. Depois de aplicada:

```bash
uv run python manage.py makemigrations --check --dry-run
```

## Validar automaticamente

```bash
uv run pytest
```

Pontos de atenção (mapa completo SC → teste no [plan](plan.md#estratégia-de-testes)):

```bash
uv run pytest tests/governanca
```

```bash
uv run pytest tests/editor/test_editor_autorizacao.py tests/editor/test_editor_fronteiras.py tests/editor/test_editor_acesso.py
```

```bash
uv run pytest tests/interface/test_demonstracao_operador.py tests/participacao/test_entrada_aceitacao.py::test_10_nenhum_mecanismo_de_autenticacao
```

Resultado esperado: tudo verde. A suíte da 009, executada pela fixture `client` como
operador fictício A (CPAEG), passa sem mudança de comportamento (SC-003). O teste de
ausência de autenticação da 005 continua verde.

## Roteiro manual (casos A a L da spec)

Abra `http://localhost:8000/editor/`.

| Passo | Ação | Esperado |
|-------|------|----------|
| 1 | Abrir `/editor/` sem escolher operador | Levado a `/demonstracao/operador/`, sem ver conteúdo do instrumento |
| 2 | Em `/demonstracao/operador/`, ver a lista | A: "CPAEG — atuação institucional"; B: "CSAEG — unidade Vitória"; C: "Sem atuação institucional ativa". Texto dizendo que a escolha só identifica |
| 3 | Atuar como C (volta ao início do editor) | 403 "Não há vínculo institucional ativo para este operador." em qualquer página (casos C, H) |
| 4 | Atuar como B; abrir `/editor/` e a Pesquisa da baseline | Só Versões publicadas ("Demonstração — cópia da referência 2024"), aviso "Somente Versões publicadas são exibidas para a sua atuação"; sem "Nova Pesquisa" nem "Nova Versão" |
| 5 | Como B, abrir a Versão publicada e a prévia | Leitura e prévia; nenhuma ação, nem "Nova Versão a partir desta" |
| 6 | Como B, colar o endereço de um rascunho (copiado como A) e do diagnóstico | 403 "Seu vínculo institucional atual não permite consultar Versões em rascunho. Ele permite consultar o instrumento publicado." (caso D) |
| 7 | Como B, enviar um POST direto de escrita (ver abaixo) | 403 "Seu vínculo institucional atual não permite editar este instrumento."; nada gravado; nenhum erro de formulário (caso J) |
| 8 | Atuar como A | Editor completo da 009; cabeçalho "Atuação: Comissão Própria de Acompanhamento do Egresso (CPAEG) — atuação institucional" (caso A) |
| 9 | Como A, criar Versão a partir da baseline, editar a cópia, ver diagnóstico e prévia | Igual à 009 (caso B) |
| 10 | Como A, abrir a Versão publicada | Leitura; única ação "Nova Versão a partir desta" (caso E) |
| 11 | Como A, procurar "publicar" | Não existe (caso K) |
| 12 | Desativar o vínculo de A (abaixo) e recarregar | 403 "Não há vínculo institucional ativo…", na requisição seguinte |
| 13 | Reativar o vínculo de A (abaixo) e recarregar | Editor completo de novo |
| 14 | Parar o servidor, subir sem `TRAJETORIA_DEMONSTRACAO=1`, abrir `/editor/` e `/demonstracao/operador/` com o cookie de A ainda no navegador | 404 em ambas (caso I) |

POST direto do passo 7 (com o cookie e o token CSRF do navegador, por exemplo pelas
ferramentas do navegador): enviar o formulário de "Nova Pesquisa" copiado de uma sessão
como A. Alternativa automatizada: `test_editor_autorizacao.py`, parametrizado por rota.

Desativar e reativar (passos 12 e 13) pelo mecanismo administrativo, que é a operação de
aplicação (não há tela nem comando):

```bash
PGDATABASE=trajetoria_demo uv run python manage.py shell -c "from trajetoria.governanca.consultas import vinculos_ativos; from trajetoria.governanca.operacoes import desativar_vinculo; [desativar_vinculo(v) for v in vinculos_ativos('demonstracao:operador-a')]"
```

```bash
PGDATABASE=trajetoria_demo uv run python manage.py shell -c "from trajetoria.governanca.models import Papel; from trajetoria.governanca.operacoes import registrar_vinculo; registrar_vinculo('demonstracao:operador-a', Papel.CPAEG)"
```

## Acessibilidade e responsividade

Repita, nas três variantes de recusa e em `/demonstracao/operador/`, o roteiro de
teclado, foco visível, 320 px e zoom de 200% da
[009](../009-editor-pesquisa-versao/quickstart.md).

## O que não deve existir

- tela, rota ou comando de gestão de vínculos;
- login, senha, sessão, conta ou superusuário;
- identificador de operador aceito por parâmetro de endereço ou cabeçalho;
- ação de publicar, aprovar ou pedir aprovação;
- papel além de CPAEG e CSAEG.
