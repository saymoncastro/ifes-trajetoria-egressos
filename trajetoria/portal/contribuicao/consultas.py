"""Leituras da Manifestação (026). Nada grava.

Sem chave estrangeira (plan R2), a Pessoa e a Conclusão são lidas em lote pelo identificador,
só para apresentação.
"""

from dataclasses import dataclass

from trajetoria.academico.models import ConclusaoAcademica, Pessoa
from trajetoria.portal.models import Manifestacao


def conclusoes_de_referencia(pessoa) -> list:
    """Só Conclusões Acadêmicas da Pessoa (D-2603), na ordem do Início."""
    return list(pessoa.conclusoes.all())


def da_pessoa(pessoa):
    return Manifestacao.objects.filter(pessoa_id=pessoa.pk)


def tem_manifestacao(pessoa) -> bool:
    return da_pessoa(pessoa).exists()


def enviadas(pessoa) -> int:
    """Ativas (não retiradas): o "Adiante" do Início (032 FR-009)."""
    return da_pessoa(pessoa).filter(retirada_em__isnull=True).count()


def ultima_ativa(pessoa) -> dict | None:
    """A manifestação ativa mais recente, para a participação (032 FR-008): forma, quem
    recebe e os marcos registrados, com a data. `None` sem nenhuma ativa."""
    from django.utils import timezone

    from trajetoria.portal.contribuicao import mensagens as m
    from trajetoria.portal.models import Forma

    manifestacao = da_pessoa(pessoa).filter(retirada_em__isnull=True).first()
    if manifestacao is None:
        return None

    def data(momento):
        return timezone.localtime(momento).strftime("%d/%m/%Y")

    marcos = [(m.MARCO_ENVIADA, data(manifestacao.registrada_em))]
    if manifestacao.contato_registrado_em is not None:
        marcos.append((m.MARCO_CONTATO.format(destino=m.destino(manifestacao.unidade, inicio=True)),
                       data(manifestacao.contato_registrado_em)))
    return {
        "pk": manifestacao.pk,
        "forma": Forma(manifestacao.forma).label,
        "quem_recebe": m.quem_recebe(manifestacao.unidade),
        "marcos": marcos,
    }


def da_pessoa_ou_none(pessoa, pk) -> Manifestacao | None:
    return da_pessoa(pessoa).filter(pk=pk).first()


def ativas_do_escopo(escopo):
    """Só as ativas (FR-005): a retirada sai da lista e do CSV. CSAEG: as unidades do
    escopo; CPAEG: todas (DP-2501)."""
    ativas = Manifestacao.objects.filter(retirada_em__isnull=True)
    if escopo.institucional:
        return ativas
    return ativas.filter(unidade__in=sorted(escopo.unidades))


@dataclass(frozen=True)
class Descrita:
    manifestacao: Manifestacao
    conclusao: ConclusaoAcademica | None
    nome: str | None


def descrever(manifestacoes, *, com_nome: bool = False) -> list[Descrita]:
    """A formação (e, para a unidade, o nome) de cada manifestação, em duas consultas."""
    manifestacoes = list(manifestacoes)
    conclusoes = ConclusaoAcademica.objects.in_bulk({m.conclusao_id for m in manifestacoes})
    nomes = {}
    if com_nome:
        nomes = dict(
            Pessoa.objects.filter(pk__in={m.pessoa_id for m in manifestacoes})
            .values_list("pk", "nome")
        )
    return [
        Descrita(m, conclusoes.get(m.conclusao_id), nomes.get(m.pessoa_id)) for m in manifestacoes
    ]
