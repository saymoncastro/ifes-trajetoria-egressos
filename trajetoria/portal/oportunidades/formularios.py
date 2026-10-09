"""Formulário da curadoria (025 contracts/curadoria.md; T033).

Só converte a entrada para os argumentos de `operacoes` (padrão de `trajetoria/editor/
formularios.py`): quem valida o domínio e grava é a operação. As opções de unidade e de
público vêm do escopo e dos valores registrados nas Conclusões (research R8): um valor fora
delas, mesmo num POST forjado, é recusado aqui e nada é gravado.
"""

from django import forms

from trajetoria.editor.formularios import Formulario
from trajetoria.portal.models import RESUMO_MAXIMO, TITULO_MAXIMO, Categoria
from trajetoria.portal.oportunidades import mensagens as m
from trajetoria.portal.oportunidades.consultas import opcoes_de_publico, unidades_responsaveis

_DATA = {"type": "date"}


def _data(rotulo):
    return forms.DateField(
        label=rotulo,
        input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(format="%Y-%m-%d", attrs=_DATA),
        error_messages={"required": m.ERROS["data"], "invalid": m.ERROS["data"]},
    )


def _publico(rotulo):
    return forms.MultipleChoiceField(
        label=rotulo,
        required=False,
        widget=forms.CheckboxSelectMultiple,
        error_messages={"invalid_choice": m.ERROS["publico"]},
    )


class OportunidadeForm(Formulario):
    titulo = forms.CharField(
        label="Título", required=False, strip=False,
        widget=forms.TextInput(attrs={"maxlength": TITULO_MAXIMO}),
    )
    resumo = forms.CharField(
        label="Resumo", required=False, strip=False,
        widget=forms.Textarea(attrs={"rows": 4, "maxlength": RESUMO_MAXIMO}),
    )
    categoria = forms.ChoiceField(
        label="Categoria", required=False, choices=Categoria.choices, widget=forms.RadioSelect,
        error_messages={"invalid_choice": m.ERROS["categoria"]},
    )
    unidade_responsavel = forms.ChoiceField(
        label="Unidade responsável", required=False,
        error_messages={"invalid_choice": m.ERROS["unidade_responsavel"]},
    )
    endereco = forms.CharField(
        label="Endereço oficial (página da oportunidade)", required=False, strip=False,
        widget=forms.URLInput(attrs={"inputmode": "url"}),
    )
    inicio = _data("Início da divulgação")
    fim = _data("Fim da divulgação")
    publico_unidades = _publico("Público: unidades")
    publico_niveis = _publico("Público: níveis")
    publico_cursos = _publico("Público: cursos")

    def __init__(self, escopo, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["unidade_responsavel"].choices = [
            (u, u or m.IFES_INSTITUCIONAL) for u in unidades_responsaveis(escopo)
        ]
        for campo, valores in opcoes_de_publico().items():
            self.fields[campo].choices = [(v, v) for v in valores]

    def dados(self) -> dict:
        """Argumentos para `operacoes.cadastrar` e `operacoes.editar`."""
        return dict(self.cleaned_data)
