# Checkpoint 2 — preparação de cada sessão

Complementa o [protocolo](protocolo.md), que define critérios, roteiro e leitura do
resultado. Este arquivo é a lista prática do moderador.

> **Situação: NÃO APLICADO.** Nenhuma sessão foi feita. Do protótipo do bloco Comunidade,
> só a parte de Encontros existe (031, revisão 14 do roadmap); Histórias e Encontre colegas
> ainda não. As pendências Q1 a Q7 estão abertas; Q8 foi decidida.

## Sequência até os resultados

1. Checkpoint 1 aplicado, lido e com os ajustes integrados (roadmap, §13.3, passos 3 e 4).
2. Protótipo estático da Comunidade produzido e revisado pelo solicitante (passo 5; Q7).
3. Roteiro com teclado e leitor de tela cobrindo a contribuição, do início à retirada (passo
   2 do roadmap). O roteiro com teclado foi **executado** na versão C em 2026-10-11, com a
   contribuição incluída e os achados A-01 a A-04 não corrigidos
   ([validação da 032](../../../specs/032-convergencia-visual-c/validacao.md)). O teste com
   leitor de tela continua **não executado**.
4. Resolver Q1 a Q7.
5. Aplicar, registrar e consolidar em outro PR, com a leitura do protocolo.

## Antes de começar o ciclo de sessões (uma vez)

- [ ] Ambiente local pronto, conforme [docs/desenvolvimento/ambiente-local.md](../../desenvolvimento/ambiente-local.md), na `main` com a 032 e os ajustes do Checkpoint 1. Anotar o commit em cada ficha.
- [ ] Portal ligado: `TRAJETORIA_PORTAL` ausente ou diferente de `0`.
- [ ] Num banco recém-preparado, conferir que cada persona mostra o esperado no [oráculo da 025](../../../specs/025-oportunidades-curadas-portal/contracts/pertinencia.md) (com a seção de encontros da 032 para Bruno) e as contribuições fictícias de Diego e Bruno. Anotar qualquer divergência antes da primeira sessão.
- [ ] Protótipo da Comunidade aberto no computador do moderador, **fora** da aplicação.
- [ ] Um e-mail fictício por participante para a contribuição, no domínio reservado `example.invalid` (por exemplo, `participante-1@example.invalid`). Nunca o e-mail real da pessoa.
- [ ] Se Q5 mantiver a tarefa V1: um segundo navegador, ou outro perfil, para o operador fictício. Janelas anônimas do mesmo navegador compartilham a sessão.
- [ ] Cópias em branco da [ficha do produto](ficha-participante.md) e da [ficha do bloco Comunidade](ficha-bloco-comunidade.md).

## Antes de **cada** sessão

O participante envia e retira uma contribuição, o que muda o que o Início mostra. Cada
sessão começa de um banco recém-preparado. Pare o servidor antes:

```bash
source .env && dropdb --force "$PGDATABASE" && createdb "$PGDATABASE" && uv run python manage.py migrate && uv run python manage.py preparar_demonstracao
```

```bash
source .env && uv run python manage.py runserver 127.0.0.1:8000
```

- [ ] Navegador do computador do moderador, numa aba anônima sem sessão anterior, a 375×812.
- [ ] Abrir `http://127.0.0.1:8000/entrar/` e usar "Usar estes dados" da persona principal.
- [ ] Participação e eventual gravação só conforme Q3. Sem Q3 resolvida, não há sessão.

## Personas

| Persona | Formações | Para que serve na sessão |
|---|---|---|
| **Ana** | Uma (Serra) | Persona principal: oportunidade pela formação e geral; sem contribuição prévia |
| **Maria** | Duas (Serra e Cefor) | Persona principal: oportunidades por curso e por nível; sem contribuição prévia |
| **Diego** | Três (Vila Velha) | Persona principal, se for a mais parecida. Já tem uma contribuição fictícia: o Início mostra "1 contribuição enviada" |
| **Bruno** | Duas (Vitória) | Tarefa A1: único com a seção de encontros. Também tem uma contribuição fictícia |
| **Fernanda** | Uma concluída e uma matrícula ativa (Cariacica) | Tarefa V1: só a oportunidade geral O1. Depois que o moderador retira O1, a área fica vazia |

