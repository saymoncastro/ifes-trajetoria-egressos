# Inventário do Formulário Egresso do Ifes 2024

**Fontes de referência**:

| Fonte | Situação no repositório | SHA-256 |
|-------|-------------------------|---------|
| Formulário original: `formulario-egresso-ifes-2024-original.pdf` (exportação em PDF da tela de edição do Google Formulários, impressa em 29/07/2026, 31 páginas) | **Arquivo de trabalho local, não versionado.** Motivo: a exportação original contém a URL administrativa (de edição) do Google Formulários em todas as páginas. | `781349e8f7e87f80c79715e4e0d97b5939ad5a8deabaf162a454d54ad5df0854` |
| Referência sanitizada do formulário (exportação pela visualização de respondente) | Ainda não gerada. Quando versionada, registrar aqui nome e SHA-256. | — |
| PAEG: [paeg-resolucao-cs-177-2023-anexo.pdf](paeg-resolucao-cs-177-2023-anexo.pdf) | Versionada (documento público). | `3ed544792923feb40c0d6f3e9e7c04d91e8d313dac1c28bf040f99418b6cbec0` |

## Natureza deste documento

Este inventário é **transcrição e análise descritiva** do instrumento atual, que a
Constituição (Princípio XIII) define como referência funcional inicial. Ele **não** é
spec, **não** propõe revisão metodológica e **não** decide quais perguntas serão
mantidas, removidas ou alteradas.

- Textos de perguntas, opções e descrições estão transcritos como aparecem no PDF,
  incluindo erros de digitação.
- A coluna **Origem provável** é **hipótese** de classificação (Princípio III:
  institucional / derivado / declarado). A classificação efetiva depende da fonte
  acadêmica oficial e da qualidade dos seus dados, que são `DECISÃO PENDENTE`.
- A seção **Observações** registra fatos observados no instrumento. Nenhuma observação
  autoriza alterar o instrumento (Princípio XIII); cada uma deve ser tratada, se for o
  caso, por spec ou revisão metodológica explícita e aprovada.
- Condicionais, erros e peculiaridades descritos aqui são **comportamento observado da
  implementação atual** (Google Formulários), **não requisitos obrigatórios de
  migração**. A spec correspondente deverá distinguir **intenção do instrumento** de
  **limitação ou acidente da implementação**, preservando a intenção (Princípio XIII).
- As classes de origem seguem a terminologia **institucional / derivável / declarada /
  a investigar**.

## Visão geral

| Item | Valor |
|------|-------|
| Título exibido | Egresso Ifes |
| Perguntas numeradas | 54 |
| Seções (navegação do Google Formulários) | 14 (a 14ª é a tela final) |
| Perguntas com ramificação por resposta | Q1, Q14, Q33, Q46, Q51 |
| Campo de identificação do respondente | O instrumento não solicita explicitamente nome, CPF, e-mail ou matrícula; a configuração externa de identificação/coleta do Google Formulários não foi verificada |
| Formações por resposta | Uma (o respondente escolhe um nível e um curso) |
| Contato informado | egressos@ifes.edu.br; (27) 99527-0027 |

### Tipos de pergunta usados

| Tipo (Google Formulários) | Como aparece no PDF | Perguntas |
|---------------------------|---------------------|-----------|
| Múltipla escolha (uma opção, botões) | "Marcar apenas uma oval." sem indicação "Dropdown" | Q1, Q5, Q6, Q14, Q33, Q45, Q46, Q51 |
| Lista suspensa (uma opção) | "Marcar apenas uma oval." com indicação "Dropdown" | Q2, Q4, Q7–Q9, Q11–Q13, Q15–Q19, Q22–Q25, Q27–Q31, Q34, Q35, Q37–Q41, Q49 |
| Caixas de seleção (várias opções) | "Marque todas que se aplicam." | Q26, Q32, Q47 |
| Resposta curta (texto) | Linha de resposta | Q3, Q10 |
| Escala linear 1–5 | Escala "Disc…" (rótulo truncado no PDF) a "Concordo totalmente" | Q20, Q21, Q36, Q42–Q44, Q48, Q50, Q52–Q54 |

## Estrutura de seções e navegação

| Seção | Título | Perguntas | Navegação ao final da seção |
|-------|--------|-----------|-----------------------------|
| 1 | (cabeçalho) / Termos e condições | Q1 | Q1 = "Não" → seção 14 (fim); "Sim" → seção 2 |
| 2 | Informações Pessoais | Q2–Q9 | → seção 3 |
| 3 | Informações do curso | Q10–Q14 | Por Q14 → seção 4, 5, 6 ou 7 |
| 4 | Ensino Médio/Técnico Integrado | Q15 | → Q20 (seção 8) |
| 5 | Técnico Concomitante / Subsequente /EJA - PROEJA | Q16, Q17 | → Q20 (seção 8) |
| 6 | Graduação | Q18 | → Q20 (seção 8) |
| 7 | Pós-Graduação | Q19 | → Q20 (seção 8) |
| 8 | Avaliação | Q20–Q33 | Por Q33: "Sim" → Q34 (seção 9); "Não" → Q45 (seção 10) |
| 9 | Egresso que trabalha | Q34–Q44 | → Q46 (seção 11) |
| 10 | Egresso que não trabalha | Q45 | → Q46 (seção 11) |
| 11 | Estudo | Q46–Q48 | Por Q46: "Sim" → Q49 (seção 12); "Não" → Q52 (seção 13) |
| 12 | Egresso que estuda | Q49–Q51 | Q51 = "Instituição Privada" → Q52; padrão da seção → Q52 |
| 13 | (sem título visível no PDF) | Q52–Q54 | → seção 14 |
| 14 | Este formulário chegou ao fim! | — | Envio |

