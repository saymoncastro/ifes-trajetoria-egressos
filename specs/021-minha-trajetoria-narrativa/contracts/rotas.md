# Contrato: rotas e telas

Todas as rotas existem só com o modo de demonstração ligado. Desligado, o
`ModoDemonstracaoMiddleware` devolve 404 em toda rota, o que cumpre o FR-069.

## Rotas novas (app `narrativa`, montado na raiz)

| Método | Rota | Resposta |
|---|---|---|
| GET | `/minha-trajetoria/?nome=1` | Página "Minha trajetória no Ifes" (FR-026). `nome=1` só muda a prévia e os links do card |
| GET | `/minha-trajetoria/card.png?nome=1` | **Artefato principal.** `image/png` 1080 × 1920, `inline; filename="minha-trajetoria-ifes.png"`. Abre como imagem salvável e alimenta a prévia `<img>`. Com a rasterização indisponível, devolve 404 (research R11) |
| GET | `/minha-trajetoria/card.svg?nome=1` | Representação-base. `image/svg+xml`, `attachment; filename="minha-trajetoria-ifes.svg"`. Só aparece na página quando o PNG está indisponível |

**Regras comuns:**

- `require_GET` e `never_cache` (`Cache-Control: no-store`).
- **Sem sessão de Pessoa:** redireciona para `/acesso/`, como em `/formacoes/`.
- **Sessão de Pessoa sem Participação concluída ancorada em Conclusão sua:** redireciona
  para `/formacoes/`, sem mensagem sobre narrativa (FR-002).
- **Sessão de declarante (019):** sem Pessoa, recebe o mesmo tratamento de "sem sessão".
- **Nome:** `nome=1` só tem efeito quando `Pessoa.nome` existe. Qualquer outro valor, ou
  a ausência do parâmetro, gera o card sem nome.
- **Sem efeito colateral:** nenhuma escrita em banco e nenhum log com dado pessoal
  (FR-008, FR-045).

## Página `/minha-trajetoria/` (estrutura revisada em 2026-10-05: capítulos; FR-026, FR-083)

```text
[faixa de demonstração existente]
ABERTURA     imagem do catálogo + legenda "Unidade X · ilustração"
             h1 Minha trajetória no Ifes · nome (se houver)
             O Ifes registra N formações concluídas por você.
CAPÍTULO     "Capítulo k de N" (só com 2 ou mais capítulos)
  Sua formação              [P2] frase de início; nó da 1ª formação (ano, curso, atributos, "Há N anos")
  Sua continuidade no Ifes  (só com 2 ou mais formações) linha do tempo + "Depois dessa formação…"
  Naquele ano no Ifes       (só com agregado) cartões: número grande + frase completa + apuração
  Seu card                  prévia PNG, nome, Baixar, Compartilhar (como abaixo)
a  Voltar às suas formações → /formacoes/
```

A estrutura anterior, abaixo, fica como registro da versão implementada em 2026-10-04.

### Versão de 2026-10-04 (superada na composição)

```text
[faixa de demonstração existente]
h1  Minha trajetória no Ifes
section  "O que o Ifes registra sobre você"        (sempre)
         Registros de {nome}                         (se houver nome)
         O Ifes registra N formações concluídas por você.
section  "Sua trajetória acadêmica"                 (sempre que houver formação)
         ol: uma formação por item: frase do catálogo + atributos presentes
             (nível · modalidade · forma de oferta) + tempo (FR-020)
             [P2] frase de início, se houver
section  "Outras formações no Ifes"                 (só com 2 ou mais formações e frase "depois")
section  "Naquele ano no Ifes"                      (P2, só com agregado selecionado)
section  "Seu card"  (id="card")
         <img> da PNG 9:16 (alt descritivo); tocar e segurar salva no celular
         form GET → /minha-trajetoria/?nome=1#card:
                   [ ] Incluir meu nome no card     (só se houver nome)
                   [Atualizar prévia]
         <a download> Baixar imagem                 (PNG; com o PNG indisponível, o SVG)
         <button hidden> Compartilhar               (revelado só com navigator.canShare({files});
                                                    abre o menu de compartilhamento do celular)
a  Voltar às suas formações → /formacoes/            (FR-030)
```

## Rotas existentes alteradas

| Rota / tela | Mudança | Origem |
|---|---|---|
| `/participacoes/<uuid>/concluida/` (âncora institucional) | A única ligação passa a ser "Ver minha trajetória no Ifes" → `/minha-trajetoria/`. Título, frase de registro, agradecimento ou encerramento e contexto ficam iguais | FR-003, revisa 014 FR-041 |
| `/participacoes/<uuid>/concluida/` (âncora declarada) | Sem mudança | FR-007 |
| `/formacoes/` | (a) Ligação "Ver minha trajetória no Ifes" quando o FR-001 for atendido. (b) Frase de antecipação quando houver pesquisa a iniciar ou retomar (research R15). (c) Título "Suas formações no Ifes" (research R16, ponto de revisão) | FR-005, FR-070, FR-006 |
| `aviso.html` | Ligação "Ver suas formações no Ifes" (research R16) | FR-006 |

**Não muda:** as telas de Seção, a tela de concluir, o fluxo da 019 e as rotas de
operador.
