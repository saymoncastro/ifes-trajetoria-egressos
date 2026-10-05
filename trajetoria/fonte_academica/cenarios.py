"""Conjunto canônico da fonte simulada.

Reproduz exatamente specs/001-nucleo-academico-fonte-simulada/contracts/cenarios-simulados.md.
Todos os dados são fictícios: prefixo `SIM-` e sobrenome "Exemplo". Unidades e cursos são
apenas plausíveis no Ifes e não declaram quais valores existem na fonte real (DP-004, DP-007).

A situação acadêmica é vocabulário interno desta fonte, não do NIAE. Só `concluida` é
reconhecida como conclusão (decisão da própria fonte; para a fonte real, DP-008).
"""

from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True)
class PessoaSimulada:
    id_externo: str
    nome: str | None
    cpf: str | None = field(default=None, repr=False)
    data_nascimento: date | None = field(default=None, repr=False)


@dataclass(frozen=True)
class RegistroSimulado:
    id_externo: str
    id_pessoa: str
    situacao: str | None
    curso: str | None = None
    unidade: str | None = None
    nivel: str | None = None
    modalidade: str | None = None
    forma_oferta: str | None = None
    ano_conclusao: int | None = None
    data_conclusao: date | None = None


CONCLUIDA = "concluida"

TADS = "Tecnologia em Análise e Desenvolvimento de Sistemas"
GRAD, TEC, POS = "Graduação", "Técnico", "Pós-graduação"
PRES, EAD = "Presencial", "A distância"

PESSOAS: tuple[PessoaSimulada, ...] = (
    # CPFs e datas fictícios (018 research R13): dígito verificador válido, nada real.
    PessoaSimulada("SIM-P-0001", "Ana Exemplo", "00000000191", date(1998, 4, 12)),  # A
    PessoaSimulada("SIM-P-0002", "Bruno Exemplo", "11144477735", date(1990, 9, 3)),  # B
    # C — "experiência esperada"
    PessoaSimulada("SIM-P-0003", "Maria Exemplo", "00000000272", date(1997, 11, 25)),
    # D — três conclusões
    PessoaSimulada("SIM-P-0004", "Diego Exemplo", "00000000353", date(1994, 2, 8)),
    PessoaSimulada("SIM-P-0005", "Elisa Exemplo", None, date(2001, 6, 30)),  # E — sem CPF
    # F1 — só matrícula ativa
    PessoaSimulada("SIM-P-0006", "João Exemplo", "00000000434", date(2003, 3, 14)),
    # F2 — conclusão + matrícula ativa
    PessoaSimulada("SIM-P-0007", "Fernanda Exemplo", "00000000515", date(1999, 8, 21)),
    # F3 — nenhum registro concluído
    PessoaSimulada("SIM-P-0008", "Gustavo Exemplo", "00000000604", date(2000, 1, 17)),
    PessoaSimulada("SIM-P-0009", None, "00000000787", None),  # sem nome; sem data
    # Homônimos com o mesmo CPF: colisão de cadastro
    PessoaSimulada("SIM-P-0010", "Carla Exemplo", "00000000868", date(1992, 5, 5)),
    PessoaSimulada("SIM-P-0011", "Carla Exemplo", "00000000868", date(1995, 10, 19)),
    # 019: presente na fonte, excluída do preparo para validar por referência.
    PessoaSimulada("SIM-P-0012", "Helena Exemplo", "00000001082", date(1980, 6, 30)),
)

