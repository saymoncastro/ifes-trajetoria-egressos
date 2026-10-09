# Checkpoint 1 — bloco P: página pública (Feature 029)

Escrito em 2026-10-09, **antes** de qualquer sessão. Acrescenta um bloco ao
[protocolo do Checkpoint 1 da 024](../024-inicio-egresso-portal/evidencias/protocolo-checkpoint-1.md).
Os critérios SC-008 a SC-016 da 024, o limiar e a leitura do resultado **não mudam**.

> **Situação: NÃO APLICADO.** Os resultados entram em outro PR, depois da aplicação.

## O que o bloco quer saber

Se a página pública faz um egresso que nunca usou o Portal entender, em poucos segundos,
por que vale entrar, **sem** acreditar que o Portal oferece algo que não oferece.

São observações qualitativas, com 5 a 8 pessoas. A maioria é referência, não validação
estatística. **Não são** medidas de conversão nem de retenção:

- dizer que entraria não é entrar;
- dizer por que voltaria não é voltar;
- preferir uma versão por gosto ("gostei mais") não conta para nenhum critério.

## Material

- **Versão atual:** a página pública da 028, em `/` da demonstração, sem sessão.
- **Versão proposta:** o protótipo da 029 ([proposta](prototipo/proposta.html)), aberto no
  computador do moderador. A chamada principal leva à `/entrar/` da demonstração; se o
  servidor não estiver em `127.0.0.1:8000`, gerar de novo com
  `prototipo/gerar.py --base http://127.0.0.1:PORTA`.
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
| P-01: benefício real em 5 s | P1 | cita ao menos um destes: ver as formações reconhecidas pelo Ifes; o card para guardar ou compartilhar; oportunidades divulgadas para a formação | maioria, na primeira versão vista |
| P-02: nenhuma função inexistente | P1, P2 | **não** atribui ao Portal função que não existe (rede de contatos, vagas ou emprego garantidos, serviço, comunidade, mensagens, eventos próprios). Anotar **qual** foi atribuída | nenhum participante |
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
| P-01 atinge a referência na proposta e não na atual | A proposta segue para implementação, com os ajustes observados |
| P-01 não atinge a referência na proposta | Revisar a primeira tela da proposta antes de implementar |
| P-06 não atinge a referência | Rever identidade e explicação dos dados; registrar se a dúvida é sobre a identificação (018), que esta feature não muda |
| P-07 favorece a atual com justificativa de conteúdo | Rever a proposta antes de implementar |

Qualquer decisão de implementar depende da aprovação do solicitante (spec da 029).

## Registro

Uma ficha por participante, a partir do [modelo do bloco P](checkpoint/ficha-bloco-p.md),
junto da ficha da 024, **sem nome, CPF ou contato**. A síntese vai para a `validacao.md`
da 029, numa seção "Checkpoint 1 — bloco P", com as contagens "x de N" e as frases
literais. Nenhuma contagem é apresentada como taxa de conversão.
