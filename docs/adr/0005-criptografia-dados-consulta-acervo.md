# ADR 0005 — Criptografia dos dados para consulta ao acervo

Data: 2026-10-04. Estado: implementada para demonstração com dados fictícios.

A Feature 019 precisa comparar identificadores sem abri-los e permitir uma consulta
humana explícita ao acervo. HMAC-SHA-256 da 018 atende à comparação; sua irreversibilidade
não atende à consulta. CPF e nascimento ficam cifrados num registro separável, criado
junto com a declaração. Nenhum valor é copiado para Pessoa, instrumento ou Resposta.

Usamos Fernet da biblioteca PyCA `cryptography`, com autenticação e finalidade explícita
no conteúdo cifrado. A chave A (`TRAJETORIA_CHAVE_SELO_DECLARACAO`) protege apenas os selos
transitórios, com prazo curto e finalidade de trânsito ou início. A chave B
(`TRAJETORIA_CHAVE_CONSULTA_ACERVO`) protege os dados persistidos, com finalidade `acervo`
e UUID da declaração. A abertura confere ambos. As chaves ficam no ambiente e são
validadas antes do uso: formato válido, diferentes entre si e das demais chaves.

Selos só circulam em POST com CSRF. O selo de início carrega uma chave de criação UUID
única, cuja restrição no banco garante consumo idempotente. Nenhum selo é guardado na
sessão ou URL. As respostas têm `no-store`; os campos POST sensíveis são anotados para
não aparecer em relatórios de erro. A revelação exige capacidade e escopo, e registra
operador, declaração e momento na mesma transação antes da abertura, sem os valores.

A 019 aceita uma chave B. Quando a DP-1903 definir rotação, `MultiFernet` permitirá uma
lista: a primeira chave cifra e as demais decifram. Toda chave antiga deve permanecer
até todos os registros terem sido recifrados com `MultiFernet.rotate()`. Retirar antes
uma chave torna dados ilegíveis, equivalendo a descarte. Não é necessária coluna de
versão da chave. A chave A pode ser trocada sem recifrar dados persistidos.

O descarte futuro é a remoção de `DadosConsultaAcervo`, sem efeito sobre declaração,
decisão, Participação, Respostas ou snapshots. Não há descarte automático nesta feature.
Custódia, retenção, base legal e procedimento de rotação permanecem em DP-1903; o uso
real permanece bloqueado pelas decisões da 018 e DP-1901 a DP-1903.

Alternativas rejeitadas: só HMAC não permite consulta humana; uma chave para ambas as
finalidades mistura ciclos de vida; AES-GCM direto exige administrar nonce; cifra própria
não é aceitável; `pgcrypto` enviaria a chave ao banco; uma nova biblioteca como PyNaCl
não acrescenta benefício ao caso. A dependência aprovada está em `tests/dependencias.py`.
