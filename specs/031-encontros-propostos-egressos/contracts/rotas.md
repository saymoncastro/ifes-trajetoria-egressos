# Contrato — rotas e autorização

Todas as rotas existem só com `TRAJETORIA_PORTAL` ligado e no modo de demonstração. Sem o
Portal, respondem "não encontrado" (FR-035). Todas funcionam sem JavaScript. As telas
correspondentes estão no [protótipo](../prototipo/index.html).

## Egresso

| Rota | Método | Quem | Resposta | Tela |
|---|---|---|---|---|
| `/encontros/` | GET | Pessoa com Conclusão | Página Encontros: "Propostos por egressos" (pertinentes, por data) e "Eventos do Ifes" (itens A da 025) | p2, p11 |
| `/encontros/propor/` | GET, POST | Pessoa com Conclusão | Formulário; POST válido mostra "Confira e envie"; acima do limite, erro de formulário (R9) | o1, o2 |
| `/encontros/propor/confirmar/` | POST | idem | Revalida tudo, grava com a versão do termo e redireciona à página do encontro | o3 → o4 |
| `/encontros/seus/` | GET | idem | "Seus encontros" do organizador | o5, o10 |
| `/encontros/<id>/` | GET | qualquer | Conforme a situação e quem vê ([FR-024a](../spec.md); research R10). Sem sessão: página neutra | p3–p10, p15, o4, o6, o9 |
| `/encontros/<id>/participar/` | POST | Pessoa com Conclusão, não organizadora | Grava a Confirmação; redireciona à página | p3 → p4 |
| `/encontros/<id>/cancelar-participacao/` | GET, POST | dona da confirmação ativa, antes do início | Confirmação e cancelamento | p5 |
| `/encontros/<id>/calendario.ics` | GET | organizador; dona de confirmação ativa | `text/calendar`, anexo ([calendário](calendario.md)) | — |
| `/encontros/<id>/editar/` | GET, POST | organizador, Em análise | Formulário preenchido | o1 |
| `/encontros/<id>/alterar-data/` | GET, POST | organizador, Publicado, antes do início | Correção operacional | o7 |
| `/encontros/<id>/corrigir-link/` | GET, POST | idem | Mesmo domínio: grava; outro domínio: vira mudança substancial, com a tela de efeito | o11 |
| `/encontros/<id>/alterar/` | GET, POST | idem | Mudança substancial; tela de efeito antes de enviar | o12 |
| `/encontros/<id>/cancelar/` | GET, POST | organizador, antes do início | Confirmação e cancelamento | o8 |
| `/encontros/<id>/denunciar/` | GET, POST | Pessoa com Conclusão, não organizadora, que vê o conteúdo (FR-024a): Publicado, ou Encerrado com confirmação ativa no término; sem denúncia anterior | Formulário; grava; volta à página com aviso | p12 → p13 |

## Moderação

| Rota | Método | Quem | Resposta | Tela |
|---|---|---|---|---|
| `/curadoria/encontros/` | GET | `pode_moderar_encontros` | Listas do escopo: para análise, nova análise e publicados com denúncias | m1, m5 |
| `/curadoria/encontros/<id>/` | GET, POST | idem, no escopo | Análise; POST publica. Em revisão, mostra os campos alterados | m2, m6 |
| `/curadoria/encontros/<id>/recusar/` | GET, POST | idem | Em análise: recusa. Em revisão: recusa a alteração (o encontro é retirado) | m3 |
| `/curadoria/encontros/<id>/retirar/` | GET, POST | idem | Publicado ou Em revisão: retirada com motivo; mostra as denúncias | m4 |

## Entrada (revisão da 024)

| Rota | Mudança |
|---|---|
| `/entrar/?encontro=<id>` | Só um UUID de Encontro existente é aceito. O destino depois da identificação passa a ser `/encontros/<id>/`; qualquer outro valor é ignorado, e o destino continua `/inicio/` (research R12) |
| `destinos.sem_pessoa` | Para `/encontros/<id>/`, leva a `/entrar/?encontro=<id>` |

## Matriz de autorização (resumo)

| Ação | Organizador | Outra Pessoa com Conclusão | Sem Conclusão / sem sessão | CSAEG da unidade responsável | CSAEG de outra unidade | CPAEG |
|---|---|---|---|---|---|---|
| Ver conteúdo publicado | sim | sim | não (neutra) | sim | não | sim |
| Ver conteúdo fora de publicado | sim | conforme FR-024a | não | sim | não | sim |
| Ver o link | sim | só com confirmação ativa e encontro Publicado | não | sim | não | sim |
| Ver a contagem | sim | não | não | sim | não | sim |
| Ver quem confirmou ou quem denunciou | não | não | não | não | não | não |
| Confirmar e cancelar a própria confirmação | não | sim | não | — | — | — |
| Denunciar | não | sim, se vê o conteúdo (FR-029) | não | — | — | — |
| Publicar, recusar, retirar | não | não | não | sim (unidade única) | não | sim (todos) |

**Respostas fora da regra:**
- encontro de outra pessoa nas rotas do organizador, ou fora do escopo na moderação:
  "não encontrado", como na 025 e na 026;
- operador sem competência: a recusa do padrão de governança;
- situação mudou entre a exibição e a ação: página de conflito, sem gravar nada.
