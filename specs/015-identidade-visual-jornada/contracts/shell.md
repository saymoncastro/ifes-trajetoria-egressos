# Contrato: shell da jornada

Vale para toda página que estende `interface/base.html`: trajetória, Seções, conclusão,
confirmação, telas de estado (`aviso.html`), entrada e operador da demonstração. **Não**
vale para 403/404/500 (globais — research R5) nem para editor e acompanhamento (bases
próprias).

## Ordem no documento

1. "Pular para o conteúdo" (inalterado).
2. **Faixa de demonstração** (`role="note"`), cor `--cor-demonstracao`:
   - texto atual de ambiente fictício;
   - quando houver Pessoa de demonstração: "Pessoa fictícia: {nome}", "Trocar de pessoa"
     e o formulário "Encerrar demonstração" — **movidos do cabeçalho**, com textos,
     destinos e CSRF inalterados.
   - *(Revisado pela 018 e pela 019; registrado em 2026-10-05.)* Hoje o texto da faixa é
     "Ambiente de demonstração. Todos os dados são fictícios. A confirmação usa CPF e data
     de nascimento fictícios e não é autenticação forte." Com Pessoa confirmada, a faixa
     mostra "Pessoa fictícia: {nome}". Com Pessoa ou declarante da 019, mostra um único
     botão "Sair" (POST com CSRF para `/acesso/sair/`). "Trocar de pessoa" e "Encerrar
     demonstração" não existem mais. Fonte de verdade:
     `trajetoria/interface/templates/interface/base.html`.
3. **Cabeçalho do produto** (`<header>`):
   - borda superior 4 px `--cor-marca` (fio de marca);
   - assinatura oficial (SVG inline, `role="img"`, nome acessível "Instituto Federal do
     Espírito Santo"), primeira no cabeçalho;
   - separador vertical 1 px `--cor-borda-suave`;
   - "Trajetória Ifes" em texto, 18 px/700 (não é `h1`, não é ligação);
   - "Acompanhamento de egressos", 15 px, `--cor-texto-suave`, só a partir de `30em`;
   - borda inferior 1 px `--cor-borda-suave`; sem navegação.
4. `<main id="conteudo">` (inalterado).
5. **Rodapé**: borda superior 1 px `--cor-borda-suave`; "Instituto Federal do Espírito
   Santo" (15 px, `--cor-texto-suave`); em demonstração, a linha atual de ambiente
   fictício abaixo.

## Regras da assinatura (FR-017)

| Regra | Verificação |
|---|---|
| Marca sistêmica/Reitoria, de fonte oficial (`marca-ifes.zip`, research R3) | Origem registrada no registro de validação |
| Sem redesenho, recoloração, distorção, recorte, contorno, composição com o nome do produto | Comparação com o arquivo oficial |
| Símbolo ≥ 30 px | Medida no registro (375 e 1280 px) |
| Área de proteção ≥ 1 módulo livre | Medida no registro |
| Versão colorida sobre branco | Inspeção |
| Antes do nome do produto, subordinando-o | Ordem no documento e na tela |

## Limites (FR-016, FR-019)

| Medida | Limite | Condição |
|---|---|---|
| Altura do cabeçalho | ≤ 68 px a 375 px; ≤ 80 px a 1280 px | Fonte a 100%; faixa de demonstração fora da medida (gate, rodada 3: era 64 px) |
| Tamanho da assinatura | 63 px de altura (símbolo de 36 px) a partir de 22em (352 px); 54 px (símbolo de 31 px) abaixo disso | O nome do produto fica ao lado da assinatura com fonte a 100% |
| Altura do rodapé | ≤ 120 px a 375 px | Sem a linha de demonstração |
| Rolagem horizontal | 0 | 320 a 1280 px, fonte de 100% a 200% |
