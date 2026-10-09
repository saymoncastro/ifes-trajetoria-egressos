# Implementation Plan: Volte ao Ifes — o egresso se oferece para contribuir

**Branch**: `claude/029-pagina-publica` (documentos) | **Date**: 2026-10-09 | **Spec**: [spec.md](spec.md)

> **Situação.** Plan, tasks e protótipos revisados pelo solicitante em 2026-10-09.
> **Implementação autorizada no mesmo dia, só na demonstração**, em branch e PR próprios
> (T001 das [tasks](tasks.md); roadmap, revisão 10). O Checkpoint 1 continua **NÃO
> APLICADO** e será aplicado depois da 026 e da 029 implementadas. D4 e D5 continuam
> pendentes para uso real.

## Summary

A 026 abre o sentido egresso → Ifes do Portal: um egresso com Conclusão Acadêmica oferece uma
contribuição (lista fechada), indica a formação de referência e um e-mail para a resposta,
lê o texto de ciência e confirma. A unidade da formação recebe numa lista do seu escopo,
exporta CSV, faz o contato fora do sistema e registra o marco "contato feito", que o egresso
vê. O egresso pode retirar a qualquer momento.

- **Um modelo novo, `Manifestacao`, no app `trajetoria/portal`**, ao lado de `Oportunidade`.
  Migração aditiva, sem chave estrangeira para o núcleo (R2).
- **Subpacote `portal/contribuicao/`** no molde de `portal/oportunidades/`: regras,
  operações (único caminho de escrita), consultas, governança, formulários, mensagens, views
  do egresso e views da unidade.
- **E-mail próprio da contribuição** (D-2602), separado do `ContatoDaPessoa` da 020 (R3).
- **Ciência versionada** gravada na manifestação (XVII; R4).
- **Marco único "contato feito"** gravado pela unidade (D-2601; R5).
- **Bloco no Início** e item na navegação, só para quem tem Conclusão (R9, R10).

Nenhuma dependência nova, nenhum JavaScript, nenhuma mudança em Pessoa, Conclusão, Contato,
Campanha, Participação, snapshot ou exportação analítica.

## Technical Context

**Language/Version**: Python 3.13 (uv)

**Primary Dependencies**: Django 5.2. Nada novo (`tests/dependencias.py` inalterado). Da
biblioteca padrão: `csv`, `io`

**Storage**: PostgreSQL 16. Uma tabela nova, `portal_manifestacao`

**Testing**:
- pytest + pytest-django; regras e CSV testados sem banco;
- testes por requisição para o fluxo do egresso e as telas da unidade;
- Portal desligado com `pytest.mark.urls`, como na 024 e na 025;
- fronteira: núcleo sem menção ao Portal; analítico e mobilização sem a Manifestação;
- medidas no navegador a 375×812, 320 px com fonte a 200% e 1440×900

**Target Platform**: servidor Linux; navegadores atuais; sem JavaScript

**Project Type**: aplicação web Django renderizada no servidor

**Performance Goals**: sem meta nova. O Início ganha uma consulta (existe manifestação ativa?)

**Constraints**:
- só demonstração; camada desligável; o núcleo não cita a camada;
- o egresso grava só a própria manifestação e a retirada;
- ordem do Início preservada com o bloco novo; convite continua por último;
- textos provisórios (DP-801); vocabulário da ADR 0009 (decisão 7) e da 025

**Scale/Scope**:
- 1 modelo e 1 migração no `portal`;
- subpacote `portal/contribuicao/` com cerca de 8 módulos;
- cerca de 8 templates (5 do egresso, 3 da unidade);
- cerca de 7 arquivos de teste novos e 3 revisados (fronteira, Início, navegação)

## Pesquisa e decisões técnicas

