"""Exportação analítica de um snapshot (specs/013-exportacoes-analiticas-gen).

Representação tabular de **um** snapshot analítico explicitamente informado: o mesmo dataset
lógico (Dados, Dicionário, Metadados) serializado em CSV (pacote ZIP) e em XLSX. Nada aqui
grava — nem banco, nem disco, nem log de conteúdo — e nada cria verdade nova: a fonte é a
fronteira de leitura da 012 e a Versão imutável. Pacote comum, não app Django: sem modelos,
migrations, views, rotas ou comandos (research R2).

Sem interface nesta feature. Quem expuser estas operações DEVE restringi-las à atuação CPAEG
ativa, em escopo institucional, e NÃO DEVE oferecê-las à CSAEG (spec FR-102, FR-103).

Decisões pendentes que este pacote respeita:

- 012/DP-1201: nenhum snapshot é oficial; toda exportação recebe o snapshot.
- DP-1301: quem gera, recebe e compartilha os arquivos; custódia e rotação da chave de
  pseudonimização.
- DP-1302: mecanismo de consumo pelo GeN; aqui só o contrato de dados, sem transporte.
- DP-1303: respostas sensíveis e reidentificação; pseudonimizado, nunca "anônimo".
- 002/DP-006: chaves de coluna locais à Versão; nenhuma correspondência entre Versões.
- 005/DP-503: Respostas de rascunho só quando válidas para o percurso, marcadas.
- 006/DP-601: concluída por recusa é concluída; nenhuma coluna de recusa.
"""
