from django import forms


class EntradaForm(forms.Form):
    cpf = forms.CharField(
        required=False,
        strip=False,
        label="CPF",
        widget=forms.TextInput(
            attrs={
                "id": "cpf",
                "inputmode": "numeric",
                "autocomplete": "off",
                "aria-describedby": "dica-cpf",
            }
        ),
    )
    data_nascimento = forms.CharField(
        required=False,
        strip=False,
        label="Data de nascimento",
        widget=forms.TextInput(
            attrs={
                "id": "data_nascimento",
                "inputmode": "numeric",
                "autocomplete": "bday",
                "aria-describedby": "dica-data_nascimento",
            }
        ),
    )