| # | Decisão | Alternativas rejeitadas | Por quê |
|---|---|---|---|
| R1 | Modelo no app `portal`; lógica em `portal/contribuicao/` | App novo | Mesmo precedente da 025 (R1); a camada continua desligável em um lugar só |
| R2 | **Sem chave estrangeira** para o núcleo: `pessoa_id` e `conclusao_id` como UUID, mais `unidade` (texto) copiada da Conclusão no registro | FK para Pessoa e Conclusão | Mantém a regra da 025 e o teste de fronteira (que passa a admitir dois modelos, ambos sem FK). A integridade (a Conclusão é da Pessoa) é verificada em `operacoes.py`, único caminho de escrita. A unidade copiada define o escopo de quem recebe e não muda se a fonte for reimportada |
| R3 | **E-mail na manifestação**, obrigatório, sem pré-preenchimento, validado como na 020 | Ler ou gravar `ContatoDaPessoa` | O registro da 020 é imutável, entra na política de convites e a tela promete que não terá outra finalidade (D-2602). Validação reaproveitada da 020 (`contato/endereco.py`: `normalizar_email`, `email_valido`), sem gravar contato |
| R4 | Ciência: texto em `contribuicao/mensagens.py` com a constante `VERSAO_DA_CIENCIA`; a versão vai para a manifestação | Termo em tabela | Um texto por vez; versionar por constante basta para relacionar versão, momento e manifestação (XVII), sem modelo de termos |
| R5 | `contato_registrado_em` e `contato_registrado_por` (identificador opaco do operador), em par, uma vez | Tabela de eventos; estados | D-2601 pede um marco, não workflow. Mesmo padrão de `publicada_em`/`publicada_por` da 025 |
| R6 | Unicidade parcial: uma ativa por (`pessoa_id`, `conclusao_id`, `forma`) com `retirada_em IS NULL` | Validação só no formulário | Garante FR-006 no banco, inclusive em corrida de dois envios |
| R7 | Regra nomeada `pode_receber_contribuicoes` (CPAEG ou CSAEG ativo) e escopo de `escopo_de_acompanhamento`, em `contribuicao/governanca.py` | Regra em `trajetoria/governanca` | O núcleo não conhece competências da camada (precedente 025, R2) |
| R8 | CSV gerado na camada com `csv`, UTF-8, neutralizando fórmulas (`=`, `+`, `-`, `@`, tabulação, retorno) | Reaproveitar `exportacao` | A exportação analítica não pode conhecer a Manifestação (FR-016); a proteção contra fórmulas é testada aqui |
| R9 | Navegação ganha "Contribuir" depois de "Oportunidades", para quem tem Conclusão | Sem item na navegação | FR-011. Risco: seis itens no celular. Medir a 320 px com fonte a 200%; se passar de duas linhas, o rótulo fica "Contribuir" e a ordem não muda |
| R10 | Bloco "Contribuir com o Ifes" no Início, entre Oportunidades e o convite, com orçamento de 200 px a 375 px | Sem bloco | FR-011; o convite continua por último (ADR 0009, decisão 8). Com manifestação ativa, o bloco mostra "Suas contribuições" |
| R11 | Fluxo em três telas, sem estado em sessão: escolha (GET/POST) → confirmação (POST com campos ocultos validados de novo) → resultado (redirecionamento para o detalhe da própria manifestação) | Assistente com sessão | Sem JavaScript e sem estado oculto no servidor; a gravação revalida tudo (forma, Conclusão da Pessoa, e-mail, versão) |
| R12 | Rotas da unidade sob `/curadoria/contribuicoes/`, com a mesma escolha de operador da 025 (destino registrável) | Área nova | Uma área de operação do Portal; reaproveita o ponto neutro da 025 (R3 dela) |
| R13 | Demonstração: duas manifestações fictícias para o operador ver a lista, criadas pelo sinal `cenario_preparado` (precedente 025, R4) | Lista vazia | A tela da unidade precisa de conteúdo para ser avaliada |

## Modelo de dados

`Manifestacao` (tabela `portal_manifestacao`):

| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID | chave |
| `pessoa_id` | UUID | obrigatório; sem FK (R2) |
| `conclusao_id` | UUID | obrigatório; Conclusão da Pessoa, verificada na escrita |
| `unidade` | texto | copiada da Conclusão; define o escopo de quem recebe |
| `forma` | texto (`choices`) | lista fechada: `mentoria`, `experiencia`, `oportunidade`, `pesquisa_extensao`, `parceria`, `historia` |
| `mensagem` | texto | opcional; até 500 caracteres |
| `email` | texto | obrigatório; até 254; finalidade própria (D-2602) |
| `versao_da_ciencia` | texto | obrigatório |
| `registrada_em` | data e hora | obrigatório |
| `contato_registrado_em`, `contato_registrado_por` | data e hora, texto | em par ou ambos nulos; só uma vez |
| `retirada_em` | data e hora | nula enquanto ativa |

Restrições no banco: `forma` válida; tamanhos; par do contato coerente; unicidade parcial
(R6). Situação derivada: retirada se `retirada_em`; senão, contato registrado se
`contato_registrado_em`; senão, enviada.

## Rotas

| Rota | Método | Quem | O que faz |
|---|---|---|---|
| `/contribuir/` | GET, POST | Pessoa com Conclusão | Escolha da forma, da formação e da mensagem; POST válido mostra a confirmação |
| `/contribuir/confirmar/` | POST | idem | Confirmação com o texto de ciência e o e-mail; grava e redireciona ao detalhe |
| `/contribuicoes/` | GET | idem | "Suas contribuições" |
| `/contribuicoes/<uuid>/` | GET | dona | Detalhe e resultado: o que enviou, para quem, o que acontece depois, situação |
| `/contribuicoes/<uuid>/retirar/` | GET, POST | dona | Confirmação e retirada |
| `/curadoria/contribuicoes/` | GET | CPAEG/CSAEG | Lista das ativas do escopo |
| `/curadoria/contribuicoes/exportar.csv` | GET | idem | CSV das ativas do escopo |
| `/curadoria/contribuicoes/<uuid>/contato/` | GET, POST | idem, no escopo | Confirmação e registro do marco "contato feito" |

Fora do escopo ou de outra Pessoa: 404 (como a 025). Sem Conclusão: o fluxo não aparece e a
rota responde 404.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Verificação | Princípios | Pré | Pós | Evidência / observação |
|---|---|---|---|---|---|
| 1 | Longitudinalidade | I | ✅ | ✅ | A Manifestação não se liga a Participação nem a Campanha |
| 2 | Pessoa × Conclusão | I, XI | ✅ | ✅ | Uma manifestação, uma Conclusão de referência; a unidade vem dela (R2) |
| 3 | Múltiplas formações | XI | ✅ | ✅ | A pessoa escolhe a formação; unidades diferentes recebem manifestações diferentes |
| 4 | Definição de egresso | II | ✅ | ✅ | Só Pessoa com Conclusão; Formação Declarada fora (D-2603) |
| 5 | Preservação e migrações | VIII, XXVII | ✅ | ✅ | Tabela nova, migração aditiva; retirada e contato registram momento, nada é apagado |
| 6 | Pesquisa/Versão/Campanha/Participação | VII | ✅ | ✅ | Não lê nem altera; "Contribuir" não é a pesquisa (texto e Checkpoint 2) |
| 7 | Proveniência e tipos de dado | III, IV | ✅ | ✅ | A manifestação é declarada pela pessoa; a formação de referência é institucional |
| 8 | Fronteira e camada de relacionamento | VI; ADR 0008 | ✅ | ✅ | Tudo no `portal`; núcleo sem menção (teste); fora do analítico e da mobilização (teste); desligável |
| 9 | Governança e escopo | X, XII | ✅ | ✅ | Regra nomeada na camada; CSAEG por unidade; CPAEG institucional como hipótese (DP-2501) |
| 10 | Privacidade e minimização | XVI | ✅ | ✅ | Só o e-mail necessário à resposta; mensagem curta com orientação; CSV sem CPF nem nascimento; base legal e retenção pendentes (D5) |
| 11 | Consentimento identificável | XVII | ✅ | ✅ | Versão da ciência e momento na manifestação (R4) |
| 12 | Autorização | X, XII | ✅ | ✅ | Egresso: sessão da 018 e posse da manifestação. Operador: vínculos relidos a cada pedido e escopo revalidado na escrita |
| 13 | Acessibilidade | XX | ✅ | ✅ | `fieldset`/`legend`, erros associados, resumo de erros, 44×44 px, foco da 015, sem JavaScript |
| 14 | Mobile e esforço | XIV, XXI | ✅ | ✅ | Três telas; formação pré-selecionada quando há só uma; orçamento do bloco no Início (R10) |
| 15 | Testes | XXV, XXVI | ✅ | ✅ | Ver "Testes" |
| 16 | Over engineering | XXII | ✅ | ✅ | Um modelo; sem workflow, notificação, termos em tabela nem JavaScript |
| 17 | Exportações | XVIII | ✅ | ✅ | Só o CSV operacional da unidade; nada no analítico |
| 18 | Decisões pendentes | XXIX | ✅ | ✅ | D4, D5, DP-801 e DP-2501 com solução provisória (abaixo) |