### Fluxo resumido

```text
S1 Termos (Q1) ──Não──────────────────────────────────────────────────────────► S14 Fim
   │Sim
   ▼
S2 Pessoais (Q2–Q9) → S3 Curso (Q10–Q14)
                          │ Q14
          ┌───────────────┼───────────────┬───────────────┐
          ▼               ▼               ▼               ▼
   S4 Méd/Téc Int.  S5 Conc/Subs/EJA  S6 Graduação   S7 Pós-Graduação
      (Q15)           (Q16, Q17)        (Q18)           (Q19)
          └───────────────┴───────┬───────┴───────────────┘
                                  ▼
                       S8 Avaliação (Q20–Q33)
                                  │ Q33
                      ┌──Sim──────┴──────Não──┐
                      ▼                        ▼
            S9 Trabalha (Q34–Q44)    S10 Não trabalha (Q45)
                      └───────────┬────────────┘
                                  ▼
                        S11 Estudo (Q46–Q48)
                                  │ Q46
                      ┌──Sim──────┴──────Não──┐
                      ▼                        │
            S12 Estuda (Q49–Q51)               │
                      └───────────┬────────────┘
                                  ▼
                       S13 Impactos (Q52–Q54) → S14 Fim
```

**Semântica das condicionais**: no Google Formulários, a ramificação por resposta é
aplicada **ao sair da seção**, não imediatamente após a pergunta. Por isso, todas as
perguntas de uma seção são exibidas juntas, independentemente da resposta à pergunta que
ramifica. Consequências observadas estão em O-8, O-15 e O-16; são comportamento
observado da ferramenta, não regra a reproduzir.

## Inventário das perguntas

Legenda: **Obr.** = obrigatória (asterisco no PDF). **Origem provável**: I = institucional,
D = derivável, Dc = declarada; "I?" = a investigar (candidato a institucional, sujeito à
existência e à qualidade da fonte).

### Seção 1 — Cabeçalho e Termos e condições

**Texto de abertura (transcrição)**:

> Prezado(a) egresso(a) do Ifes,
>
> É com muita satisfação que nós, do Instituto Federal do Espírito Santo (Ifes), nos
> dirigimos a você para convidá-lo(a) a participar da Pesquisa com Egressos(as). Nesta
> pesquisa, desejamos conhecer quais as oportunidades que o Ifes proporcionou para a sua
> vida pessoal e profissional.
>
> A sua participação na pesquisa é muito importante e contribuirá para compreendermos
> como a educação oferecida pelo Ifes colaborou no processo de sua formação
> profissional, de sua inserção no mundo do trabalho e na melhoria de vida. Basta que
> você responda a este questionário!
>
> Se você tiver alguma dúvida sobre esta pesquisa ou sobre sua participação, por favor,
> entre em contato pelo e-mail: egressos@ifes.edu.br ou pelo telefone (27) 99527-0027.

**Termos e condições (transcrição)**:

> Para participar deste estudo, você não terá nenhum custo, nem receberá qualquer
> vantagem financeira e tem garantida plena liberdade de recusar-se a participar ou
> retirar seu consentimento, sem necessidade de comunicado prévio. A sua participação é
> voluntária e a recusa em participar não acarretará qualquer penalidade ou modificação
> na forma em que será atendido(a) pelo Ifes. Você não será identificado(a) em nenhuma
> publicação que possa resultar desta pesquisa.
>
> O Ifes tratará a sua identidade com padrões de sigilo e confidencialidade, atendendo à
> legislação brasileira, em especial, à Resolução 466/2012 do Conselho Nacional de Saúde,
> e utilizará as informações somente para fins de gestão educacional, além dos
> acadêmicos e científicos.

| Nº | Pergunta | Tipo | Obr. | Opções | Condicional | Origem provável |
|----|----------|------|------|--------|-------------|-----------------|
| Q1 | Você concorda com os termos acima? | Múltipla escolha | Sim | Sim; Não | "Não" → seção 14 (fim) | Dc (manifestação de consentimento — Princípio XVII) |

### Seção 2 — Informações Pessoais

| Nº | Pergunta | Tipo | Obr. | Opções | Condicional | Origem provável |
|----|----------|------|------|--------|-------------|-----------------|
| Q2 | Qual é o seu sexo/identidade de gênero? | Lista suspensa | Sim | Masculino; Feminino; Mulher trans/travesti; Homem trans; Pessoa não binária; Prefiro não responder | — | Dc (ver O-6) |
| Q3 | Quantos anos você tem? | Resposta curta | Sim | — | — | D, se a data de nascimento estiver disponível institucionalmente; senão Dc |
| Q4 | Como você se autodeclara? | Lista suspensa | Sim | Branco(a); Preto(a); Pardo(a); Amarelo(a); Indígena | — | Dc (ver O-6, O-7) |
| Q5 | Você é PcD (Pessoa com deficiência)? | Múltipla escolha | Sim | Sim; Não | — | Dc (ver O-6) |
| Q6 | Se sim, qual a deficiência? | Múltipla escolha | Não | Deficiência física; Deficiência visual; Deficiência intelectual; Deficiência auditiva | Nenhuma condicional técnica (ver O-8) | Dc |
| Q7 | Qual o seu estado civil? | Lista suspensa | Sim | Solteiro(a); Casado(a); Divorciado(a); Separado(a); Viúvo(a) | — | Dc |
| Q8 | Qual é o nível de escolaridade do seu pai? | Lista suspensa | Sim | Lista E (abaixo) | — | Dc |
| Q9 | Qual é o nível de escolaridade da sua mãe? | Lista suspensa | Sim | Lista E (abaixo) | — | Dc |

