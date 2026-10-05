# Contrato — Transporte, renderer e envio

## Modos (`comunicacao/transporte.py`)

```text
transporte_de_envio() -> Transporte(modo: "teste" | "demonstracao" | "real", conexao())
RecusaDeTransporte(categoria)   # nunca carrega texto de exceção externa
```

A decisão é tomada antes de qualquer mensagem ou conexão. Os modos são exclusivos, e
qualquer outra combinação recusa com `transporte_inseguro`.

| Modo | Exige |
| --- | --- |
| teste | `TRAJETORIA_COMUNICACAO_TESTE is True` e `EMAIL_BACKEND` locmem |
| demonstracao | `TRAJETORIA_DEMONSTRACAO`; `TRAJETORIA_ENVIO_REAL != "1"`; backend SMTP; host em loopback; porta 1025; sem usuário e senha; sem TLS e SSL; timeout 5; remetente `trajetoria@example.invalid`; URL `TRAJETORIA_URL_ENTRADA_DEMONSTRACAO` validada pela 016 |
| real | `TRAJETORIA_ENVIO_REAL == "1"`; demonstração desligada; backend SMTP; porta inteira de 1 a 65535; TLS ou SSL; usuário e senha não vazios; `TRAJETORIA_REMETENTE_INSTITUCIONAL` válido; `TRAJETORIA_URL_ENTRADA` em `https`, sem credenciais, query ou fragmento; base **sem** dados simulados |

- Com a demonstração desligada, o middleware torna toda rota 404. O modo real **só existe
  como validação** desta fronteira, testada com `override_settings`. A ativação depende do
  Gate B, inclusive da DP-2010.
- O fornecedor nunca é nomeado no código. A troca para API de provedor fica restrita a
  este módulo.

## Destinatário por modo

- Todos os modos: `normalizar_email`, exatamente um destinatário, sem CC/BCC nem anexos e
  sem cabeçalhos extras.
- Teste e demonstração: domínio exatamente `example.invalid`.
- Real: qualquer domínio válido.

## Renderer (`comunicacao/convite.py`)

```text
renderizar_convite(nome_pessoa, nome_campanha, url, *, modo) -> Convite
Convite.mensagem(destinatario, connection) -> EmailMultiAlternatives
```

- **Templates**:
  - demonstração e teste: `convite.txt` e `convite.html` (016, inalterados);
  - real: `convite_real.txt` e `convite_real.html`, provisórios e marcados como pendentes
    de aprovação (DP-2003, 008/DP-801).
- **Conteúdo**:
  - personalização: só saudação com o nome e nome da Campanha;
  - link neutro igual para todos;
  - nenhum identificador de Pessoa, Conclusão, Lote, membro ou token;
  - nenhum recurso externo, pixel ou rastreador (`validar_conteudo`, com a URL permitida
    do modo).

## Envio (`mobilizacao/operacoes.py`)

```text
enviar_lote(lote_id, operador, *, agora=None) -> ResultadoDoEnvio
ResultadoDoEnvio(processados, submetidos, falhas, restantes_nao_tentados,
                 interrompido: bool, nao_enviaveis: int, saiu_da_coleta: bool)
```

Algoritmo (research R7):

1. Revalidar: capacidade, Lote visível, `estado(campanha) == EM_COLETA`,
   `transporte_de_envio()`, origem da base compatível com o modo.
2. Escolher até `TRAJETORIA_LOTE_ENVIO_POR_ACAO` membros `NAO_TENTADO`, por `pk`.
3. Para cada membro (*code review de 2026-10-05*):
   - **(0)** reconferir que a Campanha continua `EM_COLETA`. Se não estiver, encerrar a
     ação com `saiu_da_coleta`; os restantes continuam `NAO_TENTADO`;
   - **(0')** renderizar e validar a mensagem no modo, **antes** de reservar. Recusa
     determinística (contato fora do domínio do modo, conteúdo ou cabeçalho inválidos)
     conta como `nao_enviavel`: nada é transmitido e o membro continua `NAO_TENTADO`,
     nunca "resultado incerto";
   - **(a)** transação curta: `select_for_update(skip_locked=True)`; ainda `NAO_TENTADO`;
     gravar `EM_TENTATIVA` e `tentativa_iniciada_em`; commit. A unicidade por Pessoa e
     Campanha é garantida pela restrição `membro_uma_abordagem_por_campanha` (FR-025);
   - **(b)** enviar a mensagem já validada, com o contato congelado, por
     `send(fail_silently=False)`;
   - **(c)** retorno 1 grava `SUBMETIDO_AO_TRANSPORTE`. `SMTPException` ou `OSError`
     gravam `FALHA_DE_TRANSPORTE`. Os dois gravam `resultado_em`;
   - **(d)** outra exceção: interrompe a ação; o membro fica em `EM_TENTATIVA`
     (incerto); nenhum outro é tentado nesta ação.
4. Uma conexão por mensagem, fechada em `finally`, como na 016.

**Nunca**: retry automático, reabrir `EM_TENTATIVA`, "entregue", "aberto" ou "clicado".

## Confirmação (`mobilizacao/operacoes.py`)

```text
previa(campanha, escopo, filtros) -> Previa(conclusoes, pessoas, com_contato, sem_contato,
                                           excluidas)
confirmar_lote(campanha_id, operador, nome, filtros, confirmo_abrangencia, *, agora=None)
    -> LoteDeMobilizacao
```

- A seleção é compartilhada entre `previa` e `confirmar_lote`, na ordem de FR-017.
- `confirmar_lote` trava a Campanha (`select_for_update`), recalcula, recusa Lote vazio e
  grava o Lote e os membros numa transação.
- A Campanha deve estar `EM_PREPARACAO` ou `EM_COLETA`.
