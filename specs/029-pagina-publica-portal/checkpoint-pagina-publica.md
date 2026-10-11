# Checkpoint 1 — bloco P: página pública (Feature 029)

Escrito em 2026-10-09, **antes** de qualquer sessão. Acrescenta um bloco ao
[protocolo do Checkpoint 1 da 024](../024-inicio-egresso-portal/evidencias/protocolo-checkpoint-1.md).
Os critérios SC-008 a SC-016 da 024, o limiar e a leitura do resultado **não mudam**.

> **Situação: NÃO APLICADO.** Os resultados entram em outro PR, depois da aplicação.
>
> **Sequência revista em 2026-10-09** (roadmap, revisão 10): o bloco será aplicado depois da
> 029 implementada, com "Contribuir com o Ifes". A "versão proposta" passa a ser a página
> servida em `/`, e a "versão atual" (028) precisa de outra forma de ser mostrada, como uma
> captura ou um protótipo estático. A seção "Material" é revista antes da aplicação, sem
> mudar perguntas nem critérios.

## Revisão de 2026-10-11 — versão C (Feature 032)

*(Roadmap, revisão 13. Prevalece sobre as seções abaixo onde houver diferença; o texto
abaixo fica como histórico.)*

- **Versão avaliada: a página pública C**, servida em `/` sem sessão pela `main` com a 032
  integrada (`63b9447` ou posterior). O commit vai na ficha. A página da 029 deixou de ser
  servida: a 032 revisou a ordem, as chamadas e a composição (032 FR-005, FR-006).
- **Comparação histórica: depende de P6** ([preparação](../024-inicio-egresso-portal/evidencias/checkpoint-1/preparacao-sessao.md)).
  As opções são comparar a C com a página da 029, com a da 028 ou não comparar.
  - **Recomendação deste kit, a decidir em P6:** a C sempre primeiro, para que P-01 e P-02
    da C tenham todos os participantes; a página da 029 como segunda versão, só para as
    etapas P3 e P4 e o P-07. O P-07 fica marcado como influenciado pela ordem.
  - **Página da 029:** cópia estática [`prototipo/proposta.html`](prototipo/proposta.html),
    com estilo embutido, aberta no computador do moderador. É o protótipo que a
    implementação da 029 reproduz, com três diferenças pequenas registradas na
    [validação da 029](validacao.md) (nível dos títulos dos exemplos, legenda do card e
    rótulo da categoria). As chamadas apontam para `/entrar/` da demonstração: o moderador
    não as segue.
  - **Página da 028:** cópia estática [`prototipo/atual.html`](prototipo/atual.html). Deixa
    de ser a comparação padrão, porque já foi substituída duas vezes.
  - Se P6 decidir alternar a ordem, valem as regras de "Ordem e contrabalanceamento"
    abaixo, com a C no lugar da "proposta".
- **O que a C mostra.** Menu da página com Encontros, Oportunidades e Contribuir (âncoras) e
  "Entrar"; abaixo de 480 px, só "Entrar". Abertura "Sua história com o Ifes" com a linha
  Ingresso → Adiante; como funciona; "Ninguém se forma sozinho", com um encontro de exemplo;
  oportunidades; contribuição e participação; o card de exemplo e a chamada final. Todos os
  exemplos têm o selo "Exemplo com dados fictícios".
- **Olhar livre (P2).** "Sem entrar" quer dizer não seguir "Conhecer o Portal", "Entrar" nem
  "Entrar para oferecer". As âncoras do menu podem ser usadas.
- **P-01, benefícios reais na C.** São os mesmos três do FR-005 da 029: oportunidades
  divulgadas pelo Ifes para a formação; contribuir com o Ifes (oferecer-se à unidade) e
  participar (pesquisa de acompanhamento, e-mail); ver as formações reconhecidas pelo Ifes
  ou o card. A C dá destaque próprio aos **encontros de egressos divulgados pela unidade,
  com link oficial**. Eles contam como o benefício "oportunidades", porque já estão no
  FR-005 ("eventos") e na categoria "Eventos" da 025 (alternativa A), e não como benefício
  novo. O critério e a lista de benefícios não mudam; só se explicita como ler a seção de
  encontros.
