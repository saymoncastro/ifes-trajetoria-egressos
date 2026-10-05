# Quickstart — validar a Feature 017

Roteiro de validação. Ver [plan.md](plan.md), [rotas](contracts/rotas.md),
[domínio](contracts/dominio.md) e [data-model](data-model.md).

## Pré-requisitos

Python 3.13, uv, PostgreSQL local e banco fictício `trajetoria_demo`, conforme
[001/quickstart](../001-nucleo-academico-fonte-simulada/quickstart.md). Comandos na raiz do
repositório.

```bash
createdb trajetoria_demo
uv sync --extra dev
PGDATABASE=trajetoria_demo uv run python manage.py migrate
PGDATABASE=trajetoria_demo TRAJETORIA_DEMONSTRACAO=1 uv run python manage.py preparar_demonstracao
PGDATABASE=trajetoria_demo TRAJETORIA_DEMONSTRACAO=1 uv run python manage.py runserver 127.0.0.1:8000
```

O preparo mantém: "Demonstração — coleta ampla" e "— coleta sobreposta" EM COLETA (Versão
"Demonstração — cópia da referência 2024", publicada por meio técnico); "Demonstração —
rodada em preparação" nunca aberta, sem período e com a baseline 2024 em rascunho;
operadores A (CPAEG), B (CSAEG Vitória) e C (sem vínculo).

**Não encerre as duas Campanhas abertas do preparo**: o preparo recusa repetir-se quando
elas deixam de estar em coleta, e recomeçar exige recriar o banco. Use Campanhas novas para
exercitar abrir e encerrar.

## Verificação automática

```bash
uv run pytest tests/campanha tests/governanca tests/acompanhamento tests/comunicacao
```

```bash
uv run pytest
```

```bash
uv run ruff check .
git diff --name-only HEAD -- "*.py" | xargs uv run ruff format --check
```

```bash
PGDATABASE=trajetoria_demo uv run python manage.py makemigrations --check --dry-run
```

Esperado: tudo verde; nenhuma migração pendente (FR-025).

## Roteiro manual (http://127.0.0.1:8000/acompanhamento/)

1. **Operador A (CPAEG)**. A lista mostra "Nova Campanha".
2. **Criar sem período** (US1): Nova Campanha → nome "Pesquisa Institucional de Egressos
   2027", Versão "Pesquisa Institucional de Egressos — Demonstração — cópia da referência
   2024" → Salvar. Esperado: detalhe "Em preparação", impedimento "O período de coleta não foi
   definido", só "Editar configuração". A escolha de Versão não oferece a baseline em
   rascunho; o formulário não tem campo de público ou critério.
3. **Erros** (US1): Editar configuração com só o início → erro no fim; início depois do fim
   → erro no início; nome em branco → erro no nome; valores digitados preservados.
4. **Período futuro**: início daqui a 30 dias → impedimento "A coleta poderá ser aberta a
   partir de …", sem "Abrir coleta".
5. **Período que inclui hoje** → "Abrir coleta" aparece. Acionar: a confirmação lista
   "Demonstração — coleta ampla" e "— coleta sobreposta" com o aviso de que alguns egressos
   podem ter mais de uma pesquisa. Cancelar não muda nada; confirmar → "Em coleta", "Aberta
   em", "Encerramento previsto", "Encerrar coleta"; sem "Editar configuração".
6. **Remover período** (US2): em outra Campanha nova com período, apagar as duas datas →
   recusa "pode ser corrigido, mas não removido".
7. **Rascunho atual** (US2): "Demonstração — rodada em preparação" → impedimentos de Versão
   não publicada e de período; Editar configuração mostra a baseline marcada "não publicada
   — impede a abertura"; trocar pela cópia publicada e definir período que inclui hoje →
   impedimentos somem.
8. **Abrangência restrita**: detalhe de "Demonstração — coleta sobreposta" mostra o aviso de
   leitura (Vila Velha; Pós-graduação) e só "Encerrar coleta" — **não** encerrar esta.
9. **Encerrar** (US4): na Campanha aberta no passo 5 → confirmação → "Encerrada",
   "Encerrada em … (antecipadamente)", nenhuma ação de gestão; "Comunicação simulada"
   continua presente. Reenviar o POST (voltar e confirmar de novo) → aviso de já encerrada.
