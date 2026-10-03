# Quickstart: validar a Feature 015 (gate)

Guia para executar o gate da 015 e preencher o
[registro de validação](contracts/registro-validacao.md). Ambiente da demonstração da
008, **só com dados fictícios**.

## 0. Pré-requisito: assinatura oficial (bloqueada por D-03)

O ZIP oficial da marca sistêmica foi inspecionado em 2026-10-03 e **não contém SVG**
(research R3). Até a ACS fornecer a assinatura horizontal colorida em SVG:

- o cabeçalho é implementado e medido **sem** a assinatura (nenhum substituto);
- SC-001 fica **reprovado/pendente** no registro, e a 015 não fecha o gate;
- quando o SVG chegar: registrar nome, origem e SHA-256 em research R3 e no registro,
  incluí-lo como recebido e repetir a rodada.

## 1. Preparar

```bash
uv sync --extra dev
```

```bash
createdb trajetoria_015
```

```bash
PGDATABASE=trajetoria_015 uv run python manage.py migrate
```

```bash
PGDATABASE=trajetoria_015 TRAJETORIA_DEMONSTRACAO=1 uv run python manage.py preparar_demonstracao
```

```bash
PGDATABASE=trajetoria_015 TRAJETORIA_DEMONSTRACAO=1 uv run python manage.py runserver
```

Sem migração nova (SC-013):

```bash
uv run python manage.py makemigrations --check --dry-run
```

## 2. Validação automatizada

```bash
uv run pytest
```

| O que comprova | Onde |
|---|---|
| Inclusão das folhas por página; troca A/B só nos dois tokens de ação; verde da marca só gráfico; seletores administrativos sem tokens; papéis de cor; assinatura com nome acessível; sem recurso externo | `tests/interface/test_interface_identidade.py` (research R9) |
| Comportamento e textos da 014/008 inalterados | `tests/interface/` existentes |
| Editor e acompanhamento sem regressão de comportamento | `tests/editor`, `tests/acompanhamento` |

Sem JavaScript:

```bash
grep -rn "<script" trajetoria/interface/templates trajetoria/demonstracao/templates
```

## 3. Rodada do gate (navegador, viewport emulada)

Para cada situação G1–G4 do [registro](contracts/registro-validacao.md), a 375, 390, 430
e 1280 px, com fonte a 100% e 200%:

1. **G1 — Trajetória:** entrar como Maria (seleção) e como Diego; em Diego, iniciar,
   marcar uma resposta e "Salvar e sair" (aviso `salvo`).
2. **G2 — Seção 8:** percorrer até "Avaliação" (Maria ou Elisa); marcar Opções e pontos.
3. **G3 — Pendência e erro:** Seção 2 com 1 de 8 respondida → "Salvar e continuar";
   Seção 8 com descrição de "Outro" sem a Opção.
4. **G4 — Conclusão e confirmação:** concluir uma Participação.

Em cada tela, medir com estilo computado e capturar:

- altura do cabeçalho (sem a faixa) e do rodapé; altura do símbolo da assinatura e área
  livre em volta;
- contraste dos pares usados (texto, ligações, botões, estados, contornos);
- `document.documentElement.scrollWidth === innerWidth` (sem rolagem horizontal);
- foco por teclado em cada tipo de elemento; resumo focado ao carregar (G3);
- G3 em escala de cinza;
- cada captura nomeada `R{rodada}-G{situação}-{A|B}-{largura}-{fonte}` e anexada ao PR
  (não versionada);
- 014 SC-006 a SC-010 (escala de 1 a 5 numa linha; áreas ativáveis; largura dos botões;
  primeira ação na primeira tela).

## 4. Comparação A × B (sem mecanismo de execução)

1. Em `estilo.css`, trocar **só** `--cor-acao` e `--cor-acao-forte` para os valores da
   Direção A (`#195128` / `#00420c`).
2. Recarregar e capturar G1–G4 a 375 e 1280 px; medir contrastes.
3. Restaurar a Direção B (`#1351b4` / `#0c326f`). Conferir que o diff final não contém
   a troca:

```bash
git diff --stat
```

## 5. Raio e divisor (hipóteses)

- Trocar `--raio` entre 4 e 0 px; capturar G2 e G3 a 375 px; decidir e registrar.
- Testar um divisor suave entre Perguntas em G2 a 375 px; manter só se o registro
  mostrar necessidade.

## 6. Regressão administrativa (SC-012)

Capturar **antes** (na `main`) e **depois** (na branch), a 375 e 1280 px: lista de
Pesquisas, edição de Pergunta (009), painel de uma Campanha (011). Esperado: 0
diferenças. A prévia de Seção do editor deve mostrar as Perguntas com a tipografia e os
estados da jornada.

## 7. Fechar a rodada

Preencher `validacao.md` (só texto; capturas anexadas ao PR pelos identificadores). Critério reprovado → corrigir na mesma branch → nova rodada.
Todos aprovados → a 015 está pronta para merge. Revisão perceptiva (ACS, CPAEG/Proex,
egressos) fica registrada como pendente ou realizada, sem bloquear o merge.
