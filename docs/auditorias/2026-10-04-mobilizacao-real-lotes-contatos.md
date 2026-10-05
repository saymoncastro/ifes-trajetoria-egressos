# Auditoria arquitetural e de produto — Feature 020: mobilização real, Lotes e contatos do egresso

Data: 2026-10-04 · Base: `main` em `ff12566` (PR #29, Feature 019 mergeada).
Revisada em 2026-10-05 sobre `main` em `04efabd` (PRs #30–#33: Features 021 e 022 e
correções documentais).

Este documento só faz diagnóstico e recomendação. Prepara a spec da Feature 020. Nada foi
implementado, nenhum plan, task, migração ou commit foi produzido, a Constituição não foi
alterada e a Feature 019 não foi tocada.

**Revisão de 2026-10-05 (main avançou).** Três fatos novos ajustam esta auditoria:

- **021 FR-071.** O enriquecimento da 021 entrou por uma capacidade **separada** da
  `FonteAcademica`, com carga própria
  (`fonte_academica/contexto_da_trajetoria.py`, `contexto_trajetoria/carga.py`). Assim
  `obter_pessoa()`, `PessoaEncontrada` e a incorporação ficaram intactos, e falha do
  enriquecimento nunca afeta identidade (018) nem incorporação. O contato importado segue o
  mesmo precedente (§5.3 revista).
- **021 FR-003.** A tela de Participação concluída passou a ter **uma única ação**, "Ver
  minha trajetória no Ifes". O convite de e-mail não pode competir com ela. A §7.1 foi
  revista: ação principal preservada, convite secundário e revisão pontual da 021 FR-003.
- **021 e 022** declaram "020: independente" (021 FR-009/FR-070; 022, Relação). A 020
  preserva isso: a narrativa e o vídeo não dependem de contato, e o contato não depende
  deles (§17).

Constituição (2.0.0), ADR 0004 e nota de roadmap da 020 não mudaram. A Constituição
continua 2.0.0.

**Natureza dos dados.** O sistema não está conectado à base acadêmica real. Esta auditoria
**não mede** cobertura, qualidade, atualidade, domínio ou formato de contatos reais, e não
afirma que a fonte real oferece e-mail ou telefone. Tudo o que depende da fonte real está
em §18 (Gate A) como roteiro futuro, **não executado**.

**Fontes lidas**:

- Constituição 2.0.0 e ADR 0004 (com a revisão da 019) e ADR 0005.
- Specs 001, 004, 005, 006, 007, 010, 011, 012, 013, 016, 017, 018 e 019 (esta só para
  entender identidade e formação).
- Na revisão: specs 021 (Minha Trajetória) e 022 (vídeo), apenas nos pontos de contato com
  a 020 (tela de conclusão, fronteira de contexto, independência).
- [Nota de roadmap da 020](../roadmap/020-mobilizacao-real-lotes.md).
- Código em `academico`, `fonte_academica`, `comunicacao`, `campanha`, `governanca`,
  `acompanhamento`, `analitico`, `exportacao`, `acesso`, `declaracao`, `interface`,
  `demonstracao` e `config/settings.py`, além dos testes de fronteira de 012, 013, 016 e 010.

---

## 1. Objetivo e fronteira exata

**Objetivo.** Uma Campanha mobiliza grupos de egressos por meio de Lotes operacionais
reproduzíveis. Os Lotes usam contatos com proveniência conhecida e registram o contato
efetivamente usado e o resultado mínimo da tentativa. Mobilização nunca vira critério de
elegibilidade.

> Mobilizar um grupo não significa restringir quem pode responder.

**Dentro da 020** (recomendação, detalhada nas seções seguintes):

1. Contato de e-mail da Pessoa como registro próprio, separado de `Pessoa`, com origem e
   momento de obtenção, sem sobrescrita.
2. Contato importado por uma capacidade de contatos da fonte, separada da fronteira
   acadêmica da 001 (precedente da 021 FR-071), com o adaptador simulado fornecendo apenas
   endereços fictícios `example.invalid`.
3. Atualização voluntária do e-mail pelo egresso, fora do instrumento, a partir da tela
   de Participação concluída.
4. Lote de Mobilização pertencente a uma Campanha, criado já congelado: membros por
   Pessoa e contato escolhido no momento da confirmação.
5. Envio por e-mail dos membros do Lote, com situação individual persistida e retomável
   sem reenvio.
6. Fronteira de transporte com três modos — teste, demonstração e real — e o modo real
   **desativado até o Gate B**.
7. Capacidades nomeadas e reversíveis para consultar, criar e enviar Lotes.
8. Retirada da tela de comunicação simulada da 016, que o Lote substitui.

**Fora da 020**: WhatsApp, SMS, push, telefone (ver §5.4), LinkedIn, Lattes, Portal,
diretório, scheduler, automação recorrente, lembretes, reenvio deliberado, opt-out
operacional, confirmação de e-mail, webhooks de bounce, pixel ou tracking, personalização
avançada, fila distribuída, retry automático, edição de texto da mensagem e lista
individual de destinatários na interface. Ver §21.

**Invariantes que a 020 não pode tocar**:

- Lote não é população da pesquisa e não altera a abrangência da Campanha (ADR 0004).
- Lote não cria Participação, não concede identidade nem acesso.
- O link continua neutro, sem token nem identificador (016 FR-021/022; 018 FR-053).
- 012 e 013 não recebem contato nem marcador de mobilização.

---

## 2. Inventário da Feature 016 e o que reutilizar

| Elemento da 016 | Onde | Reutilização na 020 |
| --- | --- | --- |
| Fronteira de contato "Pessoa → zero ou um endereço" (FR-011) | `comunicacao/contatos.py:20-23` | **Conceito preservado**, implementação substituída. O mapa fixo `SIM-P-xxxx → example.invalid` passa a vir do adaptador simulado de contatos (capacidade separada, §5.3) e é gravado como contato importado. |
| Ordem Conclusões → escopo → Pessoas distintas → contato (FR-009) | `comunicacao/consultas.py:35-52` | **Reutilizada** como base da seleção do Lote, acrescida de filtros do Lote e da exclusão por mobilização anterior (§10). |
| Renderer único para prévia e envio (FR-020), texto + HTML, sem recursos externos (FR-017/018) | `comunicacao/convite.py:34-47`, templates `convite.txt/html` | **Reutilizado.** O texto atual é próprio da demonstração ("dados e contatos fictícios"). O modo real exige texto institucional (Gate B). |
| `EmailMultiAlternatives` com uma conexão por mensagem, uma tentativa e `finally close` | `operacoes.py:62-95` | **Reutilizado.** A situação passa a ser persistida por membro. |
| Situações `sem_contato`, `nao_tentada`, `submetida`, `falha`; proibição de "entregue" (FR-026) | `operacoes.py:64-82` | **Reutilizadas e persistidas**, com nomes honestos (§14). |
| Barreiras de transporte: loopback:1025, sem credenciais, remetente e destinatário `example.invalid`, URL local | `seguranca.py:14-102` | **Preservadas como modo demonstração.** Não servem ao modo real, como a própria 016 declara (`seguranca.py:1`). |
| Validação de conteúdo (sem `script`, `img`, `url(`, links externos) | `seguranca.py:105-118` | **Reutilizada nos dois modos.** No modo real, a URL permitida passa a ser a URL neutra configurada. |
| Capacidade `pode_simular_comunicacao` (CPAEG ou CSAEG, escopo da 011) | `governanca/regras.py:78-80` | **Substituída** por capacidades específicas de Lote (§15). |
| Rotas `campanhas/<uuid>/comunicacao/` e `…/simular/` | `acompanhamento/urls.py:17-18` | **Retiradas.** O Lote substitui a simulação. |
| Recusa por categoria fixa, sem texto de exceção (FR-037) | `comunicacao/acesso.py:25-31` | **Reutilizada.** |
| Nenhuma persistência (FR-033) | — | **Revista.** A 020 tem consumidor concreto para histórico (DP-1607 resolvida no limite do Lote). |

**Leitura crítica.** A 016 entrega um bom esqueleto de mensagem e de transporte, mas três
coisas impedem tratá-la como "trocar Mailpit por SMTP":

1. não há contato real nem modelo de contato;
2. não há seleção reproduzível — o público é recalculado a cada execução;
3. não há memória de quem já foi abordado, e repetir a ação reenvia para todos (016 FR-029).

O ponto 3 é aceitável numa caixa local e inaceitável no envio real.

---

## 3. Inventário relevante da 017

- Campanha não tem coluna de estado. `EM_PREPARACAO`, `EM_COLETA` e `ENCERRADA` são
  derivados de `aberta_em`, `encerrada_em` e período (`campanha/consultas.py:40-74`).
- Só a CPAEG gere Campanha (`pode_gerir_campanha`, `regras.py:83`); a CSAEG não gere
  (017 C2, DP-403).
- A 017 proíbe na Campanha Lote, coorte, foco, mailing e seleção de egressos (FR-024,
  `spec.md:500-502`; fora de escopo `:680-681`). A 020 respeita isso: **o formulário da
  Campanha não muda**.
- Ponto de encaixe: o detalhe da Campanha (`acompanhamento/campanha.html`), onde hoje fica
  o link "Comunicação simulada" (`:29`), passa a ter "Lotes de mobilização".
- O teste `tests/acompanhamento/test_acompanhamento_acesso.py:64-77` exige marcador de
  gate em toda rota do acompanhamento. Rotas novas precisam de marcador próprio.
- `populacao_no_momento(campanha)` (`consultas.py:223`) é a única definição de
  abrangência e deve ser consumida, não reimplementada.

---

## 4. Lacunas atuais para comunicação real

| Lacuna | Evidência |
| --- | --- |
| Nenhum contato persistido nem no contrato da fonte | `academico/models.py`, `fonte_academica/contrato.py`; 001 `spec.md:392-394` adiava e-mail e telefone até haver consumidor concreto |
| Nenhuma seleção congelada nem histórico | 016 FR-033 |
| Nenhuma proteção contra disparo repetido | 016 FR-029 |
| Transporte limitado a loopback e a `example.invalid` | `seguranca.py:81-102` |
| Texto da mensagem é de demonstração | `convite.txt:1-9` |
| URL neutra validada só como `http://127.0.0.1:8000/acesso/` | `seguranca.py:35-56` |
| Capacidade de comunicação explicitamente não produtiva | `regras.py:78-80` |
| Sessão do egresso só aceita fonte simulada | `acesso/sessao.py:18` (correto até o Portão da 018) |
| Decisões institucionais abertas | DP-1601…1608, 004/DP-407, 001/DP-009 |

A 020 resolve as lacunas técnicas. As institucionais continuam pendentes e são o Gate B
(§19).

---

## 5. Modelo mínimo de contato

### 5.1 Contato separado de Pessoa

`Pessoa` continua identidade de domínio (Terminologia; 001 FR-003). Adicionar
`Pessoa.email` teria três defeitos:

- obrigaria a escolher um valor e sobrescrever o outro, violando o Princípio III
  ("nenhuma das fontes sobrescrita silenciosamente");
- perderia a origem e o momento (Princípio IV);
- reescreveria o histórico de Lotes que usaram o valor anterior (§9).

**Recomendação: um registro próprio, `ContatoDaPessoa`, imutável depois de gravado.**

| Atributo | Significado |
| --- | --- |
| Pessoa | Dono do contato. A Conclusão não tem contato (contato não é contexto acadêmico). |
| Canal | E-mail. É o único canal da 020 (§5.4). |
| Valor | O endereço, normalizado só no que é seguro (espaços externos; domínio em minúsculas). |
| Origem | `FONTE_ACADEMICA` (com o código do provider) ou `EGRESSO`. |
| Obtido em | Momento da importação (origem fonte) ou do informe (origem egresso). |

**O que fica de fora e por quê**:

- **"Verificado", "atualizado", "válido", "qualidade" ou score.** Não há consumidor nem
  evidência. Origem não é qualidade: um contato da fonte tem verificação e atualidade
  *desconhecidas*, e isso se representa pela **ausência** de afirmação, não por um campo
  com valor "desconhecido". Se a confirmação de e-mail vier a existir (§7.4), ela será um
  registro próprio, como a validação da 019.
- **"Ativo/inativo", "principal" e "preferido".** A precedência é calculada pela política
  (§6). Nada é marcado.
- **Rótulo "pessoal/institucional".** A fonte pode não distinguir (Gate A). Sem consumidor.

### 5.2 Imutabilidade e "atualização"

- Um informe do egresso **acrescenta** um registro novo. Não altera nem apaga o anterior,
  seja importado ou informado.
- Uma reimportação que observa um valor novo acrescenta um registro. Valor igual da mesma
  origem não duplica (idempotência).
- Exclusão e expurgo por retenção são decisão institucional pendente (DP-2006). A 020 não
  apaga contatos.

### 5.3 Contato importado: capacidade separada da fonte acadêmica

*(Revisto em 2026-10-05 pelo precedente da 021 FR-071.)*

A versão inicial estendia `PessoaEncontrada` com e-mails. Isso faria a incorporação e a
identificação da 018, que usam `obter_pessoa()`, dependerem de um dado que não é de
identidade. Uma falha ou mudança no contato afetaria o acesso. A 021 resolveu o mesmo
problema para ingresso e agregados com uma capacidade separada. A 020 segue o precedente:

- **Fronteira de contatos da fonte.** É própria e separada da `FonteAcademica`. Para
  Pessoas já incorporadas, informa zero ou mais e-mails por Pessoa, na ordem de preferência
  que o adaptador declara. A peculiaridade da fonte — vários campos, campo institucional,
  histórico — fica no adaptador (Princípio V). Um adaptador real pode ler a mesma view
  larga e alimentar os três contratos (acadêmico, contexto da 021 e contatos).
- **`FonteAcademica`, `PessoaEncontrada`, `ConclusaoNaFonte`, `CAMPOS_DE_CONTEXTO` e a
  incorporação da 001 não mudam.** Acesso (018), incorporação (001), declaração e validação
  (019) não importam nem chamam a capacidade de contatos.
- **Carga de contatos à parte.** Grava cada e-mail observado como `FONTE_ACADEMICA`, com o
  código da fonte, a posição na ordem e o momento.
  - A consulta à fonte ocorre fora da transação.
  - Indisponibilidade não grava nada, não se confunde com "sem contato" e não se propaga.
  - Falha de uma Pessoa não interrompe as demais.
  - Não atualiza `Pessoa`.
  - O padrão é o de `contexto_trajetoria/carga.py`.
- **Na demonstração.** O preparo carrega contatos depois da incorporação, como já carrega o
  contexto da 021. O adaptador simulado de contatos fornece os endereços fictícios hoje
  fixos em `comunicacao/contatos.py`, só no domínio `example.invalid`:
  - SIM-P-0010 continua sem contato;
  - ao menos uma Pessoa tem dois e-mails, para exercitar a ordem.
  - O acervo histórico (019) não fornece contato.
- **Sem carga em massa nova.** A carga real e sua periodicidade dependem do Gate A e de
  DP-1601.

### 5.4 E-mail sim, telefone/WhatsApp não (por ora)

O roadmap pede "prever" e-mail e WhatsApp. A auditoria recomenda **só e-mail na 020**:

- **Consumidor.** A 020 envia apenas e-mail. Telefone não teria consumidor. O Princípio
  XVI (NON-NEGOTIABLE) veda coletar dado "apenas porque poderá ser útil no futuro".
- **Canal.** WhatsApp real está fora de escopo (DP-1608), e um número declarado não é
  WhatsApp verificado.
- **Fonte.** Nada no código ou nas specs demonstra que a fonte oferece telefone (§18).
- **Custo de adiar.** Baixo. O registro de contato já tem canal, e acrescentar um segundo
  canal é aditivo.

Telefone e WhatsApp entram quando houver canal e finalidade decididos (DP-1608, DP-2003).

### 5.5 Proteção em repouso

E-mail precisa ser legível para envio, logo HMAC sozinho não serve.

**Alternativas**:

| Opção | Prós | Contras |
| --- | --- | --- |
| **(a) Claro no banco, acesso só por operações nomeadas (recomendada)** | Simples. Nenhuma chave nova a gerir para cada envio. O e-mail não é credencial: a 018 não autentica por e-mail e a 020 não cria link mágico. | Um dump do banco expõe a lista. Isso é mitigado no nível de infraestrutura, que já protege as Respostas. |
| (b) Criptografia de aplicação (Fernet, como ADR 0005) | Defesa contra dump. Padrão já conhecido no projeto. | A ADR 0005 cifrou CPF e data porque eles **são** o fator de verificação da 018. E-mail não tem esse papel. Exigiria chave e rotação (DP-1903) e decifração em todo envio, sem índice possível para deduplicar. Seria analogia, não risco. |
| (c) Claro + HMAC auxiliar | Comparar sem ler | Sem consumidor: a deduplicação é por Pessoa, nunca por endereço (016 FR-009). |

**Controles da opção (a), obrigatórios na spec**:

- Nenhum e-mail aparece em URL, log, mensagem de erro, 011, 012, 013, telas públicas nem
  telas administrativas. Operadores veem **apenas contagens**.
- O egresso não vê o contato armazenado (§7.3).
- Só duas operações leem o valor: a confirmação do Lote (para congelar a referência) e o
  envio (para endereçar).
- Testes de fronteira (como os de 012 e 013) garantem a ausência de contato nas saídas.
- Cifragem em repouso pela infraestrutura institucional e retenção são **Gate B**
  (DP-2006). Se a instituição exigir cifragem de aplicação, a troca para (b) é localizada
  no registro de contato.

---

## 6. Proveniência e política de escolha do contato

**Política determinística e explicável**, aplicada a uma Pessoa num instante *t*:

1. O e-mail informado pelo próprio egresso **mais recente** até *t*.
2. Sem ele, o e-mail importado da fonte acadêmica da **observação mais recente** até *t*,
   o primeiro na ordem declarada pelo adaptador.
3. Sem nenhum dos dois, a Pessoa fica **sem contato utilizável**.

Justificativas:

- A declaração do próprio titular é a manifestação mais direta. Não é "mais verdadeira" —
  é a que ele escolheu para ser contatado, e a escolha é explicável a ele.
- Dentro da mesma origem, vale o mais recente: o histórico permanece, mas o uso segue o
  último registro.
- O contato importado permanece e volta a valer se o egresso não tiver informado nenhum.
- Não há aleatoriedade, score nem combinação.
- Um registro cujo endereço não passa na validação sintática (a da 016, sem a exigência de
  `example.invalid` no modo real) não é utilizável, e a política passa ao candidato
  seguinte na mesma ordem.

O Lote grava **qual** registro foi escolhido. Isso dá origem e valor por referência a um
registro imutável, sem cópia. A explicação de cada escolha é, portanto, reconstruível.

O Gate A pode refinar o passo 2 (por exemplo, preferir um campo pessoal a um institucional
antigo). Esse refinamento fica no adaptador, que declara a ordem, sem mudar a política.

---

## 7. Atualização voluntária pelo egresso

### 7.1 Onde e quando

- **Ponto de entrada** *(revisto em 2026-10-05 pela 021 FR-003)*. A tela de Participação
  concluída (`interface/concluida.html`) agora tem uma única ação: "Ver minha trajetória
  no Ifes" (021 FR-003). Alternativas:

  | Opção | Efeito |
  | --- | --- |
  | **(a) Convite secundário na tela de conclusão (recomendada)** | Mantém "Ver minha trajetória no Ifes" como ação principal e primeira. Abaixo dela, com menor destaque, um link "Quer manter seu e-mail atualizado com o Ifes?". A 021 FR-003 passa de "única ação" para "ação principal" (nota de revisão). Preserva o pedido de oferecer o contato após a conclusão. |
  | (b) Convite dentro da página "Minha trajetória" | Acopla contato e devolutiva. Contraria a independência pedida pelo solicitante e declarada na 021 FR-009 ("NÃO DEVE depender de contato … nem da 020"). |
  | (c) Só na escolha de formações (`/formacoes/`) | Não toca a 021, mas some do momento pós-conclusão, onde o convite faz sentido. |

  Na opção (a), o convite **não** é uma tela intermediária entre a conclusão e a Minha
  Trajetória e não condiciona nada. A página de e-mail é própria e **fora** do percurso do
  instrumento e da narrativa. Depois de salvar ou recusar, oferece voltar à escolha de
  formações e, quando disponível, à Minha Trajetória.
- **Requisitos de acesso.** Exige sessão do egresso da 018 (`pessoa_em_uso`). Usa só a
  Pessoa da sessão; nenhuma Pessoa vem do cliente.
- **Independência.** Não depende de Versão nem de Resposta, não altera Participação e não é
  condição de nada. A página pode ser alcançada de novo por quem tem sessão, sem exigir
  nova Participação. A 020 só a anuncia na tela de conclusão.
- **Formação declarada.** Sessões de declarante (019) não têm Pessoa (`pessoa=None`). A
  oferta **não aparece** para elas, sem tratamento especial inventado (§17).

### 7.2 Conteúdo da página

- Um campo de e-mail, opcional. A finalidade é declarada em texto institucional
  provisório: "contato do Ifes para pesquisas de acompanhamento de egressos". O texto
  definitivo é Gate B (DP-2003).
- Declaração explícita de que o e-mail **não será público** e não será usado para outra
  finalidade.
- "Agora não" tem o mesmo peso visual de "Salvar". Não há recompensa nem bloqueio.
- Ao salvar, grava um registro `EGRESSO` com momento e responde com confirmação neutra.

### 7.3 Não exibir o contato armazenado

O acesso da 018 é CPF + data de nascimento: verificação proporcional à pesquisa, não ao
cadastro. Mostrar o e-mail guardado revelaria dado pessoal a quem conhecesse esses dois
dados. Recomendação:

- **não exibir** o contato atual;
- informar apenas que "o e-mail que você informar passa a ser usado nos próximos contatos
  do Ifes sobre pesquisas".

Isso também elimina a necessidade de "editar" ou "remover" um valor visível.

### 7.4 Confirmação de e-mail (link ou OTP)

**Fica fora da 020.**

- **Consumidor.** O uso do endereço é só receber convite com link neutro. Um endereço
  errado ou de terceiro recebe uma mensagem sem dado pessoal.
- **Custo.** Confirmar exige envio real (bloqueado até o Gate B), token individual,
  expiração e tela própria.
- **Risco aceito.** Quem souber CPF + data de outra pessoa pode registrar um e-mail para
  ela. O efeito é desviar convites neutros, não acessar dados. O risco fica registrado
  (DP-2004), e a confirmação entra quando houver consumidor (por exemplo, a Minha
  Trajetória).

### 7.5 Remoção, oposição, preferência

- A 020 não oferece "remover meu e-mail" nem "não quero receber". São opt-out e oposição
  (DP-1606), decisões institucionais.
- O Gate B exige essa decisão **antes** do envio real, porque a mensagem real precisa dizer
  como o egresso deixa de receber.

---

## 8. Semântica do Lote

> **Lote de Mobilização**: onda operacional, pertencente a uma Campanha, que registra quais
> Pessoas foram selecionadas para abordagem, por qual contato e com qual resultado mínimo
> de tentativa.

- **Pertence a uma Campanha.** É só uma relação; o Lote não copia o estado da Campanha.
- **Membros são subconjunto da abrangência.** Abordar quem a Campanha não admite seria
  convite enganoso. O Lote é sempre a interseção: abrangência × escopo do operador ×
  filtros.
- **Não é população.** 011 continua contando elegíveis pela 004, e o Lote não aparece em
  admissão, entrada, 007, 012 ou 013.
- **Não exclui ninguém.** Uma Pessoa fora de qualquer Lote responde normalmente.
- **Filtros.** Unidade (uma ou mais), nível e intervalo de ano de conclusão.
  - Curso entra como filtro textual opcional, por igualdade, sem normalização
    (010/DP-1005).
  - "Situação de contato" **não** é filtro: membros sem contato ficam registrados como sem
    contato, o que é mais informativo e evita um segundo vocabulário.
  - Modalidade e forma de oferta ficam fora, por falta de caso concreto.
- **Nome.** Um rótulo curto do operador, para distinguir ondas. Não tem significado de
  domínio.

---

## 9. Grão do membro

**Grão: Pessoa.** Um membro é (Lote, Pessoa), único no Lote.

- Uma Pessoa com várias Conclusões no recorte recebe **uma** mensagem: o convite é neutro e
  não escolhe formação (016 FR-016/022). A 007 resolve a formação na entrada.
- Não se grava quais Conclusões casaram com o filtro. Não há consumidor, e o link não
  carrega formação. Os filtros do Lote ficam gravados, e o motivo de inclusão é explicável
  por eles no momento da confirmação.

O membro grava:

- a Pessoa;
- o **registro de contato escolhido** (ou nenhum), por referência imutável;
- a situação da tentativa e seus instantes (§14).

---

## 10. Filtros e ordem de seleção

Ordem obrigatória, avaliada no momento da confirmação:

```text
Conclusões na abrangência da Campanha (004 populacao_no_momento)
  → restrição ao escopo do operador (010/011: unidades da CSAEG)
  → filtros do Lote (unidade, nível, ano, curso)
  → Pessoas distintas (por identidade interna; nunca por nome ou e-mail)
  → exclusão das Pessoas já mobilizadas nesta Campanha (§12)
  → escolha do contato de cada Pessoa (§6)
  → membros congelados
```

- **Filtrar antes de deduplicar.** Filtro é atributo da Conclusão. Uma Pessoa entra se
  **alguma** Conclusão dela satisfaz abrangência, escopo e filtros.
- **Escopo antes dos filtros.** Uma CSAEG Serra nunca seleciona por uma Conclusão de
  Vitória. A mesma Pessoa pode ter também Conclusão em Vitória: o convite neutro não revela
  isso, e a Pessoa entra uma vez.
- **Contato por último.** Ausência de contato não remove a Pessoa: ela fica membro sem
  contato.

---

## 11. Congelamento

**Alternativas**:

| Opção | Descrição | Avaliação |
| --- | --- | --- |
| **(A) Lote nasce congelado (recomendada)** | O operador ajusta filtros numa prévia transitória, com contagens recalculadas e nada gravado. "Confirmar Lote" grava o Lote já com membros e contatos. | Um único estado persistido de seleção. Nenhum rascunho para limpar. A prévia é o "rascunho". |
| (B) Rascunho persistido → Confirmado | O Lote é gravado com filtros editáveis e congelado depois. | Exige estado, edição, exclusão de rascunho e regra para rascunho velho. O único ganho — retomar a preparação outro dia — não tem caso concreto. |

Na opção (A), o congelamento grava:

- filtros;
- momento da confirmação;
- operador;
- escopo aplicado;
- membros;
- contato escolhido por membro (o registro carrega origem e momento de obtenção).

**Cenário de referência**:

- 04/10: o Lote A congela o membro P com o registro `antigo@…` (origem fonte).
- 05/10: o egresso informa `novo@…`, gravado como um novo registro.
- O histórico do Lote A continua apontando para `antigo@…`. O envio do Lote A, mesmo que
  ocorra depois de 05/10, usa o contato congelado.
- Um Lote B futuro escolheria `novo@…`. P, porém, já foi mobilizado nesta Campanha (§12).

**Por que o contato do envio é o congelado e não o vigente no envio.** O operador confirma
o que viu. Trocar o endereço entre a confirmação e o envio tornaria o histórico dependente
do momento do clique. O intervalo entre os dois passos é curto por desenho (§13).

Lote confirmado **não é editado nem apagado**. Se não for enviado, permanece como registro
de que foi preparado.

---

## 12. Duplicidade entre Lotes

**Regra padrão.** Na confirmação de um Lote da Campanha X, uma Pessoa é **excluída** se
já for membro de outro Lote de X em qualquer situação diferente de "sem contato":
não tentado, tentativa em curso, submetido, falha ou incerto.

| Situação no Lote anterior | Pode entrar num novo Lote de X? | Por quê |
| --- | --- | --- |
| Sem contato | **Sim** | Nenhuma mensagem saiu. Se o egresso informar e-mail depois, pode ser abordado. |
| Não tentado (Lote anterior ainda não enviado) | Não | Será abordado pelo Lote anterior. |
| Submetido ao transporte | Não | Já abordado. |
| Falha de transporte | Não | Reenvio deliberado é DP-2005. |
| Resultado incerto | Não | Pode ter saído. |

- A interface mostra quantas Pessoas foram excluídas por "já mobilizadas nesta Campanha".
- Na outra Campanha, nada é afetado (nova rodada, novo convite).
- **Defesa em profundidade.** No envio, antes de cada mensagem, verifica-se de novo se a
  Pessoa não tem outro membro submetido, incerto ou em curso em X. Isso protege contra
  Lotes confirmados em concorrência; o plan decide o mecanismo de serialização.

---

## 13. Comunicação real

**Preservado da 016**:

- renderer único;
- texto + HTML;
- uma mensagem por destinatário, sem CC/BCC nem anexos;
- link neutro igual para todos;
- nenhum CPF, identificador acadêmico, token ou identificador de Lote ou membro no
  conteúdo ou na URL;
- a comunicação não cria Participação nem autentica.

**Ação "Enviar Lote"**:

- POST explícito com CSRF, revalidando no servidor capacidade, escopo, estado da Campanha
  (§14) e configuração de transporte.
- Processa os membros **não tentados**, um a um, uma tentativa cada.
- Grava a situação **de cada membro no momento da tentativa** (não ao final). Uma execução
  interrompida pode ser retomada pela mesma ação: só os não tentados são processados.
- **Antes** de submeter, marca o membro como "tentativa em curso". Se o processo cair entre
  a submissão e o registro do resultado, o membro fica **incerto** e **nunca é tentado
  automaticamente de novo**. Isso evita duplicidade silenciosa.
- Sem fila, scheduler, retry automático ou envio em segundo plano. O plan decide se o
  processamento é limitado por requisição (lotes muito grandes processados em várias ações
  de "continuar envio"). A semântica de retomada torna isso seguro.

**Fronteira de transporte e modos** (configuração explícita; nenhum padrão implícito
habilita envio):

| Modo | Quando | Barreiras |
| --- | --- | --- |
| Teste | Suíte | Backend em memória, somente sob marcador de teste (como a 016). |
| Demonstração | Demonstração ligada | As barreiras atuais da 016: loopback, sem credenciais, remetente e destinatários `example.invalid`, URL local. |
| Real | **Desativado até o Gate B** | Exige ativação explícita, backend SMTP com TLS, credenciais só por ambiente, remetente institucional configurado, URL neutra `https` configurada e base **sem** dados simulados. Recusa modo demonstração ligado. |

- O fornecedor não é codificado. A fronteira é o backend de e-mail do framework, com
  validação própria do sistema. Trocar SMTP por API de provedor é decisão do plan após o
  Gate B (DP-1604).
- **Texto.** O modo demonstração mantém o texto atual. O modo real usa um texto
  institucional **provisório** e não editável, marcado como dependente de aprovação
  (DP-2003, 008/DP-801). Não há editor.

---

## 14. Estados de envio

**Por membro**, persistidos:

| Situação | Significado | Quando |
| --- | --- | --- |
| `SEM_CONTATO` | Nenhum contato utilizável na confirmação | Gravada na confirmação; final |
| `NAO_TENTADO` | Membro com contato aguardando envio | Gravada na confirmação |
| `EM_TENTATIVA` | Tentativa iniciada, resultado ainda não registrado | Antes do submit |
| `SUBMETIDO_AO_TRANSPORTE` | O backend aceitou a mensagem | Final |
| `FALHA_DE_TRANSPORTE` | O backend recusou ou houve erro de transporte | Final (sem retry) |

- `EM_TENTATIVA` que sobrevive à execução é apresentado como **resultado incerto**.
- Não existem `ENTREGUE`, `BOUNCE`, `ABERTO` nem `CLICADO`. Aceite do transporte não
  comprova entrega.
- Eventos de entrega só com provedor e contrato técnico definidos (DP-1604).

**Do Lote**: nenhum campo de estado. A situação é **derivada** das situações dos membros:
não enviado, envio parcial ou envio concluído. Assim não se duplica estado.

---

## 15. Governança

| Ação | Capacidade proposta | Quem, na interpretação local reversível | Observação |
| --- | --- | --- | --- |
| Ver Lotes e contagens de uma Campanha | `pode_consultar_lotes` | CPAEG (todos); CSAEG (Lotes cujo recorte de unidades está contido nas suas) | Mesma visibilidade de Campanha da 011 |
| Preparar (prévia) e confirmar Lote | `pode_preparar_lote` | CPAEG (institucional); CSAEG (só nas suas unidades, filtro de unidade obrigatório dentro do escopo) | Aplicação nas unidades (PAEG Art. 22, IV), como na 016 |
| Enviar Lote | `pode_enviar_lote` | CPAEG; CSAEG no seu escopo — **somente demonstração** enquanto DP-1602 estiver aberta | O modo real não fica disponível sem Gate B, qualquer que seja a capacidade |
| Ver histórico de envio | coberto por `pode_consultar_lotes` | — | Apenas agregados; nenhuma lista individual |
| Atualizar o próprio contato | sessão do egresso (018) | O egresso, sobre a própria Pessoa | Não é capacidade administrativa |

- **Separar "preparar" de "enviar".** Permite, no Gate B, decidir que só uma instância
  envia (por exemplo, a comunicação institucional) sem mexer na preparação.
- Acompanhar (011) **não** concede nenhuma dessas ações, e `pode_gerir_campanha` também
  não.
- O operador é gravado na confirmação e no envio, como a 019 faz na validação. Isso é
  rastreabilidade proporcional, porque envio real é ação de risco. Retenção desse registro
  é DP-2006.

---

## 16. Privacidade e LGPD

- **Finalidade.** Contato para convites de pesquisa de acompanhamento. Nenhum outro uso.
  Base legal e transparência são Gate B (DP-1603).
- **Minimização.** Só e-mail; sem telefone, LinkedIn ou Lattes; sem "verificado" nem
  "qualidade"; operadores sem acesso a endereços individuais.
- **Saídas.** Nenhum contato em URLs, logs, mensagens de erro, 011, 012, 013, telas
  públicas ou telas administrativas. Testes de fronteira dedicados.
- **Exposição pública.** E-mail nunca é público. Preferência de comunicação ≠ opt-in de
  exposição (roadmap item 6). Portal e perfil têm finalidade própria futura.
- **Retenção.** Contatos e histórico de Lotes não têm expurgo na 020 (DP-2006). O envio
  real fica bloqueado sem essa decisão.
- **Dados reais.** Nenhum. A demonstração usa apenas `example.invalid`.

---

## 17. Efeitos nas features anteriores

| Feature | Efeito |
| --- | --- |
| 001 | **Contrato e incorporação inalterados** (precedente da 021 FR-071). Nova capacidade de contatos da fonte, separada, com carga própria. `Pessoa` e `ConclusaoAcademica` não mudam. A vedação da 001 de "não incorporar e-mail" ganha nota de revisão: o e-mail é admitido pela 020, com consumidor concreto, fora do contrato acadêmico (como a 018 fez com CPF e a 021 com ingresso). |
| 004 | Nenhuma mudança de critério, população ou admissão. ADR 0004 ganha nota "Lote especificado na 020". |
| 005/006/007 | Nenhuma. A tela de conclusão ganha um convite opcional fora do percurso. |
| 010 | Três capacidades novas no conjunto enumerado por `test_governanca_regras.py`. `pode_simular_comunicacao` é retirada. |
| 011 | Indicadores inalterados. O detalhe da Campanha troca "Comunicação simulada" por "Lotes de mobilização". Nenhum indicador de "convidados" no painel de coleta. |
| 012 | Inalterada. Snapshots históricos intocados. Teste de fronteira já proíbe `email` e `telefone`. |
| 013 | Inalterada. Contato e Lote fora das colunas. |
| 016 | A tela e a capacidade de simulação são retiradas. Renderer, validações e barreiras viram o modo demonstração do envio por Lote. FR-033 é revista. DP-1601 e DP-1607 ficam parcialmente resolvidas; DP-1602…1606 e DP-1608 continuam. |
| 017 | Formulário da Campanha inalterado. Lotes ficam no detalhe da Campanha. |
| 018 | A sessão do egresso passa a autorizar também "informar meu e-mail". FR-053 (link neutro) preservado. |
| 019 | **Nenhuma alteração.** Declarante sem Pessoa não recebe a oferta. Uma formação validada liga-se a uma Conclusão cuja Pessoa já entra pela população normal. Nada é especial. |
| 014 / 021 | **Impacto compartilhado, apesar da independência funcional.** A tela de conclusão ancorada em Conclusão mantém "Ver minha trajetória no Ifes" como ação principal e ganha o convite secundário (§7.1). Nota de revisão na 021 FR-003 ("única ação" → "ação principal") e, por consequência, na 014 FR-041. A narrativa, o card e a 021 FR-009/FR-070 não mudam: nenhum benefício depende de contato. |
| 022 | Nenhuma. O vídeo não lê contato (022 já veda e-mail e telefone no conteúdo). |
| Documentação institucional (`docs/documentacao/index.html`) | Atualizada na consolidação da spec (decisão de 2026-10-05), distinguindo especificada, implementada e habilitada para uso real. |

---

## 18. Gate A — Profiling futuro da fonte real de contatos

**NÃO EXECUTADO. Nenhum resultado é conhecido ou simulado nesta auditoria.**

**Objetivo.** Antes de implementar o adaptador real, saber o que a fonte acadêmica oferece
como contato, com que cobertura e com que confiabilidade, para refinar o adaptador e a
ordem do §6. A arquitetura da 020 não muda com o resultado.

**Condições**:

- ambiente institucional autorizado;
- consultas executadas por quem já tem acesso à fonte;
- **somente agregados** saem do ambiente;
- células com menos de 10 Pessoas são suprimidas;
- nenhum endereço, nome, CPF ou matrícula sai do ambiente;
- base legal do levantamento verificada antes (001/DP-009).

**Perguntas e consultas agregadas**:

1. **Existência.** Quais tabelas e campos guardam e-mail, telefone ou celular? Têm
   documentação ou dicionário de dados? (Inspeção de esquema, sem ler valores.)
2. **Relação com a identidade.** O contato liga-se ao identificador da pessoa, ao do
   aluno/matrícula ou ao do curso? Uma Pessoa com várias matrículas tem contatos
   diferentes por matrícula?
3. **Cobertura.** Percentual de egressos (Pessoas com Conclusão) com ao menos um e-mail
   não vazio, quebrado por ano de conclusão (faixas), unidade, nível e modalidade.
4. **Sintaxe.** Percentual de valores que passam na validação sintática usada pelo
   sistema; categorias de falha (sem `@`, espaços, vários endereços num campo).
5. **Multiplicidade.** Distribuição do número de e-mails distintos por Pessoa (0, 1, 2,
   3+).
6. **Compartilhamento.** Número de endereços associados a mais de uma Pessoa (indica
   e-mail de responsável, genérico ou erro).
7. **Institucional × pessoal.** Proporção de endereços em domínios do próprio Ifes
   (contagem por classe "domínio institucional/outro", sem listar domínios externos).
8. **Atualidade.** Há data de atualização? Distribuição por faixa de ano da última
   atualização, cruzada com o ano de conclusão.
9. **Telefone.** Existe campo? Cobertura, formato e possibilidade de distinguir celular.
10. **Inconsistências históricas.** Variação de cobertura e formato entre períodos (por
    exemplo, antes e depois de migrações de sistema).

**Riscos**:

- expor dado pessoal fora do ambiente;
- tratar uma amostra como população;
- confundir "campo preenchido" com "contato válido";
- inferir atualidade sem data de atualização.

**Decisões da 020 que o Gate A pode refinar** (sem mudar a arquitetura):

- a ordem de preferência declarada pelo adaptador;
- inclusão de telefone como segundo canal (com DP-1608);
- necessidade de confirmação de e-mail (DP-2004);
- prioridade operacional de pedir atualização a coortes antigas;
- filtros de Lote úteis na prática.

**A arquitetura já suporta**:

- muitos egressos sem e-mail (membros sem contato, contados);
- só e-mail antigo (usado até o egresso informar outro);
- vários e-mails por Pessoa (ordem do adaptador; todos preservados);
- inexistência de telefone (nenhum campo depende dele);
- variação histórica (nenhum percentual é premissa).

---

## 19. Gate B — Antes do envio real

O modo real permanece **desativado** até que estejam resolvidos e registrados:

| Item | Decisão | Instância provável (a confirmar) | DP |
| --- | --- | --- | --- |
| Base legal e finalidade do uso do contato para convite | Jurídica/LGPD | Encarregado, Proex | DP-1603 |
| Transparência: texto ao egresso na mensagem e na página de atualização | Editorial/jurídica | Proex, comunicação, encarregado | DP-2003 |
| Remetente institucional (endereço, nome, domínio, SPF/DKIM/DMARC) | Institucional/técnica | DTI, comunicação | DP-2002 |
| Provedor/SMTP, limites de envio, reputação | Técnica | DTI | DP-1604 |
| Credenciais e segredos (cofre, rotação, acesso) | Técnica | DTI | DP-1604 |
| Retenção de contatos e histórico de Lotes | Jurídica | Encarregado, CPAEG | DP-2006 |
| Quem prepara e quem autoriza envio real; por unidade | Governança | CPAEG/Proex, CSAEGs, DIREC | DP-1602, 004/DP-407 |
| Opt-out e preferência de comunicação; como a mensagem os oferece | Jurídica/operacional | Encarregado, CPAEG | DP-1606 |
| Suporte ao egresso (respostas ao remetente, reclamações) | Operacional | DIREC, CSAEGs | DP-2007 |
| Fonte real de contatos e adaptador (após Gate A) | Técnica/institucional | DTI, responsáveis pela fonte | DP-1601 |
| Identificação produtiva de operadores | Técnica | DTI | 010/DP-1001 |
| Observabilidade: o que registrar sobre envio sem dado pessoal | Técnica | DTI | DP-2008 |

---

## 20. Decisões pendentes

Novas (numeração DP-2001 em diante):

| ID | Pergunta | Hipótese local reversível |
| --- | --- | --- |
| DP-2001 | Quem prepara e quem envia Lotes em produção (refina DP-1602) | CPAEG institucional e CSAEG por unidade, só em demonstração |
| DP-2002 | Remetente institucional | Remetente fictício na demonstração; o modo real exige configuração explícita |
| DP-2003 | Texto institucional do convite real e da página de atualização de e-mail | Texto provisório, marcado como não aprovado |
| DP-2004 | Confirmação de e-mail informado pelo egresso | Sem confirmação; risco de convites desviados aceito em demonstração |
| DP-2005 | Reenvio deliberado (falha, incerto, nova onda na mesma Campanha) | Nenhum reenvio; a Pessoa fica excluída de novos Lotes da mesma Campanha |
| DP-2006 | Retenção e expurgo de contatos e do histórico de Lotes e envios | Nada é apagado |
| DP-2007 | Suporte e caixa de resposta | Nenhum |
| DP-2008 | Observabilidade do envio real (métricas e logs sem dado pessoal) | Logs apenas de categoria |
| DP-2009 | Telefone/WhatsApp como canal (com DP-1608) | Não coletado |

Herdadas e preservadas: DP-1601…1608, 004/DP-406, 004/DP-407, 004/DP-408, 001/DP-009,
005/DP-504, 010/DP-1001, 010/DP-1005, 017/DP-1701, 018/DP-1801…1803 e 019/DP-1908.

---

## 21. Riscos de overengineering (e o que foi cortado)

| Tentação | Por que cortar |
| --- | --- |
| Rascunho de Lote persistido | Prévia transitória basta (§11). |
| Estado de Lote | É derivado dos membros. |
| Score de qualidade, "verificado", "principal" | Sem evidência nem consumidor. |
| Criptografia de aplicação do e-mail | Analogia com CPF, não risco equivalente (§5.5). |
| Telefone/WhatsApp agora | Sem consumidor (Princípio XVI). |
| Confirmação de e-mail | Sem consumidor. Exige envio real. |
| Fila, worker, scheduler, retry | A retomada idempotente resolve a interrupção. Piloto é controlado. |
| Webhooks, bounce, abertura, clique | Sem provedor. Tracking contraria o link neutro. |
| Editor de mensagem, personalização | Texto institucional fixo. |
| Lista individual de destinatários na interface | Expõe contato. Agregados bastam. |
| Atribuição de resposta ao Lote ("conversão") | O link neutro não permite. Seria inferência falsa. |
| Multicanal genérico, `NotificationService`, plugins | 016 FR-034 continua valendo. |
| Filtro por situação de contato | Membros sem contato já são contados. |
| Opt-out implementado sem decisão | Princípio XXIX; fica no Gate B. |

**Métricas permitidas no Lote**:

- membros;
- com contato;
- sem contato;
- excluídos por mobilização anterior;
- não tentados;
- submetidos ao transporte;
- falhas;
- incertos.

Nada disso é chamado de alcance, entrega ou conversão. A tela diz que pertencer ao Lote
não prova que a comunicação causou a resposta.

---

## 22. Recomendação arquitetural

Construir a 020 como **três peças pequenas** sobre a 016:

1. **Contato da Pessoa.** Registro imutável de e-mail com origem (fonte acadêmica ou
   egresso) e momento. É importado por capacidade separada da fronteira acadêmica e
   acrescido pelo egresso numa página opcional pós-conclusão. A escolha segue uma política determinística: egresso
   mais recente → fonte mais recente → sem contato.
2. **Lote de Mobilização.** Pertence à Campanha e nasce congelado a partir de uma prévia
   transitória:
   - abrangência → escopo → filtros → Pessoas distintas → exclusão de já mobilizadas na
     Campanha → contato;
   - membros por Pessoa, com referência ao contato escolhido.
3. **Envio por Lote.** Ação explícita, retomável e sem reenvio silencioso, com situações
   honestas por membro. A fronteira de transporte tem os modos teste, demonstração e real,
   com o real desligado até o Gate B.

**Momento em relação à Campanha** (revalidado em cada ação, sem copiar estado):

| Ação | EM_PREPARACAO | EM_COLETA | ENCERRADA |
| --- | --- | --- | --- |
| Ver Lotes | Sim | Sim | Sim |
| Prévia e confirmar Lote | Sim | Sim | Não |
| Enviar Lote | **Não** | Sim | **Não** (os membros não tentados permanecem não tentados) |

O envio só ocorre EM_COLETA. Convidar para uma pesquisa que ainda não aceita respostas, ou
que já encerrou, levaria a "sem pesquisa disponível". Se a Campanha encerra entre a
confirmação e o envio, a ação é recusada e os membros permanecem `NAO_TENTADO`.

**Forks resolvidos por recomendação** (para revisão do solicitante, sem bloquear a spec):

- §5.4: só e-mail, sem telefone/WhatsApp;
- §5.5: e-mail em claro com controles de aplicação;
- §11: Lote nasce congelado, sem rascunho persistido;
- §12: sem contato pode voltar; falha não volta;
- §7.3: o egresso não vê o e-mail guardado;
- §5.3 (revisão de 2026-10-05): contato importado por capacidade separada, com o contrato
  acadêmico intacto;
- §7.1 (revisão de 2026-10-05): convite secundário na tela de conclusão, com revisão
  pontual da 021 FR-003.

Nenhum deles exige decisão institucional para especificar; todos são reversíveis
localmente.

Com isso, a auditoria considera que **não há fork arquitetural material que impeça a
spec**. Segue para `/speckit-specify`.

---

## 23. Decisões do solicitante (2026-10-05)

| # | Decisão |
| --- | --- |
| E1 | **Confirmada.** Só e-mail. WhatsApp e telefone ficam pendentes até haver finalidade e uso concreto (DP-2009). |
| E2 | **Aceita somente na demonstração.** O plan justifica os controles de proteção do §5.5. Antes do uso real, a proteção em repouso é revista e a decisão registrada (nova DP-2010, item do Gate B). |
| E3–E6 | **Mantidas** como propostas (§§11, 12, 7.3, 11). |
| E7 | **Confirmada.** A independência funcional de 021 e 022 continua, mas **não elimina o impacto compartilhado** da 020 na tela de Participação concluída. A 020 revisa pontualmente a 021 FR-003 ("única ação" → "ação principal") e a 014 FR-041, e a documentação explicita que essa tela é definida por 014, 021 e 020. |
| Documentação | A documentação institucional é atualizada já na consolidação da spec, com três estados distintos: especificada, implementada (só demonstração) e habilitada para uso real (após os Gates A e B). |

Próximas etapas autorizadas: `/speckit-plan`, `/speckit-tasks` e `/speckit-analyze`, com
correção dos achados críticos. Implementação, não por ora. O plan mantém o adaptador
fictício e o envio real desativado, e inclui validação de:

- concorrência entre Lotes;
- retomada após interrupção;
- idempotência da carga de contatos;
- isolamento dos contatos em relação ao acesso e à narrativa.