**Lista E — escolaridade (Q8 e Q9)**: Sem instrução; Ensino fundamental incompleto;
Ensino fundamental completo; Ensino médio incompleto; Ensino médio completo; Ensino
superior incompleto; Ensino superior completo; Especialização incompleta; Especialização
completa; Mestrado incompleto; Mestrado completo; Doutorado incompleto; Doutorado
completo; Pós-doutorado incompleto; Pós-doutorado completo; Não sei dizer; Não se aplica.

### Seção 3 — Informações do curso

| Nº | Pergunta | Tipo | Obr. | Opções | Condicional | Origem provável |
|----|----------|------|------|--------|-------------|-----------------|
| Q10 | Em que ano você concluiu o seu curso no Ifes? *(descrição: "Exemplo: 2020, 2021, 2022, etc.")* | Resposta curta | Sim | — | — | I (Conclusão Acadêmica) |
| Q11 | Em qual campus você concluiu seu curso? | Lista suspensa | Sim | Lista C (abaixo) | — | I (Conclusão Acadêmica) |
| Q12 | Você é egresso(a) de qual modalidade? | Lista suspensa | Sim | Presencial; À distância | — | I (Conclusão Acadêmica) |
| Q13 | Você foi admitido(a) ao curso do Ifes como estudante: | Lista suspensa | Sim | Cotista (vagas de cotas, ações afirmativas); Não cotista (vagas de ampla concorrência); Outros: transferência, remoção, reopção, reingresso, novo curso, etc. | — | I (forma de ingresso; ver O-12) |
| Q14 | Indique o questionário que pretende preencher | Múltipla escolha | Sim | Ensino Médio/Técnico Integrado; Técnico Concomitante/Subsequente/EJA-PROEJA; Graduação; Pós-Graduação | → Q15; → Q16; → Q18; → Q19, respectivamente | I (nível da Conclusão Acadêmica; ver O-13) |

**Lista C — campus (Q11)**, 23 opções: Alegre; Aracruz; Barra de São Francisco;
Cachoeiro de Itapemirim; Cariacica; Cefor; Centro-Serrano; Colatina; Guarapari; Ibatiba;
Itapina; Linhares; Montanha; Nova Venécia; Piúma; Presidente Kennedy; Santa Teresa; São
Mateus; Serra; Venda Nova do Imigrante; Viana; Vila Velha; Vitória.

### Seções 4 a 7 — Curso por nível

Todas as perguntas desta parte são candidatas a dado **institucional** (curso e forma de
oferta da Conclusão Acadêmica). As listas são estáticas no formulário (ver O-14).

| Nº | Seção | Pergunta | Tipo | Obr. | Opções | Navegação após a seção | Origem provável |
|----|-------|----------|------|------|--------|------------------------|-----------------|
| Q15 | 4 — Ensino Médio/Técnico Integrado | Você é egresso(a) de qual Curso? | Lista suspensa | Sim | Lista 15 | → Q20 | I |
| Q16 | 5 — Técnico Concomitante / Subsequente /EJA - PROEJA | Você é egresso(a) de qual forma de oferta? | Lista suspensa | Sim | Concomitante; Subsequente; EJA-PROEJA | — | I |
| Q17 | 5 — Técnico Concomitante / Subsequente /EJA - PROEJA | Você é egresso(a) de qual Curso? | Lista suspensa | Sim | Lista 17 | → Q20 | I |
| Q18 | 6 — Graduação | Você é egresso(a) de qual Curso? | Lista suspensa | Sim | Lista 18 | → Q20 | I |
| Q19 | 7 — Pós-Graduação *(descrição da seção: "Tem que atualizar a lista de cursos, adicionando doutorado")* | Você é egresso(a) de qual Curso? | Lista suspensa | Sim | Lista 19 | → Q20 | I |

<details>
<summary><strong>Lista 15</strong> — Ensino Médio/Técnico Integrado (33 opções)</summary>

Fiz apenas o Ensino Médio; Técnico em Administração; Técnico em Agricultura; Técnico em
Agroindústria; Técnico em Agropecuária; Técnico em Alimentação Escolar; Técnico em
Alimentos; Técnico em Aquicultura; Técnico em Automação Industrial; Técnico em
Biotecnologia; Técnico em Edificações; Técnico em Eletromecânica; Técnico em
Eletrotécnica; Técnico em Estradas; Técnico em Florestas; Técnico em Guia de Turismo;
Técnico em Hospedagem; Técnico em Informática; Técnico em Informática para Internet;
Técnico em Infraestrutura Escolar; Técnico em Internet das Coisas; Técnico em Logística;
Técnico em Manutenção de Sistemas Metroferroviários; Técnico em Mecânica; Técnico em Meio
Ambiente; Técnico em Metalurgia; Técnico em Mineração; Técnico em Pesca; Técnico em
Portos; Técnico em Química; Técnico em Secretaria Escolar; Técnico em Segurança do
Trabalho; Técnico em Zootecnia.

</details>

<details>
<summary><strong>Lista 17</strong> — Técnico Concomitante/Subsequente/EJA-PROEJA (47 opções)</summary>

