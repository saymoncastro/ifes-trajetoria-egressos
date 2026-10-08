# Checkpoint 1 — preparação de cada sessão

Complementa o [protocolo](../protocolo-checkpoint-1.md), que define critérios, roteiro e
leitura do resultado. Este arquivo é a lista prática do moderador.

## Antes de começar o ciclo de sessões (uma vez)

- [ ] Ambiente local pronto, conforme [docs/desenvolvimento/ambiente-local.md](../../../../docs/desenvolvimento/ambiente-local.md), com a `main` atualizada (024 integrada).
- [ ] Portal ligado: `TRAJETORIA_PORTAL` ausente ou diferente de `0`.
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

- [ ] Navegador numa aba anônima, sem sessão anterior. No computador, viewport de 375×812; no celular, o navegador do aparelho na mesma rede.
- [ ] Abrir só o endereço raiz (`http://127.0.0.1:8000/`). Não abrir `/acesso/`: esse é o caminho do convite, fora deste teste.
- [ ] Escolher a persona mais parecida com a história do participante:

  | Persona (painel "Usar estes dados") | Quando usar |
  |---|---|
  | **Ana** | Uma formação |
  | **Maria** | Duas formações, graduação e especialização |
  | **Diego** | Três formações (técnico, licenciatura, mestrado) |

- [ ] Gravação de tela só com o consentimento registrado (ver pendência P3).

## Durante a sessão

- Seguir o roteiro do protocolo **na ordem**.
- Não usar "portal", "pesquisa", "trajetória" nem "início" antes de o participante usá-las.
- Não ajudar nas tarefas 5 e 6. Se a pessoa travar por mais de 2 minutos, anotar "não" e seguir.
- Cronometrar as tarefas 5 (achar a trajetória) e 6 (achar retrato e e-mail).
- Anotar frases literais curtas, sem identificar a pessoa.
- Só depois do roteiro: mostrar o mockup, dizer que é um protótipo e anotar as reações à parte.

## Depois da sessão

- [ ] Preencher a ficha em até 1 hora, enquanto a memória está fresca.
- [ ] Salvar como `participante-N.md` nesta pasta, sem nome, CPF, e-mail nem telefone.
- [ ] Apagar gravações locais conforme a regra de retenção combinada (P3).

## Pendências antes da primeira sessão

| # | Pendência | Quem decide |
|---|---|---|
| P1 | Confirmar o tamanho da amostra e o limiar propostos no protocolo: **5 participantes** e "maioria" = **4 de 5** | Solicitante |
| P2 | Recrutamento: quem convida, por qual canal e com qual perfil. O protocolo pede ao menos 1 pessoa com mais de uma formação, ao menos 1 formada há mais de 5 anos e ninguém da equipe | Solicitante, com CSAEG/CPAEG se usar contatos institucionais |
| P3 | Termo de participação e de gravação: texto, guarda e prazo de retenção. O protocolo diz "segue o procedimento do NIAE", mas o repositório não registra esse procedimento | Encarregado de dados, com CPAEG (`DECISÃO PENDENTE`) |
| P4 | Teste com leitor de tela (VoiceOver ou NVDA) antes ou durante as sessões. A passada de teclado e da árvore de acessibilidade já foi feita (ver validação) | Solicitante (quem executa) |
