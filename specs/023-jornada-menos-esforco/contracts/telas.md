# Contrato de telas — Feature 023

Textos provisórios (008/DP-801). A ordem listada é a ordem no documento.

## Entrada (`/acesso/`)

- Dica da data: "Só os números, por exemplo 05031994, ou DD/MM/AAAA" (FR-029).
- Aviso por código (ver [rotas.md](rotas.md)).
- `NAO_CONFIRMADA` (FR-021), idêntica para toda causa:
  1. mensagem da 018: "Não foi possível confirmar os dados informados.";
  2. lista numerada:
     1. "Confira se o CPF e a data de nascimento estão certos." + ação "Conferir os dados"
        (leva a `#cpf`);
     2. "Se estiverem certos, sua formação pode ainda não estar na nossa base. Você pode
        informá-la, e ela passará por verificação institucional." + botão "Informar minha
        formação".
- Sem "Continuar para suas formações" depois de uma tentativa que falhou (FR-022).

## Seção (`/participacoes/<p>/secoes/<n>/`)

1. aviso (percurso, anterior, recuperado), quando houver;
2. linha da parte: "Parte X · faltam no máximo N partes" ou "Parte X · última parte"; acima dela, quando a Seção anterior foi salva, a linha "Parte anterior salva." (FR-013);
3. título principal (014 FR-023, inalterado);
4. resumo de erros ou pendências (inalterado);
5. contexto compacto (inalterado);
6. na primeira Seção, `<details>` "Sobre esta pesquisa" com o texto de abertura (FR-025);
7. texto da Seção (visível);
8. Perguntas. Enunciado: obrigatória com " (obrigatória)" só para tecnologia assistiva;
   opcional com "(opcional)" visível (FR-023). Duas Opções curtas lado a lado (FR-024).
   Complemento: rótulo "Descreva o que se encaixa em «Opção»"; oculto até marcar a Opção
   (FR-018). No erro: visível, com a mensagem "Você escreveu uma descrição para «Opção», mas
   a opção não está marcada. Marque «Opção» ou apague a descrição." (FR-020);
9. em Seções com mais de 8 Perguntas, depois da Pergunta ⌈n/2⌉: "Precisa parar? O que você
   marcou até aqui fica salvo." + botão secundário "Salvar e sair" (`name=depois
   value=sair`) (FR-010);
10. rodapé: "Salvar e continuar", "Salvar e sair"; terciárias: "Voltar à seção anterior"
    (quando houver) e, **só com erro de forma**, "Sair sem salvar esta seção" (FR-026).

Título da aba: título da Seção ou "Parte X" (FR-015).

## Suas formações (`/formacoes/`)

Por formação em andamento, abaixo da situação: "Você parou em «Título» · faltam no máximo
N partes", "Você parou na parte X · faltam no máximo N partes" (sem título) ou "Falta só
concluir" (jornada finalizada) (FR-017). Com N = 0: "Você parou em «Título» · é a última
parte".

## Concluir a pesquisa

1. título "Concluir a pesquisa";
2. "Você chegou ao fim da pesquisa. Depois de concluída, ela não poderá ser alterada.";
3. botão "Concluir pesquisa";
4. "Se quiser revisar alguma resposta antes de concluir, volte a uma das partes:" + lista
   (título da Seção ou "Parte X");
5. contexto da formação.

## Pesquisa concluída

1. bloco de confirmação (título, frase de registro);
2. agradecimento ou texto de encerramento da Versão;
3. (Conclusão, com outra formação pendente) "Você também pode responder sobre:" + linha
   compacta + botão "Responder sobre esta formação" / "Continuar a pesquisa desta formação";
   com mais de uma: ligação "Ver todas as suas formações";
4. "Ver minha trajetória no Ifes" (Conclusão) ou "Ver suas formações informadas"
   (declarada);
5. convite de e-mail (Conclusão);
6. contexto da formação.

## Declaração (`/declaracao/…`)

- Formulário: nome com `autocomplete="name"`; nível em botões de opção dentro de
  `fieldset`/`legend` (FR-031).
- Confirmação: "curso · unidade · nível · ano"; nota de verificação; botão primário
  "Começar"; formulário "Corrigir" (secundário); "Sair" com menor ênfase (FR-032).
- Lista de formações informadas: por item em andamento, a mesma indicação de "Você parou
  em…" (FR-017).
