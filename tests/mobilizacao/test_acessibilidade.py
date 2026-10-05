"""Telas de Lote e "Meu e-mail" acessíveis, sem JavaScript (020 FR-045; T054)."""

import re

import pytest

from tests.editor.construcao_editor import A
from trajetoria.mobilizacao.operacoes import confirmar_lote

pytestmark = pytest.mark.django_db


def _paginas(ampla, cliente):
    lote = confirmar_lote(ampla.pk, A, "Vitória", {"unidades": ["Vitória"]})
    base = f"/acompanhamento/campanhas/{ampla.pk}/lotes/"
    return [
        cliente.get(base),
        cliente.get(base + "?previa=1"),
        cliente.get(base + "?previa=1&unidade=Serra"),
        cliente.get(f"{base}{lote.pk}/"),
        cliente.post(f"{base}{lote.pk}/enviar/"),
        cliente.post(base + "confirmar/", {"nome": "", "unidade": "Serra"}),
    ]


def test_estrutura(ampla, clientes):
    for resposta in _paginas(ampla, clientes[A]):
        html = resposta.content.decode()
        assert '<html lang="pt-BR">' in html and html.count("<h1>") == 1
        assert 'href="#conteudo"' in html and 'id="conteudo"' in html
        assert "<script" not in html.lower()
        for campo in re.findall(r'<input type="(?:text|number|checkbox)"[^>]*id="([^"]+)"', html):
            assert f'<label for="{campo}">' in html, campo
        for select in re.findall(r'<select[^>]*id="([^"]+)"', html):
            assert f'<label for="{select}">' in html


def test_formularios_e_avisos(ampla, clientes):
    paginas = _paginas(ampla, clientes[A])
    lista = paginas[2].content.decode()
    assert lista.count("<fieldset>") == 2 and lista.count("<legend>") == 2
    assert 'role="status"' in lista  # prévia
    assert "<caption>" in paginas[0].content.decode()
    assert 'role="alert"' in paginas[5].content.decode()  # nome inválido: texto, não só cor
    assert 'role="status"' in paginas[4].content.decode()  # resultado do envio
