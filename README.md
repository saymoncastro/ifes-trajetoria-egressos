# Trajetória Ifes

Software do Núcleo Institucional de Acompanhamento de Egressos (NIAE) do Ifes.

## Começando

- **Subir o ambiente local, do clone aos testes:** [docs/desenvolvimento/ambiente-local.md](docs/desenvolvimento/ambiente-local.md). É o ponto de partida; os quickstarts abaixo validam features isoladas.
- Agentes de IA: [AGENTS.md](AGENTS.md).
- Implantação em VM Ubuntu no datacenter: [docs/implantacao/datacenter-ubuntu.md](docs/implantacao/datacenter-ubuntu.md); operação: [docs/implantacao/operacao-producao.md](docs/implantacao/operacao-producao.md).
- Princípios do projeto: [Constituição](.specify/memory/constitution.md).

## Features

- Validação da Feature 001 (núcleo acadêmico e fonte simulada): [quickstart da Feature 001](specs/001-nucleo-academico-fonte-simulada/quickstart.md)
- Instrumento de pesquisa (Pesquisa, Versão e estrutura): [quickstart da Feature 002](specs/002-pesquisa-versao-instrumento/quickstart.md)
- Migração semântica do Formulário Egresso Ifes 2024 (baseline em rascunho, 54 perguntas, Matriz de Migração Q1–Q54): [quickstart da Feature 003](specs/003-migracao-semantica-instrumento/quickstart.md)
- Campanhas e população elegível: [quickstart da Feature 004](specs/004-campanhas-populacao-elegivel/quickstart.md)
- Participação e respostas em rascunho: [quickstart da Feature 005](specs/005-participacao-respostas-rascunho/quickstart.md)
- Jornada de resposta e conclusão: [quickstart da Feature 006](specs/006-jornada-conclusao-participacao/quickstart.md)
- Contextualização da formação e entrada na pesquisa: [quickstart da Feature 007](specs/007-contextualizacao-formacao-entrada/quickstart.md)
- Interface navegável de demonstração (dados fictícios, sem autenticação): [quickstart da Feature 008](specs/008-interface-navegavel-pesquisa/quickstart.md)
- Editor institucional de Pesquisa e Versão (só no modo local não produtivo, `TRAJETORIA_DEMONSTRACAO=1`; não publica): [quickstart da Feature 009](specs/009-editor-pesquisa-versao/quickstart.md)
- Governança, papéis e escopos institucionais (vínculos CPAEG/CSAEG autorizam o editor; operador fictício só no modo de demonstração; o editor continua indisponível para uso produtivo enquanto não houver identificação de operadores — DP-1001): [quickstart da Feature 010](specs/010-governanca-papeis-escopos/quickstart.md)
- Acompanhamento operacional da coleta (`/acompanhamento/`; indicadores agregados e derivados por Campanha — elegíveis atuais, Participações iniciadas e concluídas, recortes acadêmicos —, CPAEG institucional e CSAEG por unidade; sem modelos novos, sem dados individuais; só no modo de demonstração): [quickstart da Feature 011](specs/011-acompanhamento-operacional-coleta/quickstart.md)
- Dataset analítico reprodutível (snapshot imutável de Campanha encerrada; operação de domínio, sem tela): [quickstart da Feature 012](specs/012-dataset-analitico-reprodutivel/quickstart.md)
- Exportações analíticas e contrato de dados para o GeN (CSV/XLSX pseudonimizado, contrato v2; operação de domínio, sem tela): [quickstart da Feature 013](specs/013-exportacoes-analiticas-gen/quickstart.md)
- Polish consolidado da jornada do egresso (salvar e sair, pendência × erro, alvos de toque): [quickstart da Feature 014](specs/014-polish-jornada-egresso/quickstart.md)
- Identidade visual da jornada (tokens, shell institucional, assinatura; validação institucional pendente): [quickstart da Feature 015](specs/015-identidade-visual-jornada/quickstart.md)
- Mobilização por Lotes e contatos do egresso (`/acompanhamento/campanhas/<id>/lotes/`: prévia, Lote congelado por Pessoa e envio retomável por e-mail; `/meu-email/`: atualização voluntária pelo egresso; contatos fictícios carregados pelo `preparar_demonstracao`, Mailpit local; envio real desativado até os Gates A e B; somente demonstração): [quickstart da Feature 020](specs/020-mobilizacao-real-lotes-contatos/quickstart.md). Substitui a comunicação simulada da [Feature 016](specs/016-mobilizacao-comunicacao-simulada/quickstart.md).
- Gestão mínima de Campanha (criar, editar, abrir e encerrar pela CPAEG; somente demonstração): [quickstart da Feature 017](specs/017-gestao-minima-campanha/quickstart.md)
- Identificação e acesso do egresso (`/acesso/`; CPF e data de nascimento conferidos por HMAC; somente demonstração): [quickstart da Feature 018](specs/018-identificacao-acesso-egresso/quickstart.md)
- Formação declarada e validação posterior (fonte digital ou acervo, quarentena analítica e dados de consulta cifrados; somente demonstração): [quickstart da Feature 019](specs/019-formacao-declarada-validacao/quickstart.md)
- Minha trajetória no Ifes (`/minha-trajetoria/`; devolutiva depois da pesquisa, montada só com fatos institucionais e com card vertical 9:16 em PNG; ingresso e agregados vêm de uma fonte de contexto simulada, separada da fonte acadêmica, carregada pelo `preparar_demonstracao`; somente demonstração): [quickstart da Feature 021](specs/021-minha-trajetoria-narrativa/quickstart.md)
- Minha trajetória em vídeo (`/minha-trajetoria/`, bloco "Vídeo da sua trajetória"; MP4 vertical de ~8 s, sem áudio, que é o card da 021 em movimento, renderizado pelo projeto Node `video/` com Remotion e processado por `manage.py processar_videos`; somente demonstração): [quickstart da Feature 022](specs/022-minha-trajetoria-video/quickstart.md)
- Jornada de resposta com menos esforço, sem mudar o instrumento (envio guardado quando a sessão expira, próxima formação na confirmação, "Parte X · faltam no máximo N", complemento só com "Outro" marcado, não confirmação em dois passos; somente demonstração; base na [auditoria de esforço](docs/auditorias/2026-10-05-auditoria-esforco-preenchimento.md)): [quickstart da Feature 023](specs/023-jornada-menos-esforco/quickstart.md)
- Início do egresso e shell do Portal (`/`, `/entrar/`, `/inicio/`; primeira camada do Portal do Egresso como hipótese de produto, só na demonstração, sobre o núcleo e com a coleta independente — [ADR 0008](docs/adr/0008-portal-do-egresso-camada-de-relacionamento.md); o convite continua em `/acesso/` → `/formacoes/`; Minha trajetória, card e vídeo para quem tem Conclusão Acadêmica, mesmo sem ter respondido; `TRAJETORIA_PORTAL=0` desliga): [quickstart da Feature 024](specs/024-inicio-egresso-portal/quickstart.md)
- Documentação institucional, funcional e conceitual (página estática; abrir `docs/documentacao/index.html` no navegador): [docs/documentacao/](docs/documentacao/index.html)
