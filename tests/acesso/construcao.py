from dataclasses import dataclass
from datetime import UTC, date, datetime

from django.apps import apps


@dataclass(frozen=True)
class Dados:
    cpf: str
    data: date | None

    @property
    def cpf11(self):
        return self.cpf.replace(".", "").replace("-", "")

    @property
    def nascimento(self):
        return self.data.strftime("%d/%m/%Y") if self.data else ""


ANA = Dados("000.000.001-91", date(1998, 4, 12))
BRUNO = Dados("111.444.777-35", date(1990, 9, 3))
MARIA = Dados("000.000.002-72", date(1997, 11, 25))
DIEGO = Dados("000.000.003-53", date(1994, 2, 8))
ELISA = Dados("", date(2001, 6, 30))
JOAO = Dados("000.000.004-34", date(2003, 3, 14))
FERNANDA = Dados("000.000.005-15", date(1999, 8, 21))
GUSTAVO = Dados("000.000.006-04", date(2000, 1, 17))
SEM_NOME = Dados("000.000.007-87", None)
CARLA1 = Dados("000.000.008-68", date(1992, 5, 5))
CARLA2 = Dados("000.000.008-68", date(1995, 10, 19))
HELENA = Dados("000.000.010-82", date(1980, 6, 30))
DADOS = (ANA, BRUNO, MARIA, DIEGO, ELISA, JOAO, FERNANDA, GUSTAVO, SEM_NOME, CARLA1, CARLA2, HELENA)
AGORA = datetime(2026, 10, 4, 12, tzinfo=UTC)


def preparar_material(*ids):
    from trajetoria.acesso.material import incorporar_com_material
    from trajetoria.fonte_academica.simulada import FonteSimulada

    return [incorporar_com_material(FonteSimulada(), i) for i in ids]


def linhas_de_dominio():
    return {
        m._meta.label: sorted(list(m.objects.values()), key=repr)
        for m in apps.get_models(include_auto_created=True)
        if m._meta.app_label in ("academico", "participacao", "acesso", "campanha", "instrumento")
    }


@dataclass
class Relogio:
    agora: datetime = AGORA