Técnico em Administração; Técnico em Agricultura; Técnico em Agrimensura; Técnico em
Agroindústria; Técnico em Agropecuária; Técnico em Alimentação Escolar; Técnico em
Automação Industrial; Técnico em Biotecnologia; Técnico em Cadista para a Construção
Civil; Técnico em Cafeicultura; Técnico em Comércio; Técnico em Comércio Exterior;
Técnico em Controle Ambiental; Técnico em Desenvolvimento de Sistemas Web com
Metodologias Ágeis; Técnico em Edificações; Técnico em Eletricista Instalador Predial de
Baixa Tensão; Técnico em Eletromecânica; Técnico em Eletrotécnica; Técnico em Estradas;
Técnico em Eventos; Técnico em Florestas; Técnico em Gastronomia; Técnico em
Geoprocessamento; Técnico em Gestão da Qualidade em Serviço; Técnico em Gestão e
Inovação de Processos Químicos e Biotecnológicos; Técnico em Guia de Turismo; Técnico em
Hospedagem; Técnico em Informática; Técnico em Infraestrutura Escolar; Técnico em
Logística; Técnico em Manutenção e Suporte em Informática; Técnico em Mecânica; Técnico
em Meio Ambiente; Técnico em Metalurgia; Técnico em Mineração; Técnico em Multimeios
Didáticos; Técnico em Operadores de Instrumentos Topográficos; Técnico em Petroquímica;
Técnico em Portos; Técnico em Processamento de Pescado; Técnico em Química; Técnico em
Redes de Computadores; Técnico em Saneamento; Técnico em Secretaria Escolar; Técnico em
Segurança do Trabalho; Técnico em Sustentabilidade Ambiental e Inovação; Técnico em
Treinamento e Instrução de Cães-Guia.

</details>

<details>
<summary><strong>Lista 18</strong> — Graduação (50 opções)</summary>

EaD - Complementação Pedagógica: Matemática, Física, Biologia e Química; EaD - Letras
Inglês - Segunda Licenciatura; EaD - Licenciatura em Informática; EaD - Licenciatura em
Letras - Português; EaD - Licenciatura em Pedagogia; EaD - Tecnologia em Gestão Pública;
EaD - Tecnologia em Sistemas para Internet; Bacharelado em Administração; Bacharelado em
Agronomia; Bacharelado em Arquitetura e Urbanismo; Bacharelado em Biomedicina;
Bacharelado em Ciências Biológicas; Bacharelado em Ciência da Computação; Bacharelado em
Ciências Econômicas; Bacharelado em Ciência e Tecnologia de Alimentos; Bacharelado em
Engenharia Ambiental; Bacharelado em Engenharia Civil; Bacharelado em Engenharia de
Aquicultura; Bacharelado em Engenharia de Controle e Automação; Bacharelado em Engenharia
de Minas; Bacharelado em Engenharia de Pesca; Bacharelado em Engenharia de Produção;
Bacharelado em Engenharia Elétrica; Bacharelado em Engenharia Mecânica; Bacharelado em
Engenharia Metalúrgica; Bacharelado em Engenharia Química; Bacharelado em Engenharia
Sanitária e Ambiental; Bacharelado em Física; Bacharelado em Geologia; Bacharelado em
Química Industrial; Bacharelado em Sistemas de Informação; Bacharelado em Zootecnia;
Licenciatura em Ciências Agrícolas; Licenciatura em Ciências Biológicas; Licenciatura em
Ciências da Natureza; Licenciatura em Física; Licenciatura em Geografia; Licenciatura em
História; Licenciatura em Letras - Português; Licenciatura em Letras - Português/Inglês;
Licenciatura em Matemática; Licenciatura em Pedagogia; Licenciatura em Química;
Tecnologia em Análise e Desenvolvimento de Sistemas; Tecnologia em Cafeicultura;
Tecnologia em Gestão Ambiental; Tecnologia em Logística; Tecnologia em Redes de
Computadores; Tecnologia em Saneamento Ambiental; Tecnologia em Sistemas para Internet.

</details>

<details>
<summary><strong>Lista 19</strong> — Pós-Graduação (77 opções)</summary>

