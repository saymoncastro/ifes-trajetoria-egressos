# Quickstart — validação da Feature 023

Pré-requisito: ambiente local conforme
[docs/desenvolvimento/ambiente-local.md](../../docs/desenvolvimento/ambiente-local.md),
com `preparar_demonstracao` executado e o servidor em `127.0.0.1:8000`.

## 1. Testes automatizados

```bash
uv run pytest tests/acesso/test_pendente.py tests/participacao/test_jornada_maximo.py tests/interface/test_interface_esforco.py
```

```bash
uv run pytest
```

Esperado: tudo verde, incluindo os testes de não regressão do instrumento
(`tests/instrumento/`) e da 014.

## 2. Sessão expirada com envio preservado (US1)

1. Suba o servidor com `TRAJETORIA_SESSAO_INATIVIDADE=1`.
2. Entre como Fernanda (painel fictício), inicie, responda a Seção 1 e marque parte da
   Seção 2 sem enviar.
3. Espere mais de 1 minuto e toque em "Salvar e continuar".
4. Esperado: entrada com "Por segurança…" e "O que você marcou nesta parte foi guardado…".
5. Entre de novo como Fernanda. Esperado: a Seção 2 com as marcações e "Recuperamos o que
   você tinha marcado…". No banco, nenhuma Resposta nova até "Salvar e continuar".
6. Repita o passo 3 e entre como Ana. Esperado: a tela de formações de Ana, sem nenhuma
   recuperação.

## 3. Próxima formação (US2)

Entre como Bruno, conclua a primeira formação (Q1 = "Não" é o caminho mais curto) e veja,
na confirmação, "Você também pode responder sobre: Bacharelado em Engenharia Civil ·
Vitória · 2020" com o botão. Um toque deve abrir a Seção 1 da segunda formação.

## 4. Parte e retomada (US3)

Em cada Seção, confira "Parte X · faltam no máximo N partes" (Seção 1 da baseline: "Parte 1 ·
faltam no máximo 8 partes"; "Avaliação": "faltam no máximo 4 partes"). Use "Salvar e sair" e veja na tela
de formações "Você parou em «…»".

## 5. Complemento (US4)

Na "Avaliação", o campo "Descreva…" só aparece ao marcar "Outro:". Para forçar o erro,
marque "Outro:", digite, desmarque e envie: a Seção volta com o campo visível e a nova
mensagem; nada foi gravado.

## 6. Medição de rolagem (SC-006)

Com o viewport em 375×812, percorra o cenário A da auditoria e some
`document.documentElement.scrollHeight / 812` em cada tela. Meta: ≤ 25 telas, com a
pergunta da Seção 1 a ≤ 1,4 tela do topo. Registre as capturas em
`specs/023-jornada-menos-esforco/evidencias/`.

## 7. Sem JavaScript (SC-010)

Desative o JavaScript no navegador e repita os passos 2 a 5 (no passo 5, sem
`:has()`, o campo aparece sempre).
