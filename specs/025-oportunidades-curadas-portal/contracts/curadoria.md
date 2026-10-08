# Contrato: curadoria (025 FR-025 a FR-035)

Todas as rotas existem só no modo de demonstração **e** com o Portal ligado. Com o Portal
desligado, respondem 404.

## Acesso (decorador `curadoria`, no padrão de `acompanhamento.acesso.gestao`)

1. Sem operador: 303 → `/demonstracao/operador/?destino=curadoria`. O destino é registrado
   pelo Portal no mapa fechado (R3).
2. `pode_curar_oportunidades(vinculos)` falso: 403, com a página de recusa do
   acompanhamento: "A curadoria de oportunidades não está disponível para esta atuação."
3. Escopo: a CPAEG é institucional; a CSAEG, as unidades dos seus vínculos (R2).
4. A view recebe `request.escopo` e `request.atuacao`. O identificador do operador nunca vai
   para o template.

Layout: `acompanhamento/base.html`, com a faixa, a atuação e a trilha. Não usa o Django
admin.

## Rotas

| Rota | Método | Descrição | Respostas |
|---|---|---|---|
| `/curadoria/oportunidades/` | GET | Lista do escopo (FR-027) | 200 |
| `/curadoria/oportunidades/nova/` | GET, POST | Cadastro (FR-028) | 200; 422 com erros; 303 → lista `?aviso=cadastrada` |
| `/curadoria/oportunidades/<uuid>/editar/` | GET, POST | Edição (FR-029) | 200; 422; 409 conflito; 404 fora do escopo; 303 `?aviso=editada` |
| `/curadoria/oportunidades/<uuid>/publicar/` | GET, POST | Confirmação com prévia e publicação (FR-030) | 200; 409; 404; 303 `?aviso=publicada` |
| `/curadoria/oportunidades/<uuid>/retirar/` | GET, POST | Confirmação e retirada (FR-031) | 200; 409; 404; 303 `?aviso=retirada` |

- **Fora do escopo:** 404, como no 011, para não revelar que a oportunidade existe.
- **Formulários:** CSRF; `never_cache`; destinos fixos.

## Lista

Uma tabela com `caption`, cabeçalhos com `scope` e a rolagem da 011. Colunas:
- título;
- unidade responsável ("Ifes (institucional)" quando `""`);
- categoria;
- período (dd/mm/aaaa a dd/mm/aaaa);
- estado (R5);
- ações disponíveis no estado ("Editar", "Publicar", "Retirar").

O link "Nova oportunidade" fica acima. Sem itens, o texto é "Nenhuma oportunidade no escopo
da sua atuação."

## Formulário (cadastro e edição)

| Campo | Controle | Regra | Mensagem de erro (provisória) |
|---|---|---|---|
| Título | texto, `maxlength=120` | FR-002 | "Informe um título de até 120 caracteres." |
| Resumo | área de texto, `maxlength=300` | FR-002 | "Informe um resumo de até 300 caracteres." |
| Categoria | rádio, 6 opções | FR-003 | "Escolha uma categoria." |
| Unidade responsável | seleção: as do escopo; "Ifes (institucional)" só para a CPAEG | FR-005, FR-026 | "Escolha uma unidade da sua atuação." |
| Endereço oficial | `type="url"`, `inputmode="url"` | R6 | "Informe um endereço completo que comece com https://, sem usuário, senha nem número IP." |
| Início e fim da divulgação | datas | FR-006; publicada: fim ≥ hoje | "O fim da divulgação não pode ser anterior ao início." / "Para encerrar antes do prazo, retire a oportunidade." |
| Público: unidades, níveis e cursos | três grupos de caixas de seleção (`fieldset` + `legend`) com os valores registrados, como estão escritos (R8) | FR-007 | — |
| Ajuda do público | texto fixo | — | "Sem nenhuma marcação, a oportunidade aparece para todos os egressos do Ifes. Com marcações, aparece para quem tem uma formação que atende a todas elas." |

- **Erros:** junto do campo, com `aria-describedby` e `aria-invalid`, e resumo no topo, como
  no 017 (`editor/_erros.html`, `editor/_campo.html`).
- **Foco:** vai ao primeiro campo com erro.

## Confirmações

- **Publicar.** A prévia é o item exatamente como no contrato do egresso (`_oportunidade.html`
  compartilhado). Abaixo dela:
  - "Público: todos os egressos do Ifes" ou "Público: quem concluiu {critérios}";
  - o período;
  - "Endereço: {domínio completo}", em destaque. Para site externo: "Este endereço não é de
    um site do Ifes. Confira se é a página oficial da oportunidade."

  Botões: "Publicar" e "Cancelar".
- **Retirar.** "A oportunidade sai da vista dos egressos imediatamente. A retirada não pode
  ser desfeita." Botões: "Retirar" e "Cancelar".

## Conflito (FR-034)

409, com a página de conflito no padrão da 017: "Esta oportunidade mudou desde que você abriu
a página." Link de volta à lista. Nada é gravado.

## Avisos (vocabulário fechado, `?aviso=`)

| Aviso | Texto |
|---|---|
| `cadastrada` | "Oportunidade salva como rascunho." |
| `editada` | "Alterações salvas." |
| `publicada` | "Oportunidade publicada." |
| `retirada` | "Oportunidade retirada da divulgação." |

## Fora

- Exclusão; duplicação; histórico.
- Contagem de egressos alcançados (FR-026).
- Busca e filtros.
- Upload; editor rico.
