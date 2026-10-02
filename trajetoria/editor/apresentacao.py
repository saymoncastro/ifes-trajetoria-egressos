"""Apresentação do instrumento ao operador (research R9; FR-032, FR-049, FR-060, FR-070).

Funções puras sobre `ConteudoVersao` (002): rótulos por **ordinal** (a ordem, não o valor de
`posicao`, que tem lacunas depois de remoções), tipos, escala e destinos em palavras. Nenhum
identificador técnico vai para o texto: UUIDs só aparecem em endereços.
"""

from dataclasses import dataclass
from uuid import UUID

from trajetoria.instrumento.conteudo import ConteudoOpcao, ConteudoSecao, ConteudoVersao, Escala
from trajetoria.instrumento.models import TipoPergunta

LIMITE_DO_TEXTO = 80

# Tipos que têm Opções (002 FR-040): única definição usada por rotas, páginas e resumos.
TIPOS_DE_ESCOLHA = (TipoPergunta.ESCOLHA_UNICA, TipoPergunta.ESCOLHA_MULTIPLA)

TIPOS = {
    TipoPergunta.ESCOLHA_UNICA: ("Escolha única", "o respondente marca uma Opção"),
    TipoPergunta.ESCOLHA_MULTIPLA: (
        "Escolha múltipla",
        "o respondente marca nenhuma, uma ou várias Opções",
    ),
    TipoPergunta.TEXTO_CURTO: ("Texto curto", "o respondente escreve um texto simples"),
    TipoPergunta.ESCALA: ("Escala", "o respondente marca um ponto de um intervalo numérico"),
}


@dataclass(frozen=True)
class Localizacao:
    rotulo: str
    endereco: str


def ordinais(conteudo: ConteudoVersao) -> dict[UUID, int]:
    """Ordinal de cada Seção na Versão, de cada Pergunta na sua Seção e de cada Opção na sua
    Pergunta (1-based, na ordem das posições)."""
    resultado = {}
    for i, secao in enumerate(conteudo.secoes, 1):
        resultado[secao.id] = i
        for j, pergunta in enumerate(secao.perguntas, 1):
            resultado[pergunta.id] = j
            for k, opcao in enumerate(pergunta.opcoes, 1):
                resultado[opcao.id] = k
    return resultado


def _resumo(texto: str) -> str:
    return texto if len(texto) <= LIMITE_DO_TEXTO else texto[: LIMITE_DO_TEXTO - 1] + "…"


def rotulo_secao(ordinal: int, secao) -> str:
    return f"Seção {ordinal} — {secao.titulo}" if secao.titulo else f"Seção {ordinal} (sem título)"


def rotulo_pergunta(ordinal_secao: int, ordinal: int, pergunta) -> str:
    return f"Pergunta {ordinal} da Seção {ordinal_secao}: {_resumo(pergunta.texto)}"


def rotulo_opcao(ordinal_secao: int, ordinal_pergunta: int, opcao) -> str:
    return f"Opção «{opcao.texto}» da Pergunta {ordinal_pergunta} da Seção {ordinal_secao}"


def descrever_escala(escala: Escala) -> str:
    pontos = escala.fim - escala.inicio + 1
    extremos = "; ".join(
        f"{ponto} = «{rotulo}»" if rotulo else f"{ponto} sem rótulo"
        for ponto, rotulo in (
            (escala.inicio, escala.rotulo_inicio),
            (escala.fim, escala.rotulo_fim),
        )
    )
    texto = f"De {escala.inicio} a {escala.fim} ({pontos} pontos). {extremos}."
    if pontos > 2:
        texto += " Pontos intermediários aparecem só com o número."
    return texto


def nome_da_secao(conteudo: ConteudoVersao, secao_id: UUID) -> str:
    for i, secao in enumerate(conteudo.secoes, 1):
        if secao.id == secao_id:
            return rotulo_secao(i, secao)
    return "uma Seção fora desta Versão"


def destino_da_secao(conteudo: ConteudoVersao, secao: ConteudoSecao) -> str:
    """O que vem depois da Seção quando nenhum desvio é acionado (002 FR-048, FR-049)."""
    if secao.encaminhamento_id is not None:
        return f"segue para a {nome_da_secao(conteudo, secao.encaminhamento_id)}"
    indice = conteudo.secoes.index(secao)
    if indice + 1 < len(conteudo.secoes):
        return f"segue a ordem ({rotulo_secao(indice + 2, conteudo.secoes[indice + 1])})"
    return "finaliza o instrumento"


def destino_da_opcao(conteudo: ConteudoVersao, opcao: ConteudoOpcao) -> str | None:
    """O desvio da Opção, ou `None` sem desvio (002 FR-050)."""
    if opcao.regra is None:
        return None
    if opcao.regra.finaliza:
        return "finaliza o instrumento"
    return f"segue para a {nome_da_secao(conteudo, opcao.regra.destino_secao_id)}"


def anotacao_previa(conteudo: ConteudoVersao, opcao: ConteudoOpcao) -> str | None:
    """Informação estrutural da pré-visualização — nunca simulação (FR-088)."""
    if opcao.regra is None:
        return None
    inicio = f"Se «{opcao.texto}» for escolhida na aplicação real,"
    if opcao.regra.finaliza:
        return f"{inicio} o instrumento é finalizado."
    destino = nome_da_secao(conteudo, opcao.regra.destino_secao_id)
    return f"{inicio} a próxima seção será: {destino}."


