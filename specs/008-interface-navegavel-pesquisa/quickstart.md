# Quickstart: validar a Feature 008

Guia para comprovar, de ponta a ponta, que a interface atende a spec. Pré-requisitos e
banco são os mesmos da
[Feature 001](../001-nucleo-academico-fonte-simulada/quickstart.md#pré-requisitos):
`uv` e PostgreSQL 16+ local.

> **Ambiente de demonstração, somente dados fictícios.** O modo de demonstração NÃO DEVE
> ser ativado em ambiente acessível a egressos nem sobre banco com dados reais
> (FR-002). Não há autenticação: escolher uma pessoa não comprova identidade.
> 001/DP-009 e 005/DP-504 continuam bloqueando o uso com dados reais.

## Preparar

```bash
uv sync --extra dev
```

Use um banco local **dedicado** à demonstração (o preparo recusa banco com dados que não
sejam da fonte simulada):

```bash
createdb trajetoria_demo
```

Os três comandos abaixo, com as variáveis `PGDATABASE=trajetoria_demo` e
`TRAJETORIA_DEMONSTRACAO=1`, deixam a demonstração no ar (SC-001):

```bash
PGDATABASE=trajetoria_demo uv run python manage.py migrate
```

```bash
PGDATABASE=trajetoria_demo TRAJETORIA_DEMONSTRACAO=1 uv run python manage.py preparar_demonstracao
```

```bash
PGDATABASE=trajetoria_demo TRAJETORIA_DEMONSTRACAO=1 uv run python manage.py runserver
```

Abra `http://localhost:8000/`. O preparo imprime as pessoas fictícias e a situação que
cada uma demonstra ([contrato](contracts/demonstracao.md#passos-só-operações-existentes-fr-013)).

A 008 **não tem migração**:

```bash
uv run python manage.py makemigrations --check --dry-run
```

## Validar automaticamente

Suíte completa (001 a 007 devem continuar verdes; o único teste existente ajustado é
`test_10` da 007, restrito aos apps de domínio — [plan](plan.md#necessidade-de-voltar-à-spec-ou-às-features-anteriores)):

```bash
uv run pytest
```

Só a interface:

```bash
uv run pytest tests/interface
```

Lint e verificação do Django:

```bash
uv run ruff check .
```

```bash
uv run python manage.py check
```

Mapa dos testes para os critérios de sucesso: [research R19](research.md#r19--estratégia-de-testes).

## Roteiro manual

Cada roteiro corresponde a um cenário ponta a ponta da spec. Faça-os também com
**JavaScript desativado** no navegador (FR-080).

### E2E-1 — Jornada principal (Ana Exemplo)

1. Em `/`, confira a faixa "Ambiente de demonstração" e escolha **Ana Exemplo**.
2. A tela diz "Esta pesquisa refere-se à sua formação" com curso, unidade e ano, e só há
   **"Iniciar a pesquisa"**.
3. Inicie: a Seção 1 aparece com o texto de abertura. Marque "Sim" e salve.
4. Em "Informações Pessoais", deixe uma pergunta obrigatória em branco e salve: a mesma
   Seção volta com "Há problemas nesta seção" e a mensagem na pergunta; as demais
   respostas continuam lá.
5. Siga: Q14 = "Graduação" → Seção "Graduação" → "Avaliação" (marque "Outro:" em uma
   escolha múltipla e descreva) → "Atualmente você trabalha?" = "Sim" → "Egresso que
   trabalha".
6. No meio dessa Seção, clique em **"Encerrar demonstração"**.
7. Escolha **Ana Exemplo** de novo: agora o botão é **"Continuar a pesquisa"**, que leva à
   Seção onde você parou, com as respostas salvas (inclusive o complemento).
8. Termine até a Seção final; na tela de conclusão, leia o aviso e **"Concluir pesquisa"**.
9. Confirmação: "Pesquisa concluída", agradecimento, contexto da formação, texto de
   encerramento; nenhuma resposta, comprovante ou botão de edição.
10. Volte às formações: "Pesquisa já respondida", sem ação. Tente o endereço de uma Seção
    no histórico do navegador: "Esta pesquisa já foi respondida."

### E2E-2 — Q1 = Não (Carla Exemplo, Redes de Computadores)

1. Escolha a **Carla Exemplo** cuja formação é Redes de Computadores (Serra).
2. Inicie, marque "Não" na Seção 1 e salve: vai direto à tela de conclusão.
3. Conclua: mesma confirmação neutra; nada fala em consentimento ou recusa.

### E2E-3 — Seleção entre formações (Maria Exemplo)

1. Escolha **Maria Exemplo**: a tela pergunta "Sobre qual formação do Ifes você
   responderá esta pesquisa?" com duas formações e nenhuma sugerida.
2. Inicie a primeira, responda a Seção 1, clique em "Sair e continuar depois".
3. As duas continuam como alternativas: uma para continuar, outra para iniciar.

### Outras situações

- **Diego Exemplo**: duas formações pendentes (Técnico e Licenciatura) com ação; o Mestrado
  aparece como "não está disponível neste momento" (ambiguidade), sem nomear Campanhas.
- **Bruno Exemplo**: seleção entre as duas formações; **Carla Exemplo (Pedagogia)**: entrada
  direta. Na demonstração ninguém com formação fica "sem pesquisa": a coleta ampla não tem
  critério. *(Revisado pela ADR 0004 — ver `docs/adr/0004-abrangencia-da-campanha-nao-e-foco-de-mobilizacao.md`.)*
- **Homônimas**: as duas "Carla Exemplo" aparecem distintas pelo resumo das formações.
- **Pessoa sem nome**: aparece como "Pessoa fictícia sem nome informado".
- **Modo desligado**: reinicie o `runserver` sem `TRAJETORIA_DEMONSTRACAO=1`; toda página
  responde "Página não encontrada".

### Encerramento durante o preenchimento (opcional)

Coberto por teste automatizado (E2E-4). Para ver manualmente, com uma Seção aberta no
navegador, encerre a Campanha pela operação da 004 fora da interface e envie a Seção:

```bash
PGDATABASE=trajetoria_demo uv run python manage.py shell -c "from trajetoria.campanha.models import Campanha; from trajetoria.campanha.operacoes import encerrar; print(encerrar(Campanha.objects.get(nome='Demonstração — coleta ampla')))"
```

A Seção responde "O período de resposta desta pesquisa foi encerrado…"; nada foi
gravado. Para recomeçar a demonstração, recrie o banco:

```bash
dropdb trajetoria_demo
```

### Acessibilidade e responsividade (roteiro mínimo)

- **Teclado**: percorra E2E-1 só com Tab, Shift+Tab, Espaço, setas e Enter; o foco está
  sempre visível; "Pular para o conteúdo" é o primeiro item.
- **Leitor de tela** (VoiceOver ou NVDA): cada pergunta de escolha é anunciada como grupo
  com o enunciado; "(obrigatória)" é lido; ao voltar com erros, o título começa com
  "Erro:" e o resumo é anunciado.
- **Largura de 320 px** (modo responsivo do navegador) e **zoom de 200%**: sem rolagem
  horizontal da página; botões e opções confortáveis ao toque.
- **Sem cor**: em escala de cinza, "obrigatória", erros e estados continuam
  compreensíveis.