Aperfeiçoamento em Educação para o Trânsito; Aperfeiçoamento em Estruturas de Aço;
Doutorado em Educação em Ciências e Matemática; EaD - Aperfeiçoamento em Aspectos
Técnicos da Mineração de Rochas Ornamentais; EaD - Aperfeiçoamento em Design
Educacional; EaD - Aperfeiçoamento em Educação Especial Inclusiva; EaD - Aperfeiçoamento
em Formação Docente para Educação a Distância; EaD - Aperfeiçoamento em Gestão Aplicada à
Política; EaD - Aperfeiçoamento em Internet das Coisas; EaD - Aperfeiçoamento em Mentoria
para a Educação Profissional e Tecnológica; EaD - Aperfeiçoamento em Tecnologias
Digitais Aplicadas à Educação; EaD - Especialização em Agroecologia e Sustentabilidade;
EaD - Especialização em Ciências Policiais; EaD - Especialização em Controle de Qualidade
e Segurança de Alimentos; EaD - Especialização em Docência para a Educação Profissional e
Tecnológica (DocentEPT); EaD - Especialização em Educação a Distância; EaD -
Especialização em Educação em Humanidades; EaD - Especialização em Educação Especial
Inclusiva; EaD - Especialização em Ensino Interdisciplinar em Saúde e Meio Ambiente; EaD
- Especialização em Gestão da Inovação; EaD - Especialização em Gestão Escolar para
profissionais da Educação; EaD - Especialização em Informática na Educação; EaD -
Especialização em Práticas Pedagógicas; EaD - Lato Sensu em Educação: Metodologias e
Práticas para o Ensino Fundamental; EaD - Lato Sensu em Finanças Corporativas; EaD - Lato
Sensu em Práticas Pedagógicas para Educação Profissional e Tecnológica; Especialização em
Agroecologia e Sustentabilidade; Especialização em Currículo e Ensino na Educação Básica;
Especialização em Docência nos Anos Iniciais do Ensino Fundamental: Língua Portuguesa e
Matemática; Especialização em Educação e Divulgação em Ciências; Especialização em
Educação Profissional e Tecnológica; Especialização em Eficiência Energética;
Especialização em Energias Renováveis e Eficiência Energética; Especialização em
Engenharia de Infraestrutura Urbana; Especialização em Engenharia Elétrica com ênfase em
Sistemas Inteligentes Aplicados à Automação; Especialização em Engenharia Ferroviária
com ênfase em Via Permanente; Especialização em Ensino de Ciências Naturais com ênfase em
Física ou Química; Especialização em Georreferenciamento de Imóveis Rurais e Urbanos;
Especialização em Gestão Pública; Especialização em Informática na Educação;
Especialização em Meio Ambiente; Especialização em Prática Pedagógicas para Professores;
Especialização em Recursos Hídricos; Especialização no Ensino de Ciências, Saúde e
Ambiente; Lato Sensu em Administração/Gestão Pública; Lato Sensu em Agricultura
Sustentável; Lato Sensu em Análise e Gestão Ambiental; Lato Sensu em Conectividade e
Tecnologias da Informação; Lato Sensu em Desenvolvimento de Aplicações Inteligentes; Lato
Sensu em Educação Ambiental e Sustentabilidade; Lato Sensu em Educação Profissional e
Tecnologia; Lato Sensu em Eficiência Energética Industrial; Lato Sensu em Engenharia de
Produção com ênfase em Ciência de Dados; Lato Sensu em Engenharia de Produção com ênfase
em Tecnologias da Decisão; Lato Sensu em Ensino de Ciências da Natureza; Lato Sensu em
Gestão Ambiental; Lato Sensu em Gestão Empresarial; Lato Sensu em Geoprocessamento; Lato
Sensu em Mineração de Dados Educacionais; Lato Sensu em Pedagogia da Alternância; Lato
Sensu em Práticas Educacionais; Lato Sensu em Práticas Pedagógicas; Lato Sensu em
Tecnologias de Produção de Rochas Ornamentais; Mestrado em Agroecologia; Mestrado em
Computação Aplicada; Mestrado em Educação em Ciências e Matemática; Mestrado em
Engenharia Ambiental; Mestrado em Engenharia de Controle e Automação; Mestrado em
Engenharia Elétrica; Mestrado em Engenharia Metalúrgica e de Materiais; Mestrado Nacional
Profissional em Ensino de Física; Mestrado Profissional em Educação Profissional e
Tecnológica (ProfEPT); Mestrado Profissional em Ensino de Humanidades; Mestrado
Profissional em Letras em Rede Nacional; Mestrado Profissional em Propriedade
Intelectual e Transferência de Tecnologia para Inovação; Mestrado Profissional em
Química; Mestrado Profissional em Tecnologias Sustentáveis.

</details>

### Seção 8 — Avaliação

Escalas lineares desta seção: 1 a 5, rótulo esquerdo truncado no PDF ("Disc…"), rótulo
direito "Concordo totalmente".

| Nº | Pergunta | Tipo | Obr. | Opções | Condicional | Origem provável |
|----|----------|------|------|--------|-------------|-----------------|
| Q20 | Indique o seu grau de concordância com a afirmação "Após o curso no Ifes, meu gosto por cultura, em geral, aumentou." | Escala 1–5 | Sim | — | — | Dc |
| Q21 | Indique o seu grau de concordância com a afirmação "Após o curso no Ifes, meu acesso à cultura, em geral, aumentou." | Escala 1–5 | Sim | — | — | Dc |
| Q22 | Você participou de ações de extensão durante o curso? | Lista suspensa | Sim | Sim; Não | — | I? (ver O-11) |
| Q23 | Você foi monitor(a) de disciplinas durante o curso? | Lista suspensa | Sim | Sim; Não | — | I? |
| Q24 | Você fez algum tipo de estágio durante o curso? | Lista suspensa | Sim | Sim; Não | — | I? |
| Q25 | Você participou de atividades acadêmicas (seminários, feiras, jornadas, etc) durante o curso? | Lista suspensa | Sim | Sim; Não | — | Dc |
| Q26 | Que tipo de publicação você realizou durante o curso? | Caixas de seleção | Sim | Artigos técnico científicos; Anais de Congresso; Livro; Capítulos de livro; Não houve; Outro: (texto) | — | Dc |
| Q27 | Você fez intercâmbio no exterior durante o curso? | Lista suspensa | Sim | Sim; Não | — | I? |
| Q28 | Durante o curso, você participou das atividades de grupos de pesquisas e de estudos? | Lista suspensa | Sim | Sim; Não | — | Dc |
| Q29 | Você mantém algum vínculo com o curso, como participação em grupos de pesquisa ou de estudos? | Lista suspensa | Sim | Sim; Não | — | Dc (situação atual) |
| Q30 | Você foi membro de empresa júnior durante o curso no Ifes? | Lista suspensa | Sim | Sim; Não | — | Dc |
| Q31 | Você participou de iniciação científica? | Lista suspensa | Sim | Sim; Não | — | I? |
| Q32 | Você recebeu algum tipo de bolsa? *(descrição: "Obs: Não considerar auxilio estudantil como bolsa.")* | Caixas de seleção | Sim | Ensino; Pesquisa; Extensão; Não recebi; Outro: (texto) | — | I? |
| Q33 | Atualmente você trabalha? | Múltipla escolha | Sim | Sim; Não | "Sim" → Q34; "Não" → Q45 | Dc |

### Seção 9 — Egresso que trabalha

