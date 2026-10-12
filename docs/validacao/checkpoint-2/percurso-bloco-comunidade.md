# Checkpoint 2 — percurso curto do bloco Comunidade

Complementa o [protocolo](protocolo.md) (parte 2) e a [preparação](preparacao-sessao.md).
Escrito em 2026-10-11, **antes** de qualquer sessão.

> **Situação: NÃO APLICADO.** Este percurso é uma proposta. Ele só vale depois que o
> solicitante aprovar o material (Q7) e de resolvidas as pendências listadas no fim.

## Para que serve

- **As 33 telas da 031 cobrem a spec, não a sessão.** A sessão precisa de um caminho curto, na
  ordem do protocolo (Histórias → Encontros → Encontre colegas). Ele deve produzir evidência
  para a escolha entre 031 e 030 e para as condições do E1.
- **Duração-alvo:** cerca de 15 minutos.
- **Telas:** 12, mais 3 opcionais.

## Material

| Parte | Onde | O que é |
|---|---|---|
| Comunidade, Histórias e Encontre colegas | [`docs/prototipos/2026-10-11-comunidade/`](../../prototipos/2026-10-11-comunidade/index.html) | Sete telas conceituais. Não abrem a 030 nem especificam o diretório |
| Encontros | [protótipo da 031](../../../specs/031-encontros-propostos-egressos/prototipo/index.html) | Seleção de telas abaixo |

**Abrir as telas.** As fontes do Portal não carregam a partir de `file://`. Por isso, as telas
são abertas por um servidor estático local, na raiz do repositório:

```bash
python3 -m http.server 8031 --bind 127.0.0.1
```

Depois, abrir `http://127.0.0.1:8031/docs/prototipos/2026-10-11-comunidade/c0-comunidade.html`
no mesmo navegador da parte 1, a 375×812.

## Percurso

O moderador lê a abertura literal do protocolo ("ideias que **ainda não existem**"). Ele não
explica as telas e não usa "comunidade" nem "encontro" antes de a pessoa ver as telas que as
usam.

| # | Tela | Tarefa do protocolo | O que se anota | Minutos |
|---|---|---|---|---|
| 1 | [c1 · Histórias](../../prototipos/2026-10-11-comunidade/c1-historias.html) | H1: "O que é esta página?" | CM-C4 (leitura) | 1 |
| 2 | [c2 · Uma história](../../prototipos/2026-10-11-comunidade/c2-historia.html) | H1: "Quem escreveu este texto e quem decidiu publicá-lo?"; H2 | CM-C4; **CM-U4** | 2 |
| 3 | [p2 · Encontros](../../../specs/031-encontros-propostos-egressos/prototipo/p2-encontros.html) | F1: "Qual a diferença entre estes dois? Quem organiza cada um?"; "Por que este aparece para você?" | **CM-C1**; CM-F1 | 2 |
| 4 | [p3 · Página do encontro](../../../specs/031-encontros-propostos-egressos/prototipo/p3-encontro.html) | F2: "Se você marcar 'Vou participar', quem fica sabendo? Quem recebe o link?"; F3 | **CM-C2**; **CM-U2** | 2 |
| 5 | [p4 · Confirmado](../../../specs/031-encontros-propostos-egressos/prototipo/p4-confirmado.html) | "Se a data mudar depois que você baixou o calendário?"; "Se você não puder ir?" | CM-C2 (o link apareceu); CM-F3; CM-F4 | 1,5 |
| 6 | [p7 · Fora do público](../../../specs/031-encontros-propostos-egressos/prototipo/p7-fora-do-publico.html) | "Você poderia participar deste? Por quê?" | CM-F5 | 1 |
| 7 | [o1 · Propor um encontro](../../../specs/031-encontros-propostos-egressos/prototipo/o1-propor.html) | F4: "Você proporia um encontro? Sobre o quê, e para quem?" A pessoa só olha, sem preencher | **CM-U1** | 1,5 |
| 8 | [o4 · Em análise](../../../specs/031-encontros-propostos-egressos/prototipo/o4-em-analise.html) | "Depois de enviar, quem vê? E se o Ifes não aceitar?" | CM-F2 | 1 |
| 9 | [c3 · Aparecer em Encontre colegas](../../prototipos/2026-10-11-comunidade/c3-colegas-aderir.html) | D1: "Como alguém passa a aparecer nesta lista? O que os outros veem?"; D2 | **CM-C3**; **CM-U3** | 1,5 |
| 10 | [c4 · Lista](../../prototipos/2026-10-11-comunidade/c4-colegas-lista.html) | D1, continuação: "O que você sabe destas pessoas?" | CM-C3 | 0,5 |
| 11 | [c5 · Pedir contato](../../prototipos/2026-10-11-comunidade/c5-colegas-pedido.html) | D1: "Como alguém falaria com você?" | CM-C3 (aceite, nenhum contato antes) | 1 |
| 12 | [c0 · Comunidade](../../prototipos/2026-10-11-comunidade/c0-comunidade.html) | Fechamento: "Pelo que você viu, o que mais este lugar faria?" | **CM-C4** | 1 |

