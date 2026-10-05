# Auditoria arquitetural, de dados e de produto — Feature 021: Minha Trajetória

Data: 2026-10-04 · Base: `main` em `ff12566` (PR #29, Feature 019 mergeada).

Este documento só faz diagnóstico e prepara a spec da Feature 021. Nada foi implementado.
Não há plan, task, migração nem commit. A Constituição não foi alterada.

A solicitação diz que a 019 está "em implementação". No repositório ela já está mergeada
(`b5f2db7`, PR #29), restrita à demonstração. Isso não muda nada abaixo: a 021 usa da 019
apenas a distinção entre formação institucional e declarada.

**Revisões do solicitante (2026-10-04), já refletidas na spec e no plan:**

1. **Ingresso.** A justificativa para mantê-lo separado foi corrigida (§5.3).
2. **Apurações.** O agregado só aparece quando há exatamente uma apuração conhecida
   (§7, §8).
3. **Fronteira do enriquecimento.** Ingresso e agregados não viajam em
   `obter_pessoa()`/`PessoaEncontrada`, que servem à 018. Chegam por uma capacidade de
   contexto da trajetória separada da `FonteAcademica`. Uma única view larga continua
   possível, porque quem separa é o adaptador (§7).
4. **Foco do card.** Compartilhamento em rede social no formato vertical, especialmente o
   story do Instagram (9:16). O PNG é o artefato principal (§12).

**Fontes lidas**

- Constituição 2.0.0.
- Specs 001, 002, 003, 004, 005, 006, 007, 008, 011, 012, 013, 014, 015, 017, 018 e 019.
- Roadmap da 020.
- Auditorias de 2026-10-01 (UX da 008), 2026-10-02 (identidade da experiência),
  2026-10-03 (identidade e acesso, identidade visual, mobile-first) e 2026-10-04 (019).
- Inventário do formulário 2024.
- Código em `fonte_academica`, `academico`, `analitico`, `exportacao`, `campanha`,
  `acompanhamento`, `participacao`, `interface`, `acesso`, `declaracao`, `instrumento` e
  `formulario_2024`.

**Visão do solicitante preservada**

- A 021 transforma fatos institucionais confiáveis em uma devolutiva personalizada depois
  da participação.
- O conteúdo é determinístico, sem IA generativa.
- Nada pode ser inventado: fatos, datas, eventos, estatísticas ou relações acadêmicas.
- "A view pode ser larga e conveniente; o modelo do Trajetória não precisa ser largo e
  duplicado."

---

## 1. Inventário do que existe hoje no código

### 1.1 Fronteira acadêmica (001)

- **Contrato** (`trajetoria/fonte_academica/contrato.py`):
  - `ConclusaoNaFonte` (:33-50) tem `id_externo`, `curso`, `unidade`, `nivel`,
    `modalidade`, `forma_oferta`, `ano_conclusao` e `data_conclusao`. Atributo ausente é
    `None`; cadeia vazia é proibida.
  - `PessoaEncontrada` (:57-77) traz `id_externo`, `nome`, as `conclusoes`, e `cpf` e
    `data_nascimento` (`repr=False`, usados só na fronteira de identidade da 018).
  - O protocolo `FonteAcademica` (:107-117) tem só `obter_pessoa(id)` e
    `obter_conclusao(id)`.
  - Não existe operação que liste o universo nem que devolva qualquer agregado.
- **`CAMPOS_DE_CONTEXTO`** (:54) é derivado do próprio dataclass: todo campo novo em
  `ConclusaoNaFonte` entra nele automaticamente. Hoje ele alimenta:
  - a incorporação e a comparação de divergências (`academico/incorporacao.py:205`);
  - a fonte simulada (`simulada.py:71-75`);
  - a captura do snapshot da 012 (`analitico/operacoes.py:73, 95, 116`);
  - a leitura do contexto congelado (`analitico/consultas.py:168, 208`).
- **Models** (`academico/models.py`):
  - `Pessoa` tem `fonte`, `id_externo` e `nome` (opcional, só apresentação).
  - `ConclusaoAcademica` tem os sete atributos de contexto, `fonte`, `id_externo` e
    `incorporado_em`.
  - Nenhum campo é declarado ou derivado.
- **Incorporação** (`academico/incorporacao.py`):
  - É sob demanda, uma Pessoa por vez, idempotente e nunca atualiza.
  - Uma divergência é só sinalizada em log, sem valores pessoais.
- **Fonte simulada** (`fonte_academica/simulada.py`, `cenarios.py`):
  - Doze Pessoas fictícias. Só `situacao == "concluida"` vira conclusão.
  - A Maria (SIM-P-0003) tem duas formações em unidades diferentes. O Diego (SIM-P-0004)
    tem três, em níveis diferentes.
- **Acervo histórico (019)**:
  - Uma validação pelo acervo cria uma Pessoa nova com `nome=None` e uma
    `ConclusaoAcademica` com `fonte="acervo_historico"`.
  - Essa Pessoa nunca é fundida com outra (`declaracao/acervo.py:75-110`).

### 1.2 Jornada do egresso (005–008, 014, 015, 018, 019)

- **Identificação (018)**:
  - Por CPF e data de nascimento, verificados por HMAC contra material importado.
  - A sessão guarda só UUIDs: 30 min de inatividade e 480 min no máximo.
  - Toda view de interface restringe a Participação à Pessoa da sessão
    (`interface/views.py:98-108`).
- **Tela "Sua trajetória no Ifes"** (`/formacoes/`, `views.py:183-220`):
  - Lista todas as Conclusões da Pessoa e a situação de cada pesquisa.
  - É operacional: escolher por qual formação responder.
  - A 014 FR-035 proíbe reordenar, descrever a ordem como cronológica, inferir
    continuidade ou verticalização, linha do tempo gráfica e comparação com outras
    pessoas.
- **Tela de conclusão** (`/participacoes/<uuid>/concluida/`, `views.py:487-520`,
  `interface/concluida.html`, 12 linhas):
  - Mostra "Pesquisa concluída", a frase de registro, o agradecimento ou o texto de
    encerramento da Versão, o contexto da formação e um link "Ver sua trajetória no Ifes"
    para `/formacoes/`.
  - Restrições vigentes:
    - 008 FR-062/063: simples, sem download, comprovante, certificado nem identificador.
    - 014 FR-038 a 041: nenhuma ação além da ligação para a trajetória.
- **Participação ancorada em Formação Declarada (019)**:
  - Não há Pessoa nem Conclusão (`participacao/models.py:60-62`).
  - A sessão do declarante guarda só UUIDs de declaração.
- **Visual** (015):
  - Tokens em `interface/templates/interface/estilo.css:14-58`, incluídos inline em
    `base.html`. Não há `staticfiles` nem CDN.
  - A fonte é `system-ui`. Não há JavaScript na jornada.
  - O único ativo é `assinatura.svg`. É uma conversão do EPS oficial, não fornecida pela
    ACS (D-03 aberta para publicação).
  - Não há fotos.
- **Ferramentas**:
  - Dependências: Django 5.2, psycopg, cryptography e XlsxWriter.
  - Não há biblioteca de imagem (Pillow, cairosvg, resvg), Node nem `package.json`.

### 1.3 Instrumento e Respostas

- `Pergunta` (`instrumento/models.py:125-138`) tem UUID próprio de cada Versão, sem
  código ou conceito estável.
- `Resposta` (`participacao/models.py:77-114`) é chaveada por `(participacao, pergunta)`.
- Uma camada semântica entre Versões é **proibida** por decisão repetida:
  - 002 FR-033;
  - 003 FR-012 (Q1–Q54 nunca persistidos);
  - 009 FR-103, 012 FR-077 e 013 FR-056.
- A comparabilidade entre Versões é a **002/DP-006**, pendente na CPAEG.
- Os códigos Q existem só em `formulario_2024/declaracao.py`. A situação profissional é a
  Q33 ("Atualmente você trabalha?"), não a Q35.
- Não existe no repositório documento de "análise metodológica do novo instrumento". O
  tema aparece só como pendente (002/DP-004; 019 spec :1093, :1227).

### 1.4 Contagens existentes

- 011 e 012 agrupam por unidade, curso, nível, modalidade, forma de oferta e ano.
- O universo, em ambas, é a população de **uma Campanha**: Conclusões já incorporadas que
  atendem aos critérios (`campanha/consultas.py:223-226`).
- Não existe contagem institucional fora de Campanha.

---

## 2. Mapa de dados: disponíveis hoje × futuros

| Dado | Existe hoje? | Origem | Confiabilidade conhecida? | Utilizável na narrativa? | Privado / compartilhável |
|---|---|---|---|---|---|
| Nome da Pessoa | Sim, opcional (`Pessoa.nome`) | Institucional (fonte) | Não se sabe se é nome civil ou social (decisão pendente) | Sim, se presente; nunca como recurso principal | Privado por padrão; no card só por escolha do egresso |
| Curso | Sim, opcional | Institucional | Vocabulário da fonte (001/DP-004) | Sim | Compartilhável |
| Unidade/campus | Sim, opcional | Institucional | Idem (001/DP-007) | Sim | Compartilhável |
| Nível | Sim, opcional | Institucional | Idem | Sim, exibido como está, sem traduzir | Compartilhável |
| Modalidade | Sim, opcional | Institucional | Idem | Sim | Compartilhável |
| Forma de oferta | Sim, opcional | Institucional | Idem | Sim, só na experiência privada | Privado por padrão (pouco valor no card) |
| Ano de conclusão | Sim, opcional | Institucional | Granularidade preservada (001 FR-011) | Sim | Compartilhável |
| Data de conclusão | Sim, opcional | Institucional | Idem | Sim, sem fabricar precisão | Privado por padrão (no card, só o ano) |
| Outras Conclusões da mesma Pessoa | Sim (`pessoa.conclusoes`) | Institucional | Só da mesma fonte; Pessoas de fontes diferentes não são fundidas | Sim | Compartilhável |
| Quantidade de formações registradas | Calculável | Derivado | Igual à das Conclusões | Sim, como "o Ifes registra N formações" | Compartilhável |
| Tempo desde a conclusão | Calculável | Derivado (data de referência) | Exato só com data completa | Sim, com regra de granularidade (§4.4) | Privado |
| Ordem temporal das formações | Calculável | Derivado | Só quando os anos são conhecidos e distintos | Sim, com regra estrita (§4.4) | Compartilhável |
| Ano/data de ingresso | **Não** | Institucional futuro | Desconhecida; não se sabe se a fonte real tem | Só quando existir (P2, simulado) | Privado por padrão |
| Forma de ingresso, cota | Não (001 FR-012) | Institucional futuro | — | Não na 021 (sensível) | Nunca no card |
| Conclusões do mesmo curso + unidade + ano | **Não** | Agregado institucional futuro | Depende da definição da fonte real | Só quando existir (P2, simulado) | Compartilhável sob decisão pendente |
| Conclusões da unidade no ano | **Não** | Agregado institucional futuro | Idem | Idem | Idem |
| Turma, coorte, matriculados, ingressantes, taxa de conclusão | Não; sem definição (011/DP-1102) | — | — | **Não** | — |
| Pesquisa, extensão, monitoria, IC, bolsas, estágio, mobilidade | Não; hoje só declarados (Q22–Q32) | Institucional futuro, outras fontes | — | Só como marcos de fontes futuras (P3) | A decidir |
| Situação profissional, relação trabalho-formação | Só como Resposta de uma Versão | Declarado | Sem conceito estável entre Versões | **Não** no MVP | Nunca no card |
| Respostas em geral | Sim | Declarado | — | Não (008/DP-802 pendente) | Nunca |
| Formação Declarada não validada | Sim (019) | Declarado | Pendente de validação | Não: não é fato institucional | — |
| Fotos de campus ou históricas | Não | — | Direitos desconhecidos | Não no MVP | — |
| Marca/assinatura do Ifes | `assinatura.svg` (conversão não oficial) | — | D-03 aberta | Só na tela; no card, sob decisão pendente | — |

---

## 3. Crítica do storyboard atual

O storyboard/mockup que motivou a 021 é bom como direção de produto. Mas várias de suas
frases não são deriváveis dos dados:

| Elemento do storyboard | Problema | Tratamento |
|---|---|---|
| "Foi aqui que tudo começou — 2005" | Não há ingresso no contrato. Deduzir 2005 de "conclusão 2008 − 3 anos" é invenção | Proibido sem ingresso. Com ingresso (P2): "Sua trajetória no Ifes começou em 2005." |
| "Sua turma de 2005" | "Turma" tem definição acadêmica própria; a métrica disponível seria "conclusões no mesmo ano" | Proibido. Já vedado pela auditoria de 2026-10-02 (§5) |
| "1.240 alunos estudavam no campus" | "Matriculado naquele ano" exige definição temporal precisa e fonte | Proibido |
| Fotos do campus "da época" | Sem metadado de período, sugerem um fato pessoal | Sem fotos no MVP; ativo decorativo futuro sem afirmação (§14) |
| "Você viveu uma época especial" | Sem fonte | Proibido |
| Bloco "Hoje: trabalha na área" | Dado declarado, acoplado ao número de pergunta de uma Versão | Fora do MVP (§4.3) |
| Projetos, IC, bolsas | Não há fonte institucional | Fora até existir uma fonte (P3) |
| Sequência curso → especialização | É válida: duas Conclusões da mesma Pessoa com anos conhecidos | Mantida, como "depois, você também concluiu", sem "verticalização" |
| Card final com marca do Ifes | D-03 aberta; risco de parecer documento oficial | Card sem brasão, selo nem assinatura enquanto a decisão estiver pendente |

A arquitetura de sequência do storyboard (o que o Ifes sabe → formações → contexto →
card) é boa e se mantém. O que muda é que cada bloco **some** quando não há dado que o
sustente.

---

## 4. Arquitetura de `TrajetoriaNarrativa`

### 4.1 Quatro classes de conteúdo

| Classe | O que é | Onde mora | Exemplo |
|---|---|---|---|
| A. Fato institucional pessoal | Atributo de uma Conclusão Acadêmica (ou complemento dela, P2) | `ConclusaoAcademica`; complemento separado (§5) | ADS, Serra, 2022 |
| B. Derivado | Calculado na montagem da narrativa; **nunca gravado** | Só na `TrajetoriaNarrativa` | "2 formações", "desde 2022" |
| C. Declarado | Resposta da pesquisa | `Resposta` | Fora do MVP |
| D. Contexto institucional agregado | Fato sobre um grupo, não sobre a Pessoa nem sobre a Conclusão | Entidade própria, deduplicada (§6) | "27 conclusões de ADS na Serra em 2022" |

### 4.2 O objeto

```text
TrajetoriaNarrativa                          (puro, determinístico, serializável)
├── referencia            data de referência usada nos derivados (entrada explícita)
├── identidade_de_exibicao nome (opcional) — só o que a fonte informa
├── formacoes[]           uma por Conclusão da Pessoa: curso, unidade, nível,
│                         modalidade, forma de oferta, ano/data — origem "institucional"
│                         + complemento opcional (P2): ingresso
├── marcos[]              vazio até existir fonte (P3)
├── derivados[]           tipo + valor + regra de derivação ("formacoes_registradas", …)
├── contextos_agregados[] métrica + recorte + valor + apuração + fonte (P2)
└── compartilhavel        subconjunto permitido no card (§10), calculado, não editável
```

- Cada elemento leva sua **origem** (institucional, derivado ou agregado), conforme os
  Princípios III e IV.
- Não é um dump de model: não leva `id`, `fonte`, `id_externo`, CPF, data de nascimento,
  UUIDs nem `incorporado_em`.
- Não contém regra de fonte. Recebe fatos já incorporados.
- A **data de referência é entrada**. Mesma entrada, mesma narrativa. O teste fixa a data.
- **Não é persistida.** É montada sob demanda a partir do que já está persistido. Nenhuma
  migração é necessária em P1.
- As frases vêm de um catálogo fechado de formulações (§17), escolhidas por regra e
  preenchidas só com valores existentes. Nada de texto livre.

### 4.3 Dados declarados: decisão

Não existe camada semântica estável entre Versões, e a criação dela é vedada por quatro
specs e pendente na 002/DP-006. Usar a Q33 da baseline 2024 amarraria a narrativa a uma
Versão. Os textos e posições mudam na próxima Versão, e a narrativa quebraria ou mentiria
em silêncio.

**Decisão:** a 021 não consome Respostas. O MVP omite os dados declarados.

O consumo futuro depende de a CPAEG resolver a 002/DP-006 (correspondência conceitual
entre Versões). Isso fica registrado como oportunidade P3, sem desenho prévio. Também
mantém a 008/DP-802 (ver as próprias respostas) intocada.

### 4.4 Regras de derivação (as que evitam invenção)

- **Formações registradas:**
  - É o número de Conclusões da Pessoa da sessão, todas de uma mesma fonte (as Pessoas de
    fontes diferentes não são fundidas, 019).
  - A frase é "O Ifes registra N formações concluídas por você", nunca "você fez N cursos
    no Ifes".
- **Ordem temporal:**
  - Uma formação só é colocada "antes" ou "depois" de outra quando ambas têm ano e os anos
    são diferentes.
  - Com o mesmo ano, ou com ano ausente, aparece sem relação temporal.
  - Nunca "verticalização", que é indicador da PAEG com semântica própria (Art. 10, III).
- **Tempo desde a conclusão:**
  - Com data completa, conta anos completos até a data de referência.
  - Só com o ano, a frase usa "desde 2022", sem contar anos. Isso evita o erro de um ano
    (dezembro de 2022 → janeiro de 2025 não são "3 anos").
- **Primeira formação conhecida:** a de menor ano. Com empate, nenhuma é "a primeira".
- **Nada é estimado:** nem ingresso por duração do curso, nem período de estudo, nem idade.

---

## 5. Enriquecimento acadêmico individual (P2): ingresso

### 5.1 Impacto real de acrescentar `ano_ingresso` a `ConclusaoNaFonte` / `ConclusaoAcademica` (alternativa A)

- **`CAMPOS_DE_CONTEXTO`:** o campo entra automaticamente.
- **Incorporação:**
  - Passa a persistir e comparar o campo.
  - Toda Conclusão incorporada antes da mudança diverge (`ATRIBUTOS_DIFERENTES`) quando a
    fonte passar a informá-lo. Como a incorporação nunca atualiza, o valor nunca chegaria
    a essas Conclusões.
- **Snapshot da 012:** quebra por desenho.
  - `RegistroDoSnapshot` e `ContextoCongelado` têm sete campos explícitos.
  - A 012 FR-040 diz: "NENHUM atributo novo DEVE ser criado na Conclusão".
  - A 012 research R5 manda falhar para forçar decisão explícita.
  - Mesmo corrigido, haveria uma armadilha de reprodutibilidade: snapshot antigo com `NULL`
    seria lido como "não informado", quando na verdade foi "não capturado".
- **Exportação (013):**
  - O cabeçalho não muda sozinho (`COLUNAS_BASE` é fixa).
  - Incluir o campo exigiria nova versão do contrato (013 FR-065).
- **Critérios da Campanha:** nada muda automaticamente. A 004 já veda critério por forma
  de ingresso. Se o campo estivesse no contexto, seria um convite a ampliar critérios sem
  decisão.
- **001 FR-012:** veda "forma de ingresso… além do contexto mínimo" até haver necessidade
  concreta.
- **Migrations:** coluna nova em `ConclusaoAcademica` e em `RegistroDoSnapshot`.

### 5.2 Alternativa B — complemento acadêmico opcional, separado do contexto fundamental

- Um **complemento da Conclusão** (nome conceitual): fato institucional individual, opcional,
  1:1 com a Conclusão, com fonte e momento de obtenção.
- Fica **fora** de `CAMPOS_DE_CONTEXTO`. Por isso:
  - não entra no snapshot da 012, nas exportações da 013 nem nos critérios da Campanha;
  - não entra na divergência de contexto da incorporação.
- Obtido pela mesma fronteira acadêmica, na mesma incorporação. A fonte o informa ou não.
- A gravação segue a regra da 001: insere uma vez, nunca atualiza, sinaliza divergência
  sem gravá-la.
- Vale para Conclusões já incorporadas: quando a fonte passar a informar o complemento,
  ele pode ser acrescentado sem tocar o contexto fundamental. Acrescentar o que não existia
  não é sobrescrever.

### 5.3 Recomendação

**B**, pelo motivo certo (corrigido na revisão do solicitante, 2026-10-04).

A 012 não congela para sempre a evolução do domínio acadêmico. Se o ingresso se mostrar um
fato estrutural, 001 e 012 podem ser revistas de forma explícita, e o custo listado em
§5.1 seria então o preço legítimo de evoluir o núcleo. O motivo para não ampliar
`ConclusaoAcademica` **agora** é outro:

- o ingresso não existe na fonte real conhecida;
- não é necessário hoje para Campanha, Participação ou snapshot;
- seu uso inicial é enriquecer a narrativa;
- o núcleo acadêmico fundamental não deve ser alterado só para satisfazer uma composição
  visual.

Como consequência, e não como razão, B também evita reabrir 012, 013 e 004 e mantém
`CAMPOS_DE_CONTEXTO` como o conjunto que a 011/012 recortam.

O custo é uma entidade pequena, opcional e com um consumidor concreto (a narrativa). Isso
atende ao Princípio XXII.

Se um dia o ingresso virar recorte analítico ou critério, essa decisão será tomada por uma
spec própria, que pode promovê-lo ao contexto com migração explícita (Princípio XXVII).

A Constituição já cita "ingresso" como exemplo de dado institucional da Conclusão
(Terminologia; Princípio III). B não exige emenda. Exige revisar a 001 FR-012, que passa a
admitir um complemento fora do contexto mínimo.

**Semântica que a fonte precisa declarar:** "ingresso" é o ingresso **na matrícula que
resultou nesta Conclusão**. Reingresso, transferência e aproveitamento são decisão
pendente (registro acadêmico). Na fonte simulada, o valor é fictício e declarado como tal.

---

## 6. Contexto institucional agregado (P2)

### 6.1 Modelo conceitual — poucas métricas, semântica explícita

```text
ContextoInstitucionalAgregado
├── fonte                 qual fonte institucional apurou (mesmo código das Conclusões)
├── metrica               enumeração FECHADA, duas métricas
├── recorte               determinado pela métrica (curso+unidade+ano | unidade+ano)
├── ano_de_referencia     ano civil de conclusão
├── valor                 inteiro ≥ 0
├── apurado_em            referência temporal da apuração informada pela fonte
└── obtido_em             quando o NIAE recebeu (proveniência)
```

Não é framework de indicadores: nada de métrica configurável, fórmula, dimensão genérica ou
cadastro de indicadores. Uma terceira métrica exige spec.

**Métrica 1 — `conclusoes_curso_unidade_ano`**

- **O que conta:** quantas Conclusões a fonte reconhece (pela mesma regra que reconhece a
  Conclusão do egresso) para aquele curso, naquela unidade, com ano de conclusão igual
  àquele ano civil.
- **Denominador:** não há. É uma contagem absoluta.
- **Inclui** a Conclusão do próprio egresso. Conta conclusões, não pessoas distintas.
- **Frase:** "Em 2022, o curso Tecnologia em Análise e Desenvolvimento de Sistemas
  registrou 27 conclusões na unidade Serra, incluindo a sua."

**Métrica 2 — `conclusoes_unidade_ano`**

- Mesma regra, todos os cursos e níveis da unidade naquele ano civil.
- **Frase:** "Em 2022, a unidade Serra registrou 812 conclusões."

A unidade é exibida como a fonte a informa ("Serra", "Cefor"), sem acrescentar "Campus":
as unidades do Ifes incluem campus avançado e Cefor (PAEG, Art. 2º). As frases usam "na
unidade {unidade}". O plan pode refinar o texto sem inferir o tipo de unidade.

**Vedados sem definição comprovada:** turma, coorte, matriculados, ingressantes, taxa de
conclusão, percentuais e qualquer comparação ("mais que", "uma das N melhores").

### 6.2 Não calcular a partir da base local

- O protocolo não lista o universo.
- A incorporação é sob demanda, e a 018 nunca incorpora no login.
- A validação da 019 cria Conclusões uma a uma.

A base local é, portanto, **parcial por construção**: contém quem foi incorporado até
agora. Contar Conclusões locais por curso, unidade e ano produziria um número falso, e
"ausente localmente" não é "zero institucional".

**Regra:** os agregados vêm só da fonte institucional, por uma operação própria do
contrato. Nunca são calculados do banco do NIAE.

**Guarda barata de consistência:** se o valor recebido for **menor** que o número de
Conclusões da mesma fonte já incorporadas naquele recorte, o agregado é incoerente. Ele
não é exibido, e a incoerência é sinalizada em log sem dados pessoais. A base local serve
como limite inferior, nunca como valor.

### 6.3 Fonte simulada

- Declara agregados fictícios para os recortes das Pessoas simuladas, coerentes com a guarda
  acima.
- Fica explicitamente marcada como simulação. Não afirma que o Q-Acadêmico os fornece.

---

## 7. Agregados na própria view acadêmica

A ideia do solicitante é aceitável e boa: uma view de integração "pronta para consumo" que
repete os agregados em cada linha (funções de janela tornam isso trivial).

```text
IDENTIDADE  cpf · data_nascimento · nome                    → fronteira da 018
FORMAÇÃO    id_conclusao · curso · campus · nível · …        → ConclusaoNaFonte (contexto)
            ano_ingresso                                     → complemento (§5)
CONTEXTO    concluintes_curso_campus_ano · concluintes_campus_ano → ContextoInstitucionalAgregado
```

- **Quem separa é o adaptador**, como manda o Princípio V. Ele lê a linha larga, distribui
  cada coluna para o conceito certo e **deduplica** o contexto pela chave
  (fonte, métrica, recorte, ano).
- **O contrato não fica largo.** O contrato da fronteira expõe os agregados por uma operação
  ou estrutura própria. O formato da view é detalhe do adaptador.
- **Duas linhas da mesma view podem trazer valores diferentes** para o mesmo recorte, por
  exemplo quando a view é lida em momentos diferentes.
  - Com referências de apuração distintas, são duas apurações. Ambas são registradas, e a
    narrativa omite o agregado enquanto houver mais de uma (§8; DP-2109).
  - Com a mesma apuração e valores diferentes, o adaptador sinaliza erro de fonte e não
    escolhe um dos valores.

---

## 8. Persistência e deduplicação dos agregados

- **Persistidos, deduplicados e fora da Pessoa e da Conclusão.** Um registro por
  (fonte, métrica, recorte, ano, apuração).
- Várias trajetórias leem o mesmo registro. O "27" é gravado uma vez, não 500 vezes.
- **Sem sobrescrita silenciosa:**
  - uma apuração nova é um registro novo;
  - registros antigos não são editados.
- **Escolha entre apurações** (revisão do solicitante, 2026-10-04): nenhuma autoridade é
  inferida da ordem temporal.
  - A narrativa usa o agregado só quando há **exatamente uma** apuração conhecida para
    fonte, métrica e recorte, e informa a referência temporal ("dados de 2026").
  - Com mais de uma, omite.
  - A regra institucional de vigência fica pendente (DP-2109 na spec).
- **Por que persistir, e não consultar a fonte na hora:**
  - o NIAE já trabalha sobre o que foi materializado (a 018 nunca consulta a fonte no
    login, a 011 conta sobre o incorporado);
  - uma fonte real pode ser carga ou view em lote, não serviço online;
  - a proveniência (Princípio IV) exige saber quando o valor foi obtido.
- **Quando a carga acontece** fica para o plan, ligado à 001/DP-006 (gatilho de
  incorporação).

---

## 9. Relação com a Feature 012

- A 012 é fotografia analítica de Campanha. Nem o universo (população de uma Campanha) nem
  a finalidade (análise reprodutível) servem para "27 conclusões do curso no ano".
- **A 021 não lê snapshots.** O contexto histórico institucional é outra capacidade e não
  depende de ter havido uma Campanha.
- **A 021 não altera a 012.** Com a alternativa B, nem o complemento nem o agregado entram
  em `CAMPOS_DE_CONTEXTO`, e a 012 FR-040 permanece literalmente válida. Isso deve ter
  teste.

---

## 10. Fronteira entre privado e compartilhável

| Conteúdo | Experiência privada | Card compartilhável (padrão) |
|---|---|---|
| Nome | Sim, se informado, em tom discreto | **Só se o egresso marcar** "incluir meu nome" |
| Curso, unidade, ano de conclusão | Sim | Sim |
| Nível, modalidade | Sim | Sim |
| Forma de oferta, data completa | Sim | Não |
| Outras formações | Sim | Sim |
| Formações registradas (derivado) | Sim | Sim |
| Tempo desde a conclusão | Sim | Não |
| Ingresso (P2) | Sim | Não por padrão |
| Agregados (P2) | Sim | Sim, sujeito à decisão pendente sobre publicação de agregados |
| Respostas, renda, emprego, situação profissional, deficiência, raça/cor, contato, CPF, data de nascimento | **Nunca** | **Nunca** |

- **Não há editor de privacidade.** A única escolha é a de incluir o nome. O restante é fixo
  e conservador.
- **Compartilhar é baixar o arquivo.** O sistema não hospeda página pública, link
  permanente nem URL compartilhável. O compartilhamento acontece fora do sistema, por ação
  do egresso.
- **O card não pode parecer documento oficial** (008 FR-063): sem brasão, selo,
  assinatura, QR, identificador, data de emissão nem "certificado". Na demonstração, leva a
  marca de dados fictícios.

---

## 11. Desenho do MVP (P1)

- **Onde vive:**
  - Uma página própria, "Minha trajetória no Ifes", para a Pessoa identificada na sessão
    (018) que tenha ao menos uma Participação concluída ancorada em Conclusão
    institucional sua.
  - A regra de acesso é [Hipótese] de devolutiva e é reversível.
  - Chega-se a ela pela tela de conclusão (cuja ação única passa a ser "Ver minha trajetória
    no Ifes") e por um link em `/formacoes/` enquanto a regra for atendida.
  - A tela de conclusão continua dizendo "Pesquisa concluída". O "obrigado" isolado deixa
    de ser o fim.
  - O título da nova página não pode ser igual ao de `/formacoes/` ("Sua trajetória no
    Ifes"). O plan escolhe o texto.
- **Seções**, cada uma só quando há dado:
  1. "O que o Ifes registra sobre você": formações registradas, de qual fonte, com a
     ressalva de que é o que a instituição registra.
  2. "Sua trajetória acadêmica": formações com curso, unidade, nível, modalidade e ano, em
     ordem só quando derivável (§4.4).
  3. "Outras formações no Ifes": quando houver mais de uma. "Depois dessa formação, você
     também concluiu…" só com anos conhecidos e distintos.
  4. "Naquele ano no Ifes": P2, agregados, quando existirem.
  5. "Seu card": prévia e download.
- **Sem placeholders** que insinuem fatos ausentes. Nada de "—", "em breve" ou "carregando
  marcos".
- **Sem JavaScript obrigatório:** rolagem vertical por seções, acessível (WCAG 2.1 AA) e
  mobile-first. Uma melhoria progressiva visual é opcional e decisão do plan.
- **Fora da jornada da pesquisa.** Não altera a Participação nem as Respostas, não faz parte
  da Versão, não condiciona a conclusão, não depende de contato nem da 020, e não exige
  compartilhar nada.
- **Não aparece** para participação ancorada em Formação Declarada sem validação (não há
  Pessoa nem fato institucional). A tela de conclusão da 019 fica como está.
- **Pessoa do acervo histórico** (validada pela 019): a narrativa tem só aquela Conclusão e
  nenhum nome, e funciona assim.

---

## 12. Card estático: recomendação SVG → PNG

- **SVG como representação canônica**, gerado no servidor a partir de
  `TrajetoriaNarrativa.compartilhavel` com um template de tokens.
- **PNG derivado do mesmo SVG** por rasterização no servidor.
- A mesma narrativa produz SVG idêntico byte a byte. O PNG só não muda se a rasterização
  for fixa (fonte embutida e mesmo motor).
- **Custo real** (para o plan, em Complexity Tracking):
  - Hoje não há biblioteca de imagem.
  - O PNG exige uma dependência de rasterização (por exemplo um *wheel* autocontido como o
    resvg, ou cairosvg com Cairo do sistema).
  - Exige também uma **fonte embutida**, porque `system-ui` não existe no servidor. Uma
    fonte de licença aberta guardada no repositório serve, e isso não reabre a D-04, porque
    não é servida ao navegador.
  - A conversão no navegador (canvas) exigiria JavaScript e daria resultado dependente do
    dispositivo. Não é recomendada.
- **Temas:** um tema no P1, derivado dos tokens da 015. Um segundo tema, compartilhando os
  componentes, entra em P3. Os temas mudam só tokens (cor, composição), nunca o conteúdo.
- **Formato:** um tamanho no P1 (vertical, adequado a celular). O plan escolhe as
  dimensões.
- **Arquivos:**
  - Nome neutro, sem nome, CPF nem curso no nome do arquivo.
  - Resposta sem cache.
  - Nada é guardado no servidor.
- **Sem foto pessoal, sem upload e sem IA.**
- **Marca:** sem brasão e sem a assinatura enquanto a D-03 (direito de uso da assinatura
  fora do sistema) estiver aberta. O texto "Instituto Federal do Espírito Santo" é fato, não
  marca.

---

## 13. Remotion: dentro da 021 ou Feature 022

**Recomendação: Feature 022 separada (alternativa B).**

- O vídeo exige Node, Chromium, FFmpeg, um worker com fila, e armazenamento e cache de
  renders. É a primeira infraestrutura assíncrona do projeto (Princípios XXII e XXIV).
- O valor do vídeo depende de decisões que a 021 ainda deixa pendentes:
  - compartilhamento;
  - marca;
  - nome social;
  - publicação de agregados.
- Construir o renderer antes delas cristaliza hipótese (Princípio XXIX).
- O contrato `TrajetoriaNarrativa` serializável é exatamente o que um renderer Remotion
  consumiria. A 021 fecha esse contrato. A 022 só acrescenta um renderer.
- **O que a 021 garante para a 022:**
  - serialização estável e documentada;
  - nenhuma frase gerada no renderer;
  - nenhuma regra de dado fora da narrativa.

---

## 14. Impactos em features existentes

| Feature | Impacto | Tipo |
|---|---|---|
| 001 | P2: o complemento (ingresso) e uma operação de agregados na fronteira; `CAMPOS_DE_CONTEXTO` inalterado. FR-012 revisada para admitir complemento fora do contexto mínimo | Revisão pontual (P2) |
| 006 | Nenhum. A Participação concluída continua imutável; a narrativa só lê | — |
| 007 | Nenhum. A ordem da 007 continua valendo em `/formacoes/`; a narrativa tem regra própria | — |
| 008 | FR-063 preservada: o download fica na página nova, não na confirmação | — |
| 014 | FR-041: a ação única da confirmação passa a levar à narrativa quando disponível; `/formacoes/` ganha um link. FR-035 continua valendo para `/formacoes/` | Revisão pontual (P1) |
| Auditoria 2026-10-02 §5 | "Comparação social / agregados" visava "Sua turma" e taxas de resposta. A 021 admite só duas contagens institucionais de conclusões, sem comparação, e mantém "turma" vedada | Esclarecimento registrado |
| 011, 012, 013 | Nenhum. Testes devem provar que nada da 021 entra no snapshot, nas exportações nem nos recortes | — |
| 004, 017 | Nenhum critério novo | — |
| 015 | Tokens reutilizados; D-03 condiciona a marca no card | — |
| 018 | Reutiliza a sessão. "Minha Trajetória" sai da lista "fora do escopo" (018 :768) para a 021 | Nota |
| 019 | Declaração não validada: sem narrativa. Pessoa do acervo: narrativa mínima | — |
| 020 | Independente | — |

---

## 15. Riscos de overengineering

| Risco | Contenção |
|---|---|
| Framework genérico de indicadores | Enumeração fechada de duas métricas; terceira só por spec |
| Persistir a narrativa ou os renders | Narrativa e card calculados sob demanda; nada guardado |
| Motor de templates de frases configurável | Catálogo fixo no código, revisável como texto (como `mensagens.py`) |
| Editor de privacidade | Uma única escolha: incluir o nome |
| Cinco temas | Um no P1, um segundo em P3 |
| Vídeo antes do contrato | 022 |
| Simular marcos de pesquisa/extensão "para ficar bonito" | Proibido; a seção não existe até haver fonte |
| Camada semântica do instrumento criada só para a 021 | Proibido; depende da 002/DP-006 |
| Ampliar o contexto fundamental por causa de um layout | Complemento separado (§5) |
| Página pública/permalink | Compartilhar é baixar |

---

## 16. Decisões pendentes e escolhas

**Fork arquitetural material que dependa do solicitante: nenhum.** As três escolhas
estruturais seguem a direção que a solicitação já indica e ficam registradas como
reversíveis:

1. ingresso como complemento separado (B);
2. agregados persistidos e deduplicados, nunca calculados localmente;
3. vídeo na 022.

Podem ser revistas no `/speckit-clarify`.

**Decisões institucionais pendentes** (vão para a spec como DP-21xx):

- Compartilhamento pelo egresso de representação com o nome do Ifes, e o uso da marca e da
  assinatura no card (D-03). Instâncias: ACS, CPAEG, encarregado de dados.
- Nome exibido: nome civil × nome social, e o que a fonte informa.
- Disponibilidade e definição real de ingresso na fonte institucional (Portão A, registro
  acadêmico).
- Definição e autorização de exibição dos agregados: o que é "conclusão" e "ano" na fonte
  real, e se há limiar mínimo de exibição.
- Acervo de imagens institucionais: direitos e metadados.
- Correspondência conceitual entre Versões, para usar dados declarados (= 002/DP-006).
- Relação da devolutiva com o Portal do Egresso (pendência constitucional).

**Herdadas e preservadas:** 001/DP-004, DP-006 e DP-007; 008/DP-801 e DP-802; 011/DP-1102;
018/DP-1805.

**Próximo passo:** spec da 021 em `specs/021-minha-trajetoria-narrativa/`, organizada em
P1/P2/P3, com checklist. Parar antes do plan.