A persona principal é a mais parecida com a história do participante, de preferência sem
contribuição prévia (Ana ou Maria), para que a tarefa R2 comece do zero. Para trocar de
persona: "Sair", depois "Usar estes dados" da outra.

## Durante a sessão

- Seguir o roteiro do protocolo **na ordem**: parte 1 (O, R, M, V, A, fechamento) e só
  depois a parte 2.
- Não usar "portal", "pesquisa", "oportunidade", "contribuir", "comunidade" nem
  "encontro" antes de o participante usar. Na parte 2, a regra é a do protocolo.
- **O4:** a pergunta é feita sem tocar no link. Os links da demonstração usam o domínio
  reservado `oportunidades.example` e não abrem página nenhuma. Se a pessoa tocar, anotar,
  voltar e dizer que, na demonstração, os links não levam a sites reais.
- **R2 e R4:** entregar o e-mail fictício quando o campo aparecer. Se a pessoa começar a
  escrever dado pessoal na mensagem, interromper com gentileza.
- **R2:** contar as telas e os toques do Início até "Confira e envie".
- **V1** (se Q5 mantiver): no outro navegador, escolher o operador A em
  `/demonstracao/operador/`, abrir `/curadoria/oportunidades/` e retirar O1. No navegador
  do participante: "Sair", Fernanda, Oportunidades.
- Anotar frases literais curtas, sem identificar a pessoa. Se a pessoa travar por mais de 2
  minutos, anotar "não" e seguir.
- **Parte 2:** ler a abertura literal do protocolo antes de mostrar o protótipo. Se a pessoa
  perguntar se algo já existe, responder que não.

## Depois da sessão

- [ ] Preencher as fichas em até 1 hora.
- [ ] Salvar como `participante-N.md` e `participante-N-comunidade.md` nesta pasta, sem
  nome, CPF, e-mail ou telefone.
- [ ] Se houve gravação, apagá-la conforme Q3.

## Pendências antes da primeira sessão

| # | Pendência | Quem decide |
|---|---|---|
| Q1 | Número de participantes e limiar. Proposta: os mesmos do Checkpoint 1, conforme P1 (5 participantes; 4 de 5 em cada critério; "parcial" não conta). Sem decisão registrada | Solicitante |
| Q2 | Moderador, recrutamento e perfil; se os participantes do Checkpoint 1 podem voltar. Nenhum da equipe | Solicitante, com CSAEG/CPAEG se usar contatos institucionais |
| Q3 | Procedimento de participação e, se houver, de gravação. Pode ser o mesmo de P3 do Checkpoint 1, se ele cobrir esta sessão. `DECISÃO PENDENTE` | Encarregado de dados, com CPAEG |
| Q4 | O que é "poucos toques" no CP2-B2. A 026 mede "do Início à confirmação em no máximo três telas" (SC-001), que é critério técnico. Falta dizer se o checkpoint usa um número ou só "sem ajuda e sem dúvida" | Solicitante |
| Q5 | Manter ou não a tarefa V1 (estado vazio), que exige o moderador retirar O1 durante a sessão | Solicitante |
| Q6 | Aprovar a leitura do resultado e o critério proposto CP2-E1 (finalidade dos dois e-mails) | Solicitante |
| Q7 | Protótipo da Comunidade: aprovação do material antes das sessões; partes 1 e 2 na mesma sessão (cerca de 40 minutos) ou em sessões separadas | Solicitante |
| Q8 | **Decidida (solicitante, 2026-10-11):** CM-F1 a CM-F5, da [spec da 031](../../../specs/031-encontros-propostos-egressos/spec.md#critérios-que-o-checkpoint-2-deve-avaliar), entram como observações exploratórias, sem limiar de aprovação nesta rodada | Solicitante |