| Nº | Pergunta | Tipo | Obr. | Opções | Condicional | Origem provável |
|----|----------|------|------|--------|-------------|-----------------|
| Q34 | Você trabalha no setor: | Lista suspensa | Sim | Misto; Público; Privado; Terceiro setor (cooperativas/sindicatos); Trabalho em mais de um setor | — | Dc |
| Q35 | O seu cargo/emprego exige como requisito o seguinte nível de escolaridade: | Lista suspensa | Sim | Nenhum nível de instrução; Ensino fundamental; Ensino médio/técnico; Graduação; Pós-graduação; Não sei dizer | — | Dc |
| Q36 | Indique o seu grau de concordância com a afirmação "O meu trabalho atual é na minha área de formação do curso do Ifes." | Escala 1–5 | Sim | — | — | Dc |
| Q37 | Você exerce cargo de chefia ou de direção atualmente? | Lista suspensa | Sim | Sim; Não | — | Dc |
| Q38 | Qual é a remuneração bruta mensal do seu trabalho? | Lista suspensa | Sim | Até 1 salário mínimo; De 1 até 2,5 salários mínimos; De 2,5 até 5,5 salários mínimos; De 5,5 até 10 salários mínimos; Acima de 10 salários mínimos | — | Dc (ver O-18, O-19) |
| Q39 | A organização na qual você trabalha é: | Lista suspensa | Sim | Micro empresa/organização (até 19 colaboradores); Pequena empresa/organização (de 20 a 99 colaboradores); Média empresa/organização (de 100 a 499 colaboradores); Grande empresa/organização (acima de 500 colaboradores); Não sei dizer | — | Dc (ver O-18) |
| Q40 | Você trabalha atualmente: | Lista suspensa | Sim | Na mesma cidade do campus do Ifes onde fiz o curso; Em outra cidade, mas na mesma região do campus do Ifes onde fiz o curso; Em outra cidade e em outra região do campus do Ifes onde fiz o curso, mas ainda no estado do Espírito Santo; Em outro estado brasileiro; Em outro país | — | Dc (relativo ao campus da Conclusão; ver O-20) |
| Q41 | Como você avalia a oferta de vagas aos profissionais da sua área de formação no Ifes? *(descrição: "Verificar lugar dessa pergunta")* | Lista suspensa | Sim | Não existem vagas de trabalho; Existem poucas vagas de trabalho; Existem muitas vagas de trabalho; Não sei dizer | — | Dc (ver O-3) |
| Q42 | Indique o seu grau de concordância com a afirmação "A realização de curso no Ifes foi indispensável para que eu conseguisse o meu trabalho atual. Sem ele, eu não teria o emprego que tenho hoje." | Escala 1–5 | Não | — | — | Dc (ver O-10) |
| Q43 | Indique o seu grau de concordância com a afirmação "A minha experiência profissional anterior foi indispensável para que eu conseguisse o meu trabalho atual." | Escala 1–5 | Sim | — | — | Dc |
| Q44 | Indique o seu grau de concordância com a afirmação "Eu usei as minhas redes de contato do Ifes para conseguir o meu trabalho atual." | Escala 1–5 | Não | — | — | Dc (ver O-10) |

Ao final da seção: → Q46.

### Seção 10 — Egresso que não trabalha

| Nº | Pergunta | Tipo | Obr. | Opções | Condicional | Origem provável |
|----|----------|------|------|--------|-------------|-----------------|
| Q45 | Você não está trabalhando por qual motivo: | Múltipla escolha | Sim | Não encontrei vaga de trabalho, mas estou à procura; Não estou à procura de vaga de trabalho no momento; Outro: (texto) | — | Dc |

Ao final da seção: → Q46.

### Seção 11 — Estudo

| Nº | Pergunta | Tipo | Obr. | Opções | Condicional | Origem provável |
|----|----------|------|------|--------|-------------|-----------------|
| Q46 | Atualmente você estuda? | Múltipla escolha | Sim | Sim; Não | "Sim" → Q49; "Não" → Q52 (aplicado ao sair da seção) | Dc |
| Q47 | Após o curso, você: | Caixas de seleção | Sim | Não estudei mais; Fiz cursos livres; Fiz curso técnico; Fiz curso de graduação; Fiz especialização lato sensu; Fiz mestrado; Fiz doutorado; Fiz pós-doutorado | Exibida a todos que chegam à seção (ver O-15) | Dc; parte pode ser I? se a formação posterior foi no Ifes |
| Q48 | Indique o seu grau de concordância com a afirmação "O curso que realizei, citado acima, estava totalmente relacionado à área do meu curso do Ifes." *(descrição: "Caso não tenha estudado mais deixe essa resposta em branco.")* | Escala 1–5 (rótulos "disc…" / "concordo totalmente") | Não | — | Condição apenas textual (ver O-15) | Dc |

### Seção 12 — Egresso que estuda

| Nº | Pergunta | Tipo | Obr. | Opções | Condicional | Origem provável |
|----|----------|------|------|--------|-------------|-----------------|
| Q49 | Em qual categoria de estudante você se enquadra atualmente? | Lista suspensa | Sim | Sou estudante de curso técnico; Sou estudante de curso de graduação; Sou estudante de curso de especialização lato sensu; Sou estudante de mestrado; Sou estudante de doutorado; Sou estudante de pós-doutorado | — | Dc; I? se o curso atual for no Ifes |
| Q50 | Indique o seu grau de concordância com a afirmação "O curso que estou realizando está totalmente relacionado à área do meu curso do Ifes." | Escala 1–5 | Sim | — | — | Dc |
| Q51 | A instituição na qual você está cursando é: | Múltipla escolha | Sim | Ifes; Outra Instituição Pública; Instituição Privada | "Instituição Privada" → Q52; demais → Q52 pelo padrão da seção (ver O-16) | Dc; I? se "Ifes" |

