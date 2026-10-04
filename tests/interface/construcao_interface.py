"""Auxiliares dos testes da interface (Feature 008; não são testes).

Reutilizam `tests/participacao/construcao*.py` sem alterá-los. Pessoas vêm sempre da
**fonte simulada**, a única aceita pela entrada de demonstração. O mapeamento "Qn → Pergunta"
existe só aqui, nos testes; a interface não o conhece. Somente dados fictícios.
"""

import re
from dataclasses import dataclass
from datetime import datetime
from html.parser import HTMLParser
from urllib.parse import urlsplit
from uuid import UUID

from tests.participacao import construcao as c
from tests.participacao import construcao_entrada as ce
from trajetoria.academico.models import Pessoa
from trajetoria.fonte_academica.simulada import FonteSimulada
from trajetoria.instrumento.conteudo import ConteudoSecao, conteudo_da_versao
from trajetoria.instrumento.models import TipoPergunta

TEXTO_FICTICIO = "Resposta fictícia"

PADROES_TECNICOS = (
    re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.I),
    re.compile(r"SIM-[PC]-"),
    re.compile(r"\bsimulada\b"),
    re.compile(r"Demonstração — coleta"),
    re.compile(r"Traceback|Exception|ParticipacaoRejeitada|Http404"),
    re.compile(
        r"\b(COLETA_NAO_ADMITIDA|PARTICIPACAO_CONCLUIDA|OBRIGATORIA_PENDENTE|"
        r"ESTRUTURA_NAO_SUPORTADA|OPCAO_DE_OUTRA_PERGUNTA|VALOR_VAZIO|VALOR_INCOMPATIVEL|"
        r"ESCALA_FORA_DOS_LIMITES|COMPLEMENTO_NAO_ADMITIDO|PERGUNTA_DE_OUTRA_VERSAO)\b"
    ),
)


@dataclass
class Relogio:
    agora: datetime


@dataclass
class Cenario:
    base: c.Baseline
    campanha: object

    def pessoa(self, id_externo: str) -> Pessoa:
        return ce.pessoa_da_fonte(id_externo)


def cenario_baseline(*ids) -> Cenario:
    """Cópia publicada da baseline, uma Campanha aberta de população ampla e Pessoas da fonte
    simulada (por padrão, SIM-P-0001, SIM-P-0003, SIM-P-0010 e SIM-P-0011)."""
    base = c.baseline_publicada()
    campanha = c.campanha_aberta(base.versao)
    padrao = ("SIM-P-0001", "SIM-P-0003", "SIM-P-0010", "SIM-P-0011")
    ce.incorporar(FonteSimulada(), *(ids or padrao))
    return Cenario(base, campanha)


def entrar_como(client, pessoa) -> None:
    from django.utils import timezone

    from trajetoria.acesso.models import MaterialDeVerificacao
    from trajetoria.acesso.sessao import dados_de_sessao

    material = MaterialDeVerificacao.objects.filter(pessoa=pessoa).first()
    sessao = client.session
    sessao.update(
        dados_de_sessao(pessoa, material.atualizado_em if material else None, timezone.now())
    )
    sessao.save()
    from django.conf import settings

    client.cookies[settings.SESSION_COOKIE_NAME] = sessao.session_key


def iniciar(client, pessoa, formacao=None):
    """Escolhe a Pessoa e aciona "Iniciar/Continuar"; devolve a resposta do POST."""
    entrar_como(client, pessoa)
    dados = {} if formacao is None else {"formacao": str(formacao.pk)}
    return client.post("/formacoes/entrar/", dados)


def participacao_de(resposta):
    """`id` da Participação no `Location` de um redirecionamento."""
    return UUID(urlsplit(resposta["Location"]).path.split("/")[2])


def secao_do_conteudo(versao, posicao: int) -> ConteudoSecao:
    return next(s for s in conteudo_da_versao(versao).secoes if s.posicao == posicao)


