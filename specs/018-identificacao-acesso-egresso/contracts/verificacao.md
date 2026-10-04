# Contrato de domínio — verificação, sessão e limitação

Módulos em `trajetoria/acesso/`. Funções puras ou de leitura, exceto onde indicado.
Nenhuma delas grava Pessoa, Conclusão, Participação ou Resposta.

## `chaves.py`

| Função | Contrato |
| --- | --- |
| `chaves_de_acesso() -> Chaves` | Lê `TRAJETORIA_CHAVE_ACESSO_LOCALIZACAO` e `TRAJETORIA_CHAVE_ACESSO_VERIFICACAO`. Levanta `ChavesInvalidas` se alguma estiver ausente ou tiver menos de 32 caracteres, se forem iguais entre si ou se alguma for igual à `SECRET_KEY` ou à `TRAJETORIA_CHAVE_PSEUDONIMIZACAO`. A mensagem nunca contém a chave |
| `identificador_cpf(cpf11, chaves) -> str` | HMAC-SHA-256 hexadecimal de `"cpf:" + cpf11` com a chave de localização |
| `verificador(cpf11, data, chaves) -> str` | HMAC-SHA-256 hexadecimal de `"cpf-nascimento:" + cpf11 + ":" + data.isoformat()` com a chave de verificação |
| `chave_de_origem(endereco, chaves) -> str` | HMAC-SHA-256 hexadecimal de `"origem:" + endereco` com a chave de localização |

## `normalizacao.py`

| Função | Contrato |
| --- | --- |
| `normalizar_cpf(texto) -> str \| None` | Remove pontos, hífen e espaços. Devolve 11 dígitos se o dígito verificador for válido e os dígitos não forem todos iguais; senão, `None` |
| `cpf_utilizavel(cpf11) -> bool` | A mesma regra, para o CPF canônico vindo da fonte |
| `normalizar_data(texto, hoje) -> date \| None` | Aceita `DD/MM/AAAA` ou `DDMMAAAA`. Devolve `None` para data impossível, posterior a `hoje` ou anterior a 1900 |

## `verificacao.py`

```text
verificar(cpf_texto, data_texto, origem, *, agora) -> Confirmada | NaoConfirmada | Indisponivel | FormatoInvalido
```

| Passo | Condição | Resultado |
| --- | --- | --- |
| 1 | Origem em espera | `Indisponivel(LIMITE_TEMPORARIO)`; a submissão não é avaliada |
| 2 | Conta a submissão da origem | — |
| 3 | CPF ou data inválidos | `FormatoInvalido(campos)`; não conta falha de credencial |
| 4 | Chaves inválidas | `Indisponivel(CHAVE_NAO_CONFIGURADA)` |
| 5 | Deriva identificador e verificador | Sempre os dois |
| 6 | Outra verificação do mesmo CPF em andamento, ou CPF em espera | `Indisponivel(LIMITE_TEMPORARIO)`. A trava do CPF vale até o fim do passo 8 |
| 7 | Exatamente 1 material com esse identificador, verificador presente e igual (`compare_digest`) | `Confirmada(pessoa, versao_material)`; apaga o contador do CPF e desconta a submissão da origem |
| 8 | Qualquer outro caso | `NaoConfirmada()`; conta falha do CPF. Quando não há verificador a comparar, compara com um valor fictício |
| — | Exceção inesperada nos passos 4 a 8, inclusive do cache | `Indisponivel(FALHA_TECNICA)`; registra só o nome da classe |

**Invariantes:**

- **Sem gravação de domínio.** Nenhuma escrita além dos contadores no cache.
- **Sem valores em claro.** CPF e data nunca aparecem em exceção, log ou atributo de
  resultado.
- **Causa da não confirmação.** `NaoConfirmada` não tem campo de causa. Não é possível
  distinguir CPF inexistente, data errada, material incompleto, colisão ou Pessoa não
  importada pelo resultado, pelo tempo de execução ou pelos contadores.
- **Origem e momento.** `origem` é o `REMOTE_ADDR` da requisição. `agora` é injetável nos
  testes.

```text
CausaIndisponibilidade = CHAVE_NAO_CONFIGURADA | LIMITE_TEMPORARIO | FALHA_TECNICA
```

`Indisponivel` em `LIMITE_TEMPORARIO` carrega `espera_ate` (instante), usado só para o
cabeçalho `Retry-After`.

## `limitacao.py`

Contadores no cache `acesso` (research R8; data-model). Parâmetros em
`settings.TRAJETORIA_ACESSO_LIMITES`:

```text
{"origem": {"livres": 30, "janela": 900}, "cpf": {"livres": 3, "janela": 3600},
 "espera_base": 5, "fator": 3, "espera_maxima": 300}
```

| Função | Contrato |
| --- | --- |
| `em_espera(chave, agora) -> datetime \| None` | Instante até o qual a chave espera, ou `None` |
| `registrar(tipo, chave, agora)` | Incremento atômico. Acima de `livres`, define a espera `min(base × fator^(k−1), máxima)`, nunca além do fim da janela. A janela é **fixa** a partir da primeira contagem; ao terminar, a contagem recomeça |
| `estornar(chave)` | Desconta uma contagem; usado na confirmação para a origem |
| `zerar(chave)` | Remove o contador; usado na confirmação para o CPF |
| `travar(chave) -> bool` / `liberar(chave)` | Reserva a verificação de um CPF (expira em 10 s). Ocupada → `Indisponivel(LIMITE_TEMPORARIO)` com espera de 1 s |

Nunca há bloqueio sem prazo. Uma tentativa recusada durante a espera não incrementa nem
prolonga.

## `sessao.py`

| Função | Contrato |
| --- | --- |
| `estabelecer(request, confirmada, agora)` | `cycle_key()`. Grava `acesso.pessoa`, `acesso.confirmada_em`, `acesso.ultimo_uso` e `acesso.versao_material` e substitui qualquer sessão anterior (FR-043) |
| `pessoa_em_uso(request) -> Pessoa \| None` | Lida uma vez por requisição. Devolve `None` e executa `flush()` quando a sessão está inativa além do limite, passou da duração máxima, a Pessoa não existe ou a versão do material difere da atual. Renova `ultimo_uso` no máximo uma vez por minuto. Nunca levanta exceção por sessão ausente ou corrompida |
| `encerrar(request)` | `flush()` |
| `dados_de_sessao(pessoa, versao_material, agora) -> dict` | Pura. Monta as quatro chaves; usada por `estabelecer` e pelo auxiliar de testes |

Parâmetros: `settings.TRAJETORIA_SESSAO_INATIVIDADE` e
`settings.TRAJETORIA_SESSAO_DURACAO_MAXIMA` (`timedelta`), lidos do ambiente com padrões de
30 min e 8 h.

## Consumidores

- **`interface/views.py`** e **`demonstracao/contexto.py`**: importam `pessoa_em_uso` de
  `acesso.sessao`. Essa é a única mudança na jornada (FR-044).
- **019**: consome `NaoConfirmada` como ponto de saída (FR-035) e pode chamar `chaves` e
  `normalizacao` para classificar a declaração. A 018 não oferece outra API para isso.
