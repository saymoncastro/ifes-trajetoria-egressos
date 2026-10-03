"""As três capacidades da Feature 010 (spec FR-028 a FR-035; contracts/governanca.md) e a
regra de acompanhamento da coleta da Feature 011 (011 contracts/governanca.md).

Regras fixas e puras sobre os vínculos do operador: não leem banco, requisição, settings
nem o modo de demonstração. Um vínculo inativo não concede nada, mesmo se passado aqui.
Capacidade é a existência de **algum** vínculo ativo que a conceda; não há precedência nem
"papel ativo", e a unidade não participa (spec FR-017, FR-021).

Fundamentação: a elaboração do questionário cabe à CPAEG (PAEG Art. 21, VI); a CSAEG aplica
o questionário e reporta atualizações à CPAEG (Art. 22, IV), e por isso consulta o
instrumento publicado — interpretação operacional B6, não competência autônoma. Consultar
rascunho e elaborar são regras distintas da spec, hoje com o mesmo critério (DP-1004).
Publicar não é capacidade de ninguém (002/DP-001).

Acompanhamento da coleta (011): a CPAEG planeja, executa e avalia as atividades da PAEG no
âmbito do Ifes (Art. 21, I, III); a CSAEG o faz nas unidades e aplica o questionário
(Art. 22, I, IV). Por isso, vínculo CPAEG ativo → acompanhamento institucional; vínculo
CSAEG ativo → acompanhamento das suas unidades; nenhum → nada. As duas atuações são
**nomeadas**: um papel novo não recebe acompanhamento por omissão. É interpretação
operacional (011, B1–B4), não competência autônoma; não concede gestão de Campanha nem
acesso a dado individual. Aqui, e só aqui, a unidade do vínculo tem consumidor.
"""

from dataclasses import dataclass

from trajetoria.governanca.models import Papel

__all__ = [
    "EscopoDeAcompanhamento",
    "escopo_de_acompanhamento",
    "pode_acompanhar_coleta",
    "pode_simular_comunicacao",
    "pode_consultar_publicado",
    "pode_consultar_rascunho",
    "pode_elaborar_instrumento",
]


def pode_consultar_publicado(vinculos) -> bool:
    return any(v.ativo for v in vinculos)


def pode_consultar_rascunho(vinculos) -> bool:
    return any(v.ativo and v.papel == Papel.CPAEG for v in vinculos)


def pode_elaborar_instrumento(vinculos) -> bool:
    return any(v.ativo and v.papel == Papel.CPAEG for v in vinculos)


@dataclass(frozen=True)
class EscopoDeAcompanhamento:
    """Institucional (CPAEG, sem unidades) ou as unidades dos vínculos CSAEG ativos."""

    institucional: bool
    unidades: frozenset[str]


def pode_acompanhar_coleta(vinculos) -> bool:
    return any(v.ativo and v.papel in (Papel.CPAEG, Papel.CSAEG) for v in vinculos)


def escopo_de_acompanhamento(vinculos) -> EscopoDeAcompanhamento | None:
    """CPAEG ativo prevalece (precedência fixa, sem "papel ativo"); vários CSAEG somam
    unidades; sem vínculo ativo de CPAEG ou CSAEG, `None`."""
    ativos = [v for v in vinculos if v.ativo]
    if any(v.papel == Papel.CPAEG for v in ativos):
        return EscopoDeAcompanhamento(institucional=True, unidades=frozenset())
    unidades = frozenset(v.unidade for v in ativos if v.papel == Papel.CSAEG)
    if unidades:
        return EscopoDeAcompanhamento(institucional=False, unidades=unidades)
    return None


def pode_simular_comunicacao(vinculos) -> bool:
    """Capacidade exclusiva da demonstração 016; não concede comunicação real."""
    return any(v.ativo and v.papel in (Papel.CPAEG, Papel.CSAEG) for v in vinculos)