def dados_validos(secao: ConteudoSecao, escolhas: dict | None = None) -> dict:
    """POST que responde todas as obrigatórias da Seção (e as Perguntas de `escolhas`):
    escolha única → Opção de `escolhas[id]` (texto) ou a primeira; múltipla → a primeira;
    texto → `TEXTO_FICTICIO`; escala → início."""
    escolhas = escolhas or {}
    dados = {}
    for p in secao.perguntas:
        if not (p.obrigatoria or p.id in escolhas):
            continue
        campo = f"p{p.posicao}"
        if p.tipo == TipoPergunta.ESCOLHA_UNICA:
            texto = escolhas.get(p.id)
            opcao = next(o for o in p.opcoes if o.texto == texto) if texto else p.opcoes[0]
            dados[campo] = str(opcao.posicao)
        elif p.tipo == TipoPergunta.ESCOLHA_MULTIPLA:
            dados[campo] = [str(p.opcoes[0].posicao)]
        elif p.tipo == TipoPergunta.TEXTO_CURTO:
            dados[campo] = TEXTO_FICTICIO
        else:
            dados[campo] = str(p.escala.inicio)
    return dados


def escolhas_por_id(base: c.Baseline, escolhas: dict[str, str]) -> dict:
    """{"Q14": "Graduação"} → {id da Pergunta: "Graduação"}."""
    return {base.q(int(k[1:])).id: v for k, v in escolhas.items()}


def posicao_da_url(url: str) -> int | None:
    m = re.search(r"/secoes/(\d+)/", url)
    return int(m.group(1)) if m else None


def percorrer_pela_interface(client, participacao_id, versao, escolhas: dict, limite=30):
    """Envia Seção a Seção, seguindo os redirecionamentos, até a tela de conclusão. Devolve
    as posições das Seções apresentadas e a última URL."""
    url = client.get(f"/participacoes/{participacao_id}/")["Location"]
    apresentadas = []
    for _ in range(limite):
        posicao = posicao_da_url(url)
        if posicao is None:
            return apresentadas, url
        assert "pendencias" not in url, url
        apresentadas.append(posicao)
        secao = secao_do_conteudo(versao, posicao)
        resposta = client.post(urlsplit(url).path, dados_validos(secao, escolhas))
        assert resposta.status_code == 302, (posicao, resposta.status_code)
        url = resposta["Location"]
    raise AssertionError("percurso não terminou")


class _Texto(HTMLParser):
    def __init__(self):
        super().__init__()
        self.partes = []
        self._ignorar = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("style", "script"):
            self._ignorar += 1

    def handle_endtag(self, tag):
        if tag in ("style", "script"):
            self._ignorar -= 1

    def handle_data(self, data):
        if not self._ignorar:
            self.partes.append(data)


def texto_visivel(resposta) -> str:
    """Texto do HTML sem marcação, estilo e atributos — o que a pessoa lê."""
    parser = _Texto()
    parser.feed(resposta.content.decode())
    return re.sub(r"\s+", " ", " ".join(parser.partes)).strip()


def tecnicos_em(texto: str) -> list[str]:
    return [m.group(0) for padrao in PADROES_TECNICOS for m in padrao.finditer(texto)]


# --- Leitura das folhas de estilo da página (015; sem navegador) ----------------------------
# A cascata é aproximada, suficiente para as folhas do projeto: regras de classe e de tag,
# combinador descendente (">" tratado como descendente), um nível de @media, `var()` pelos
# tokens do `:root`. Seletores com pseudo-classe, atributo, "+" ou "~" no último composto não
# casam com o alvo (são inspecionados diretamente por `regras`).


@dataclass(frozen=True)
class Regra:
    media: str  # prelúdio do @media, ou "" fora de @media
    seletor: str
    declaracoes: dict[str, str]


def folhas(html: str) -> str:
    """O CSS de todos os `<style>` da página, sem comentários."""
    blocos = re.findall(r"<style>(.*?)</style>", html, re.S)
    return re.sub(r"/\*.*?\*/", "", "\n".join(blocos), flags=re.S)


def _declaracoes(corpo: str) -> dict[str, str]:
    pares = (d.split(":", 1) for d in corpo.split(";") if ":" in d)
    return {nome.strip().lower(): valor.strip() for nome, valor in pares}


