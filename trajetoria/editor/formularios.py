"""Formulários do editor (research R11): um por ação do operador.

Só **convertem** a entrada para os argumentos das operações da 002 — texto exatamente como
digitado, opcional vazio → `None`, número inteiro. Nenhuma regra do domínio é repetida aqui
(texto obrigatório, unicidade, complemento único, escala válida, tipo compatível): quem
recusa é a 002, e a view associa a recusa ao campo. Nenhum `ModelForm`.
"""

from django import forms

from trajetoria.editor import mensagens
from trajetoria.editor.apresentacao import TIPOS
from trajetoria.instrumento.conteudo import Escala
from trajetoria.instrumento.models import TipoPergunta


def texto_opcional(valor: str | None) -> str | None:
    """Campo vazio ou só com espaços é ausência (002 FR-010, FR-025); o resto vai como está."""
    return None if valor is None or not valor.strip() else valor


def _texto(rotulo, *, linhas=False, ajuda=""):
    widget = forms.Textarea(attrs={"rows": 4}) if linhas else forms.TextInput
    return forms.CharField(
        label=rotulo, required=False, strip=False, widget=widget, help_text=ajuda
    )


class Formulario(forms.Form):
    """Base comum: liga ajuda e erros aos controles (`aria-describedby`, `aria-invalid`) para
    tecnologias assistivas (FR-110). Os ids seguem `id_<campo>-ajuda` e `id_<campo>-erro`,
    a convenção verificada pela suíte de acessibilidade herdada da 008."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for nome in self.fields:
            self._descrever(nome)

    def _descrever(self, nome):
        campo = self.fields[nome]
        auto_id = self[nome].auto_id
        ids = [f"{auto_id}-ajuda"] if campo.help_text else []
        if self._errors and nome in self._errors:
            ids.append(f"{auto_id}-erro")
            campo.widget.attrs["aria-invalid"] = "true"
        if ids:
            campo.widget.attrs["aria-describedby"] = " ".join(ids)

    def add_error(self, field, error):
        super().add_error(field, error)
        for nome in self.fields:
            self._descrever(nome)


class PesquisaForm(Formulario):
    nome = _texto("Nome administrativo da Pesquisa")
    confirmar_nome_repetido = forms.BooleanField(
        label="Criar mesmo assim, com o nome repetido", required=False
    )


class DesignacaoForm(Formulario):
    designacao = _texto("Designação da Versão", ajuda="Por exemplo: 2026.")


class DadosVersaoForm(Formulario):
    designacao = _texto("Designação da Versão")
    titulo = _texto("Título apresentado (opcional)")
    texto_abertura = _texto("Texto de abertura (opcional)", linhas=True)
    texto_encerramento = _texto("Texto de encerramento (opcional)", linhas=True)

    def argumentos(self) -> dict:
        d = self.cleaned_data
        return {
            "designacao": d["designacao"],
            "titulo": texto_opcional(d["titulo"]),
            "texto_abertura": texto_opcional(d["texto_abertura"]),
            "texto_encerramento": texto_opcional(d["texto_encerramento"]),
        }


class SecaoForm(Formulario):
    titulo = _texto("Título da Seção (opcional)")
    texto = _texto("Texto introdutório (opcional)", linhas=True)
    encaminhamento = forms.ChoiceField(
        label="Depois desta Seção, quando nenhum desvio for acionado",
        required=False,
        error_messages={"invalid_choice": mensagens.CONFLITO},
    )

    def __init__(self, destinos, *args, **kwargs):
        """`destinos`: (valor, rótulo) das demais Seções da Versão, sem filtro de posição
        (destino anterior é problema do diagnóstico A, não regra do formulário)."""
        super().__init__(*args, **kwargs)
        self.fields["encaminhamento"].choices = [("", "Seguir a ordem"), *destinos]

    def argumentos(self) -> dict:
        d = self.cleaned_data
        return {"titulo": texto_opcional(d["titulo"]), "texto": texto_opcional(d["texto"])}


class TipoPerguntaForm(Formulario):
    """Passo de escolha do tipo (GET, sem escrita): exatamente os quatro tipos da 002."""

    tipo = forms.ChoiceField(
        label="Tipo da Pergunta",
        widget=forms.RadioSelect,
        choices=[
            (tipo.value, f"{nome} — {descricao}") for tipo, (nome, descricao) in TIPOS.items()
        ],
    )


def _inteiro(rotulo):
    return forms.IntegerField(
        label=rotulo, required=False, error_messages={"invalid": mensagens.NUMERO_INTEIRO}
    )


class PerguntaForm(Formulario):
    """Dados da Pergunta. O tipo nunca é campo: é fixado na criação (002 FR-062); a escala só
    existe para o tipo escala."""

    texto = _texto("Texto da Pergunta", linhas=True)
    texto_explicativo = _texto("Texto explicativo (opcional)", linhas=True)
    # Conversão de entrada, não regra do domínio: a operação da 002 exige um booleano.
    obrigatoria = forms.ChoiceField(
        label="Obrigatoriedade",
        widget=forms.RadioSelect,
        choices=[("sim", "Obrigatória"), ("nao", "Opcional")],
        error_messages={"required": mensagens.OBRIGATORIEDADE},
    )

    def __init__(self, tipo, *args, **kwargs):
        self.tipo = TipoPergunta(tipo)
        super().__init__(*args, **kwargs)
        if self.tipo != TipoPergunta.ESCALA:
            for nome in ("inicio", "fim", "rotulo_inicio", "rotulo_fim"):
                del self.fields[nome]

    inicio = _inteiro("Limite inicial da escala")
    fim = _inteiro("Limite final da escala")
    rotulo_inicio = _texto("Rótulo do limite inicial (opcional)")
    rotulo_fim = _texto("Rótulo do limite final (opcional)")

    def argumentos(self) -> dict:
        d = self.cleaned_data
        argumentos = {
            "texto": d["texto"],
            "texto_explicativo": texto_opcional(d["texto_explicativo"]),
            "obrigatoria": d["obrigatoria"] == "sim",
        }
        if self.tipo == TipoPergunta.ESCALA:
            argumentos["escala"] = Escala(
                d["inicio"], d["fim"], texto_opcional(d["rotulo_inicio"]),
                texto_opcional(d["rotulo_fim"]),
            )  # fmt: skip
        return argumentos


class MoverPerguntaForm(Formulario):
    secao = forms.ChoiceField(
        label="Seção de destino",
        error_messages={"required": "Escolha uma Seção.", "invalid_choice": mensagens.CONFLITO},
    )

    def __init__(self, destinos, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["secao"].choices = [("", "Escolha…"), *destinos]


class OpcaoForm(Formulario):
    texto = _texto("Texto da Opção", ajuda="Gravado exatamente como digitado.")
    complemento = forms.BooleanField(
        label="Aceita complemento escrito (como em «Outro: ...»)", required=False
    )
    desvio = forms.ChoiceField(
        label="Desvio de navegação quando esta Opção for escolhida",
        required=False,
        error_messages={"invalid_choice": mensagens.CONFLITO},
    )

    def __init__(self, destinos=None, *args, **kwargs):
        """`destinos`: (valor, rótulo) de todas as Seções da Versão, só para escolha única
        (002 FR-050). Sem eles, o campo não existe."""
        super().__init__(*args, **kwargs)
        if destinos is None:
            del self.fields["desvio"]
        else:
            self.fields["desvio"].choices = [
                ("", "Sem desvio (segue o fluxo da Seção)"),
                ("finalizar", "Finalizar o instrumento"),
                *destinos,
            ]

    def argumentos(self) -> dict:
        d = self.cleaned_data
        return {"texto": d["texto"], "complemento_textual": d["complemento"]}
