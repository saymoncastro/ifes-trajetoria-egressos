"""Nenhum dado individual (Feature 011; spec FR-080 a FR-084; SC-005).

As páginas recebem só objetos de valor e a Campanha. A única UUID é a da Campanha (e, para
quem pode consultá-la, a da Versão no link do editor)."""

import re

import pytest

from tests.acompanhamento import construcao as k
from tests.acompanhamento.conftest import TEXTO_DECLARADO
from trajetoria.academico.models import ConclusaoAcademica, Pessoa
from trajetoria.participacao.models import Participacao, Resposta

RECORTES = ("unidade", "curso", "nivel", "modalidade", "forma-oferta", "ano-conclusao")
UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
INDIVIDUAIS = (Pessoa, ConclusaoAcademica, Participacao, Resposta)


def _paginas(cliente, ref):
    paginas = [cliente.get("/acompanhamento/")]
    for campanha in (ref.I, ref.R, ref.P, ref.E):
        paginas += [k.detalhe(cliente, campanha, r) for r in RECORTES]
    return [p for p in paginas if p.status_code in (200, 403)]


def _valores_do_contexto(contexto):
    for camada in contexto:
        for valor in camada.values() if hasattr(camada, "values") else ():
            yield valor
            if isinstance(valor, list | tuple):
                for item in valor:
                    yield item
                    if isinstance(item, dict):
                        yield from item.values()


@pytest.mark.parametrize("perfil", ["cliente_cpaeg", "cliente_csaeg_vitoria", "cliente_duas_csaeg"])
def test_nenhum_dado_individual_no_html(ref, perfil, request):
    cliente = request.getfixturevalue(perfil)
    nomes = list(Pessoa.objects.values_list("nome", flat=True))
    externos = list(Pessoa.objects.values_list("id_externo", flat=True))
    externos += list(ConclusaoAcademica.objects.values_list("id_externo", flat=True))
    individuais = {str(pk) for m in (ConclusaoAcademica, Participacao, Pessoa)
                   for pk in m.objects.values_list("pk", flat=True)}  # fmt: skip
    permitidas = {str(c.pk) for c in (ref.I, ref.R, ref.P, ref.E)}
    permitidas |= {str(ref.inst.versao.pk), str(ref.P.versao.pk)}
    for resposta in _paginas(cliente, ref):
        html = resposta.content.decode()
        for texto in [*nomes, *externos, TEXTO_DECLARADO]:
            assert texto not in html, texto
        uuids = set(UUID.findall(html))
        assert not uuids & individuais
        assert uuids <= permitidas


def test_contexto_dos_templates_sem_instancias_individuais(ref, cliente_cpaeg):
    for resposta in _paginas(cliente_cpaeg, ref):
        for valor in _valores_do_contexto(resposta.context):
            assert not isinstance(valor, INDIVIDUAIS), type(valor)