REGISTROS: tuple[RegistroSimulado, ...] = (
    # A
    RegistroSimulado(
        "SIM-C-0001", "SIM-P-0001", CONCLUIDA, TADS, "Serra", GRAD, PRES, None,
        2022, date(2022, 12, 16),
    ),
    # B — mesmo campus, períodos diferentes
    RegistroSimulado(
        "SIM-C-0002", "SIM-P-0002", CONCLUIDA, "Técnico em Edificações", "Vitória", TEC,
        PRES, "Integrado", 2014,
    ),
    RegistroSimulado(
        "SIM-C-0003", "SIM-P-0002", CONCLUIDA, "Bacharelado em Engenharia Civil", "Vitória",
        GRAD, PRES, None, 2020, date(2020, 7, 10),
    ),
    # C — unidades diferentes
    RegistroSimulado(
        "SIM-C-0004", "SIM-P-0003", CONCLUIDA, TADS, "Serra", GRAD, PRES, None, 2022,
    ),
    RegistroSimulado(
        "SIM-C-0005", "SIM-P-0003", CONCLUIDA, "Especialização em Informática na Educação",
        "Cefor", POS, EAD, None, 2025, date(2025, 3, 28),
    ),
    # D — níveis diferentes
    RegistroSimulado(
        "SIM-C-0006", "SIM-P-0004", CONCLUIDA, "Técnico em Química", "Vila Velha", TEC, PRES,
        "Integrado", 2012,
    ),
    RegistroSimulado(
        "SIM-C-0007", "SIM-P-0004", CONCLUIDA, "Licenciatura em Química", "Vila Velha", GRAD,
        PRES, None, 2017,
    ),
    RegistroSimulado(
        "SIM-C-0008", "SIM-P-0004", CONCLUIDA, "Mestrado Profissional em Química",
        "Vila Velha", POS, PRES, None, 2020,
    ),
    # E
    RegistroSimulado(
        "SIM-C-0009", "SIM-P-0005", CONCLUIDA, "Técnico em Agropecuária", "Alegre", TEC, PRES,
        "Integrado", 2019,
    ),
    # F1
    RegistroSimulado(
        "SIM-C-0901", "SIM-P-0006", "matricula_ativa", "Bacharelado em Sistemas de Informação",
        "Cachoeiro de Itapemirim", GRAD, PRES,
    ),
    # F2
    RegistroSimulado(
        "SIM-C-0010", "SIM-P-0007", CONCLUIDA, "Técnico em Mecânica", "Cariacica", TEC, PRES,
        "Subsequente", 2018,
    ),
    RegistroSimulado(
        "SIM-C-0902", "SIM-P-0007", "matricula_ativa", "Bacharelado em Engenharia Mecânica",
        "Cariacica", GRAD, PRES,
    ),
    # F3
    RegistroSimulado(
        "SIM-C-0903", "SIM-P-0008", "evasao", "Técnico em Logística", "Viana", TEC, PRES,
        "Concomitante",
    ),
    RegistroSimulado(
        "SIM-C-0904", "SIM-P-0008", "transferencia", "Licenciatura em Matemática",
        "Cachoeiro de Itapemirim", GRAD, PRES,
    ),
    RegistroSimulado(
        "SIM-C-0905", "SIM-P-0008", "situacao_legada_x", "Técnico em Informática", "Colatina",
        TEC, PRES, "Subsequente",
    ),
    RegistroSimulado(
        "SIM-C-0906", "SIM-P-0008", None, "Tecnologia em Logística", "Cariacica", GRAD, PRES,
    ),
    # Sem nome
    RegistroSimulado(
        "SIM-C-0011", "SIM-P-0009", CONCLUIDA, "Técnico em Informática", "Colatina", TEC, PRES,
        "Subsequente", 2021,
    ),
    # Homônimos
    RegistroSimulado(
        "SIM-C-0012", "SIM-P-0010", CONCLUIDA, "Licenciatura em Pedagogia", "Vitória", GRAD,
        PRES, None, 2016,
    ),
    RegistroSimulado(
        "SIM-C-0013", "SIM-P-0011", CONCLUIDA, "Tecnologia em Redes de Computadores", "Serra",
        GRAD, PRES, None, 2023,
    ),
    RegistroSimulado(
        "SIM-C-0014", "SIM-P-0012", CONCLUIDA, "Técnico em Informática", "Serra", TEC,
        PRES, "Subsequente", 2004,
    ),
)

# 019: credencial fictícia que não identifica nenhuma Pessoa da fonte.
PAR_DECLARANTE = ("00000000949", date(2001, 6, 30))
PESSOAS_NAO_PREPARADAS = frozenset({"SIM-P-0012"})

# 021 (P2): contexto da trajetória, fictício; não afirma que a fonte real fornece ingresso
# ou agregados (021 FR-064). Ingresso por conclusão: (ano, data ou None).
COMPLEMENTOS: dict[str, tuple[int, date | None]] = {
    "SIM-C-0001": (2019, None),  # Ana, TADS
}
# (métrica, curso, unidade, ano, valor, apurado_em). Coerentes com as conclusões simuladas do
# recorte (FR-060); Vila Velha e Cefor ficam sem agregado, para exercitar a ausência.
APURACAO_SIMULADA = date(2026, 1, 31)
AGREGADOS: tuple[tuple[str, str | None, str, int, int, date], ...] = (
    ("conclusoes_curso_unidade_ano", TADS, "Serra", 2022, 27, APURACAO_SIMULADA),
    ("conclusoes_unidade_ano", None, "Serra", 2022, 812, APURACAO_SIMULADA),
)