def _blocos(css: str, media: str = "") -> list[Regra]:
    saida, i = [], 0
    while True:
        abre = css.find("{", i)
        if abre == -1:
            return saida
        preludio = css[i:abre].strip()
        nivel, j = 1, abre + 1
        while nivel:
            nivel += {"{": 1, "}": -1}.get(css[j], 0)
            j += 1
        corpo = css[abre + 1 : j - 1]
        if preludio.startswith("@media"):
            saida += _blocos(corpo, preludio[len("@media") :].strip())
        else:
            for seletor in preludio.split(","):
                saida.append(Regra(media, " ".join(seletor.split()), _declaracoes(corpo)))
        i = j


def regras(html: str) -> list[Regra]:
    """As regras das folhas da página, na ordem do documento."""
    return _blocos(folhas(html))


def tokens(html: str) -> dict[str, str]:
    return {
        nome: valor
        for regra in regras(html)
        if regra.seletor == ":root"
        for nome, valor in regra.declaracoes.items()
        if nome.startswith("--")
    }


def resolver(valor: str, mapa: dict[str, str]) -> str:
    """Substitui `var(--x)` (e `var(--x, reserva)`) pelos valores dos tokens."""
    padrao = re.compile(r"var\(\s*(--[\w-]+)\s*(?:,\s*([^()]*))?\)")
    for _ in range(10):
        novo = padrao.sub(lambda m: mapa.get(m[1], m[2] or m[0]), valor)
        if novo == valor:
            return " ".join(valor.split())
        valor = novo
    return valor


_COMPOSTO = re.compile(r"^([a-z][\w-]*)?((?:\.[\w-]+)*)$")


def _casa(composto: str, tag: str, classes: set[str]) -> bool:
    m = _COMPOSTO.match(composto)
    if not m:
        return False
    proprias = set(re.findall(r"\.([\w-]+)", m[2] or ""))
    return bool((not m[1] or m[1] == tag) and proprias <= classes and (m[1] or proprias))


def _casa_ancestral(composto: str, ancestrais: set[str]) -> bool:
    """Ancestral por classes e tag (`ancestrais` mistura nomes de classes e de tags)."""
    m = _COMPOSTO.match(composto)
    if not m or not (m[1] or m[2]):
        return False
    return (not m[1] or m[1] in ancestrais) and set(
        re.findall(r"\.([\w-]+)", m[2] or "")
    ) <= ancestrais


def _especificidade(seletor: str) -> tuple[int, int]:
    partes = [p for p in seletor.replace(">", " ").split()]
    classes = sum(p.count(".") + p.count("[") + p.count(":") - 2 * p.count("::") for p in partes)
    tags = sum(1 for p in partes if re.match(r"^[a-z]", p))
    return classes, tags


def valor(
    html: str,
    ancestrais: set[str],
    classe: str = "",
    tag: str = "",
    propriedades: str | tuple[str, ...] = "color",
    media: str | None = None,
) -> str | None:
    """Valor efetivo (tokens resolvidos) de um elemento `tag.classe` (classes separadas por
    espaço) dentro de ancestrais com as classes/tags `ancestrais`.

    `propriedades`: um nome ou uma tupla de nomes concorrentes (ex.: um lado de borda e seus
    atalhos); vence a declaração de maior especificidade, depois a última. `media`: inclui
    também as regras de @media cujo prelúdio contém esse texto.
    """
    nomes = (propriedades,) if isinstance(propriedades, str) else propriedades
    classes = set(classe.split())
    melhor, chave = None, (-1, -1, -1)
    for ordem, regra in enumerate(regras(html)):
        if regra.media and (media is None or media not in regra.media):
            continue
        if "+" in regra.seletor or "~" in regra.seletor:
            continue
        *antes, ultimo = regra.seletor.replace(">", " ").split()
        if not _casa(ultimo, tag, classes):
            continue
        if not all(_casa_ancestral(parte, ancestrais) for parte in antes):
            continue
        for nome in nomes:
            if nome in regra.declaracoes:
                k = (*_especificidade(regra.seletor), ordem)
                if k >= chave:
                    melhor, chave = regra.declaracoes[nome], k
    return resolver(melhor, tokens(html)) if melhor is not None else None
