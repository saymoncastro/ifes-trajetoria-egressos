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
    resposta = client.post("/demonstracao/escolher/", {"pessoa": str(pessoa.pk)})
    assert resposta.status_code == 302, resposta.status_code


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
