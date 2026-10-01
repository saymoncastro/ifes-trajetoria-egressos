"""Formulário da Seção (008 contracts/formulario-secao.md; research R6, R9, R10).

Derivado **só** do instrumento (`ConteudoSecao`, 002) e das Respostas atuais (005): nenhuma
Pergunta, Seção ou Opção tem tratamento próprio (FR-034). Campos por **posição** da Pergunta
na Seção (`p<n>`, `p<n>-complemento`, `p<n>-remover`); valores de Opção pela posição da
Opção — o HTML não carrega identificadores técnicos.

Todos os campos são opcionais: a obrigatoriedade é indicada na tela, mas quem decide o que é
exigido no percurso é a 006 (FR-038, FR-051). A validação aqui é de **forma** (FR-044):
Opção ou ponto de escala inexistente, e complemento sem a Opção que o admite marcada — a
mesma regra da 005 (FR-030 a), apresentada antes da gravação.
"""

from dataclasses import dataclass, field, replace

from django import forms

from trajetoria.instrumento.conteudo import ConteudoPergunta, ConteudoSecao
from trajetoria.instrumento.models import TipoPergunta
from trajetoria.interface import mensagens

# Escolha única com mais Opções que isto vira lista suspensa (R10): critério só de contagem.
LIMITE_RADIOS = 10

RADIO, LISTA, CAIXAS, TEXTO, ESCALA = "radio", "lista", "caixas", "texto", "escala"


def modo_de(pergunta: ConteudoPergunta) -> str:
    if pergunta.tipo == TipoPergunta.ESCOLHA_UNICA:
        return LISTA if len(pergunta.opcoes) > LIMITE_RADIOS else RADIO
    return {
        TipoPergunta.ESCOLHA_MULTIPLA: CAIXAS,
        TipoPergunta.TEXTO_CURTO: TEXTO,
        TipoPergunta.ESCALA: ESCALA,
    }[pergunta.tipo]


@dataclass(frozen=True)
class Valor:
    """O que o egresso enviou para uma Pergunta, já limpo. Tudo `None` (e `opcoes` vazio) é
    ausência de Resposta (FR-041)."""

    opcao: int | None = None  # posição da Opção (escolha única)
    opcoes: frozenset[int] = frozenset()  # posições (escolha múltipla)
    texto: str | None = None  # exatamente como digitado (FR-042)
    escala: int | None = None
    complemento: str | None = None
    remover: bool = False

    @property
    def ausente(self) -> bool:
        return self.remover or (
            self.opcao is None and not self.opcoes and self.texto is None and self.escala is None
        )


@dataclass
class Item:
    """Uma Pergunta pronta para o template: só dados de apresentação."""

    pergunta: ConteudoPergunta
    modo: str
    opcoes: list = field(default_factory=list)  # dicts: valor, texto, marcado, id
    texto: str = ""
    complemento: dict | None = None  # rotulo, valor
    remover: dict | None = None  # marcado
    descricao_escala: str | None = None
    erros: list[str] = field(default_factory=list)

    @property
    def nome(self) -> str:
        return f"p{self.pergunta.posicao}"

    @property
    def descrito_por(self) -> str:
        ids = []
        if self.pergunta.texto_explicativo:
            ids.append(f"{self.nome}-explicacao")
        if self.descricao_escala:
            ids.append(f"{self.nome}-escala")
        if self.erros:
            ids.append(f"{self.nome}-erro")
        return " ".join(ids)


def _vazio(texto) -> bool:
    return texto is None or not texto.strip()


