"""Conversão da entrada; as operações da Campanha validam o domínio."""

from django import forms

from trajetoria.editor.formularios import Formulario


class CampanhaForm(Formulario):
    nome = forms.CharField(label="Nome", required=False, strip=False)
    versao = forms.ChoiceField(
        label="Versão",
        error_messages={
            "required": "Escolha uma Versão.",
            "invalid_choice": "Escolha uma das Versões disponíveis.",
        },
    )
    inicio = forms.DateField(
        label="Início (opcional)",
        required=False,
        input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
        error_messages={"invalid": "Informe uma data válida."},
    )
    fim = forms.DateField(
        label="Fim (opcional)",
        required=False,
        input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
        error_messages={"invalid": "Informe uma data válida."},
    )

    def __init__(self, versoes, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["versao"].choices = [("", "Escolha…"), *versoes]