10. **Período encerrado sem abertura**: criar Campanha com período inteiramente no passado
    → lista e detalhe mostram "Período encerrado — Campanha nunca aberta" e "Editar
    configuração"; corrigir para período que inclui hoje → "Em preparação".
11. **Operador B (CSAEG)** (US5): lista e detalhe como antes, sem nenhuma ação de gestão;
    abrir diretamente `/acompanhamento/campanhas/nova/` e `/<uuid>/abrir/` → "Acesso não
    permitido". **Operador C** → recusa. Sem operador → escolha de operador.
12. **Modo desligado**: reiniciar sem `TRAJETORIA_DEMONSTRACAO` → rotas inexistentes (404).
13. **Acessibilidade**: percorrer formulário e confirmações só com teclado; 320 px de
    largura e 200% de ampliação sem perda de conteúdo.


## Evidências da implementação — 2026-10-03

- Worktree: `claude/spec-017-campaign-management-e96f8f`, baseline `5e50fec`.
- Banco **novo e isolado** `trajetoria_demo_017`, criado e migrado para a validação;
  `trajetoria_demo` existente foi preservado. Servidor local na porta 8017; segunda
  instância na 8018 com modo desligado.
- Chrome: criação sem período; rejeições de nome vazio, período incompleto e invertido,
  preservação de valores e foco automático no primeiro campo com erro; período futuro
  com data de abertura; correção para período atual; confirmação com aviso e nomes das
  duas Campanhas em coleta; cancelamento sem escrita; abertura e encerramento da Campanha
  **nova** "Pesquisa Institucional de Egressos 2027 — validação 017".
- Rodada em preparação: rascunho atual pré-selecionado e marcado; substituição pela cópia
  publicada e período atual; recusa de remoção do período; período passado mostrado como
  "Período encerrado — Campanha nunca aberta"; correção devolve "Em preparação".
- Abrangência da coleta sobreposta lida (Vila Velha; Pós-graduação), sem qualquer alteração.
  As duas Campanhas abertas do preparo continuam **EM COLETA**, confirmado no banco.
- Operadores B e C: criação direta recusada sem dados de Campanha; B não vê "Nova
  Campanha". Após encerrar atuação, rota direta redireciona à escolha de operador.
  Instância com modo desligado apresenta "Página não encontrada".
- Layout de formulário com erro em **320 px**: largura do documento = largura do viewport
  (320), sem rolagem horizontal; rótulos, resumo de erros, foco e botão de envio visíveis.
  Zoom **nativo de 200%** confirmado no Chrome: documento = viewport (756 px), sem perda
  de conteúdo; zoom e override de viewport restaurados após validação.
- Reenvio de encerramento confirmado por cliente HTTP Django no mesmo banco, com aviso
  `ja-encerrada` e retrato da linha idêntico. Revalidação entre GET/POST, CSRF e todas as
  recusas são também cobertos pelos testes automatizados.
- Evidência visual da Campanha encerrada: [`evidencias/017-campanha-encerrada.png`](evidencias/017-campanha-encerrada.png)
  (gerada em 2026-10-03 como `/tmp/ifes-017-validacao.png` e versionada em 2026-10-05).
- `manage.py check`: nenhuma ocorrência; `makemigrations --check --dry-run`: nenhuma mudança.
- A normalização de formato do repositório inteiro feita na implementação foi revertida no
  code review: o CI só exige `ruff check`, e os 41 arquivos alheios à 017 (todos com AST
  idêntica) voltaram ao estado da `main`. Só os arquivos tocados pela 017 são formatados.
- Checklist de requisitos continua com seus **16 itens revisados**, sem alteração dos
  marcadores durante a implementação. Não há `.specify/extensions.yml` nem hooks registrados.

- Resultado final: **2033 testes passaram** após as correções do code review, 1 de volume desmarcado pela configuração;
  `ruff check .` e `git diff --check` passaram; formato verificado só nos arquivos da 017.
- Servidores de validação encerrados; banco isolado mantido para reprodução do cenário.
