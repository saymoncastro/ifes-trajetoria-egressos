# Quickstart: validar a Feature 014

Guia para comprovar que o polish atende a spec. O ambiente é o da
[demonstração da 008](../008-interface-navegavel-pesquisa/quickstart.md#preparar): `uv`,
PostgreSQL 16+ e um banco local dedicado, **só com dados fictícios**.

## Preparar

```bash
uv sync --extra dev
```

```bash
createdb trajetoria_polish
```

```bash
PGDATABASE=trajetoria_polish uv run python manage.py migrate
```

```bash
PGDATABASE=trajetoria_polish TRAJETORIA_DEMONSTRACAO=1 uv run python manage.py preparar_demonstracao
```

```bash
PGDATABASE=trajetoria_polish TRAJETORIA_DEMONSTRACAO=1 uv run python manage.py runserver
```

A 014 não tem migração (SC-013):

```bash
uv run python manage.py makemigrations --check --dry-run
```

## 1. Validação automatizada (fecha a feature — FR-049)

Suíte completa: interface, editor (009), acompanhamento (011), demonstração e demais
features.

```bash
uv run pytest
```

Só a jornada do egresso:

```bash
uv run pytest tests/interface
```

| O que comprova | Onde |
|---|---|
| Matriz do rodapé, regra de verdade, botão bloqueador (SC-002 a SC-004, SC-015) | `tests/interface/test_interface_rodape.py` |
| Pendência × erro (SC-001), títulos, linha de contexto, `radiogroup` | `test_interface_secao.py`, `test_interface_gravacao.py` |
| Trajetória: ordem da 007, "sem pesquisa" omitido, ambiguidade, avisos (SC-011) | `test_interface_formacoes.py`, `test_interface_encerramento.py` |
| Confirmação com um agradecimento (SC-012) | `test_interface_conclusao.py` |
| E2E-1 a E2E-4 sem JavaScript; verificador de acessibilidade (SC-013) | `test_interface_aceitacao.py`, `test_interface_acessibilidade.py` |
| Sem regressão automatizada fora da jornada (SC-014, parte 1) | `tests/editor`, `tests/acompanhamento`, `tests/interface/test_demonstracao_operador.py` |

Nenhum `<script>` nos templates (SC-013):

```bash
grep -rn "<script" trajetoria/interface/templates trajetoria/demonstracao/templates
```

## 2. Verificação em navegador real (implementação)

Com o servidor no ar, no painel de navegador (Chromium), com viewport emulada. Use as
Pessoas fictícias **Ana**, **Maria**, **Diego** e **Elisa** da demonstração.

### 2.1 Enter não envia (SC-005)

1. Diego, Seção 3: digite um ano no primeiro campo e pressione Enter. **Esperado:**
   nenhum envio; a página continua igual, sem resumo.
2. Maria, Seção 10: digite na descrição de "Outro" e pressione Enter. **Esperado:**
   nenhum envio.
3. Tab até "Salvar e continuar" e Enter; depois Tab até "Salvar e sair" e Espaço.
   **Esperado:** cada um executa a sua ação.

**Limitação conhecida (não é critério da 014).** No Chromium, com teclado físico, Enter
com o foco num **rádio** ou numa **caixa de seleção** pode acionar o envio, como já
acontecia antes da 014 ([research R2](research.md#r2--enterir-botão-de-envio-padrão-desabilitado),
correção). Espaço continua sendo a interação convencional para marcar rádio e caixa.
Não será introduzido JavaScript só para interceptar esse caso. Isso não altera a solução
do achado mobile MF-02, que é a tecla "Ir"/Enter depois de **digitar**.

### 2.2 Área ativável (SC-007)

Na Seção 8 de Elisa a 375×667, execute no console. O resultado esperado é `[]`:

```js
[...document.querySelectorAll('.pergunta .opcao')].flatMap(o => {
  o.scrollIntoView({ block: 'center' });
  const r = o.getBoundingClientRect(), id = o.querySelector('input').id;
  const pontos = [[r.left + 1, r.top + 1], [r.right - 1, r.top + 1], [r.left + 1, r.bottom - 1],
                  [r.right - 1, r.bottom - 1], [r.left + r.width / 2, r.top + r.height / 2]];
  const perdidos = pontos.filter(([x, y]) => {
    const e = document.elementFromPoint(x, y);
    return !(e && (e.id === id || e.closest('label')?.htmlFor === id));
  });
  return [...(perdidos.length ? [id] : []), ...(r.width < 44 || r.height < 44 ? [id + ' < 44px'] : [])];
})
```

### 2.3 Escala numa linha e ausência de rolagem (SC-006, SC-008)

Para cada largura (320, 360, 375, 390, 412, 430) e fonte raiz (`100%`, `115%`, `130%`,
`150%`, `200%`), aplique a fonte com
`document.documentElement.style.fontSize = '115%'` e execute:

```js
({ linhasDaEscala: [...document.querySelectorAll('.escala')].map(e =>
     new Set([...e.querySelectorAll('.opcao')].map(o => Math.round(o.getBoundingClientRect().top))).size),
   rolagemHorizontal: document.documentElement.scrollWidth > innerWidth })
```

**Esperado:** todas as escalas de 5 pontos com `1` linha e `rolagemHorizontal: false`.
Para uma escala de 11 pontos, crie-a numa Versão de teste pelo editor (009) e confira
`rolagemHorizontal: false` a 320 px, com as linhas alinhadas.

### 2.4 Rodapé e conclusão (SC-009)

A 375 px e a 480 px, numa Seção:

- largura de cada botão = largura útil da coluna;
- distância entre a borda inferior de "Salvar e sair" e o topo da primeira ligação de
  `.saidas` ≥ 32 px.

Na tela "Concluir a pesquisa": cada ligação de `.lista-secoes` com altura ≥ 44 px.

### 2.5 Trajetória na primeira tela (SC-010)

A 375×667, para Ana, Maria e Diego: o topo da primeira ação (botão ou, sem ação, a
mensagem de estado) menos a altura da faixa e do cabeçalho de demonstração deve ser ≤
667 px.

### 2.6 Sem regressão visual fora da jornada (SC-014, parte 2)

Capture, antes (na `main`) e depois, a 375 e 1280 px:

- lista de Pesquisas e edição de Pergunta (009);
- painel de uma Campanha (011);
- entrada e operador da demonstração.

**Esperado:** nenhuma diferença. A prévia de Seção do editor deve mostrar os controles
como na jornada.

### 2.7 Percurso de leitura

Ana, jornada completa:

1. Salve a Seção 2 com 3 de 8 Respostas. Confira "Ainda faltam estas perguntas:", a frase
   de salvamento e o título da aba "Faltam respostas: …".
2. Envie a Seção 1 vazia. Confira que nenhuma frase fala em salvamento.
3. "Salvar e sair" com Respostas: aviso de salvamento na trajetória.
4. "Salvar e sair" numa Seção vazia: aviso neutro.
5. "Sair sem salvar esta seção" com uma marcação: nenhuma gravação e nenhum aviso.
6. Conclua e confira a confirmação.

## 3. Validação posterior em aparelho real [T] (FR-050 — não bloqueia o fechamento)

Roteiro da [auditoria mobile, seção 15](../../docs/auditorias/2026-10-03-mobile-first-experiencia.md#15-o-que-não-foi-possível-testar),
num **iPhone com Safari** e num **Android com Chrome**. Registre o resultado em
`docs/auditorias/` quando executado.

| Item | O que testar | Observar |
|---|---|---|
| 1 | Marcar metade da Seção 8; trocar de aplicativo por 2 a 10 min; voltar | A página recarrega? As marcações voltam? "Salvar e sair" resolve a interrupção voluntária? |
| 3 | Digitar o ano na Seção 3 e tocar na tecla de retorno; repetir na descrição de "Outro" | Rótulo da tecla; a Seção **não** é enviada; o foco avança? |
| 3b | *Observação complementar, não bloqueante:* teclado físico (Bluetooth) com foco num rádio ou numa caixa e Enter | Registrar se envia (Safari pode diferir do Chromium); não é critério da 014 |
| 4 | Cenário do MF-03 com gesto de voltar | Aparece a resposta antiga ou a gravada? **Só insumo de decisão futura; nada muda nesta feature** |
| 5 | Polegar entre o círculo e o número da escala e abaixo do rótulo das Opções | Todo toque marca a opção? |
| 9 | Fonte do sistema "Grande" e "Máxima" | A escala de 5 pontos continua numa linha? |
| 7 e 8 | VoiceOver e TalkBack, se houver aparelho | O foco vai ao resumo? Ele é anunciado (uma ou duas vezes)? O grupo de rádios não inclui "Deixar esta pergunta sem resposta"? O enunciado é lido duas vezes? |
