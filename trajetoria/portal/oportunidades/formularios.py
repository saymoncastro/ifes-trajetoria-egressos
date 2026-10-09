"""Formulário da curadoria (025 contracts/curadoria.md; T033).

Só converte a entrada para os argumentos de `operacoes` (padrão de `trajetoria/editor/
formularios.py`): quem valida o domínio e grava é a operação. As opções de unidade e de
público vêm do escopo e dos valores registrados nas Conclusões (research R8): um valor fora
delas, mesmo num POST forjado, é recusado aqui e nada é gravado.

Na edição, os valores já gravados também são opções, mesmo que tenham deixado de existir
nas Conclusões (DP-1005): aparecem marcados e identificados, e só saem se o operador os
desmarcar. Sem isso, editar o título apagaria um critério e alargaria o público em
silêncio (code review do PR #49).
"""

from django import forms

from trajetoria.editor.formularios import Formulario
from trajetoria.portal.models import RESUMO_MAXIMO, TITULO_MAXIMO, Categoria
from trajetoria.portal.oportunidades import mensagens as m
from trajetoria.portal.oportunidades.consultas import opcoes_de_publico, unidades_responsaveis

FORA_DO_REGISTRO = "{valor} (não está nas formações registradas hoje)"

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
    # Assinatura do conteúdo lido (edição): detecta mudança concorrente (operacoes.assinatura).
    versao = forms.CharField(required=False, widget=forms.HiddenInput)

    def __init__(self, escopo, *args, instancia=None, **kwargs):
        super().__init__(*args, **kwargs)
        opcoes = opcoes_de_publico()
        unidades = unidades_responsaveis(escopo, opcoes["publico_unidades"])
        if instancia is not None and instancia.unidade_responsavel not in unidades:
            unidades.append(instancia.unidade_responsavel)  # gravada e já fora do registro
        self.fields["unidade_responsavel"].choices = [
            (u, u or m.IFES_INSTITUCIONAL) for u in unidades
        ]
        for campo, valores in opcoes.items():
            gravados = (getattr(instancia, campo) or []) if instancia is not None else []
            antigos = [v for v in gravados if v not in valores]
            self.fields[campo].choices = [(v, v) for v in valores] + [
                (v, FORA_DO_REGISTRO.format(valor=v)) for v in antigos
            ]

    def dados(self) -> dict:
        """Argumentos de conteúdo para `operacoes.cadastrar` e `operacoes.editar`."""
        return {k: v for k, v in self.cleaned_data.items() if k != "versao"}

    def versao_lida(self) -> str | None:
        return self.cleaned_data.get("versao") or None
