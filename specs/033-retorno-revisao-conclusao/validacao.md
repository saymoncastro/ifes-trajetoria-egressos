# Validação: Retorno à conclusão depois de revisar (033)

## Testes automatizados

- `tests/interface/test_interface_revisao.py`: 30 testes por requisição, um ou mais por
  cenário de aceitação (US1 a US4) e pelas bordas da spec. O teste
  `test_qualquer_parte_custa_um_envio` repete o SC-001 nas 9 partes do percurso de Ana.
- Requisitos revisados, com nota no próprio teste:
  - `test_interface_conclusao.py`: o `href` da revisão passa a ter `?revisao=1` (FR-001);
  - `test_interface_identidade.py`: a variante fixa de cada aviso ganha `caminho` e
    `revisada` (FR-006, FR-007).
- Nenhum outro teste da jornada mudou de expectativa (SC-004).

## Roteiro manual na demonstração (T008)

**Executado em 2026-10-12** sobre esta branch, no navegador do app (Chromium) a 375×812.
Servidor próprio em `127.0.0.1:8033` com banco recém-preparado (`preparar_demonstracao`).
Persona Ana Exemplo, percurso "trabalha e estuda" (9 partes). As partes foram preenchidas
por script no navegador; as ações abaixo foram feitas com cliques.

| # | Ação | Resultado |
|---|---|---|
| 1 | Na conclusão, tocar em "Informações Pessoais" | Abre `secoes/2/?revisao=1`. A linha diz "Parte 2 · revisando suas respostas"; respostas gravadas preenchidas; botões "Salvar e voltar à conclusão" e "Salvar e sair"; "Voltar à seção anterior" presente |
| 2 | Trocar o sexo/identidade de gênero e tocar em "Salvar e voltar à conclusão" | Volta à conclusão com "Parte salva." no topo. **1 envio** (US1.2) |
| 3 | Na conclusão, tocar em "Avaliação", trocar "Atualmente você trabalha?" para "Não" e salvar | Abre "Egresso que não trabalha" (`secoes/10/?revisao=1&aviso=caminho`) com o aviso "Sua resposta mudou o caminho da pesquisa. Confira esta parte para concluir." e "Parte 6 · revisando suas respostas" (US2.1) |
| 4 | Responder o motivo e salvar | Volta à conclusão com "Parte salva.". A lista tem "Egresso que não trabalha" no lugar de "Egresso que trabalha"; "Estudo", "Egresso que estuda" e "Parte 9" não foram reapresentadas. **2 envios** (US2.2, SC-002) |

Nenhum achado. Leitor de tela não executado (fora do escopo desta entrega; segue pendente
no roteiro da versão C).