### Seção 13 — (sem título visível)

Escalas: 1 a 5, rótulo esquerdo truncado ("Disc…"), rótulo direito **"Corcordo
totalmente"** (grafia do original; ver O-4).

| Nº | Pergunta | Tipo | Obr. | Opções | Condicional | Origem provável |
|----|----------|------|------|--------|-------------|-----------------|
| Q52 | Indique o seu grau de concordância com a afirmação "O meu curso no Ifes mudou a minha vida para melhor. Hoje, eu me considero uma pessoa diferente de quem eu era antes do Ifes." | Escala 1–5 | Sim | — | — | Dc |
| Q53 | Indique o seu grau de concordância com a afirmação "A situação econômica da minha família melhorou após eu ter concluído o curso no Ifes." | Escala 1–5 | Sim | — | — | Dc |
| Q54 | Indique o seu grau de concordância com a afirmação "Eu acredito que sou exemplo e inspiração para outras pessoas (amigos, colegas, familiares) se espelharem e ampliarem seus horizontes de estudos e profissionais." | Escala 1–5 | Sim | — | — | Dc |

### Seção 14 — Encerramento

> Este formulário chegou ao fim!
>
> Agradecemos imensamente a atenção dispensada e a participação na pesquisa.

## Síntese por origem provável (hipótese)

| Origem provável | Perguntas | Implicação sob a Constituição |
|-----------------|-----------|-------------------------------|
| **Institucional** (dados da Conclusão Acadêmica) | Q10, Q11, Q12, Q13, Q14, Q15, Q16, Q17, Q18, Q19 | Principais candidatas a sair da jornada e ser apresentadas como contexto (Princípios III e XIV). Exige fonte acadêmica com qualidade suficiente e tratamento explícito de divergências. |
| **Derivável** | Q3 (idade) | Calculável se a data de nascimento vier da fonte institucional; o momento do cálculo precisa ficar registrado. |
| **A investigar** (candidato a institucional) | Q22, Q23, Q24, Q27, Q31, Q32; parte de Q47, Q49 e Q51 | Depende de existirem registros institucionais confiáveis (extensão, monitoria, estágio, intercâmbio, IC, bolsas). Pode não haver fonte, ou ela pode ser incompleta. |
| **Declarada** | Q1, Q2, Q4–Q9, Q20, Q21, Q25, Q26, Q28–Q30, Q33–Q46, Q48, Q50, Q52–Q54 | Candidatas a permanecer na jornada. Q4 (raça/cor), Q5 e Q6 (deficiência) merecem tratamento reforçado; ver O-6. |

## Correspondência provável com os indicadores da PAEG (Art. 10, III)

Correspondência interpretativa, para orientar specs. Não define cálculo de indicador.

| Indicador (PAEG, Art. 10, III) | Perguntas relacionadas | Observação |
|--------------------------------|------------------------|------------|
| Empregabilidade | Q33, Q34, Q39, Q45 | — |
| Verticalização dos estudos | Q46, Q47, Q49, Q51 | — |
| Realização profissional | Q36, Q37, Q38, Q42, Q52 | — |
| Taxa de retenção no emprego | Nenhuma pergunta direta | Só é observável longitudinalmente, comparando Participações da mesma Conclusão Acadêmica (Princípio I). Pergunta nova seria oportunidade metodológica futura (Princípio XIII). |
| Retorno para a educação continuada | Q46, Q47, Q48, Q49, Q50, Q51 | — |

## Observações

Fatos observados no instrumento. Não são decisões.

**Identificação, consentimento e privacidade**

- **O-1 — Identificação do respondente.** O instrumento exibido não solicita
  explicitamente nome, CPF, e-mail ou matrícula. Não é possível concluir apenas pelo PDF
  se a aplicação atual identifica ou não o respondente por configuração do Google
  Formulários (coleta de e-mail, exigência de login); essa configuração não foi
  verificada. O modelo longitudinal (Princípio I) exigirá associação confiável entre
  Participação, Pessoa e Conclusão Acadêmica, o que deve ser analisado quanto a
  privacidade, transparência e eventual revisão do termo apresentado ao participante.
- **O-2 — Termo de consentimento.** O termo cita a Resolução CNS nº 466/2012 e afirma
  que o participante não será identificado em publicações, com uso das informações para
  gestão educacional e fins acadêmicos e científicos. O termo não promete anonimato da
  coleta; promete não identificação em publicações. A adequação do termo ao modelo
  longitudinal deve ser analisada (ver O-1). A base legal permanece `DECISÃO PENDENTE`
  (Princípios XVI e XVII). A promessa de não identificação em publicações restringe
  exportações destinadas a publicação.
- **O-6 — Dados pessoais e potencialmente sensíveis.** Q4 (raça/cor), Q5 e Q6
  (deficiência) merecem tratamento reforçado. A classificação jurídica de cada item,
  incluindo Q2 (sexo/identidade de gênero), não é feita neste inventário e depende de
  decisão institucional (`DECISÃO PENDENTE`, Princípio XVI). Registros institucionais
  equivalentes podem existir como autodeclaração feita no ingresso; um registro obtido
  em determinado momento não equivale a uma declaração atual. Origem e contexto temporal
  devem ser preservados, e um não substitui o outro sem decisão explícita (Princípios III
  e IV).
- **O-7 — Assimetria de "prefiro não responder".** Q2 oferece "Prefiro não responder";
  Q4, Q5 e Q7 não oferecem, e são obrigatórias.

**Notas editoriais e grafia**

- **O-3 — Notas internas de edição visíveis.** A descrição da seção 7 diz "Tem que
  atualizar a lista de cursos, adicionando doutorado", e a descrição de Q41 diz
  "Verificar lugar dessa pergunta". São anotações de edição do próprio instrumento, não
  conteúdo dirigido ao egresso.
