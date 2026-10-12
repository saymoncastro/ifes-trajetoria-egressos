# Contrato — arquivo de calendário (`.ics`)

FR-027 e FR-028; research R11. Exemplo de referência: [`prototipo/exemplo.ics`](../prototipo/exemplo.ics).

- **Formato:** iCalendar (RFC 5545), UTF-8, linhas terminadas em CRLF e dobradas em 75 octetos.
- **Resposta:**
  - `Content-Type: text/calendar; charset=utf-8`;
  - `Content-Disposition: attachment; filename="encontro.ics"`;
  - `Cache-Control: no-store`.

| Propriedade | Valor |
|---|---|
| `PRODID` | `-//Ifes//Portal do Egresso (demonstracao)//PT-BR` |
| `METHOD` | `PUBLISH` |
| `UID` | `<id do Encontro>@portal-do-egresso.demonstracao`, estável, como no exemplo do protótipo |
| `DTSTAMP` | momento da geração, em UTC |
| `SEQUENCE` | 0; +1 se `data_alterada_em`; +1 se `cancelado_em` |
| `DTSTART`, `DTEND` | `inicio` e `termino` em UTC (`…Z`) |
| `SUMMARY` | título |
| `URL` | endereço absoluto de `/encontros/<id>/` |
| `DESCRIPTION` | "Encontro proposto por egresso no Portal do Egresso. O link da reunião está na página do encontro, para quem confirmou: <URL>" e o aviso de que o arquivo não muda sozinho |
| `STATUS` | `CANCELLED` se cancelado; ausente nos demais casos |

**Nunca contém:** o link da reunião, o nome de apresentação, a origem do organizador, nem
dado de quem baixa.

**Quem baixa:** o organizador, e a Pessoa com confirmação ativa. As demais pessoas recebem
"não encontrado".