Em negrito, os critérios e registros já escritos no protocolo. CM-F1 a CM-F5 são observações
exploratórias, sem limiar (Q8).

**Opcionais, só se sobrar tempo ou se a pessoa perguntar:**
- [p9 · Cancelado](../../../specs/031-encontros-propostos-egressos/prototipo/p9-cancelado.html): segunda metade de CM-F4;
- [c6 · Pedidos de contato](../../prototipos/2026-10-11-comunidade/c6-colegas-pedidos.html): recusa, bloqueio e saída da lista;
- [p6 · Endereço sem sessão](../../../specs/031-encontros-propostos-egressos/prototipo/p6-sem-sessao.html).

**Fora da sessão:** as telas da moderação (m1 a m6), os erros de formulário e as demais
situações da organizadora. Elas servem à revisão da spec, não a esta tarefa.

## Cuidados

- **Navegação.** As telas da 031 têm o item "Encontros" (H-3105); as de Histórias e Encontre
  colegas, o item "Comunidade". O moderador não comenta a diferença. Regra de linguagem do material (hipótese, não decisão pendente): cada tela usa o rótulo da capacidade que mostra ("Encontros", "Histórias", "Encontre colegas"); "Comunidade" fica só na entrada comum e no item de navegação das telas que não são de encontros. A navegação definitiva sai da spec que implementar a segunda capacidade.
- **Intenção não é adesão.** CM-U1 a CM-U4 são interesse declarado. Nenhuma contagem vira taxa.
- **Pergunta se algo existe.** Se a pessoa perguntar, o moderador responde que nada destas
  telas existe hoje e anota a pergunta na ficha ("Observações").

## Decisões de preparação ainda pendentes

**Antes do Checkpoint 1**, que vem primeiro (roadmap, §13.3), conforme a
[preparação do Checkpoint 1](../../../specs/024-inicio-egresso-portal/evidencias/checkpoint-1/preparacao-sessao.md):

| # | Pendência | Quem |
|---|---|---|
| P1 | Amostra e limiar (proposta: 5 participantes, 4 de 5) e como se aplicam ao bloco P | Solicitante |
| P2 | Moderador, recrutamento e perfil | Solicitante |
| P3 | Procedimento de participação e, se houver, de gravação. Sem ele, não há sessão | Encarregado de dados, com CPAEG |
| P4 | Teste com leitor de tela. O roteiro está pronto, mas **não foi executado** | Quem executa, a definir pelo solicitante |
| P5 | Vídeo nas sessões ou sem vídeo | Solicitante |
| P6 | Comparação histórica no bloco P | Solicitante |

**Antes do Checkpoint 2**, conforme a [preparação](preparacao-sessao.md):

| # | Pendência | Quem |
|---|---|---|
| Q1 | Número de participantes e limiar | Solicitante |
| Q2 | Moderador, recrutamento, perfil; se os participantes do Checkpoint 1 podem voltar | Solicitante |
| Q3 | Procedimento de participação e gravação (pode ser o mesmo do P3) | Encarregado de dados, com CPAEG |
| Q4 | O que é "poucos toques" no CP2-B2 | Solicitante |
| Q5 | Manter ou não a tarefa V1 (estado vazio) | Solicitante |
| Q6 | Leitura do resultado e critério proposto CP2-E1 | Solicitante |
| Q7 | Aprovação do material do bloco Comunidade, **incluindo este percurso e as telas de Histórias e Encontre colegas**; partes 1 e 2 na mesma sessão ou separadas | Solicitante |

A Q8 está decidida: CM-F1 a CM-F5 são observações exploratórias, sem limiar.

**Antes de cada sessão (execução, não decisão):**
- banco recém-preparado;
- servidor estático do material aberto;
- commit do produto e do protótipo anotado na ficha.