- **P-02, funções inexistentes na C.** O critério e a lista original continuam; a lista
  já inclui "comunidade", "rede de contatos" e "eventos próprios". Na C, anotar em especial
  se a pessoa atribui ao Portal: encontros organizados pelo Portal ou propostos por
  egressos; inscrição ou confirmação de presença em encontros; comunidade, rede ou
  diretório de colegas; contato com outros egressos; histórias de egressos publicadas. A faixa "Ninguém se forma sozinho",
  com a lista de lembranças da formação, é o ponto da C mais propenso a essa leitura. Anotar
  a frase. Dizer que a unidade divulga encontros de egressos é benefício real (P-01), e não
  falha de P-02.
- **Leitura do resultado na C** (substitui a tabela abaixo onde ela fala em "proposta",
  "atual" e "antes de implementar"):

  | Resultado | Decisão |
  |---|---|
  | P-02 falha | Corrigir o texto ou o exemplo da C que gerou a leitura, antes do Checkpoint 2 |
  | P-01 não atinge a referência na C | Revisar a primeira tela da C |
  | P-06 não atinge a referência | Rever identidade e explicação dos dados; registrar se a dúvida é sobre a identificação (018) |
  | Com comparação: P-07 favorece a versão histórica, com justificativa de conteúdo | Rever na C o ponto apontado. Não reverte a 032 automaticamente |

  Qualquer mudança de código depende de autorização do solicitante.

## O que o bloco quer saber

Se a página pública faz um egresso que nunca usou o Portal entender, em poucos segundos,
que ali existe uma relação com o Ifes (o que o Ifes oferece e como ele participa) e por que
vale entrar, **sem** acreditar que o Portal oferece algo que não oferece.

São observações qualitativas, com 5 a 8 pessoas. A maioria é referência, não validação
estatística. **Não são** medidas de conversão nem de retenção:

- dizer que entraria não é entrar;
- dizer por que voltaria não é voltar;
- preferir uma versão por gosto ("gostei mais") não conta para nenhum critério.

## Material

*(Revisto em 2026-10-10, com a 029 implementada. Perguntas e critérios não mudam.)*

- **Versão atual:** a página pública da 028, que não é mais servida. Usa-se a cópia estática
  [`prototipo/atual.html`](prototipo/atual.html), aberta no computador do moderador. Ela
  serve só para olhar: as chamadas não levam a lugar nenhum fora da demonstração.
- **Versão proposta:** a página da 029 implementada, em `/` da demonstração, sem sessão. A
  chamada principal leva à `/entrar/`.
- Mesmo ambiente do protocolo da 024 (computador do moderador, banco recém-preparado).
  O teste de 5 segundos usa 375×812, a referência de qualidade (ADR 0009, decisão 2). A
  comparação final usa também a largura de desktop (1440×900).

## Ordem e contrabalanceamento

O bloco vem **antes** da tarefa 1 da 024, porque depois de entrar a pessoa já conhece o
Portal.

- Participantes de número ímpar veem primeiro a **atual**; os pares, primeiro a
  **proposta**.
- O teste de 5 segundos da **primeira** versão vista é o resultado principal. O da
  segunda é anotado como secundário, porque a pessoa já viu a outra.
- Duração estimada: 10 minutos. A sessão da 024 passa de 25–30 para 35–40 minutos.

O moderador mantém a regra da 024: não usa "portal", "pesquisa", "trajetória" nem
"início" antes de a pessoa usar.

## Roteiro

**P1. Cinco segundos (primeira versão, 375×812).** Mostrar a primeira tela por 5 s,
cronometrados, e esconder. Perguntar:
- "O que é este lugar?"
- "O que você acha que encontraria lá dentro?"
- "Tem mais alguma coisa que este lugar ofereça?"