class FormularioDaSecao(forms.Form):
    def __init__(self, secao: ConteudoSecao, respostas: dict, data=None):
        super().__init__(data=data)
        self.secao = secao
        self.respostas = respostas
        self.limpos: dict[int, Valor] = {}
        for pergunta in secao.perguntas:
            nome = f"p{pergunta.posicao}"
            self.fields[nome] = _campo(pergunta)
            if _com_complemento(pergunta):
                self.fields[f"{nome}-complemento"] = forms.CharField(required=False, strip=False)
            if self._removivel(pergunta):
                self.fields[f"{nome}-remover"] = forms.BooleanField(required=False)
        self.initial = _iniciais(secao, respostas)

    def _removivel(self, pergunta) -> bool:
        """Rádios e escala não podem ser desmarcados sem JavaScript (R9). Só Perguntas não
        obrigatórias: numa obrigatória, remover só produz uma pendência; e a caixa vale
        também antes de gravar, para desfazer uma marcação por engano."""
        return modo_de(pergunta) in (RADIO, ESCALA) and not pergunta.obrigatoria

    def clean(self):
        dados = super().clean()
        for pergunta in self.secao.perguntas:
            nome = f"p{pergunta.posicao}"
            if nome in self.errors:
                continue
            valor = _valor(pergunta, dados.get(nome), dados.get(f"{nome}-complemento"))
            valor = replace(valor, remover=bool(dados.get(f"{nome}-remover")))
            if valor.complemento is not None and not valor.remover:
                opcao = next(o for o in pergunta.opcoes if o.complemento_textual)
                marcadas = {valor.opcao} if valor.opcao is not None else valor.opcoes
                if opcao.posicao not in marcadas:
                    self.add_error(
                        nome, mensagens.COMPLEMENTO_SEM_OPCAO.format(opcao=_nome(opcao))
                    )
                    continue
            self.limpos[pergunta.posicao] = valor
        return dados

    def itens(self, erros_extra: dict[int, list[str]] | None = None) -> list[Item]:
        """As Perguntas para o template: valores enviados (se houve envio) ou os gravados, e
        os erros do formulário mais `erros_extra` (rejeições da 005, pendências da 006)."""
        erros_extra = erros_extra or {}
        return [self._item(p, erros_extra.get(p.posicao, [])) for p in self.secao.perguntas]

    def _atual(self, nome, *, lista=False):
        if self.is_bound:
            return self.data.getlist(nome) if lista else self.data.get(nome)
        return self.initial.get(nome, [] if lista else None)

    def _item(self, pergunta: ConteudoPergunta, extra: list[str]) -> Item:
        nome = f"p{pergunta.posicao}"
        modo = modo_de(pergunta)
        item = Item(pergunta, modo)
        item.erros = [*self.errors.get(nome, []), *self.errors.get(f"{nome}-complemento", [])]
        item.erros += [e for e in extra if e not in item.erros]
        if modo == TEXTO:
            item.texto = self._atual(nome) or ""
        elif modo == ESCALA:
            marcado = str(self._atual(nome) or "")
            item.opcoes = [
                {"valor": str(i), "texto": str(i), "marcado": str(i) == marcado,
                 "id": f"{nome}-o{i}"}
                for i in range(pergunta.escala.inicio, pergunta.escala.fim + 1)
            ]  # fmt: skip
            rotulos = [
                f"{ponto} = {rotulo}"
                for ponto, rotulo in (
                    (pergunta.escala.inicio, pergunta.escala.rotulo_inicio),
                    (pergunta.escala.fim, pergunta.escala.rotulo_fim),
                )
                if rotulo
            ]
            item.descricao_escala = "; ".join(rotulos) or None
        else:
            if modo == CAIXAS:
                marcados = set(self._atual(nome, lista=True) or [])
            else:
                marcados = {self._atual(nome) or ""}
            item.opcoes = [
                {"valor": str(o.posicao), "texto": o.texto,
                 "marcado": str(o.posicao) in marcados, "id": f"{nome}-o{o.posicao}"}
                for o in pergunta.opcoes
            ]  # fmt: skip
        if f"{nome}-complemento" in self.fields:
            opcao = next(o for o in pergunta.opcoes if o.complemento_textual)
            item.complemento = {
                "rotulo": f"Descreva: «{_nome(opcao)}»",
                "valor": self._atual(f"{nome}-complemento") or "",
            }
        if f"{nome}-remover" in self.fields:
            item.remover = {"marcado": bool(self._atual(f"{nome}-remover"))}
        return item


