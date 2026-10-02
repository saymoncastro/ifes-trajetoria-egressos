# Contrato: operador fictício no modo de demonstração (`trajetoria/demonstracao`)

Atende spec FR-053 a FR-061. Extensão do adaptador temporário de identidade da 008
(`demonstracao/entrada.py`), sem mudar a escolha de Pessoa fictícia.

## `trajetoria/demonstracao/operador.py`

**Adaptador temporário.** Faz as vezes da futura identificação de operadores (DP-1001).
Não autentica, não comprova identidade e não é mecanismo de produção.

```text
OPERADORES_FICTICIOS = (
    OperadorFicticio("demonstracao:operador-a", "Operador fictício A"),
    OperadorFicticio("demonstracao:operador-b", "Operador fictício B"),
    OperadorFicticio("demonstracao:operador-c", "Operador fictício C"),
)
COOKIE = "trajetoria_demonstracao_operador"
SALT   = "operador-de-demonstracao"
```

| Função | Comportamento |
|--------|---------------|
| `operador_em_uso(request) -> str \| None` | Modo desligado → `None`, sem ler cookie. Senão lê o cookie assinado; devolve o identificador **somente** se estiver em `OPERADORES_FICTICIOS`; qualquer outro caso → `None`. Memoriza na requisição. Nunca grava, nunca levanta exceção por cookie ausente, inválido ou adulterado |
| `operador_ficticio(identificador) -> OperadorFicticio \| None` | Busca na tupla |
| `usar_operador(response, operador)` | Grava o cookie assinado (`httponly`, `samesite="Lax"`, sem `max_age`). Recusa (`ValueError`) operador fora da tupla |
| `esquecer_operador(response)` | Apaga o cookie |

Cookie independente do cookie da Pessoa fictícia.

## Rotas (em `demonstracao/urls.py`)

Todas sob o `ModoDemonstracaoMiddleware`: com o modo desligado, 404.

| Método | Rota | View | Comportamento |
|--------|------|------|---------------|
| GET | `/demonstracao/operador/` | `operadores` | Lista os três operadores fictícios. Para cada um, as atuações **lidas dos vínculos ativos** (`vinculos_ativos` + `rotulo_de_atuacao`) ou "Sem atuação institucional ativa". Indica o operador em uso. Um `<form method="post">` por operador, com botão "Atuar como Operador fictício X". Ligação "Ir para o editor" |
| POST | `/demonstracao/operador/escolher/` | `escolher_operador` | `operador` do formulário fora da tupla → 404 (padrão de `escolher` da Pessoa). Senão grava o cookie e redireciona (302) para `/editor/`, sempre o início do editor (sem parâmetro de retorno) |
| POST | `/demonstracao/operador/encerrar/` | `encerrar_operador` | Apaga o cookie e redireciona para `/demonstracao/operador/` |

A página explica: "A escolha identifica o operador apenas para demonstração. O que ele
pode fazer no editor decorre dos vínculos de governança registrados, e não desta
escolha." Sem identificador técnico visível (o valor do formulário é o identificador;
fica só em `value`).

Template: `demonstracao/templates/demonstracao/operador.html`, mesma base, estilo e
requisitos de acessibilidade da entrada de demonstração da 008.

O editor, sem operador escolhido, encaminha (302) para `/demonstracao/operador/`
([acesso-editor.md](acesso-editor.md)). É o único caminho de entrada; não há `next`.

## Preparo da demonstração (`cenario.preparar`)

Acréscimos, na mesma transação, depois das Campanhas:

1. **Recusa** se existir `VinculoDeGovernanca` cujo `identificador_operador` não esteja em
   `OPERADORES_FICTICIOS`: "O banco contém vínculos de governança que não são fictícios. O
   cenário de demonstração só é preparado num banco local com dados fictícios." (mesma
   forma da recusa existente para dados que não são da fonte simulada).
2. Garante, registrando só o que não estiver ativo:
   - `demonstracao:operador-a` → `CPAEG`;
   - `demonstracao:operador-b` → `CSAEG`, unidade `"Vitória"` (designação dos dados
     simulados).
   - `demonstracao:operador-c` → nada.
3. `VinculoRejeitado` é tratado como as demais recusas de operação do preparo.

O `Resumo` devolvido não muda. Nenhuma migração de dados.

## O que não existe

Conta, senha, sessão, login, operador padrão com acesso garantido, operador real,
identificador informado livremente, escolha de operador fora do modo de demonstração.
