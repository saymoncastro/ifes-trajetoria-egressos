# Contrato: experiência do egresso (025)

## Página `/oportunidades/` (FR-017 a FR-020, FR-023, FR-024)

**Acesso.**

| Sessão | Resposta |
|---|---|
| Pessoa com ao menos uma Conclusão | 200 |
| Pessoa sem Conclusão | 303 → `/inicio/` |
| Declarante (019) | 303 → `/declaracao/` |
| Sem sessão | 303 → `/entrar/`, ou `/entrar/?aviso=sessao` se a sessão acabou de expirar (024 FR-007) |
| Portal desligado | 404 |

- `GET` só. `never_cache`. Parâmetros ignorados.
- Shell do Portal: navegação, "Portal do Egresso", "Sair" para `/sair/` e o provedor de
  contexto da 024. `/oportunidades/` entra na lista fechada de telas com navegação.

**Estrutura, na ordem do documento:**

1. `h1` "Oportunidades".
2. Introdução: "Oportunidades divulgadas pelo Ifes, com links para as páginas oficiais.
   Aparecem pelas formações que o Ifes registra ou porque estão abertas a todos os egressos."
3. `section` com `h2` "Pela sua formação", omitida quando vazia.
4. `section` com `h2` "Para todos os egressos", omitida quando vazia.
5. Sem nenhum item: só o estado vazio (FR-018): "No momento, não há oportunidades divulgadas
   para as suas formações. Novas oportunidades aparecem aqui quando o Ifes as divulga." e um
   link "Voltar ao Início".

**Item** (`li` de uma `ul.lista-simples`), sem grade e sem imagem:

```html
<li class="oportunidade">
  <p class="oportunidade-categoria">{categoria}</p>
  <h3><a href="{endereco}" rel="noreferrer">{titulo}<span class="visualmente-oculto"> — {site do Ifes|site externo}: {domínio}</span></a></h3>
  <p>{resumo}</p>
  <p class="oportunidade-por-que">{explicação}</p>
  <p class="oportunidade-origem">Oferecida pela unidade {u} · {site do Ifes|site externo}: {domínio}</p>
</li>
```

- **Não exibe:** datas de divulgação, contagem, "recomendado" nem urgência (FR-017, FR-022).
- **Link:** na mesma aba, sem parâmetro acrescentado (R12).

## Bloco no Início (FR-021; R9)

Posição: depois de "O que você pode fazer" e antes do convite. Não existe quando a lista do
oráculo é vazia.

```html
<section class="inicio-oportunidades" aria-labelledby="titulo-oportunidades">
  <h2 id="titulo-oportunidades">Oportunidades</h2>
  <p class="oportunidade-titulo"><a href="{endereco}" rel="noreferrer">{titulo}<span class="visualmente-oculto"> — {origem do site}: {domínio}</span></a></p>
  <p class="oportunidade-por-que">{explicação}</p>
  <p class="oportunidade-origem">Oferecida … · {origem do site}: {domínio}</p>
  <p><a href="/oportunidades/">{Ver as N oportunidades | Ver a página de Oportunidades}</a></p>
</section>
```

- **Medida (SC-008):** a 375×812 com fonte a 100%, o convite desce no máximo 270 px em relação
  à mesma persona sem o bloco.
- **Se passar:** compactação do R9, em três etapas (margens, tipo de 15 px, um parágrafo só).
  Ela **nunca** remove título, explicação, unidade responsável, classificação do site nem
  domínio (FR-004, FR-013). Se ainda passar, o caso volta ao solicitante.
- **Convite:** inalterado (024 FR-020, com a revisão de 2026-10-08).
- **Vocabulário:** a palavra "Oportunidade" só aparece neste bloco. A "pesquisa" de
  acompanhamento só é chamada no convite (R11).

## Navegação (FR-020; R10)

| # | Rótulo | Endereço | Condição |
|---|---|---|---|
| 1 | Início | `/inicio/` | Sempre |
| 2 | Minha trajetória | `/minha-trajetoria/` | `elegivel` |
| 3 | **Oportunidades** | `/oportunidades/` | `elegivel` (mesmo valor, calculado uma vez) |
| 4 | Pesquisa | `/formacoes/` | Sempre |
| 5 | Meu e-mail | `/meu-email/` | Sempre |

- **Largura estável:** `data-rotulo` em cada link e reserva do negrito por `::after` (R10).
- **Medidas, na validação:**
  - mesma altura de navegação em todas as telas com navegação, a 375 px e 100%;
  - nenhuma rolagem horizontal de 320 a 1280 px, com fonte de 100% a 200%;
  - alvos de 44×44 px;
  - `h1` e síntese do Início acima da dobra a 375×812.