**Resultado do gate**: APROVADO para planejamento. Nenhuma violação. As revisões de
requisitos anteriores estão listadas na spec ("Requisitos revisados").

## Testes

| Área | Casos |
|---|---|
| Regras (sem banco) | situação derivada; formas válidas; tamanhos; e-mail inválido; neutralização de fórmulas no CSV |
| Gravação | Conclusão de outra Pessoa recusada; Formação Declarada não oferecida; unicidade parcial (inclusive dois envios); versão da ciência gravada; unidade copiada |
| Fluxo do egresso | três telas; formação única pré-selecionada; erro de e-mail na confirmação mantém as escolhas; resultado mostra a unidade; retirada com confirmação; manifestação de outra Pessoa dá 404 |
| Unidade | CSAEG vê só o escopo; CPAEG vê tudo; sem vínculo, recusa; registrar contato uma vez, só ativa e só no escopo; CSV só ativas, sem CPF nem nascimento |
| Egresso vê o marco | depois de "contato feito", "Suas contribuições" mostra a data e a unidade |
| Fronteira | núcleo sem menção ao Portal; `ContatoDaPessoa` inalterado ao contribuir; política de convites ignora o e-mail da contribuição; analítico e exportações sem a Manifestação; dois modelos no `portal`, sem FK; migração só aditiva |
| Portal desligado | rotas da 026 inexistentes; Início e coleta inalterados |
| Início e navegação | ordem com o bloco novo e convite por último; bloco ausente sem Conclusão; item na navegação; orçamento de 200 px |
| Vocabulário | sem promessa de resposta, prazo, vaga, remuneração ou certificado; vedações da ADR 0009 e da 025 |

## Critérios de entrega (antes do merge da implementação)

1. `ruff check .`, `manage.py check`, `makemigrations --check --dry-run` e a suíte completa
   passam, com o número de testes registrado na `validacao.md`.
2. Capturas do percurso do egresso (375×812 e 1440×900) e da unidade (1280×720), comparadas
   com os [protótipos](prototipo/index.html).
3. Medidas: sem rolagem horizontal de 320 a 1440 px com fonte a 200%; bloco do Início dentro
   do orçamento; navegação em até duas linhas a 375 px; alvos de 44 px; um h1 por tela.
4. Roteiro manual com teclado: contribuir, ver, retirar; operador registra contato e
   exporta.
5. Nenhuma escrita além da Manifestação, da retirada e do marco de contato (contagens antes e
   depois, como no teste `test_portal_nao_grava`).

## Sequência com a 029

1. **026 implementada e integrada** (autorizada em 2026-10-09, só na demonstração).
2. **029 incorpora "Contribuir com o Ifes"**: a seção "Como você participa" ganha a
   contribuição com o mesmo peso de Oportunidades (029 FR-006); o protótipo é regerado; o
   bloco P passa a aceitar "contribuir" em P-01.
