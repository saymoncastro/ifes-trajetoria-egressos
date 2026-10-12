# Quickstart — validar a Feature 031 depois da implementação

> **Vale só depois da implementação**, que continua condicionada ao Checkpoint 1 e ao
> Checkpoint 2 (T001 das [tasks](tasks.md); roadmap, revisão 15). Hoje não há rota nem
> modelo da 031.

## Pré-requisitos

Ambiente local conforme [docs/desenvolvimento/ambiente-local.md](../../docs/desenvolvimento/ambiente-local.md).
Depois:

```bash
source .env && uv run python manage.py migrate
```

```bash
source .env && uv run python manage.py preparar_demonstracao
```

```bash
source .env && uv run python manage.py runserver 127.0.0.1:8025
```

O preparo cria os encontros fictícios da demonstração (research R15).

## Verificações automáticas (as mesmas do CI)

```bash
uv run ruff check .
```

```bash
uv run python manage.py check
```

```bash
uv run python manage.py makemigrations --check --dry-run
```

```bash
uv run pytest
```

## Cenários manuais

Cada cenário remete à tela do [protótipo](prototipo/index.html) e ao requisito.

| # | Cenário | Como | Esperado |
|---|---|---|---|
| 1 | Descobrir | `/entrar/` como Diego → Início | Seção "Ninguém se forma sozinho." com um encontro proposto por egresso e um evento do Ifes, rótulos distintos (FR-013, FR-014; p1) |
| 2 | Confirmar e ver o link | Abrir o encontro → "Vou participar" | Ciência antes do botão; depois, o link, o `.ics` e o aviso (FR-020, FR-021, FR-028; p3, p4) |
| 3 | O link só aparece a quem confirmou | Ver o código da página antes de confirmar e sem sessão | O link não está no HTML (SC-002) |
| 4 | Endereço compartilhado | Abrir `/encontros/<id>/` numa janela sem sessão → "Confirme seus dados para ver" | Página neutra; depois da identificação, volta ao encontro (FR-022; p6) |
| 5 | Propor | `/entrar/` como Maria → Encontros → Propor | Erros por campo; "Confira e envie" diz quem analisa (CPAEG); "Em análise" (FR-002 a FR-007; o1 a o4) |
| 6 | Limite | Propor um quarto encontro ativo | Recusado no formulário, com a explicação (FR-002) |
| 7 | Moderar | Escolher o operador fictício CSAEG e depois o CPAEG em `/curadoria/encontros/` | Cada um vê o seu escopo; publicar, recusar com motivo; conflito na decisão simultânea (FR-015 a FR-019; m1 a m3) |
| 8 | Correções e alteração | Como organizador: alterar a data; corrigir o link na mesma plataforma; alterar a descrição | Avisos na página; a alteração tira o encontro das listas até a nova análise; recusar a alteração retira o encontro (FR-008; o7, o11, o12, m6, p15) |
| 9 | Cancelar e encerrar | Cancelar como organizador; avançar o relógio do teste para depois do término | Conteúdo só para quem tinha confirmado; os demais veem a situação (FR-024a; p9, p10) |
| 10 | Denunciar e retirar | Denunciar como Diego; retirar como CPAEG | A moderação vê o motivo, sem quem denunciou; a página diz "Retirado pela moderação" (FR-029, FR-017; p12, p13, m4) |
| 11 | Portal desligado | `TRAJETORIA_PORTAL=0` | Nenhuma rota da 031; a coleta não muda (FR-035) |

## Medidas e acessibilidade

- Telas do egresso: sem rolagem horizontal de 320 a 1440 px, com fonte a 100% e 200%; um h1;
  alvos de 44 px; a 375×812, título e data sem rolar.
- Comparar as capturas com o protótipo, com o arnês de `prototipo/gerar.py`.
- Roteiro manual com teclado nos cenários 2, 5, 7 e 10.