- **O-4 — Grafia.** O rótulo direito das escalas Q52–Q54 é "Corcordo totalmente". Q48
  usa rótulos em minúsculas ("disc…" / "concordo totalmente"). O rótulo esquerdo de todas
  as escalas aparece truncado no PDF como "Disc…"; o texto completo não é legível na
  fonte. Corrigir a grafia não muda o sentido. Se essa correção exige nova Versão
  (imutabilidade textual) ou pode ser registrada como correção editorial (imutabilidade
  semântica) é política de versionamento ainda não decidida; a Constituição exige nova
  Versão apenas para mudanças que alterem significado (Princípio VIII).
- **O-5 — Nota de doutorado já contemplada em parte.** A seção 7 pede para acrescentar
  doutorado, mas a Lista 19 já contém "Doutorado em Educação em Ciências e Matemática".

**Obrigatoriedade e condicionais**

- **O-8 — Q6 sem condicional técnica.** "Se sim, qual a deficiência?" é exibida a todos,
  é opcional, admite uma única opção e não tem "Outra".
- **O-10 — Obrigatoriedade irregular na seção 9.** Q42 e Q44 não são obrigatórias; Q43,
  vizinha e do mesmo formato, é.
- **O-15 — Condicionais por seção.** Q47 e Q48 estão na mesma seção de Q46 e são
  exibidas a todos que chegam à seção 11, inclusive a quem estuda atualmente. A condição
  de Q48 é só textual ("deixe em branco").
- **O-16 — Ramificação sem efeito prático.** Em Q51, "Instituição Privada" leva a Q52,
  mesmo destino do padrão da seção. A ramificação não altera o fluxo.
- **O-17 — Recusa do termo.** Q1 = "Não" leva à seção final. Pelo funcionamento do
  Google Formulários, isso provavelmente gera, se enviado, um registro contendo apenas
  Q1. Confirmar na planilha de respostas.

**Contexto acadêmico**

- **O-11 — Possível dado institucional perguntado ao egresso.** Extensão, monitoria,
  estágio, intercâmbio, iniciação científica e bolsas (Q22–Q24, Q27, Q31, Q32) podem
  existir em registros institucionais. A existência e a qualidade dessas fontes não
  foram verificadas.
- **O-12 — Q13 mistura dimensões.** As opções combinam reserva de vagas (cotista / ampla
  concorrência) com formas de ingresso (transferência, reopção, reingresso etc.).
- **O-13 — "Questionário" = nível.** Q14 pede o "questionário que pretende preencher",
  mas a escolha só muda a lista de cursos (seções 4–7). Da seção 8 em diante o conteúdo
  é igual para todos os níveis.
- **O-14 — Listas de cursos estáticas e com modalidade embutida.** As listas 15, 17, 18
  e 19 são mantidas à mão no formulário. Algumas opções carregam a modalidade no rótulo
  ("EaD - …"), sobrepondo-se a Q12. Q15 inclui "Fiz apenas o Ensino Médio", o que indica
  conclusão sem habilitação técnica no ramo Integrado.
- **O-9 — Uma formação por resposta.** O formulário não prevê que a mesma Pessoa informe
  mais de uma Conclusão Acadêmica numa mesma resposta. Isso é coerente com a relação
  Participação → uma Conclusão (Princípio I), mas a escolha de qual formação responder
  hoje fica com o próprio egresso.
- **O-20 — Referência ao campus em Q40.** As opções usam a cidade e a região do campus
  onde o curso foi feito. Para cursos a distância (por exemplo, Cefor), a referência é
  ambígua.

**Comparabilidade**

- **O-18 — Limites de faixas.** Em Q38, o valor de 1 salário mínimo pertence a duas
  faixas ("Até 1" e "De 1 até 2,5"), e o mesmo ocorre com 2,5, 5,5 e 10. Em Q39, a faixa
  média termina em 499 e a grande começa "acima de 500", deixando 500 sem faixa.
- **O-19 — Renda em salários mínimos.** Comparar Q38 entre Participações de anos
  diferentes depende do salário mínimo vigente em cada momento. O momento da
  Participação precisa ser preservado (Princípio VIII).

## Pontos para a spec de migração do instrumento

Itens que a primeira spec de migração precisa endereçar explicitamente, conforme a
Constituição, sem os decidir aqui:

1. Associação confiável entre Participação, Pessoa e Conclusão Acadêmica, com análise
   de privacidade, transparência e eventual revisão do termo (O-1, O-2).
2. Quais perguntas da seção 3 e das seções 4–7 saem da jornada e viram contexto
   apresentado, e como divergências são tratadas (Princípios III e XIV).
3. Se e como o candidato a institucional (O-11) será usado, dada a qualidade das fontes.
4. Tratamento reforçado de dados potencialmente sensíveis e preservação da origem e do
   momento de cada informação (O-6).
5. Classificação de cada condicional e peculiaridade (O-8, O-10, O-15, O-16) como
   **intenção do instrumento** ou **limitação/acidente da implementação atual**,
   preservando a intenção e documentando as correções.
6. **Decisão futura de migração de legado** (fora do escopo inicial): respostas
   históricas do Google Formulários, se importadas, podem permanecer como legado analítico
   com vínculo acadêmico desconhecido ou parcial, sem serem apresentadas como
   Participações longitudinais identificadas.
7. Tratamento das notas editoriais (O-3, O-5) e das correções de grafia (O-4) como
   decisão explícita, não como ajuste silencioso, conforme a política de versionamento
   que vier a ser definida.
