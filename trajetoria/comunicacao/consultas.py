"""População 004 → escopo das Conclusões → Pessoas distintas → contato fictício."""

from dataclasses import dataclass

from trajetoria.academico.models import Pessoa
from trajetoria.campanha.consultas import populacao_no_momento
from trajetoria.comunicacao.acesso import RecusaComunicacao
from trajetoria.comunicacao.contatos import contato_ficticio
from trajetoria.comunicacao.seguranca import validar_endereco, validar_origem


@dataclass(frozen=True)
class ItemDoPublico:
    pessoa: Pessoa
    contato: str | None


@dataclass(frozen=True)
class Publico:
    conclusoes: int
    itens: tuple[ItemDoPublico, ...]

    @property
    def totais(self):
        com = sum(i.contato is not None for i in self.itens)
        return dict(
            conclusoes=self.conclusoes,
            pessoas=len(self.itens),
            com_contato=com,
            sem_contato=len(self.itens) - com,
            previstas=com,
        )


def publico_atual(campanha, escopo):
    validar_origem()
    conclusoes = populacao_no_momento(campanha)
    if not escopo.institucional:
        conclusoes = conclusoes.filter(unidade__in=sorted(escopo.unidades))
    pessoas = Pessoa.objects.filter(pk__in=conclusoes.values("pessoa_id")).order_by(
        "id_externo", "pk"
    )
    try:
        itens = tuple(ItemDoPublico(p, contato_ficticio(p)) for p in pessoas)
        for item in itens:
            if item.contato is not None:
                validar_endereco(item.contato)
    except RecusaComunicacao:
        raise
    except Exception:
        raise RecusaComunicacao("falha_preparacao", 422) from None
    return Publico(conclusoes.count(), itens)