def _nome(opcao) -> str:
    """O texto da Opção citado numa frase fixa, sem os dois-pontos finais ("Outro:")."""
    return opcao.texto.rstrip().rstrip(":")


def _com_complemento(pergunta) -> bool:
    return any(o.complemento_textual for o in pergunta.opcoes)


def _campo(pergunta: ConteudoPergunta) -> forms.Field:
    escolha = {
        "invalid_choice": mensagens.ESCOLHA_INVALIDA,
        "invalid_list": mensagens.ESCOLHA_INVALIDA,
    }
    opcoes = [(str(o.posicao), o.texto) for o in pergunta.opcoes]
    if pergunta.tipo == TipoPergunta.ESCOLHA_UNICA:
        return forms.ChoiceField(choices=[("", "Selecione…"), *opcoes], required=False,
                                 error_messages=escolha)  # fmt: skip
    if pergunta.tipo == TipoPergunta.ESCOLHA_MULTIPLA:
        return forms.MultipleChoiceField(choices=opcoes, required=False, error_messages=escolha)
    if pergunta.tipo == TipoPergunta.TEXTO_CURTO:
        return forms.CharField(required=False, strip=False)
    pontos = range(pergunta.escala.inicio, pergunta.escala.fim + 1)
    return forms.TypedChoiceField(
        choices=[(str(i), str(i)) for i in pontos],
        coerce=int,
        empty_value=None,
        required=False,
        error_messages={"invalid_choice": mensagens.ESCALA_INVALIDA},
    )


def _valor(pergunta, bruto, complemento) -> Valor:
    complemento = None if _vazio(complemento) else complemento
    if pergunta.tipo == TipoPergunta.ESCOLHA_UNICA:
        return Valor(opcao=int(bruto) if bruto else None, complemento=complemento)
    if pergunta.tipo == TipoPergunta.ESCOLHA_MULTIPLA:
        return Valor(opcoes=frozenset(int(v) for v in bruto or ()), complemento=complemento)
    if pergunta.tipo == TipoPergunta.TEXTO_CURTO:
        return Valor(texto=None if _vazio(bruto) else bruto)
    return Valor(escala=bruto)


def _iniciais(secao: ConteudoSecao, respostas: dict) -> dict:
    """Valores gravados (005) → valores de campo. Nada vem da Conclusão (FR-028)."""
    iniciais = {}
    for pergunta in secao.perguntas:
        resposta = respostas.get(pergunta.id)
        if resposta is None:
            continue
        nome = f"p{pergunta.posicao}"
        if pergunta.tipo == TipoPergunta.ESCOLHA_UNICA:
            iniciais[nome] = str(resposta.opcao.posicao)
        elif pergunta.tipo == TipoPergunta.ESCOLHA_MULTIPLA:
            iniciais[nome] = [str(o.posicao) for o in resposta.opcoes.all()]
        elif pergunta.tipo == TipoPergunta.TEXTO_CURTO:
            iniciais[nome] = resposta.texto
        else:
            iniciais[nome] = str(resposta.escala)
        if resposta.complemento is not None:
            iniciais[f"{nome}-complemento"] = resposta.complemento
    return iniciais


def valor_gravado(pergunta: ConteudoPergunta, resposta) -> Valor:
    """A Resposta atual (005) no mesmo formato de `Valor`, para comparar com o enviado."""
    if resposta is None:
        return Valor()
    if pergunta.tipo == TipoPergunta.ESCOLHA_UNICA:
        return Valor(opcao=resposta.opcao.posicao, complemento=resposta.complemento)
    if pergunta.tipo == TipoPergunta.ESCOLHA_MULTIPLA:
        posicoes = frozenset(o.posicao for o in resposta.opcoes.all())
        return Valor(opcoes=posicoes, complemento=resposta.complemento)
    if pergunta.tipo == TipoPergunta.TEXTO_CURTO:
        return Valor(texto=resposta.texto)
    return Valor(escala=resposta.escala)
