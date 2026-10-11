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
>
> **Revisão de 2026-10-11 (versão C; roadmap, revisão 13).** A sessão avalia a versão C
> (032), com a navegação Início, Minha trajetória, Oportunidades e Participação. A 025 e a
> 026 já estão implementadas na demonstração, por isso a última linha acima é histórico.
> Continua **NÃO APLICADO**: nenhuma sessão, nenhum teste com leitor de tela e nenhum
> roteiro de teclado sobre a versão C.

## Sequência até os resultados

*(Revista em 2026-10-11. A lista de 2026-10-08 fica abaixo, como histórico.)*

1. Integrar a consolidação documental da revisão 13 (kit na versão C).
2. **Acessibilidade:** roteiro manual com teclado sobre a versão C, num navegador real, nas
   telas que o roteiro percorre (roadmap, §13.3, passo 2). **Executado em 2026-10-11**, sem
   impedimento às tarefas ([validação da 032](../../../032-convergencia-visual-c/validacao.md#roteiro-manual-com-teclado-e-árvore-de-acessibilidade-2026-10-11)).
3. Teste com leitor de tela antes das sessões (P4). Hoje **não executado**; o
   [roteiro](../../../032-convergencia-visual-c/evidencias/roteiro-leitor-de-tela.md) está pronto.
4. Resolver P1, P2, P3, P5 e P6 (abaixo).
5. Aplicar, registrar e consolidar em outro PR. A leitura segue o protocolo. Se a
   compreensão falhar, o Início e a navegação são corrigidos antes do protótipo da
   Comunidade e do Checkpoint 2; falhas só de navegação são ajustadas dentro da 024.

**Lista de 2026-10-08 (histórico):**

1. Revisar e integrar este kit (PR só da preparação).
2. Confirmar amostra e limiar (P1).
3. Definir moderador e recrutamento (P2).
4. Resolver participação e eventual gravação com os responsáveis (P3).
5. Verificar com leitor de tela antes das sessões (P4).
6. Decidir se as sessões terão vídeo (P5).
7. *(Feito em 2026-10-08.)* Aplicar os ajustes A1–A4, A6 e A7 da
   [avaliação por IA](../../../../docs/auditorias/2026-10-08-portal-checkpoints-avaliacao-ia.md)
   (ver [validação](../../validacao.md), "Revisão pós-avaliação por IA"). Não é resultado
   do Checkpoint 1.
8. Aplicar, registrar e consolidar em outro PR. Se a compreensão passar, seguir para a S2 e
   a S3. Se falhar, ajustar a S1. Falhas só de navegação são ajustadas dentro da 024.

O passo 1 foi feito pelo PR #42. A S2 e a S3 foram implementadas antes do checkpoint, por
decisão do solicitante (roadmap, revisões 5 e 10).

## Antes de começar o ciclo de sessões (uma vez)

- [ ] Ambiente local pronto, conforme [docs/desenvolvimento/ambiente-local.md](../../../../docs/desenvolvimento/ambiente-local.md), com a `main` atualizada (032 integrada: `63b9447` ou posterior). Anotar o commit em cada ficha.
- [ ] Portal ligado: `TRAJETORIA_PORTAL` ausente ou diferente de `0`.
- [ ] Vídeo conforme P5: com o renderizador instalado (§2.14 do ambiente local), o bloco de vídeo aparece em Minha trajetória; sem ele, o bloco some e isso fica anotado em cada ficha.
- [ ] Decisões do solicitante confirmadas (ver "Pendências antes da primeira sessão").
- [ ] ~~Mockup conceitual (`portal_egresso.html`) à mão, **fora** do produto, para o fim da sessão.~~ *Retirado em 2026-10-11: Oportunidades e contribuição existem no produto, e o arquivo não está no repositório (protocolo, revisão de 2026-10-11).*
- [ ] Material do bloco P conforme P6: a página C, servida em `/`, e, se houver comparação, a cópia estática da versão escolhida aberta no computador do moderador (por exemplo, [`prototipo/proposta.html`](../../../029-pagina-publica-portal/prototipo/proposta.html), da 029).
- [ ] Uma cópia em branco da [ficha](ficha-participante.md) e da [ficha do bloco P](../../../029-pagina-publica-portal/checkpoint/ficha-bloco-p.md) por participante.

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
  | **Bruno** *(acrescentado em 2026-10-11)* | Duas formações na mesma unidade (técnico e bacharelado) |

  Na demonstração, Diego e Bruno já têm uma contribuição fictícia enviada (026), e o
  Início deles mostra "1 contribuição enviada". Bruno é o único dos quatro que vê a seção de
  encontros ("Ninguém se forma sozinho"). O moderador não comenta nada disso; anota na
  ficha a persona usada.

- [ ] Participação e eventual gravação de tela só conforme o procedimento definido em P3. Sem P3 resolvida, não há sessão.

## Durante a sessão

- Seguir o roteiro do protocolo **na ordem**.
- Não usar "portal", "pesquisa", "trajetória" nem "início" antes de o participante usá-las.
- Se a pessoa clicar em "Sair" numa tela do Portal, ela volta à entrada do Portal (`/entrar/`; 024 FR-034, revisão de 2026-10-08). Anotar o momento e o que ela disse, escolher a mesma persona e retomar da tarefa em curso, sem comentar. Se ela sair de dentro de uma Seção da pesquisa, cai em `/acesso/`, fora deste teste: abrir de novo a raiz (`http://127.0.0.1:8000/`) e seguir do mesmo modo.
- A pessoa não digita dados reais: nem CPF, nem data, nem e-mail, nem mensagem. Se começar a fazer isso, o moderador interrompe com gentileza e explica que o ambiente só usa dados fictícios.
- Na versão C, o e-mail não é item da navegação: fica em Participação e no bloco "Seu canal com o Ifes" do Início. Anotar o caminho seguido na tarefa 6.
- Não ajudar nas tarefas 5 e 6. Se a pessoa travar por mais de 2 minutos, anotar "não" e seguir.
- Cronometrar as tarefas 5 (achar a trajetória) e 6 (achar retrato e e-mail).
- Anotar frases literais curtas, sem identificar a pessoa.
- ~~Só depois do roteiro: mostrar o mockup, dizer que é um protótipo e anotar as reações à parte.~~ *Retirado em 2026-10-11 (ver acima).*

## Depois da sessão

- [ ] Preencher a ficha em até 1 hora, enquanto a memória está fresca.
- [ ] Salvar como `participante-N.md` nesta pasta, sem nome, CPF, e-mail nem telefone.
- [ ] Se houve gravação, apagá-la conforme a regra de retenção definida em P3.

## Pendências antes da primeira sessão

| # | Pendência | Quem decide |
|---|---|---|
| P1 | Confirmar o tamanho da amostra e o limiar propostos no protocolo: **5 participantes** e "maioria" = **4 de 5 em cada critério**. A compreensão passa só se **cada um** de SC-008 a SC-012 atingir o limiar; "parcial" não conta. O bloco P admite 5 a 8 pessoas: com mais de 5, dizer como o limiar se aplica | Solicitante |
| P2 | Moderador e recrutamento: quem modera, quem convida, por qual canal e com qual perfil. O protocolo pede ao menos 1 pessoa com mais de uma formação, ao menos 1 formada há mais de 5 anos e ninguém da equipe | Solicitante, com CSAEG/CPAEG se usar contatos institucionais |
| P3 | Procedimento de **participação** (termo, informação ao participante) e, se houver, de **gravação** (guarda, prazo de retenção). O repositório não registra esse procedimento. Dispensar a gravação não resolve sozinho o procedimento de participação | Encarregado de dados, com CPAEG (`DECISÃO PENDENTE`) |
| P4 | Teste com leitor de tela (VoiceOver ou NVDA) **antes** das sessões, para achar obstáculos que impeçam as tarefas. **Ainda não realizado.** A passada de teclado e da árvore de acessibilidade já foi feita e é só evidência técnica (ver validação). *(2026-10-11: aquela passada é da versão de 2026-10-08. O roteiro de teclado da versão C foi executado em 2026-10-11, e o [roteiro com leitor de tela](../../../032-convergencia-visual-c/evidencias/roteiro-leitor-de-tela.md) está pronto para quem executar.)* | Solicitante (quem executa) |
| P5 | Vídeo nas sessões. SC-011 e SC-015 mencionam o vídeo; o protocolo aceita "card (ou vídeo)". Decidir entre instalar o renderizador no computador do moderador ou aplicar sem vídeo, registrando a escolha nas fichas. Origem: [avaliação técnica de 2026-10-08](../../../../docs/auditorias/2026-10-08-portal-avaliacao-tecnica.md) | Solicitante |
| P6 | *(Nova, 2026-10-11.)* Comparação histórica no bloco P. A página avaliada é a C. Decidir: (a) manter as etapas P3 e P4 do roteiro do bloco P (que não são as pendências P3 e P4 desta tabela), comparando a C com a página da 029 ([`proposta.html`](../../../029-pagina-publica-portal/prototipo/proposta.html), que a implementação da 029 reproduz); (b) comparar com a da 028 ([`atual.html`](../../../029-pagina-publica-portal/prototipo/atual.html)); ou (c) não comparar, e o P-07 não é anotado. Em (a) e (b), decidir também a ordem: alternar a primeira versão vista, como no bloco P original, ou mostrar sempre a C primeiro, para que P-01 e P-02 da C tenham todos os participantes. Ver o [bloco P](../../../029-pagina-publica-portal/checkpoint-pagina-publica.md), "Revisão de 2026-10-11" | Solicitante |
