# Validação — Feature 029, página pública (implementação na demonstração)

- **Data.** 2026-10-10.
- **Autorização.** Solicitante, 2026-10-10 (roadmap, revisão 11), depois da 026 integrada
  (#56) e da inclusão de "Contribuir com o Ifes" (#57).
- **Natureza.** Critérios medidos e testes. Os critérios qualitativos (P-01 a P-07) são do
  Checkpoint 1, **NÃO APLICADO**.

## O que mudou

- **Template e estilo:** `portal/publico.html` foi substituído pela composição do protótipo
  aprovado: relação → oportunidades → participação (com a contribuição) → trajetória →
  chamada final. A folha é `portal/publico.css`, e as regras da página da 028 saíram de
  `visual.css`.
- **Demonstração:** `portal/exemplo.demonstracao_publica()`, com as formações fictícias do
  card (FR-010), as oportunidades de exemplo no formato da 025, sem link, com a explicação
  montada pelos textos da 025, e a contribuição de exemplo (026). O componente
  `portal/_oportunidade_exemplo.html` é o item da 025 sem link.
- **Início:** `inicio.formacoes_com_origem` foi extraída do Início para servir também à
  demonstração. O comportamento do Início não muda.
- **O que não muda:** rotas, destinos, `never_cache`, `/entrar/`, `/acesso/` e as demais
  telas (FR-001, FR-002).

## Testes

- `tests/portal/test_pagina_publica.py` (7):
  - ordem da relação e contribuição abrindo a participação;
  - chamadas, âncora e nenhum link além de `/entrar/` e `#oferece`;
  - seis selos de exemplo e peças coerentes com o card;
  - textos de participação com a finalidade da 020 e sem prazo garantido;
  - vocabulário vedado;
  - sem formulário, script ou consulta a Pessoa, Conclusão, Portal, contato ou Participação;
  - composição decorativa fora da árvore de acessibilidade.
- Os testes da 028 sobre a página pública (`test_camada_visual.py`, `test_entradas.py`)
  continuam passando sem alteração.
- Verificações do CI, locais: `ruff`, `manage.py check` e `makemigrations --check` passam; suíte completa com 3342 testes aprovados, 40 ignorados (vídeo) e 2 desmarcados.

## Medidas da página implementada

Geradas por [`evidencias/medir.py`](evidencias/medir.py), com o arnês e os critérios do
protótipo sobre o HTML servido. Capturas em [`evidencias/capturas/`](evidencias/capturas/)
e medidas em [`evidencias/medidas.json`](evidencias/medidas.json).

| Critério | Resultado |
|---|---|
| SC-001: 375×812, h1, frase e chamada sem rolar | passa |
| SC-002: 1280×720 e 1440×900, também a composição da abertura | passa |
| SC-003: sem rolagem horizontal, 320 a 1440 px, fonte a 100% e 200% | passa |
| SC-004: conteúdo ≥ 1000 px entre 1280 e 1440; duas colunas a partir de 1024 e uma no celular | passa |
| SC-005: linha até ~70 a 80 caracteres | passa |
| SC-006: um h1; alvos ≥ 44 px; contraste ≥ 4,5:1 nos pares novos | passa (menor contraste: 4,8:1) |
| SC-007: vocabulário vedado | teste |
| SC-008: selos e nenhum link para área inexistente ou site real | teste |

A página implementada reproduz o protótipo (`prototipo/proposta.html`).

## Roteiro manual com teclado (2026-10-11)

Executado no navegador embutido do aplicativo Claude (Chromium), em macOS, sobre a página
servida (commit `950aea6`, banco próprio com `preparar_demonstracao`). Teclas reais (Tab,
Shift+Tab e Enter), a 1280×800 e a 375×812. O foco foi conferido a cada passo pelo elemento
ativo e pelo estilo calculado.

| Passo | Resultado |
|---|---|
| Primeiro Tab | "Pular para o conteúdo" aparece com o foco da 015 (contorno de 3 px e halo amarelo) |
| Enter em "Pular para o conteúdo" | O foco vai para `main#conteudo` |
| Tab, Tab | "Conhecer o Portal" e depois "Ver como funciona", com foco visível nos dois. Alvos de 180×44 e 185×44 px |
| Enter em "Ver como funciona" | Leva a `#oferece` ("Oportunidades para a sua formação") por âncora, sem script. A seção fica no topo da janela |
| Tab depois da âncora | Vai direto à chamada final "Conhecer o Portal", o próximo elemento focável depois da seção |
| Shift+Tab | Volta para "Ver como funciona" |
| Enter na chamada final | Abre `/entrar/` ("Confirme seus dados para entrar no Portal do Egresso"), sem mudança |
| Ordem de foco | Pular → Conhecer o Portal → Ver como funciona → Conhecer o Portal (fim). É igual à ordem visual nas duas larguras. A composição decorativa e os exemplos não recebem foco |
| 375×812 | Mesma ordem, foco visível, sem rolagem horizontal |
| Página | 0 `script`, 0 formulário, 1 h1 |
| `/acesso/` | Continua indo direto à identificação da pesquisa ("Confirme seus dados para acessar a pesquisa"), sem a página pública (US3, cenário 3) |

Nenhum achado. Capturas do foco: [`teclado-foco-1280.png`](evidencias/capturas/teclado-foco-1280.png)
("Ver como funciona" com foco) e [`teclado-foco-375.jpg`](evidencias/capturas/teclado-foco-375.jpg)
("Conhecer o Portal" com foco).

## Diferenças em relação ao protótipo

- **Títulos dos itens de exemplo:** são h3 (no protótipo, h4), para seguir a hierarquia sob
  o h2 da seção.
- **Legenda do card:** "Card de exemplo. As formações e os dados são fictícios." vai como
  texto para leitor de tela; o selo visível continua.
- **Categoria do curso:** usa o rótulo da 025, "Cursos e formação continuada".

## Pendências

- **Checkpoint 1** (024 e bloco P): NÃO APLICADO. O material do bloco P foi revisto, e a 028
  aparece pela cópia estática [`prototipo/atual.html`](prototipo/atual.html).
- **D2 e DP-801:** textos provisórios. **DP-2106:** fotografias.
- **Roteiro manual com teclado:** executado em 2026-10-11, sem achados (ver acima). Leitor
  de tela real não foi testado; a árvore de acessibilidade é verificada pelos testes.
