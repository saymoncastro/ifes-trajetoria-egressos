# Contrato HTTP e interface

Rotas incluídas em `trajetoria/acompanhamento/urls.py`; views em `trajetoria/acompanhamento/gestao/`; barreira `@gestao` em
`trajetoria/acompanhamento/acesso.py`.
Todas só existem no modo de demonstração (middleware da 008 responde 404 antes).

| Método e rota | Barreira | Entrada | Saída |
| --- | --- | --- | --- |
| GET, POST `/acompanhamento/campanhas/nova/` | `@gestao` | CSRF; `nome`, `versao`, `inicio`, `fim` | GET: formulário (ou explicação sem Versão publicada). POST ok: 302 ao detalhe `?aviso=campanha-criada`. POST com erro: 422 com erros por campo |
| GET, POST `/acompanhamento/campanhas/<uuid>/editar/` | `@gestao` | idem | GET: formulário preenchido. POST ok: 302 `?aviso=configuracao-salva`. Erro de campo: 422. Campanha já aberta: 409 |
| GET, POST `/acompanhamento/campanhas/<uuid>/abrir/` | `@gestao` | CSRF | GET: confirmação ou impedimentos. POST ok: 302 `?aviso=coleta-aberta`; já aberta: 302 `?aviso=ja-em-coleta` ou `ja-encerrada`; rejeitada: 409 com impedimentos atuais |
| GET, POST `/acompanhamento/campanhas/<uuid>/encerrar/` | `@gestao` | CSRF | GET: confirmação (só EM COLETA; caso contrário 409 explicativo). POST ok: 302 `?aviso=coleta-encerrada`; já encerrada: 302 `?aviso=ja-encerrada`; nunca aberta: 409 |

Rotas existentes alteradas apenas na apresentação:

| Rota (011) | Mudança |
| --- | --- |
| GET `/acompanhamento/` | Link "Nova Campanha" se `atuacao.gerir_campanha`; rótulo de FR-023a para todos |
| GET `/acompanhamento/campanhas/<uuid>/` | Painel de gestão (situação, impedimentos, abrangência restrita, encerramento previsto, ações) se `atuacao.gerir_campanha`; aviso pós-ação por `?aviso=` de lista fechada; rótulo de FR-023a para todos |

Lista e detalhe continuam somente GET (405 em POST). Nenhuma outra rota muda.

## Autorização e erros

- Modo desligado: 404 pelo middleware e, de novo, pela própria barreira `@gestao`.
- Sem operador: 302 para `/demonstracao/operador/?destino=acompanhamento`.
- Operador sem `pode_gerir_campanha` (CSAEG, sem vínculo, vínculo revogado): 403 pela
  `recusa()` da 011, texto "A gestão de Campanhas não está disponível para esta atuação.",
  sem dado de Campanha. Vale para GET e POST, antes de qualquer consulta ou operação.
- UUID inexistente: 404.
- CSRF ausente ou inválido: 403 do framework, antes da operação.
- Métodos diferentes de GET/POST: 405.
- Vínculos relidos a cada requisição, inclusive no POST de confirmação.
- `never_cache` em todas as rotas de gestão.

## Telas

- `acompanhamento/base.html`, trilha "Acompanhamento da coleta → Campanha → ação",
  campos com `editor/_campo.html` (rótulo, ajuda, erro com `aria-describedby`/`aria-invalid`)
  e resumo de erros com foco, como no editor.
- **Formulário (nova/editar)**: título "Nova Campanha" ou "Editar configuração"; campos Nome,
  Versão, Início (opcional), Fim (opcional); ajuda "O período pode ser definido depois; ele é
  necessário para abrir a coleta."; aviso de abrangência restrita quando houver; botões
  Salvar e Cancelar. Nenhum campo de critério, público, lote ou divulgação.
- **Confirmar abertura**: Campanha, instrumento e período que ficam fixados; "A Campanha
  passa a aceitar respostas imediatamente. Depois de aberta, a configuração não pode ser
  alterada, e não há reabertura nem prorrogação."; se hoje for o último dia do período,
  "A coleta se encerra ao fim de hoje (dd/mm/aaaa)."; se houver outras Campanhas em coleta,
  "Já existem outras Campanhas em coleta. Isso pode fazer com que alguns egressos tenham
  mais de uma pesquisa disponível." e a lista de nomes; botões "Abrir coleta" e Cancelar.
- **Confirmar encerramento**: "Novas respostas deixarão de ser aceitas. As Participações
  existentes são preservadas. Não há reabertura."; botões "Encerrar coleta" e Cancelar.
- **Painel no detalhe** (só operador gestor), depois dos dados da Campanha: situação de
  gestão, impedimentos (causa e correção), encerramento previsto quando em coleta, aviso de
  abrangência restrita quando houver, ações da matriz de FR-017. A entrada "Comunicação
  simulada" (016) permanece onde está.
- Sem JavaScript obrigatório; teclado, foco visível, 320 px e ampliação de 200%.
