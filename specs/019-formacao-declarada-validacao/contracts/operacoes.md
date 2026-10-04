# Contrato: operações e consultas

Únicos caminhos de escrita dos modelos novos. Cada operação roda numa transação e valida
tudo antes da primeira gravação. Mensagens de erro citam motivo e UUIDs técnicos, nunca
CPF, data, nome nem valores declarados.

## `declaracao.selo`

Usa duas chaves Fernet com finalidades separadas (R5):
- **chave A**, `TRAJETORIA_CHAVE_SELO_DECLARACAO`: selos transitórios;
- **chave B**, `TRAJETORIA_CHAVE_CONSULTA_ACERVO`: dados persistidos.

Antes de qualquer uso, as duas são validadas: formato Fernet, diferentes entre si e de
`SECRET_KEY`, das chaves da 018 e da pseudonimização. Se falhar, levanta
`ChaveIndisponivel`.

| Função | Chave | Contrato |
| --- | --- | --- |
| `selar_transito(cpf11, data)` | A | Finalidade `transito`. Definido na 018 (`acesso.transito`) e reexportado aqui; só a 018 o chama, ao produzir `NAO_CONFIRMADA` |
| `abrir_transito(token, agora)` | A | Devolve `(cpf11, data)`. Vencido (`TRAJETORIA_SELO_DECLARACAO_VALIDADE`), adulterado ou de outra finalidade levanta `SeloInvalido` |
| `selar_inicio(cpf11, data, dados)` | A | Finalidade `inicio`. Gera uma `chave_de_criacao` nova (UUID) junto com os cinco campos declarados |
| `abrir_inicio(token, agora)` | A | Devolve `(cpf11, data, dados, chave_de_criacao)`. Mesmas recusas de `abrir_transito` |
| `selar_consulta(declaracao_id, cpf11, data)` / `abrir_consulta(dados)` | B | Finalidade `acervo`. A abertura confere finalidade e UUID da declaração |

**Garantias.**
- Nenhuma função registra log com os argumentos.
- Os tokens só circulam em campos POST com CSRF.
- As views que recebem selo usam `sensitive_post_parameters("selo")` (R6).

## `declaracao.operacoes`

### `campanhas_compativeis(dados, *, agora)` → tupla de Campanhas

Campanhas EM COLETA cuja avaliação da 004 sobre os valores declarados não tem pendência,
desconsideradas as de `MODALIDADE` e `FORMA_OFERTA` (R9; FR-021).

### `iniciar_participacao_declarada(dados, cpf11, data, chave_de_criacao, *, origem, agora)` → `(Participacao, criada: bool)`

Passos:

1. **Idempotência.** Se já existe `FormacaoDeclarada` com essa `chave_de_criacao`:
   - mesmo `verificador`: devolve a Participação dela com `criada=False`, sem gravar nada;
   - outro `verificador`: levanta `SeloInvalido`, sem revelar nada.
2. Aplica a limitação geral por origem da 018. Se em espera, levanta `EmEspera`.
3. Valida as chaves A e B e as da 018. Se falhar, levanta `ChaveIndisponivel`.
4. `campanhas_compativeis`: nenhuma levanta `SemCampanha`; mais de uma levanta
   `Ambiguidade`.
5. Cria, na mesma transação, com a `chave_de_criacao`:
   - a `FormacaoDeclarada`, com os dois HMACs;
   - os `DadosConsultaAcervo`, com o selo de consulta;
   - a `Participacao(campanha, formacao_declarada, iniciada_em=agora)`.

- **Corrida.** Duas chamadas simultâneas com a mesma `chave_de_criacao` são decididas pelo
  `UNIQUE`. Quem perde relê e segue o passo 1.
- **Erro.** Nada é gravado.
- **Isolamento.** Nenhuma Pessoa, Conclusão ou material de verificação é tocado (FR-005).

### `declaracoes_do_par(cpf11, data)` → tupla de UUIDs

Declarações com o mesmo `verificador`. É usada só para estabelecer a sessão do declarante.

### `registrar_validacao(formacao, *, vinculos, operador, agora, resultado, candidata=None, referencia_fonte=None, acervo=None)` → `ValidacaoDaFormacao`

Passos:

1. Bloqueia a declaração.
   - Já decidida: levanta `JaDecidida`.
   - Participação não concluída: levanta `ForaDaFila`.
2. Verifica escopo e capacidade (E3).
   - Sem capacidade ou fora do escopo: levanta `ForaDoEscopo`. Isso inclui Conclusão ou
     acervo de unidade fora do vínculo da CSAEG.
3. `NAO_CONFIRMADA`: grava a decisão e encerra.
4. `CONFIRMADA`: exatamente uma origem.
   - **`candidata`**: Conclusão de Pessoa cujo material tem o mesmo `identificador_cpf`.
     Se não for, levanta `ForaDoEscopo`, que é indistinguível.
   - **`referencia_fonte`**: `obter_conclusao` na fonte configurada e depois
     `acesso.material.incorporar_com_material` para a Pessoa.
     - Inexistente ou não reconhecida: levanta `ReferenciaInexistente`.
     - Indisponível: levanta `FonteIndisponivel`.
   - **`acervo`**: `declaracao.acervo.registrar_referencia` e depois a incorporação pela
     `FonteAcervoHistorico` (contracts/fonte-acervo.md).
     - Divergente: levanta `ReferenciaDivergente`.
5. Bloqueia a linha da Conclusão (R10).
6. Grava os fatos do momento (R3):
   - `fora_da_abrangencia_na_validacao = not avaliar(campanha, conclusao).elegivel`. É fato
     congelado;
   - `conflito_detectado_na_validacao`: só se compatível, e verdadeiro quando já existe
     outra Participação **oficial** da Campanha com a mesma Conclusão efetiva. A partir daí,
     o conflito fica pendente até uma resolução futura (DP-1907).
7. Grava a decisão.

### `revelar_dados(formacao, *, vinculos, operador, agora)` → `(nome, cpf11, data)` ou `None`

Passos:
1. Verifica escopo e capacidade.
2. Valida a chave (`ChaveIndisponivel`). Nesse caso, nada é registrado.
3. Sem `DadosConsultaAcervo`: devolve `None` (descartado).
4. Grava `AcessoAosDadosDeConsulta` e depois abre o selo.

O registro e a leitura ficam na mesma transação.

## `participacao` (alterações)

| Item | Mudança |
| --- | --- |
| `iniciar_participacao` | Depois de reler a Conclusão, faz `select_for_update` nela (R10). Se não houver Participação institucional `(C, X)` mas houver declarada oficial com Conclusão efetiva X em C, devolve-a como `JA_EXISTENTE` (FR-092) |
| `consultas.participacoes_oficiais()` | QuerySet das oficiais (âncora institucional; ou confirmada, sem `fora_da_abrangencia_na_validacao` e sem conflito pendente), anotado com `conclusao_efetiva_id` (R4). O conceito de "conflito pendente" fica isolado num único `Q`, para que uma resolução futura altere só esse ponto |
| `consultas.atributo_efetivo(campo)` | Expressão `Coalesce` do atributo da Conclusão efetiva |
| `consultas.situacao_analitica(participacao)` | FR-050, para as telas e os testes |
| `entrada._participacoes_dos_pares` | Usa `participacoes_oficiais` pela Conclusão efetiva (R18) |

## `governanca.regras` (alteração)

`pode_validar_formacao(vinculos) -> bool`: CPAEG ou CSAEG ativos. O escopo é o de
`escopo_de_acompanhamento`.
