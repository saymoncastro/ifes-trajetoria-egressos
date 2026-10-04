# Auditoria arquitetural — Feature 019: formação não localizada e validação posterior

Data: 2026-10-04 · Base: `main` em `2f1ee86` (PR #28, Feature 018 mergeada).

Este documento só faz diagnóstico. Prepara a spec da Feature 019. Nada foi implementado,
nenhum plan, task, migração ou commit foi produzido, e a Constituição não foi alterada.

**Revisão de 2026-10-04.** Depois da primeira versão, o solicitante confirmou B′, trocou M1
por **M1+** (acervo histórico como fonte institucional) e corrigiu a regra de abrangência
(compatibilidade provisória e definitiva). As §§ 1, 6 e 8 a 13 refletem essas decisões. A
§13 registra as decisões.

**Segunda revisão (2026-10-04).** A hipótese "só HMAC" para CPF e data do declarante foi
abandonada. HMAC é irreversível, e quem valida precisa consultar o acervo por CPF e data.
Agora há dois usos separados:

- os HMACs continuam para candidatas, retomada e agrupamento;
- CPF e data passam a ser guardados com **criptografia reversível em nível de aplicação**,
  num conjunto próprio de dados para consulta ao acervo, com acesso restrito e registrado.

As §§ 2, 4, 8.2, 8.3, 12 e 13 foram ajustadas. A spec correspondente é a
[019](../../specs/019-formacao-declarada-validacao/spec.md).

**Fontes lidas**:

- Constituição 1.0.0.
- Specs 001, 002/003 (Versão e baseline 2024), 004, 005, 006, 007, 008, 010, 011, 012, 013,
  017 e 018.
- ADRs 0002 e 0004.
- [Auditoria de identidade e acesso](2026-10-03-identidade-acesso-egresso.md) e o adendo
  dela.
- [Inventário do formulário 2024](../referencias/formulario-egresso-ifes-2024-inventario.md).
- Código em `academico`, `fonte_academica`, `acesso`, `participacao`, `interface`,
  `campanha`, `governanca`, `acompanhamento`, `analitico`, `exportacao`,
  `formulario_2024` e `demonstracao`.

**Decisões do solicitante preservadas** (2026-10-03 e 2026-10-04):

- Identidade, formação, participação e respostas são conceitos diferentes.
- Há uma única Versão do instrumento por Campanha. Não existe questionário próprio para
  quem não tem formação localizada.
- Dados acadêmicos não pertencem ao instrumento. Quando conhecidos, vêm de
  `ConclusaoAcademica`. Quando não, vêm de `FormacaoDeclarada`.
- A baseline 2024 fica intacta.
- O egresso responde de imediato, antes da validação. Enquanto ela não sai, a resposta
  fica fora da análise oficial.
- A validação libera a resposta sem nova ação do egresso.
- A declaração original nunca é sobrescrita.
- Mobilização e Lote não interferem na validade da resposta.
- Nenhuma Pessoa é criada ou alterada só porque alguém declarou.
- Regras acordadas para a 019 no adendo da auditoria de identidade:
  - mensagem única;
  - quarentena;
  - "Conferir os dados" vem antes;
  - Pessoa só na validação.

---

## 1. Objetivo e fronteira exata

**Objetivo.** Permitir que o egresso cuja verificação na 018 resultou em `NAO_CONFIRMADA`:

- informe o contexto acadêmico mínimo da formação;
- responda imediatamente à mesma Versão aplicada pela Campanha;
- vá embora sem precisar retornar.

A instituição valida a formação depois. A resposta só entra nos dados analíticos
oficiais quando a formação estiver vinculada a uma `ConclusaoAcademica`.

**Dentro da 019**:

1. Caminho "Informar minha formação" a partir de `NAO_CONFIRMADA`, e só a partir dele
   (018 FR-035).
2. `FormacaoDeclarada`: imutável, dado declarado (Princípio III, categoria C).
3. Participação com formação declarada, que usa a jornada existente (005/006/008).
4. Quarentena analítica até a validação.
5. Fila "Validações de formação" e registro do resultado obtido junto à instância
   competente.
6. Vínculo `FormacaoDeclarada → ConclusaoAcademica` na confirmação, com a declaração
   preservada.
7. Situação analítica derivada:
   - pendente;
   - validada;
   - não confirmada;
   - fora da abrangência;
   - em conflito.
8. Ajustes de leitura em 007, 011, 012 e 013.

**Fora da 019**:

- Gov.br, OTP ou outra garantia de identidade.
- Notificação ao egresso.
- Canal de atendimento.
- Reabertura de decisão.
- Resolução do conflito por troca da Participação que conta.
- Material de acesso derivado da declaração para o egresso entrar pelo caminho principal
  na próxima rodada.
- Cadastro manual de Conclusão pelo operador. A confirmação só vincula uma Conclusão
  vinda da fonte digital ou da fonte institucional de acervo histórico (M1+, §8.3).
- Lote e mobilização real.
- Nova Versão do instrumento.

---

## 2. Inventário do que existe e pode ser reutilizado

| Capacidade | Onde | Reuso na 019 |
| --- | --- | --- |
| Escritas de Resposta e conclusão | `participacao/operacoes.py` (`_escrever`, `concluir`) | **Integral.** Dependem só de `Participacao.campanha` (Versão, coleta) e de `concluida_em`, nunca da Conclusão. Linhas 160-198 e 404-438 |
| Percurso, Seções, pendências e condicionais | `participacao/percurso.py`; 006 FR-006 a FR-008 | **Integral.** A 006 FR-007 proíbe que dado da Conclusão escolha ou pule Seção |
| Telas da jornada (Seção, conclusão, confirmação) | `interface/views.py`, `interface/gravacao.py`, `interface/formularios.py` | **Quase integral.** Mudam dois pontos: a posse (`conclusao__pessoa=pessoa`, linhas 81-92) e a fonte do contexto exibido (`participacao.conclusao`, 11 pontos) |
| Admissão (`iniciar_participacao`) | `operacoes.py:121-148` | **Não reusável como está.** Exige `ConclusaoAcademica` e avalia critérios sobre ela. Precisa de um início declarado irmão |
| Entrada e formações (007) | `participacao/entrada.py` | O **modelo mental** é reusado: lista de formações e situações. O código é da Pessoa e continua só dela |
| Verificação e saída `NAO_CONFIRMADA` | `acesso/verificacao.py`, `acesso/views.py:52-53` | Ponto de extensão previsto (018 FR-035). `verificar` não muda |
| HMAC de CPF e de CPF + data | `acesso/chaves.py` | Reusável para **identificar a declaração** (sessão, retomada, agrupamento) e para **sugerir candidato** ao validador, sem descriptografar nada. **Não serve para a busca no acervo**: é irreversível (§4) |
| Padrão de chave externa validada antes do uso | `exportacao/pseudonimos.py`; `acesso/chaves.py`; 018 FR-012 | Mesmo padrão para a chave de criptografia dos dados de consulta ao acervo, distinta das demais |
| Limitação de tentativas | `acesso/limitacao.py` | Vale para o caminho declarado, que só nasce após uma avaliação contada |
| Sessão do egresso | `acesso/sessao.py` | Hoje só identifica Pessoa. Precisa de um segundo tipo de sujeito: o declarante |
| Incorporação idempotente sob referência | `academico/incorporacao.py`; `acesso/material.py:74-98` (`incorporar_com_material`); `fonte_academica/contrato.py:86-117` (`obter_conclusao`) | **Reusável para a validação.** O operador informa a referência da formação na fonte. O sistema localiza a Conclusão ou a incorpora pelo caminho existente. Hoje nada no produto dispara isso |
| Governança e escopo | `governanca/regras.py`, `acompanhamento/acesso.py` | Nova capacidade nomeada, com barreira no padrão `@acompanhamento` |
| Snapshot e dataset (012) | `analitico/*` | Reusável, com ajuste do universo e do vínculo Participação ↔ registro |
| Exportação (013) | `exportacao/*` | Reusável, com uma coluna base nova e nova `VERSAO_CONTRATO` |

**O que não existe e a 019 precisa criar**:

- `FormacaoDeclarada`;
- o registro da validação;
- o sujeito de sessão "declarante";
- a fila;
- a situação analítica derivada.

---

## 3. Perguntas de formação do instrumento 2024

A baseline 2024 continua com Q10 a Q19 como Perguntas, classificadas pela 003 como
`CANDIDATA_A_CONTEXTO_INSTITUCIONAL` (003 FR-029). A Campanha de demonstração aplica uma
cópia dessa baseline. **Consequência transitória:** quem declara a formação também
responderá Q10 a Q19 enquanto a Campanha usar a cópia 2024, assim como já acontece com quem
tem Conclusão. A 019 **não** altera o instrumento. A retirada é trabalho da nova Versão
(CPAEG).

| Pergunta 2024 | Classe | Destino |
| --- | --- | --- |
| Q10 — ano de conclusão | **1. Contexto acadêmico** | `FormacaoDeclarada.ano_conclusao`. Consumidores: busca no acervo, fila e divergência |
| Q11 — campus | **1. Contexto acadêmico** | `FormacaoDeclarada.unidade`. Consumidores: **encaminhamento à unidade** (escopo CSAEG), busca e divergência |
| Q14 — "questionário" (= nível, O-13) | **1. Contexto acadêmico** | `FormacaoDeclarada.nivel`. Consumidores: busca, divergência e escolha da lista de curso |
| Q15, Q17, Q18, Q19 — curso | **1. Contexto acadêmico** | `FormacaoDeclarada.curso`, em texto. As listas 2024 são estáticas e mantidas à mão (O-14). Servem de sugestão, nunca de catálogo |
| Q12 — modalidade | 3. Decisão institucional | **Não coletar na 019.** Não tem consumidor para encaminhar nem para buscar que nome, curso, unidade e ano não cubram. A Conclusão confirmada traz a modalidade. Coletar só se o registro acadêmico disser que precisa (DP-1906) |
| Q16 — forma de oferta | 3. Decisão institucional | Mesmo tratamento de Q12 |
| Q13 — forma de ingresso / cotista | **2. Dado metodológico** e 3 | Não identifica a formação e não entra na declaração. Mistura dimensões (O-12) e a 001 não modela ingresso. Se continua como Pergunta na nova Versão é decisão da CPAEG |
| Q22–Q24, Q27, Q31, Q32 (extensão, monitoria, estágio...) | **2. Dado metodológico** | Continuam Perguntas. Não identificam a formação |
| Q47, Q49, Q51 (estudos posteriores) | **2. Dado metodológico** | Continuam Perguntas |

---

## 4. Modelo mínimo proposto para `FormacaoDeclarada`

Natureza: **dado declarado** (Princípio III, C). Nunca é institucional e nunca serve de
contexto oficial. É imutável a partir da criação: nem o declarante nem o operador a
editam.

| Campo | Obrigatório | Consumidor verificado |
| --- | --- | --- |
| Nome completo declarado | Sim | Busca no acervo do registro acadêmico. Sem nome não há busca em registro em papel |
| Unidade | Sim | Escopo da fila por CSAEG (010 FR-015/FR-017) e busca. Vocabulário igual ao de `ConclusaoAcademica.unidade` (DP-1005, 001/DP-007) |
| Nível | Sim | Busca e comparação |
| Curso (texto) | Sim | Busca e comparação |
| Ano de conclusão | Sim | Busca e comparação |
| Identificador protegido do CPF (HMAC, chave de localização da 018) | Sim | (a) sugerir ao validador a Pessoa com o mesmo CPF; (b) agrupar declarações do mesmo declarante |
| Verificador protegido de CPF + data (HMAC, chave de verificação da 018) | Sim | Identificar o declarante na sessão e na retomada |
| Momento da declaração | Sim | Proveniência (Princípio IV) |

**Declarado ≠ confirmado.** A declaração nunca recebe valores corrigidos. O valor
institucional confirmado fica na `ConclusaoAcademica` vinculada pela validação, e a
**divergência é derivada** da comparação entre as duas, campo a campo. Ela não é
armazenada como estado.

**CPF e data para a busca no acervo: dois usos, dois mecanismos.**

*Revisado. A primeira versão propunha guardar só HMAC e deixar o operador conferir o que
lesse no acervo. Isso falha no caso central: HMAC é irreversível, e o registro acadêmico
precisa **do CPF e da data** para procurar o egresso no acervo. O consumidor de valor
recuperável agora está verificado: é a busca humana no acervo.*

| Uso | Mecanismo | Quem usa |
| --- | --- | --- |
| **Identificação e comparação**: candidatas, retomada, agrupamento | HMAC (irreversível), chaves da 018 | O sistema, sem descriptografar nada |
| **Consulta ao acervo** | **Criptografia reversível em nível de aplicação**, com chave própria externa ao banco e distinta das chaves da 018, da pseudonimização e do framework | Operador autorizado, só na tela de validação de uma declaração |

**Dados para consulta ao acervo.** É um conjunto separado da declaração, com CPF e data de
nascimento criptografados.

- **A que pertencem.** Exclusivamente ao contexto de validação da formação. Nunca a
  Pessoa, Resposta, instrumento ou material de verificação, nem depois da confirmação.
- **Revelação.** Os valores aparecem descriptografados só por ação explícita do operador
  autorizado, no seu escopo, na tela de validação de uma declaração. Nunca na lista.
- **Registro de acesso.** Cada revelação registra quem viu, qual declaração e quando, sem
  os valores.
- **Onde nunca aparecem.** Logs, URLs, analytics, acompanhamento, snapshots, exportações e
  telas do declarante.
- **Descarte.** O conjunto é separável: pode ser descartado (política de retenção:
  DP-1903) sem tocar declaração, decisão, Participação ou Respostas.
- **Chave indisponível ou inválida.** O caminho de declaração fica temporariamente
  indisponível e nada é gravado. CPF e data nunca são gravados em claro como alternativa.
  Na tela de validação, a revelação fica indisponível.

**Relação com a 018.** 018 FR-010 continua valendo: nada é persistido em claro. A 019
acrescenta um **segundo tratamento, com finalidade distinta** (validação humana) e
retenção controlada. Isso exige registro em DP-1903 (base legal e retenção), que bloqueia
o uso real.

**Não coletar**: e-mail, telefone (não há notificação, DP-1908), matrícula (o egresso
raramente lembra; Princípio XIV), modalidade, forma de oferta e ingresso.

**Relação com Pessoa.** Nenhuma. A declaração não cria nem altera Pessoa (adendo, regra 2).
A Pessoa só aparece pela Conclusão vinculada na validação.

---

## 5. Onde a resposta "mora" antes da validação: alternativas

### Fatos do código e das specs que decidem a comparação

- **F-1.** A jornada inteira não depende da Conclusão:
  - escritas e conclusão dependem só da Participação, da Campanha e da Versão;
  - a admissão é o único ponto que exige `ConclusaoAcademica`.

  Fontes: `operacoes.py:160-198`, `:404-438`; 006 FR-006 a FR-008.
- **F-2.** A 005 FR-002 diz: Campanha e Conclusão são "ambas obrigatórias e **nunca
  alteradas depois da criação**". A 006 FR-035 preserva a Conclusão na conclusão.
  Religar uma Participação viola duas specs, e não só a "imutabilidade da 006".
- **F-3.** A 012 encontra a Participação de cada registro **na leitura**, por
  `(campanha, conclusao_id)` (`analitico/consultas.py:164-166, 184`). Toda mudança
  posterior no vínculo altera a leitura de um snapshot antigo. Isso viola a 012 FR-050 e a
  FR-080.
- **F-4.** A 001 FR-030 proíbe criar Conclusão fora da fonte. A 007 FR-010 proíbe
  "formação manual, provisória ou declarada" na entrada da 007.
- **F-5.** A Constituição define, de forma NON-NEGOTIABLE:
  - **Terminologia, Participação**: "ocorrência concreta de acompanhamento de determinada
    Conclusão Acadêmica".
  - **Terminologia, Resposta**: "informação declarada pelo participante em determinada
    Participação".
  - **Princípio I**: toda Participação relacionada a uma formação identifica a Conclusão
    observada.
  - **Princípio VII**: toda Resposta pertence à Participação e à Versão.

### Alternativa A — coleta provisória antes da Participação

```text
FormacaoDeclarada → ColetaPendente → RespostaPendente → validação → ConclusaoAcademica
                                                                   → materializa Participacao + Respostas
```

### Alternativa B — Participação com formação pendente, religada na validação

```text
Participacao(conclusao NULL, formacao_declarada) ──validação──► Participacao.conclusao := X
```

### Alternativa B′ — Participação com formação declarada, vinculada pela validação, nunca religada (recomendada)

```text
Participacao ── conclusao (institucional)          XOR  formacao_declarada
                                                            │
                                         ValidacaoDaFormacao (registro imutável)
                                                            │ CONFIRMADA
                                                            ▼
                                                    ConclusaoAcademica X
Conclusão efetiva da Participação = conclusao  OU  validação.conclusao
```

A Participação nunca muda depois de criada. O vínculo institucional mora na validação, e a
conclusão efetiva é **derivada** dela.

### Comparação

| Critério | A — coleta provisória | B — religar | B′ — vincular pela validação |
| --- | --- | --- | --- |
| Constituição | Emenda: Resposta fora de Participação viola a Terminologia e o VII (NON-NEG). Materializar depois cria Participação com fatos passados | Emenda do I e da Terminologia (Participação sem Conclusão até a validação) | Mesma emenda de B, e só ela |
| 005/006 | Duplica tabelas de Resposta ou generaliza a FK de Resposta (refatoração da 005/006/012/013). A materialização precisa contornar a admissão: com a Campanha encerrada, `iniciar_participacao` recusa | Viola 005 FR-002 e 006 FR-035 ao religar | Revisão da 005 FR-002: "uma Conclusão **ou** uma Formação Declarada, nunca alteradas". Escritas e conclusão ficam intactas |
| Reuso da jornada | Baixo: tela, validação, percurso e gravação teriam de operar sobre outro contêiner | Alto | Alto. Muda a posse e a origem do contexto exibido |
| Duplicação de lógica | Alta (validadores, percurso, conclusão e limpeza de inativas) | Baixa | Baixa: só um "início declarado" irmão de `iniciar_participacao` |
| Imutabilidade após conclusão | A materialização cria registros novos datados no passado, com proveniência ambígua | **Quebrada** | Preservada |
| Concorrência | Materialização × início institucional disputam `UNIQUE(campanha, conclusao)`, com erro em plena validação | Religação × início institucional: idem | Sem religação, não há disputa pela unicidade. O conflito é detectado e registrado na validação (§9). O início institucional passa a considerar a Participação declarada confirmada |
| Colisão com Participação existente | A materialização falha ou exige escolha | A religação falha pela unicidade ou exige fusão | Representável: os dois registros coexistem e o conflito fica fora da análise |
| 012 | Universo inalterado, mas a materialização tardia muda a leitura de snapshots | Mudar `conclusao` altera a leitura de snapshot antigo (F-3) | O universo usa só as Participações oficiais. O snapshot **congela** qual Participação compõe cada registro (§10) |
| 013 | Sem coluna de origem: a proveniência se perde na materialização | Idem | Coluna base de origem da formação, com nova `VERSAO_CONTRATO` |
| Migração e reversibilidade | Tabelas novas; reverter exige apagar coletas | `conclusao` anulável; reverter é impossível depois de religar | Aditiva: `conclusao` anulável e FK nova anulável, com CHECK de exatamente uma. Dados existentes são todos institucionais. Reverter é trivial enquanto não houver declaração |
| Operação | Duas filas mentais (coleta e Participação) | Simples, porém destrutiva | Simples: a declaração é uma Participação comum com situação analítica derivada |
| YAGNI | Infraestrutura paralela sem novo comportamento | — | O mínimo: dois registros novos e uma derivação |

**Terceira via examinada e descartada.** Uma `ConclusaoAcademica` provisória foi vetada
pelo solicitante: Conclusão é fato institucional. Também se avaliou uma "Formação
acompanhada" genérica, abstraindo Conclusão e Declaração. Ela é B′ com uma camada a mais
e sem consumidor (XXII).

---

## 6. Recomendação arquitetural

**B′**, com **M1+** para a origem da Conclusão confirmada (§8.3).

- A Participação nasce com uma `FormacaoDeclarada` em vez de uma Conclusão.
- A jornada é a mesma.
- A validação é um registro próprio, imutável, que liga a declaração a uma
  `ConclusaoAcademica`.
- A Participação nunca é alterada.
- A situação analítica é derivada e só a Participação **oficial** integra 011 (contagens
  oficiais), 012 e 013.

Isso exige **emenda constitucional** (§11). A emenda é pequena e honesta, e é exigida
também por A, onde aparece disfarçada.

---

## 7. Jornada do egresso

```text
018: CPF + data → NAO_CONFIRMADA
     "Não foi possível confirmar os dados informados."
     [Conferir os dados]  (vem antes, como na 018)
     [Informar minha formação]   ← novo; só neste resultado; nunca em
                                    VERIFICACAO_INDISPONIVEL nem em formato inválido
        │  (o par digitado segue no corpo do POST, nunca na URL; o servidor reavalia:
        │   se o par agora confirma, entra pelo caminho principal)
        ▼
Declarações deste CPF + data (só se já houver)
     "Formação informada por você: Técnico em Informática — Serra — 2004"
       · em andamento → [Continuar]
       · respondida   → "Resposta registrada; a formação passará por verificação."
     [Informar outra formação]
        ▼
Informe sua formação no Ifes
     Nome completo · Unidade (lista) · Nível (lista) · Curso (texto com sugestões) · Ano
        ▼
Campanha aplicável (sem critério; §8.1)
     0 → "Não há pesquisa disponível no momento."  (nada é gravado)
     2+ → ambiguidade operacional, como na 007     (nada é gravado)
     1 → [Começar]  → cria, numa transação, FormacaoDeclarada + Participação
        ▼
MESMA jornada da 008 (Seções, rascunho, conclusão)
     contexto: "Formação informada por você: …"  (nunca "você concluiu")
        ▼
"Obrigado. Sua resposta foi registrada.
 A formação informada passará por verificação institucional."
```

**Regras da jornada**:

- **Nunca dizer que a formação foi validada.** Nunca revelar se o CPF existe na base,
  nem a causa interna da `NAO_CONFIRMADA`, nem a existência de Pessoa.
- **Sessão do declarante.** Identifica só o par protegido (HMACs). Não guarda CPF nem data
  em claro, nem Pessoa. Expira com os parâmetros da 018.
- **Retomada e duplicidade.** O mesmo par CPF + data reencontra as próprias declarações em
  Campanha em coleta. Mostrar a declaração e o rascunho a quem conhece o par é o mesmo
  risco residual aceito na 018 (rascunho retomável).
- **Imutabilidade.** A declaração é imutável a partir do "Começar". Um erro de digitação é
  tratado na validação, como divergência.
- **Sem declaração órfã.** Desistir antes de "Começar" não grava nada.

**Quarentena.** A declaração nunca aparece para a Pessoa institucional enquanto pendente:
não vira "já respondida" na 007. Isso segue o adendo, regra 2.

---
## 8. Abrangência, fila e validação administrativa

### 8.1 Abrangência: compatibilidade provisória e definitiva

*Revisado em 2026-10-04 por decisão do solicitante. A versão anterior restringia a
declaração a Campanhas sem critério, o que contraria a ADR 0004: um egresso antigo de
pós-graduação não pode ser impedido de declarar justamente porque o instrumento é da
pós-graduação.*

**Campanha sem critério.** Admite a declaração; não há o que avaliar.

**Campanha com abrangência restrita.** Há duas avaliações.

- **Compatibilidade provisória**, no início:
  - Os valores **declarados** são avaliados com a semântica da 004: E entre critérios, OU
    dentro do conjunto, igualdade exata.
  - Unidade e nível são escolhidos em listas do mesmo vocabulário da Conclusão, para que
    a igualdade faça sentido.
  - Critério sobre atributo que a declaração não coleta (modalidade, forma de oferta) não
    impede o início. Ele fica para a compatibilidade definitiva.
- **Escolha da Campanha:** a mesma regra da 007.
  - nenhuma Campanha compatível: "sem pesquisa disponível", e nada é gravado;
  - uma: o egresso pode começar;
  - duas ou mais: ambiguidade operacional, e nada é gravado.
- **População.** A compatibilidade provisória **não** coloca a declaração na população da
  Campanha. `populacao_no_momento` e a 004 FR-016/FR-017 continuam valendo para a
  população. Só a regra de **admissão** de Participação ganha um caminho declarado.
- **Compatibilidade definitiva**, na confirmação:
  - A Conclusão vinculada é avaliada contra os critérios, que estão congelados desde a
    abertura (004).
  - Se for incompatível, a Participação fica `DECLARADA_FORA_DA_ABRANGENCIA`: preservada,
    mas não é resposta válida daquela Campanha.
  - Nada é desfeito nem migrado para outra Campanha.

Foco de mobilização e Lote nunca entram em nenhuma das duas avaliações (ADR 0004).

### 8.2 Fila "Validações de formação"

- **Lugar.** Área própria (conceitualmente `/validacoes-formacao/`), com escopo de
  governança.
  - No acompanhamento da 011 aparece só um **indicador agregado com link**, por exemplo
    "Validações de formação — 12 pendentes", no escopo do operador. A 011 FR-080/FR-084
    continuam valendo para a 011.
- **Conteúdo.** Declarações cuja Participação está **concluída** e ainda sem decisão.
  Rascunho não entra, porque não há resposta completa a liberar.
- **O que o operador vê:**
  - nome declarado;
  - unidade, nível, curso e ano declarados;
  - momento;
  - Campanha;
  - candidatos sugeridos.
- **O que o operador nunca vê:**
  - Respostas (010 FR-033; 005/DP-505);
  - HMACs;
  - CPF e data na lista. Na tela de validação de uma declaração, o operador autorizado vê
    CPF e data descriptografados só por ação explícita, e cada revelação é registrada
    (§4).
- **Candidatos sugeridos.** Se o identificador protegido do CPF declarado coincide com o
  de uma Pessoa importada, as Conclusões dela aparecem como candidatas. Isso nunca é
  revelado ao declarante.
- **Escopo:**
  - a CPAEG vê todas;
  - a CSAEG vê as declarações da unidade declarada que está no seu vínculo;
  - a CSAEG só vincula Conclusão da sua unidade e só registra acervo da sua unidade;
  - os demais casos ficam para a CPAEG.

  Isso é hipótese e depende de DP-1901.
- **Capacidade nova.** `pode_validar_formacao`, função nomeada da 010, para CPAEG e CSAEG.
  Significa **registrar o resultado obtido junto à instância competente**, não atestar
  (Princípio X).
- **Superfície nominal.** É a primeira do sistema. Depende de DP-1902; só dados fictícios
  até lá.
- **Sem workflow.** Não há estados "recebida", "em análise", "aguardando secretaria" ou
  "homologação". Sem decisão, a declaração continua PENDENTE.

### 8.3 Registro da validação — M1+

```text
[validar]
  Declaração do egresso (somente leitura)
  Resultado:  ○ Formação confirmada   ○ Formação não confirmada
  Se confirmada, a Conclusão vem de:
     (a) ConclusaoAcademica já existente  → candidato sugerido, ou referência na fonte
                                              acadêmica digital (localiza ou incorpora
                                              pelo caminho existente da 001)
     (b) Acervo histórico                   → registro da referência institucional do
                                              acervo → incorporação pela fonte
                                              ACERVO_HISTORICO (001) → Conclusão
  [Registrar validação]
```

**Por que (b) não é cadastro manual de Conclusão.**

- O operador **não** cria `ConclusaoAcademica`. Ele registra a **Referência de acervo
  histórico**: o resultado obtido no acervo, com a referência que o identifica.
  - Exemplos de referência: livro, folha, registro, processo. A forma é DP-1904.
  - Valores confirmados: unidade, nível, curso, ano de conclusão. Modalidade, forma de
    oferta e data entram quando o acervo informar.
- Esse registro é o **dado de uma fonte acadêmica institucional própria**, conceitualmente
  `ACERVO_HISTORICO`.
- Um adaptador da fronteira da 001 (Princípio V), com o mesmo contrato da fonte simulada e
  da fonte real, entrega o registro ao núcleo. A Conclusão nasce **somente** pela
  incorporação idempotente da 001, com `fonte` igual ao acervo histórico e referência de
  origem própria.
- A **Formação Declarada nunca é fonte** da Conclusão. O formulário do acervo **não é
  pré-preenchido** com os valores declarados, para que o declarado não vire institucional
  por cópia (Princípio III). O declarado aparece ao lado, só para leitura.
- 001 FR-030 continua vedando cadastro manual de Pessoa e Conclusão. A revisão necessária
  é acrescentar que fontes institucionais podem incluir o acervo histórico atestado pelo
  registro acadêmico.
- **Fronteira do NIAE** (Princípio VI). O NIAE guarda só a referência atestada necessária
  para incorporar. Não é sistema de registro acadêmico.
  - Quando houver digitalização institucional do acervo, uma fonte institucional poderá
    substituir esse registro sem tocar o núcleo (DP-1911).

**Pessoa na fonte de acervo.**

- A fonte entrega cada Referência de acervo como uma pessoa com uma Conclusão.
- Se já existir Pessoa de outra fonte para o mesmo indivíduo (candidata por CPF), a
  associação é **reconciliação entre fontes** (001/DP-003). A 019 sinaliza a provável
  coincidência, mas **não funde**.
- A cadeia Conclusão → Participação → Respostas fica correta. Só a ligação entre
  formações da mesma pessoa em fontes diferentes espera a reconciliação (DP-1909).

| Resultado registrado | Efeito |
| --- | --- |
| **CONFIRMADA** por (a) ou (b) | Vínculo declaração → Conclusão. Em seguida a compatibilidade definitiva (§8.1) e o conflito (§9) |
| **NÃO CONFIRMADA** | Declaração e Respostas preservadas; fora da análise (reabertura: DP-1905) |
| *(sem registro)* | PENDENTE |

**Registro**:

- Guarda resultado, Conclusão (quando confirmada), momento e operador.
- Uma decisão por declaração. Uma decisão concorrente recebe "já decidida".
- É imutável na 019.
- Antes de gravar, a tela pede confirmação explícita.
- A antiga "conferência por HMAC" foi retirada. Com CPF e data recuperáveis para o
  validador, ela não tem mais consumidor.

**Divergência.** É **derivada**: comparação, campo a campo, entre o declarado e a
Conclusão vinculada. É apresentada como "confirmada com dados diferentes" e não é estado
armazenado.

---

## 9. Situação analítica, divergência, não confirmação e conflito

**Situação analítica da Participação.** É derivada e avaliada nesta ordem:

| Situação | Condição | Dados oficiais (011 oficiais, 012, 013) |
| --- | --- | --- |
| `INSTITUCIONAL` | Âncora é Conclusão | Sim |
| `DECLARADA_PENDENTE` | Sem decisão | Não |
| `DECLARADA_NAO_CONFIRMADA` | NÃO CONFIRMADA | Não |
| `DECLARADA_FORA_DA_ABRANGENCIA` | CONFIRMADA, Conclusão fora dos critérios da Campanha | Não |
| `DECLARADA_EM_CONFLITO` | CONFIRMADA, compatível, e já havia Participação oficial da mesma Conclusão na Campanha | Não |
| `DECLARADA_VALIDADA` | CONFIRMADA, compatível, sem conflito | Sim, com a Conclusão como contexto **institucional** |

**Conflito.**

- Os dois registros são preservados. Nada é fundido nem excluído.
- A Participação que já integrava os dados oficiais **nunca perde essa condição** por
  validação posterior.
- O conflito é detectado na transação da confirmação, serializada por Conclusão, e fica
  na fila como "resolução administrativa pendente". A resolução é DP-1907.
- Depois de uma `DECLARADA_VALIDADA`, o início institucional do mesmo par Campanha +
  Conclusão devolve a Participação declarada como já existente, e a 007 mostra "já
  respondida".
- Antes da validação, a quarentena vale integralmente.

---

## 10. Impacto por feature

| Feature | Impacto | Natureza |
| --- | --- | --- |
| **001** | Nova fonte institucional `ACERVO_HISTORICO`, com adaptador no mesmo contrato e incorporação pelo caminho existente. Novo **disparo** de incorporação pelo operador na validação, para a fonte digital ou para o acervo. FR-030 recebe nota: cadastro manual continua vedado, e o acervo histórico atestado é fonte. Cenário simulado de formação existente na fonte e ainda não importada | Acréscimo + nota de revisão |
| **004** | Admissão de Participação declarada por compatibilidade provisória. FR-017 continua valendo para a **população**. Critérios congelados permitem a compatibilidade definitiva | Revisão de admissão (não de população) |
| **005** | FR-002: âncora "Conclusão **ou** Formação Declarada, exatamente uma, nunca alterada". FR-006: unicidade pela Conclusão efetiva oficial. Início declarado ao lado de `iniciar_participacao`. Escritas sem mudança | Revisão + migração aditiva |
| **006** | Nenhuma regra muda. FR-035 lê "preserva Campanha e âncora" | Nota |
| **007** | Participação declarada validada conta como a Participação do par. Pendente nunca conta | Ajuste de leitura |
| **008** | Posse pelo sujeito da sessão. Contexto exibido "informada por você". Mensagem final própria | Ajuste de interface |
| **010** | `pode_validar_formacao`. Escopo pela unidade declarada e pela unidade da Conclusão ou do acervo (DP-1005) | Acréscimo |
| **011** | Contagens oficiais só com Participações oficiais, com unidade pela Conclusão efetiva. Bloco agregado fora das taxas: aguardando verificação, não confirmadas, fora da abrangência, em conflito. Indicador com link para a fila | Ajuste + bloco |
| **012** | Universo: elegíveis ∪ Conclusões efetivas das Participações **oficiais**. O registro **congela a Participação** que o compõe e a origem da formação. Snapshot anterior à validação nunca muda; captura posterior inclui a validada | Revisão + migração aditiva com preenchimento determinístico |
| **013** | Coluna base da origem da formação (por exemplo, institucional, declarada validada pela fonte digital, declarada validada pelo acervo histórico; nomes no plan). O declarado nunca é exportado como contexto. Passa a `VERSAO_CONTRATO` 2. Ler FR-021 (coluna constante) | Revisão de contrato |
| **018** | FR-034 ganha a exceção prevista em FR-035. `verificar` não muda. Segundo sujeito de sessão. A barreira "só fonte simulada" da demonstração admite também o acervo histórico fictício | Revisão pontual |
| **ADR 0004** | A proposta sobre formação declarada passa a regra: provisória pelo declarado, definitiva pela Conclusão. Foco de mobilização nunca se aplica | Nota de revisão |

---

## 11. Emenda constitucional — diff mínimo para revisão

B′ **exige emenda**. O diff abaixo foi gerado aplicando a proposta a uma cópia da
Constituição 1.0.0. **Atualização:** o solicitante aprovou o diff, que foi aplicado em 2026-10-04 como **Constituição 2.0.0 (MAJOR)**. Na revisão original, **a Constituição ainda não tinha sido alterada.** A linha de versão e a data ficam
para depois da decisão sobre a classificação.

```diff
@@ -145,6 +145,14 @@
 Campus, curso e demais características acadêmicas pertencem ao contexto da Conclusão
 Acadêmica e NÃO DEVEM ser tratados como atributos permanentes da Pessoa.

+### Formação Declarada
+
+Representa a formação no Ifes informada pelo próprio egresso quando a Conclusão Acadêmica
+correspondente não pôde ser identificada. É dado declarado (Princípio III), não fato
+institucional: NÃO DEVE criar nem alterar Pessoa, NÃO DEVE ser fonte de Conclusão
+Acadêmica e NÃO DEVE substituí-la. Sua correspondência com uma Conclusão Acadêmica só se
+estabelece por validação institucional registrada, que preserva a declaração original.
+
 ### Pesquisa
@@ -161,8 +169,10 @@
 ### Participação em Pesquisa

 Representa uma ocorrência concreta de acompanhamento de determinada Conclusão Acadêmica
-em determinada Campanha. Uma mesma Conclusão Acadêmica pode possuir várias Participações
-em diferentes momentos.
+em determinada Campanha. Quando a Conclusão Acadêmica não pôde ser identificada, a
+Participação PODE ter como âncora uma Formação Declarada. A âncora de uma Participação
+NÃO DEVE ser alterada depois de criada. Uma mesma Conclusão Acadêmica pode possuir várias
+Participações em diferentes momentos.
@@ -184,7 +194,12 @@
 - Toda Participação DEVE possuir contexto temporal.
 - Toda Participação relacionada a uma formação DEVE permitir identificar
-  inequivocamente a Conclusão Acadêmica observada.
+  inequivocamente a Conclusão Acadêmica observada ou, enquanto ela não for identificada,
+  a Formação Declarada que a ancora.
+- Participação ancorada em Formação Declarada NÃO DEVE integrar dados analíticos oficiais
+  nem ser contada como resposta institucional válida enquanto validação institucional
+  registrada não a fizer corresponder a uma Conclusão Acadêmica. A validação NÃO DEVE
+  alterar a Participação, a Formação Declarada nem as Respostas.
 - Múltiplas formações da mesma Pessoa NÃO DEVEM ser artificialmente fundidas.
```

**O que deliberadamente não está no diff:**

- **Princípio III.** Já cobre a convivência entre declarado e institucional ("NENHUMA das
  fontes DEVE ser sobrescrita silenciosamente").
- **Princípio V.** Já admite providers "correspondentes às fontes institucionais
  efetivamente adotadas", o que inclui o acervo histórico.
- **Princípio VII.** A Resposta continua sempre na Participação.
- **Abrangência, conflito e fila.** São regra de spec, não de Constituição.

**Classificação: recomendação MAJOR (2.0.0).**

| Leitura | Argumento | Avaliação |
| --- | --- | --- |
| MINOR (1.1.0) | Acrescenta um termo e uma restrição. Toda Participação institucional continua sob o invariante original. Nenhum dado existente é reinterpretado. A cadeia vale integralmente para os dados oficiais | Verdadeiro sobre os **dados**, mas a regra de versionamento fala de **princípio e invariante**, não de dados |
| **MAJOR (2.0.0)** | Até aqui, "toda Participação identifica uma Conclusão" era uma **garantia** com que specs e código contavam: 005 FR-002, 006 FR-035, 011, 012 e 013, além da FK obrigatória. Depois da emenda, essa garantia passa a valer só para Participações oficiais. Afrouxar uma garantia de que consumidores dependem é, por definição, mudança incompatível. A emenda também redefine um termo da Terminologia Fundamental, num princípio NON-NEGOTIABLE | **Recomendada** |

**Justificativa da recomendação.** A Constituição define MAJOR como "mudança incompatível
de princípio [...] [ou] invariante fundamental".

- **Mudança incompatível.** A emenda obriga revisar quatro specs anteriores para que
  continuem corretas. Esse é o sinal objetivo de incompatibilidade.
- **Precedente.** Classificar como MINOR o afrouxamento de um invariante NON-NEGOTIABLE
  abriria um precedente ruim: tornaria "menores" futuras flexibilizações do núcleo.
- **Não é ruptura com o passado.** MAJOR não significa reinterpretar dados, e a emenda não
  invalida nada existente. Por isso o relatório de impacto da emenda deve listar
  explicitamente as specs que recebem notas de revisão (005, 006, 007, 008, 011, 012,
  013, 018 e ADR 0004).

---

## 12. Decisões institucionais pendentes

Nenhuma bloqueia a spec. As marcadas bloqueiam o uso real.

- **DP-1901** — Competência para atestar a conclusão e para registrar a Referência de
  acervo histórico (registro acadêmico, secretaria, CSAEG ou outra). **Bloqueia o uso
  real.**
- **DP-1902** — Quem vê os dados identificados dos declarantes, em qual escopo e com qual
  finalidade. Amplia 005/DP-505. **Bloqueia o uso real.**
- **DP-1903** — Base legal, finalidade, transparência ao declarante, retenção e descarte
  de:
  - nome;
  - HMACs;
  - **CPF e data criptografados**;
  - registros de acesso.

  Inclui prazo de descarte depois da decisão e custódia e rotação da chave de criptografia
  (com a DTI, como 018/DP-1803). Amplia 018/DP-1802. **Bloqueia o uso real.**
- **DP-1904** — Evidência mínima para confirmar e forma da referência do acervo (livro,
  folha, registro, processo).
- **DP-1905** — Reabertura ou correção de decisão e de Referência de acervo, e o efeito
  sobre snapshots posteriores.
- **DP-1906** — Dados de que o registro acadêmico precisa, **além de nome, CPF e data**,
  para localizar um egresso no acervo, por exemplo nome à época ou matrícula antiga.
  Campos novos só entram com esse consumidor.
- **DP-1907** — Resolução de conflito.
- **DP-1908** — Notificação ao egresso sobre o resultado.
- **DP-1909** — Associação da Pessoa da fonte de acervo a Pessoa de outra fonte (amplia
  001/DP-003). Também o acesso futuro do egresso validado pelo caminho principal da 018.
- **DP-1910** — Prazo e SLA da fila; pendências ao fim da rodada.
- **DP-1911** — Substituição do registro de acervo no NIAE por fonte institucional digital
  (digitalização do acervo).
- **Herdadas:**
  - 001/DP-003 e DP-007;
  - 010/DP-1005;
  - 005/DP-505, DP-507 e DP-508;
  - 018/DP-1802, DP-1804 e DP-1807.

---

## 13. Decisões do solicitante (2026-10-04)

- **B′** confirmado como arquitetura-base.
- **M1** rejeitado como estava: formação confirmada só no acervo físico ficaria pendente
  para sempre. **M1+** aprovado, com acervo histórico como fonte institucional,
  incorporação pela 001 e Formação Declarada nunca como fonte.
- **Abrangência**: compatibilidade provisória pelo declarado e definitiva pela Conclusão.
  Formação confirmada fora da abrangência fica preservada e não vale para a Campanha. Foco
  de mobilização nunca limita.
- **Fila** fora da 011, em área própria. Na 011 só um indicador agregado com link. Fluxo
  mínimo: PENDENTE → confirmada ou não confirmada.
- **Campos** da declaração mínimos. Dados adicionais só com consumidor concreto (DP-1906).
- **CPF e data do declarante** (segunda revisão):
  - HMAC para identificação e candidatas;
  - **criptografia reversível** em conjunto separado para a consulta ao acervo;
  - acesso só de perfis autorizados à validação, com registro de acesso;
  - nunca em logs, URLs, analytics, snapshots ou exportações;
  - retenção e descarte por política institucional futura (DP-1903).
- **Emenda** reconhecida. A classificação (MAJOR ou MINOR) será decidida depois da revisão
  do diff (§11).

**Novo fork?** Não. A coincidência entre a Pessoa da fonte de acervo e uma Pessoa de outra
fonte é o problema já registrado de reconciliação (001/DP-003). Ela não muda a arquitetura
e fica explícita como DP-1909.