→ P-01 e P-02.

**P2. Olhar livre (primeira versão).** "Olhe à vontade, como faria no celular, mas sem
entrar." Até 90 s. Depois:
- "O que você acha que vai encontrar depois de entrar?" → P-03
- "Você entraria? Por quê?" → P-04
- "O que faria você voltar aqui outro dia?" → P-05
- "De quem é este site? Você informaria seu CPF e sua data de nascimento aqui? Por quê?"
  → P-06

**P3. Segunda versão.** Repetir P1 e um olhar livre de até 60 s, sem as perguntas de P2.
Anotar como secundário.

**P4. Comparação (375×812 e 1440×900).** Mostrar as duas versões, nas duas larguras, na
ordem em que foram vistas. "Qual das duas explica melhor o que se encontra aqui dentro? O
que faz você dizer isso?" → P-07.

**Passagem para a 024.** "Agora entre, como se tivesse recebido este endereço de um
amigo." Começa a tarefa 1 da 024, a partir de `/` da demonstração.

## Critérios e como observar

Cada critério é anotado por participante como **sim**, **parcial** ou **não**, com a frase
literal curta que o sustenta. Só "sim" conta.

| Critério | Etapa | "Sim" quando a pessoa… | Referência |
|---|---|---|---|
| P-01: benefício real em 5 s | P1 | cita ao menos um destes: oportunidades divulgadas pelo Ifes para a formação; contribuir com o Ifes (oferecer-se à unidade); participar (pesquisa, e-mail); ver as formações reconhecidas pelo Ifes ou o card | maioria, na primeira versão vista |
| P-02: nenhuma função inexistente | P1, P2 | **não** atribui ao Portal função que não existe (rede de contatos, vagas ou emprego garantidos, serviço, comunidade, mensagens, eventos próprios, programa de mentoria, resposta ou contato garantido a quem contribui). Anotar **qual** foi atribuída | nenhum participante |
| P-03: espera o que existe | P2 | descreve o que haverá depois de entrar de modo compatível com o que existe | maioria |
| P-04: interesse declarado | P2 | diz que entraria e dá um motivo ligado a um benefício real | registro, sem limiar |
| P-05: motivo para voltar | P2 | — (só registro, para o roadmap) | sem limiar |
| P-06: confiança e identidade | P2 | reconhece o site como do Ifes **e** diz que informaria os dados, ou explica o que faltou | maioria |
| P-07: comparação | P4 | escolhe a versão que explica melhor e justifica pelo conteúdo, não só pela aparência | registro por versão |

P-01 e P-02 são anotados **separadamente**: uma pessoa pode citar um benefício real e,
ao mesmo tempo, atribuir uma função inexistente.

## Leitura do resultado

| Resultado | Decisão |
|---|---|
| P-02 falha (alguém atribui função inexistente) | Corrigir o texto ou a demonstração que gerou a leitura, antes de implementar |
| P-01 atinge a referência na proposta e não na atual | A página implementada fica, com os ajustes observados |
| P-01 não atinge a referência na proposta | Revisar a primeira tela da página implementada |
| P-06 não atinge a referência | Rever identidade e explicação dos dados; registrar se a dúvida é sobre a identificação (018), que esta feature não muda |
| P-07 favorece a atual com justificativa de conteúdo | Rever a página implementada |

Qualquer decisão de implementar depende da aprovação do solicitante (spec da 029).

## Registro

Uma ficha por participante, a partir do [modelo do bloco P](checkpoint/ficha-bloco-p.md),
junto da ficha da 024, **sem nome, CPF ou contato**. A síntese vai para a `validacao.md`
da 029, numa seção "Checkpoint 1 — bloco P", com as contagens "x de N" e as frases
literais. Nenhuma contagem é apresentada como taxa de conversão.
