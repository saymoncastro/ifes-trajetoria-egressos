# Checkpoint 1 — preparação de cada sessão

Complementa o [protocolo](../protocolo-checkpoint-1.md), que define critérios, roteiro e
leitura do resultado. Este arquivo é a lista prática do moderador.

> **Situação (2026-10-08): NÃO APLICADO.**
> - Nenhuma sessão com egressos foi feita.
> - O teste com leitor de tela também não foi feito.
> - A passada de teclado e da árvore de acessibilidade ([validação](../../validacao.md)) é
>   evidência técnica, não resultado com egressos.
> - Os resultados entram em outro PR, depois da aplicação.
> - A S2 e a S3 não começam antes da leitura dos resultados conforme este protocolo.

## Sequência até os resultados

1. Revisar e integrar este kit (PR só da preparação).
2. Confirmar amostra e limiar (P1).
3. Definir moderador e recrutamento (P2).
4. Resolver participação e eventual gravação com os responsáveis (P3).
5. Verificar com leitor de tela antes das sessões (P4).
6. Decidir se as sessões terão vídeo (P5).
7. Aplicar, registrar e consolidar em outro PR. Se a compreensão passar, seguir para a S2 e
   a S3. Se falhar, ajustar a S1. Falhas só de navegação são ajustadas dentro da 024.

## Antes de começar o ciclo de sessões (uma vez)

- [ ] Ambiente local pronto, conforme [docs/desenvolvimento/ambiente-local.md](../../../../docs/desenvolvimento/ambiente-local.md), com a `main` atualizada (024 integrada).
- [ ] Portal ligado: `TRAJETORIA_PORTAL` ausente ou diferente de `0`.
- [ ] Vídeo conforme P5: com o renderizador instalado (§2.14 do ambiente local), o bloco de vídeo aparece em Minha trajetória; sem ele, o bloco some e isso fica anotado em cada ficha.
- [ ] Decisões do solicitante confirmadas (ver "Pendências antes da primeira sessão").
- [ ] Mockup conceitual (`portal_egresso.html`) à mão, **fora** do produto, para o fim da sessão.
- [ ] Uma cópia em branco da [ficha](ficha-participante.md) por participante.

## Antes de **cada** sessão

O participante pode iniciar ou concluir uma pesquisa, o que muda o que o Início mostra.
Por isso, cada sessão começa de um banco recém-preparado. Pare o servidor antes:

```bash
source .env && dropdb --force "$PGDATABASE" && createdb "$PGDATABASE" && uv run python manage.py migrate && uv run python manage.py preparar_demonstracao
```

```bash
source .env && uv run python manage.py runserver 127.0.0.1:8000
```

- [ ] Navegador do **computador do moderador**, numa aba anônima sem sessão anterior, com viewport de 375×812 (modo de dispositivo do navegador). O celular do participante não acessa `127.0.0.1` do computador; usar o celular fica fora do primeiro ciclo.
- [ ] Abrir só o endereço raiz (`http://127.0.0.1:8000/`). Não abrir `/acesso/`: esse é o caminho do convite, fora deste teste.
- [ ] Escolher a persona mais parecida com a história do participante:

  | Persona (painel "Usar estes dados") | Quando usar |
  |---|---|
  | **Ana** | Uma formação |
  | **Maria** | Duas formações, graduação e especialização |
  | **Diego** | Três formações (técnico, licenciatura, mestrado) |

- [ ] Participação e eventual gravação de tela só conforme o procedimento definido em P3. Sem P3 resolvida, não há sessão.

## Durante a sessão

- Seguir o roteiro do protocolo **na ordem**.
- Não usar "portal", "pesquisa", "trajetória" nem "início" antes de o participante usá-las.
- Se a pessoa clicar em "Sair", ela cai em `/acesso/`, fora deste teste. Anotar o momento e o que ela disse ao ver a tela, abrir de novo a raiz (`http://127.0.0.1:8000/`), escolher a mesma persona e retomar da tarefa em curso, sem comentar a mudança de tela.
- Não ajudar nas tarefas 5 e 6. Se a pessoa travar por mais de 2 minutos, anotar "não" e seguir.
- Cronometrar as tarefas 5 (achar a trajetória) e 6 (achar retrato e e-mail).
- Anotar frases literais curtas, sem identificar a pessoa.
- Só depois do roteiro: mostrar o mockup, dizer que é um protótipo e anotar as reações à parte.

## Depois da sessão

- [ ] Preencher a ficha em até 1 hora, enquanto a memória está fresca.
- [ ] Salvar como `participante-N.md` nesta pasta, sem nome, CPF, e-mail nem telefone.
- [ ] Se houve gravação, apagá-la conforme a regra de retenção definida em P3.

## Pendências antes da primeira sessão

| # | Pendência | Quem decide |
|---|---|---|
| P1 | Confirmar o tamanho da amostra e o limiar propostos no protocolo: **5 participantes** e "maioria" = **4 de 5 em cada critério**. A compreensão passa só se **cada um** de SC-008 a SC-012 atingir o limiar; "parcial" não conta | Solicitante |
| P2 | Moderador e recrutamento: quem modera, quem convida, por qual canal e com qual perfil. O protocolo pede ao menos 1 pessoa com mais de uma formação, ao menos 1 formada há mais de 5 anos e ninguém da equipe | Solicitante, com CSAEG/CPAEG se usar contatos institucionais |
| P3 | Procedimento de **participação** (termo, informação ao participante) e, se houver, de **gravação** (guarda, prazo de retenção). O repositório não registra esse procedimento. Dispensar a gravação não resolve sozinho o procedimento de participação | Encarregado de dados, com CPAEG (`DECISÃO PENDENTE`) |
| P4 | Teste com leitor de tela (VoiceOver ou NVDA) **antes** das sessões, para achar obstáculos que impeçam as tarefas. **Ainda não realizado.** A passada de teclado e da árvore de acessibilidade já foi feita e é só evidência técnica (ver validação) | Solicitante (quem executa) |
| P5 | Vídeo nas sessões. SC-011 e SC-015 mencionam o vídeo; o protocolo aceita "card (ou vídeo)". Decidir entre instalar o renderizador no computador do moderador ou aplicar sem vídeo, registrando a escolha nas fichas. Origem: [avaliação técnica de 2026-10-08](../../../../docs/auditorias/2026-10-08-portal-avaliacao-tecnica.md) | Solicitante |
