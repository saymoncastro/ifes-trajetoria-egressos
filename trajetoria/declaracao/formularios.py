from django import forms
from django.utils import timezone

from trajetoria.declaracao.consultas import opcoes_de_nivel, opcoes_de_unidade


class FormacaoForm(forms.Form):
    nome = forms.CharField(label="Seu nome", max_length=200)
    unidade = forms.ChoiceField(label="Unidade do Ifes")
    nivel = forms.ChoiceField(label="Nível de ensino")
    curso = forms.CharField(label="Curso", max_length=300, strip=False)
    ano_conclusao = forms.IntegerField(
        label="Ano de conclusão",
        min_value=1000,
        widget=forms.NumberInput(attrs={"inputmode": "numeric", "min": "1000"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo, opcoes in [("unidade", opcoes_de_unidade()), ("nivel", opcoes_de_nivel())]:
            self.fields[campo].choices = [("", "Selecione")] + [(v, v) for v in opcoes]
        self.fields["ano_conclusao"].max_value = timezone.localdate().year
        for nome, campo in self.fields.items():
            campo.widget.attrs["id"] = nome
            campo.error_messages["required"] = "Preencha este campo."
            campo.error_messages["invalid_choice"] = "Selecione uma opção da lista."
            campo.error_messages["invalid"] = "Confira este campo."
        if self.is_bound:
            self.is_valid()
            for nome in self.errors:
                self.fields[nome].widget.attrs.update(
                    {"aria-invalid": "true", "aria-describedby": f"erro-{nome}"}
                )

    def clean_curso(self):
        curso = self.cleaned_data["curso"]
        if not curso.strip():
            raise forms.ValidationError("Informe o curso.")
        return curso

    def clean_ano_conclusao(self):
        ano = self.cleaned_data["ano_conclusao"]
        if ano > timezone.localdate().year:
            raise forms.ValidationError("Informe um ano de conclusão que já ocorreu.")
        return ano


class AcervoForm(forms.Form):
    # Só a origem acervo exige estes campos; as outras decisões usam o mesmo formulário.
    use_required_attribute = False
    unidade = forms.CharField(label="Unidade no acervo", max_length=200)
    referencia = forms.CharField(label="Referência no acervo", max_length=300)
    nivel = forms.CharField(label="Nível no acervo", max_length=200)
    curso = forms.CharField(label="Curso no acervo", max_length=300)
    ano_conclusao = forms.IntegerField(
        label="Ano no acervo",
        min_value=1000,
        max_value=9999,
        widget=forms.NumberInput(attrs={"inputmode": "numeric"}),
    )
    modalidade = forms.CharField(label="Modalidade (quando informada)", required=False)
    forma_oferta = forms.CharField(label="Forma de oferta (quando informada)", required=False)
    data_conclusao = forms.DateField(label="Data de conclusão (quando informada)", required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.is_bound:
            self.is_valid()
            for nome in self.errors:
                self.fields[nome].widget.attrs.update(
                    {
                        "aria-invalid": "true",
                        "aria-describedby": f"erro-{self.prefix}-{nome}",
                    }
                )

    def clean(self):
        dados = super().clean()
        data = dados.get("data_conclusao")
        if data and data.year != dados.get("ano_conclusao"):
            self.add_error("data_conclusao", "A data deve corresponder ao ano informado.")
        for campo in ("modalidade", "forma_oferta", "data_conclusao"):
            if not dados.get(campo):
                dados[campo] = None
        return dados
