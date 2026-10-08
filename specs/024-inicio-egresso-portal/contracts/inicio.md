# Contrato: Início do Portal (024)

`/inicio/` só aceita Pessoa na sessão, com o Portal ativo e no modo de demonstração. O
template é `portal/inicio.html`, que estende `interface/base.html` e usa o produto "Portal
do Egresso" e a navegação.

## Ordem no documento (FR-016)

| # | Bloco | Conteúdo | Fonte | Quando |
|---|---|---|---|---|
| 1 | Abertura | Ilustração vetorial do catálogo da 021 e legenda "· ilustração" | `narrativa.imagens` | Há Conclusão |
| 2 | Título (`h1`) | "Sua história com o Ifes" | Fixo | Sempre |
| 3 | Síntese | Frase da seção `o_que_o_ifes_registra`, por exemplo "O Ifes registra 2 formações concluídas por você." | Narrativa (021) | Há Conclusão |
| 4 | Formações | Uma linha por formação (curso, unidade, nível, ano), na ordem da 007, cada uma com "Registro do Ifes" em texto | Narrativa: `formacoes` | Há Conclusão |
| 5 | Derivados | Dentro de cada formação, as frases derivadas da 021 (por exemplo, "Há 1 ano desde essa conclusão."), com o selo "Calculado a partir dos registros". A linha de atributos herda a origem do fato e não repete o selo *(ajuste da implementação)* | Narrativa: frases da seção `trajetoria_academica` | Quando a 021 os produz |
| 6 | Proveniência | "Essas informações vêm dos registros acadêmicos do Ifes. Nada aqui foi respondido por você." | Fixo | Há Conclusão |
| 7 | O que você pode fazer | Lista de ações (abaixo) | — | Sempre |
| 8 | Convite | Bloco único, conforme a situação (abaixo) | `situacao_de_entrada` (007) | Conforme a situação |

Sem Conclusão Acadêmica:

- os blocos 1, 3, 4, 5 e 6 dão lugar à frase de `SEM_FORMACAO` da 007 ("Não encontramos
  formações concluídas no Ifes associadas a você.");
- a lista de ações tem só "Meu e-mail";
- não há convite.

Se a narrativa falhar, os blocos 1, 3, 4 e 5 são omitidos e o registro técnico segue o
padrão da 022, sem dado pessoal. O resto da página aparece.

## O que você pode fazer (bloco 7)

| Ação | Destino | Condição |
|---|---|---|
| "Ver minha trajetória no Ifes" | `/minha-trajetoria/` | `elegivel(pessoa)` |
| "Baixar o card da sua trajetória" | `/minha-trajetoria/#card` | `elegivel(pessoa)` |
| "Gerar o vídeo da sua trajetória" | `/minha-trajetoria/#video` | `elegivel(pessoa)` e `renderizador.disponivel()` |
| "Manter seu e-mail com o Ifes" | `/meu-email/` | Sempre. O contato não é lido |

As âncoras `#card` (`narrativa/minha_trajetoria.html`) e `#video` (`video/bloco.html`) já
existem.

## Convite à pesquisa (bloco 8, FR-020)

Uma única vez, com título de nível 2 "Pesquisa de acompanhamento".

| Resolução / situação (007) | Texto (provisório) | Ação |
|---|---|---|
| `ENTRADA_RESOLVIDA`, a formação está disponível para iniciar | "Há uma pesquisa aberta sobre {curso}. Respondê-la é como você atualiza sua trajetória com o Ifes." | "Responder" → `/formacoes/` |
| `ENTRADA_RESOLVIDA`, a formação está disponível para retomar | O mesmo texto. O "onde parou" da 023 aparece em `/formacoes/`, a um toque, sem segunda leitura da jornada no Início *(ajuste da implementação)* | "Continuar" → `/formacoes/` |
| `SELECAO_NECESSARIA` | "Há pesquisas abertas sobre {n} das suas formações. Respondê-las é como você atualiza sua trajetória com o Ifes." | "Escolher a formação" → `/formacoes/` |
| `SEM_ENTRADA_PENDENTE` | A frase da escolha de formações (014 FR-036): "Não há pesquisa pendente para você neste momento." | Nenhuma |
| `SEM_PESQUISA` | A frase da escolha de formações: "No momento, não há pesquisa disponível para as suas formações." | Nenhuma |
| `SEM_FORMACAO` | Bloco ausente | — |

## Vedações verificadas em teste (FR-019, FR-021; research R11)

- O `h1` não contém o nome da pessoa. O nome não aparece no Início: na 021 ele é discreto e
  sob escolha, e o Início não precisa dele.
- Texto visível sem: "minuto", "%", "turma", "geração", "conectad", "Olá", "Oportunidade",
  "Volte ao Ifes", "comunidade".
- "pesquisa" aparece só no bloco 8, nos rótulos da navegação e no cabeçalho do produto
  "Trajetória Ifes", se houver.
- Nenhuma ligação para endereço inexistente. Todo `href` do Início responde 200 ou 302 para
  a Pessoa de teste.
- Nenhuma Resposta é lida (verificação por consultas, como na 021).

## Medidas (FR-031, FR-032; SC-004)

- A 375×812, o `h1` e o bloco 3 ficam acima da dobra, com a faixa de demonstração incluída.
  Se a abertura ilustrada empurrar o bloco 3 para baixo da dobra, a ilustração é reduzida ou
  vai para depois do bloco 4. A decisão é tomada na captura.
- Um único `h1`. Os títulos dos blocos são `h2`. Nenhuma informação só por cor.