3. **029 implementada** (autorização separada, ainda não dada), já com a contribuição.
4. **Checkpoint 1** (024 + bloco P) sobre a experiência implementada. Isso muda a ordem
   anterior do roadmap (§8) e da 029 (spec → protótipos → Checkpoint 1 → implementação):
   a decisão de 2026-10-09 (revisão 10) troca o teste sobre protótipos pelo teste sobre o
   que existe, como já se fez com a 025.
5. **Checkpoint 2** (roadmap §7): valor recebido e reciprocidade, com a 025 e a 026.

Se a 029 for implementada antes da 026, ela sai sem a contribuição, e o passo 2 vira uma
mudança pequena de template e texto quando a 026 entrar.

## Decisões Pendentes

| ID | DECISÃO PENDENTE | Instância | Solução provisória (hipótese) | Como reverter |
|---|---|---|---|---|
| D4 | Quem recebe na operação real | Proex/CPAEG | CSAEG da unidade; CPAEG vê tudo | `contribuicao/governanca.py` |
| D5 | Base legal do e-mail da contribuição; retenção depois da retirada | Proex/CPAEG, encarregado de dados | Só demonstração; nada é apagado | Política futura; o e-mail pode ser anonimizado na retirada sem migração destrutiva |
| DP-801 | Redação das formas, da ciência e dos textos | CPAEG, ACS | Textos provisórios em `mensagens.py` | Trocar textos e subir a versão da ciência |
| DP-2501 | Atuação institucional da CPAEG | CPAEG, Proex | CPAEG vê todas | `governanca.py` |
| Checkpoint 1 | — | — | NÃO APLICADO | — |

## Project Structure

```text
specs/026-volte-ao-ifes/
├── spec.md
├── plan.md
├── tasks.md
└── prototipo/          # telas estáticas do egresso e da unidade (gerar.py, index.html)

trajetoria/portal/
├── models.py                       # + Manifestacao
├── migrations/0002_manifestacao.py
├── urls.py                         # + rotas da 026
├── contribuicao/
│   ├── regras.py                   # situação, formas, validação
│   ├── operacoes.py                # registrar, retirar, registrar contato (único caminho de escrita)
│   ├── consultas.py                # da Pessoa; do escopo
│   ├── governanca.py               # pode_receber_contribuicoes, escopo
│   ├── formularios.py
│   ├── csv.py                      # exportação da unidade, com neutralização de fórmulas
│   ├── mensagens.py                # textos e VERSAO_DA_CIENCIA
│   ├── demonstracao.py             # manifestações fictícias (sinal cenario_preparado)
│   ├── views_egresso.py
│   └── views_unidade.py
└── templates/portal/contribuicao/  # escolha, confirmar, detalhe, lista, retirar; unidade: lista, contato

tests/portal/
├── test_contribuicao_regras.py
├── test_contribuicao_egresso.py
├── test_contribuicao_unidade.py
├── test_contribuicao_fronteira.py
└── (revisados) test_fronteiras.py, test_inicio.py, test_navegacao.py
```

## Complexity Tracking

| Item | Por que é necessário | Alternativa mais simples rejeitada |
|---|---|---|
| Segundo modelo na camada e primeira escrita do egresso | É o fato que a S3 exige (roadmap) | Sem gravação, não há contribuição |
| E-mail guardado na manifestação | D-2602 e a promessa de finalidade da 020 | Reusar `ContatoDaPessoa` mudaria a finalidade daquele registro |

## Riscos de implementação

- **Expectativa frustrada** (ninguém responde): texto honesto sem prazo; o marco "contato
  feito" dá retorno visível; D4 decide quem recebe na operação real.
- **Navegação com seis itens** no celular: medida no critério de entrega (R9).
- **Tabela da unidade larga demais**: a folha da curadoria (025) impede quebra de linha nas
  células da tabela. A lista de contribuições usa cinco colunas, com e-mail sob o nome e
  mensagem sob a forma, e libera a quebra de linha só nessa tabela (protótipo u1).
- **Dado sensível na mensagem**: orientação na tela e limite de 500 caracteres.
- **Portal vazio para a unidade**: manifestações fictícias na demonstração (R13); na
  operação real, depende de divulgação.
