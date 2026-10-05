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
acesso a dado individual. A 017 concede gestão mínima pela regra independente
`pode_gerir_campanha` (C1, demonstração, DP-402 aberta).
"""

from dataclasses import dataclass

from trajetoria.governanca.models import Papel

__all__ = [
    "EscopoDeAcompanhamento",
    "escopo_de_acompanhamento",
    "pode_acompanhar_coleta",
    "pode_gerir_campanha",
    "pode_validar_formacao",
    "pode_consultar_lotes",
    "pode_preparar_lote",
    "pode_enviar_lote",
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


def pode_gerir_campanha(vinculos) -> bool:
    """017 C1: só CPAEG ativa, restrita à demonstração; DP-402 aberta.

    Não concede publicação, critérios, remoção ou mobilização.
    """
    return any(v.ativo and v.papel == Papel.CPAEG for v in vinculos)


def pode_validar_formacao(vinculos) -> bool:
    """019/E3, DP-1901: registro fictício do resultado, CPAEG ou CSAEG ativos."""
    return any(v.ativo and v.papel in (Papel.CPAEG, Papel.CSAEG) for v in vinculos)


# Lotes de mobilização (020). Três regras nomeadas: consultar, preparar/confirmar e enviar
# são ações distintas, para que a instância competente possa separá-las (DP-2001, DP-1602).
# Hoje, CPAEG ou CSAEG ativos: interpretação local reversível, **só demonstração**; o envio
# real continua bloqueado pelos Gates A e B, qualquer que seja a capacidade. Acompanhar a
# coleta (011) e gerir Campanha (017) não concedem nenhuma delas.


def pode_consultar_lotes(vinculos) -> bool:
    """020 FR-036: ver Lotes e contagens agregadas no escopo; nunca membros individuais."""
    return any(v.ativo and v.papel in (Papel.CPAEG, Papel.CSAEG) for v in vinculos)


def pode_preparar_lote(vinculos) -> bool:
    """020 FR-036: prévia e confirmação; CSAEG só nas suas unidades (FR-037)."""
    return any(v.ativo and v.papel in (Papel.CPAEG, Papel.CSAEG) for v in vinculos)


def pode_enviar_lote(vinculos) -> bool:
    """020 FR-036: envio na demonstração; não concede envio real (Gate B; DP-2001)."""
    return any(v.ativo and v.papel in (Papel.CPAEG, Papel.CSAEG) for v in vinculos)