def localizador(conteudo: ConteudoVersao) -> dict[UUID, Localizacao]:
    """Rótulo e página de correção de cada elemento da Versão (FR-070)."""
    local = {
        conteudo.id: Localizacao(
            f"a Versão «{conteudo.designacao}»", f"/editor/versoes/{conteudo.id}/"
        )
    }
    for i, secao in enumerate(conteudo.secoes, 1):
        local[secao.id] = Localizacao(rotulo_secao(i, secao), f"/editor/secoes/{secao.id}/")
        for j, pergunta in enumerate(secao.perguntas, 1):
            local[pergunta.id] = Localizacao(
                rotulo_pergunta(i, j, pergunta), f"/editor/perguntas/{pergunta.id}/"
            )
            for opcao in pergunta.opcoes:
                local[opcao.id] = Localizacao(
                    rotulo_opcao(i, j, opcao), f"/editor/opcoes/{opcao.id}/"
                )
    return local


def referencias_a(conteudo: ConteudoVersao, secao_id: UUID) -> list[str]:
    """Encaminhamentos e desvios que apontam para a Seção (002 FR-061; FR-029)."""
    referencias = []
    for i, secao in enumerate(conteudo.secoes, 1):
        if secao.encaminhamento_id == secao_id and secao.id != secao_id:
            referencias.append(f"o encaminhamento da {rotulo_secao(i, secao)}")
        for j, pergunta in enumerate(secao.perguntas, 1):
            for opcao in pergunta.opcoes:
                if opcao.regra and opcao.regra.destino_secao_id == secao_id:
                    referencias.append(f"a {rotulo_opcao(i, j, opcao)}")
    return referencias


def plural(n: int, singular: str, plural_: str, nenhum: str) -> str:
    return nenhum if n == 0 else (f"1 {singular}" if n == 1 else f"{n} {plural_}")


def resumo_da_pergunta(pergunta) -> str:
    """Opções ou intervalo, em palavras, para a estrutura (sem listar as Opções)."""
    if pergunta.tipo == TipoPergunta.ESCALA:
        return f"De {pergunta.escala.inicio} a {pergunta.escala.fim}"
    if pergunta.tipo in TIPOS_DE_ESCOLHA:
        return plural(len(pergunta.opcoes), "Opção", "Opções", "nenhuma Opção")
    return ""


def estrutura(conteudo: ConteudoVersao) -> list[dict]:
    """A visão de leitura da Versão (US5; FR-065): Seções na ordem e Perguntas resumidas."""
    secoes = []
    for i, secao in enumerate(conteudo.secoes, 1):
        perguntas = [
            {
                "id": pergunta.id,
                "endereco": f"/editor/perguntas/{pergunta.id}/",
                "ordinal": j,
                "rotulo": rotulo_pergunta(i, j, pergunta),
                "texto": pergunta.texto,
                "tipo": TIPOS[pergunta.tipo][0],
                "obrigatoriedade": "Obrigatória" if pergunta.obrigatoria else "Opcional",
                "resumo": resumo_da_pergunta(pergunta),
                "tem_desvio": any(o.regra for o in pergunta.opcoes),
                "opcoes_ids": [o.id for o in pergunta.opcoes],
                "desvios": [
                    f"«{o.texto}» → {destino_da_opcao(conteudo, o)}"
                    for o in pergunta.opcoes
                    if o.regra
                ],
            }
            for j, pergunta in enumerate(secao.perguntas, 1)
        ]
        secoes.append(
            {
                "id": secao.id,
                "endereco": f"/editor/secoes/{secao.id}/",
                "ordinal": i,
                "rotulo": rotulo_secao(i, secao),
                "quantidade": plural(len(perguntas), "Pergunta", "Perguntas", "nenhuma Pergunta"),
                "destino": destino_da_secao(conteudo, secao),
                "perguntas": perguntas,
            }
        )
    return secoes


def pergunta_apresentada(conteudo: ConteudoVersao, pergunta_id: UUID) -> dict:
    """A página de consulta da Pergunta: dados, tipo, escala explicada e Opções."""
    for i, secao in enumerate(conteudo.secoes, 1):
        for j, pergunta in enumerate(secao.perguntas, 1):
            if pergunta.id != pergunta_id:
                continue
            nome, descricao = TIPOS[pergunta.tipo]
            return {
                "rotulo": f"Pergunta {j} da Seção {i}",
                "rotulo_completo": rotulo_pergunta(i, j, pergunta),
                "secao": {
                    "rotulo": rotulo_secao(i, secao),
                    "endereco": f"/editor/secoes/{secao.id}/",
                },
                "texto": pergunta.texto,
                "texto_explicativo": pergunta.texto_explicativo,
                "tipo": nome,
                "descricao_tipo": descricao,
                "de_escolha": pergunta.tipo in TIPOS_DE_ESCOLHA,
                "admite_desvio": pergunta.tipo == TipoPergunta.ESCOLHA_UNICA,
                "obrigatoriedade": "Obrigatória" if pergunta.obrigatoria else "Opcional",
                "escala": descrever_escala(pergunta.escala) if pergunta.escala else None,
                "opcoes": [
                    {
                        "id": opcao.id,
                        "endereco": f"/editor/opcoes/{opcao.id}/",
                        "ordinal": k,
                        "rotulo": rotulo_opcao(i, j, opcao),
                        "texto": opcao.texto,
                        "complemento": opcao.complemento_textual,
                        "desvio": destino_da_opcao(conteudo, opcao),
                    }
                    for k, opcao in enumerate(pergunta.opcoes, 1)
                ],
            }
    raise KeyError(pergunta_id)
