# Validação — Feature 026, Volte ao Ifes (implementação na demonstração)

- **Data.** 2026-10-09.
- **Autorização.** T001: implementação só na demonstração, em branch e PR próprios (roadmap,
  revisão 10). Checkpoint 1 **NÃO APLICADO**; D4 e D5 continuam `DECISÃO PENDENTE`.
- **Natureza.** Verificações automáticas e medidas no navegador. Nada aqui substitui o
  Checkpoint 1 nem o Checkpoint 2: são critérios técnicos, não compreensão de egressos.

## Verificações do CI (critério de entrega 1)

| Verificação | Resultado |
|---|---|
| `uv run ruff check .` | sem apontamentos |
| `uv run python manage.py check` | sem problemas |
| `uv run python manage.py makemigrations --check --dry-run` | nenhuma mudança |
| `uv run pytest` (local) | 3335 passaram, 40 ignorados (vídeo sem renderizador), 2 desmarcados |

Testes novos da 026: 78, em quatro arquivos.

| Arquivo | Cobre |
|---|---|
| `tests/portal/test_contribuicao_regras.py` (22) | situação derivada; formas; mensagem até 500 com quebra de linha como um caractere; e-mail; neutralização de fórmulas; CSV sem CPF nem nascimento; textos sem promessa e sem vocabulário vedado; texto de ciência |
| `tests/portal/test_contribuicao_egresso.py` (30) | gravação (versão, momento, unidade copiada); Conclusão de outra Pessoa; Formação Declarada; versão não vigente; unicidade (inclusive no banco e em corrida); retirada; fluxo em três telas; formação única marcada; erros; quebras de linha; erro de e-mail mantém as escolhas; "Voltar e alterar"; duplicada; sem sessão, declarante e sem Conclusão; lista com as três situações; 404 de outra Pessoa; retirada com confirmação; bloco no Início; navegação |
| `tests/portal/test_contribuicao_unidade.py` (12) | escolha de operador com destino próprio; recusa sem vínculo; escopo CSAEG e CPAEG; lista vazia; CSV; contato feito com confirmação, uma vez, fora do escopo (404) e em retirada (409); retirada depois do contato |
| `tests/portal/test_contribuicao_fronteira.py` (14) | `ContatoDaPessoa` e política de convites intactos; operações só gravam a Manifestação; telas só gravam ao enviar e retirar; snapshot e exportação idênticos; núcleo não importa a camada; escritas só em `operacoes.py`; campos do modelo; carga fictícia idempotente e recusa orientada; Portal desligado |

Testes revisados (requisitos revisados da spec): `test_fronteiras.py` (dois modelos, sem FK;
telas da contribuição não gravam ao abrir) e `test_navegacao.py` (item "Contribuir").

## Telas reais (critérios de entrega 2 e 3)

Geradas por [`evidencias/capturar.py`](evidencias/capturar.py) a partir da aplicação servida,
sobre o banco da demonstração, numa transação desfeita no fim. Capturas em
[`evidencias/capturas/`](evidencias/capturas/), medidas em
[`evidencias/medidas.json`](evidencias/medidas.json) e CSV real em
[`evidencias/exemplo-real.csv`](evidencias/exemplo-real.csv).

| Critério | Resultado |
|---|---|
| Sem rolagem horizontal de 320 a 1440 px, fonte a 100% e 200% (telas do egresso) | nenhuma rolagem |
| Um h1 por tela | todas as telas |
| Bloco "Contribuir com o Ifes" no Início a 375 px, orçamento de 200 px (R10) | 197 px (Diego, com "Suas contribuições") |
| Navegação a 375 px, até duas linhas (R9) | 2 linhas |
| Alvos de ação de 44 px nas telas do egresso | nenhum abaixo |
| Tabela da unidade a 1280 px | cinco colunas visíveis, sem corte (u1) |

**Navegação com fonte a 200%.** A 375 px ocupa 4 linhas e a 320 px, 6 (um item por linha). R9
manda, nesse caso, manter o rótulo curto "Contribuir" e a ordem, o que foi feito. Não houve
mudança de layout da navegação.

## Comparação com os protótipos

As telas seguem os protótipos e1 a e6, u1 e u2. Diferenças:

- **Lista do egresso:** a linha diz "Unidade Vila Velha" e a situação "enviada" não repete a
  data, que já está na linha.
- **Ciência:** "Se houver interesse, o Ifes entra em contato…" e "Quando o contato for
  registrado…", sem atribuir o contato à unidade antes de D4.
- **Início:** "divulgar uma vaga da sua área" no lugar de "uma oportunidade": "Oportunidade" é
  vedada fora do bloco de Oportunidades (024 FR-021, revisado pela 025).
- **"Voltar e alterar":** é um botão que reenvia as escolhas à primeira tela, sem perdê-las.
- **Erros:** resumo de erros no topo, como na jornada, e telas para e-mail inválido (e3b) e
  escolha incompleta (e2b).
- **Tabela da unidade:** quebra de linha só onde cabe; a data não quebra.

## Desvios do plan

- **CSV:** `contribuicao/planilha.py` em vez de `contribuicao/csv.py`, para não sombrear o
  módulo `csv` da biblioteca padrão.
- **Escolha de operador:** destino próprio `contribuicoes` (além de `curadoria`), registrado
  pelo mesmo ponto neutro da 025.
- **Ligação entre as áreas:** a lista da curadoria de oportunidades ganhou o link
  "Contribuições recebidas", e a lista de contribuições, "Curadoria de oportunidades".
- **Formação sem unidade registrada:** só a atuação institucional (CPAEG) recebe, e os textos
  dizem "o Ifes".

## Pendências

- **Roteiro manual com teclado** (critério de entrega 4): não executado num navegador real.
  Verificado por estrutura: nenhum JavaScript; só links, botões e controles nativos; rótulos
  associados; foco no primeiro campo com erro; sem `tabindex` positivo.
- **D4, D5, DP-801, DP-2501:** continuam pendentes (plan, "Decisões Pendentes").
- **T024:** a atualização da 029 com "Contribuir com o Ifes" vai em PR próprio.
- **Checkpoint 1:** NÃO APLICADO; será aplicado depois da 026 e da 029 implementadas.
