# Contrato: rotas e tela do vídeo

As rotas existem só com o modo de demonstração ligado (`ModoDemonstracaoMiddleware`, FR-003).

**Regras comuns, as mesmas da 021:**

- **Sem sessão de Pessoa:** redireciona para `/acesso/`.
- **Inelegível:** redireciona para `/formacoes/`.
- **Nome:** `nome=1` só tem efeito com `Pessoa.nome`.
- **Composição recalculada pela sessão a cada requisição.** A chave nunca vem do cliente
  (FR-025).
- `never_cache` em todas as rotas.

## Rotas novas (app `video`, montado sob `/minha-trajetoria/`)

| Método | Rota | Resposta |
|---|---|---|
| POST | `/minha-trajetoria/video/` | CSRF. Campo `nome` (`1` ou ausente). Chama `solicitar` (data-model §3.1) e responde `303` para `/minha-trajetoria/?nome=1#video` (ou sem `nome`). Sem renderizador disponível → `303` sem efeito |
| GET | `/minha-trajetoria/video.mp4?nome=1` | `PRONTO` não vencido: `200` ou `206` (`Range` de um intervalo), `video/mp4`, `Content-Disposition: inline; filename="minha-trajetoria-ifes.mp4"`, `Accept-Ranges: bytes`, `Cache-Control: no-store`. `Range` inválido → `416`. Qualquer outra situação → `404` |
| GET | `/minha-trajetoria/video/estado?nome=1` | `application/json` `{"estado": "nenhum" \| "preparando" \| "pronto" \| "falhou"}`. Só para a melhoria progressiva |

**Sem efeito colateral em dados de domínio:** a única escrita é a da tabela técnica
(FR-033). Nenhum log com dado pessoal (FR-027).

## Tela: bloco `#video` no capítulo "Seu card" (`/minha-trajetoria/`)

Aparece só com `renderizador.disponivel()` (FR-037). A região de estado tem
`aria-live="polite"`.

```text
Seu card
  [prévia PNG, incluir meu nome, Baixar imagem, Compartilhar imagem]   ← 021, inalterado
  h3 Vídeo da sua trajetória
  estado = nenhum:
      p   Um vídeo curto, sem som, com o seu card em movimento.
      form POST /minha-trajetoria/video/ (nome conforme a prévia)  [Gerar vídeo]
  estado = preparando:
      p   Estamos preparando seu vídeo…  Você pode continuar usando esta página.
      a   Atualizar → /minha-trajetoria/?nome=1#video
  estado = pronto:
      video controls playsinline preload="metadata" poster="card.png?nome=1"
            aria-describedby=<descrição do card>          (sem autoplay)
      a   Baixar vídeo (MP4)    href=video.mp4?nome=1  download="minha-trajetoria-ifes.mp4"
      button Compartilhar vídeo  (só com navigator.canShare({files}); melhoria progressiva)
  estado = falhou:
      p   Não foi possível preparar o vídeo agora. Seu card continua disponível.
      form POST /minha-trajetoria/video/  [Tentar novamente]
```

- **Escolha do nome:** é a mesma da prévia do card. Mudar a escolha muda a composição, e o
  bloco reflete o estado do vídeo da nova escolha.
- **Script inline opcional** (sem recurso externo):
  - em `preparando`, consulta `/estado` a cada 3 s e recarrega a página no `#video` quando
    o estado muda;
  - liga o botão de compartilhar.
  - Sem JavaScript, tudo funciona por recarga (FR-035).
- **Textos novos:** em `trajetoria/video/mensagens.py`, revisáveis sem mudar comportamento.
  Não fazem parte do catálogo de formulações da narrativa, porque não são fatos.
