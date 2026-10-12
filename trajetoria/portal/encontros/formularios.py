"""Formulário da proposta (031 FR-002 a FR-007; protótipos o1 a o3).

Sem estado em sessão (como a 026, R11): a tela "Confira e envie" reenvia os mesmos campos,
ocultos, e a gravação revalida tudo. Os valores do público precisam estar entre os
registrados nas Conclusões (FR-004; 025 FR-007); nada é digitado livremente.
"""

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

from django.utils import timezone

from trajetoria.portal.encontros import mensagens as m
from trajetoria.portal.encontros.operacoes import Proposta, violacoes_da_proposta
from trajetoria.portal.encontros.regras import (
    ANTECEDENCIA_MAXIMA,
    ANTECEDENCIA_MINIMA,
    normalizar_texto,
)

TODOS, FORMACOES = "todos", "formacoes"
_CAMPOS_DE_PUBLICO = (
    ("publico_unidades", "unidade", m.RESUMO_UNIDADES),
    ("publico_niveis", "nivel", m.RESUMO_NIVEIS),
    ("publico_cursos", "curso", m.RESUMO_CURSOS),
)
ANCORAS = {
    "titulo": "titulo", "descricao": "descricao", "nome": "nome", "data": "data",
    "termino": "termino", "publico": "campo-publico", "link": "link", "origem": "campo-origem",
    "limite": "campo-limite",
}


@dataclass(frozen=True)
class Lida:
    proposta: Proposta
    publico: str  # TODOS ou FORMACOES
    campos: dict  # o que a pessoa enviou, para devolver ao formulário


def _data(texto: str) -> date | None:
    try:
        return date.fromisoformat(texto)
    except ValueError:
        return None


def _hora(texto: str) -> time | None:
    try:
        return time.fromisoformat(texto)
    except ValueError:
        return None


def _momento(dia: date | None, hora: time | None) -> datetime | None:
    if dia is None or hora is None:
        return None
    return timezone.make_aware(datetime.combine(dia, hora))


def limites_de_data(agora: datetime) -> tuple[date, date]:
    hoje = timezone.localdate(agora)
    return hoje + timedelta(days=ANTECEDENCIA_MINIMA), hoje + timedelta(days=ANTECEDENCIA_MAXIMA)


def ler(dados, conclusoes, opcoes_de_publico: dict, agora: datetime) -> tuple[Lida, dict]:
    """Lê e valida. Devolve a proposta e os erros por campo (texto pronto para a tela)."""
    campos = {
        "titulo": normalizar_texto(dados.get("titulo")),
        "descricao": normalizar_texto(dados.get("descricao")),
        "nome": normalizar_texto(dados.get("nome")),
        "data": (dados.get("data") or "").strip(),
        "inicio": (dados.get("inicio") or "").strip(),
        "termino": (dados.get("termino") or "").strip(),
        "link": (dados.get("link") or "").strip(),
        "origem": (dados.get("origem") or "").strip(),
        "publico": dados.get("publico") if dados.get("publico") in (TODOS, FORMACOES) else "",
    }
    erros: dict[str, str] = {}
    publico = {}
    for campo, nome, _rotulo in _CAMPOS_DE_PUBLICO:
        escolhidos = [v for v in dados.getlist(nome) if v]
        campos[nome] = escolhidos
        if campos["publico"] == FORMACOES and escolhidos:
            if not set(escolhidos) <= set(opcoes_de_publico[campo]):
                erros["publico"] = m.ERROS["publico"]
            publico[campo] = sorted(set(escolhidos))
        else:
            publico[campo] = None
    if not campos["publico"] or (
        campos["publico"] == FORMACOES and not any(publico.values())
    ):
        erros["publico"] = m.ERROS["publico"]
    dia = _data(campos["data"])
    origem = next((c for c in conclusoes if str(c.pk) == campos["origem"]), None)
    proposta = Proposta(
        titulo=campos["titulo"], descricao=campos["descricao"],
        nome_apresentacao=campos["nome"],
        inicio=_momento(dia, _hora(campos["inicio"])),
        termino=_momento(dia, _hora(campos["termino"])),
        link=campos["link"],
        conclusao_origem_id=origem.pk if origem else None,
        **publico,
    )
    de, ate = limites_de_data(agora)
    for violacao in violacoes_da_proposta(proposta, agora):
        chave = violacao.campo
        if chave == "data":
            erros["data"] = m.ERROS["data"].format(de=de.strftime("%d/%m/%Y"),
                                                   ate=ate.strftime("%d/%m/%Y"))
        elif chave in m.ERROS:
            erros.setdefault(chave, m.ERROS[chave])
    if origem is None:
        erros["origem"] = m.ERROS["origem"]
    return Lida(proposta, campos["publico"], campos), erros


def opcoes(campos: dict | None, conclusoes, opcoes_de_publico: dict, agora: datetime) -> dict:
    """Contexto do formulário: valores marcados, listas de público e formações de origem."""
    campos = campos or {}
    de, ate = limites_de_data(agora)
    listas = [
        {
            "nome": nome, "rotulo": rotulo,
            "itens": [{"valor": v, "marcado": v in campos.get(nome, [])}
                      for v in opcoes_de_publico[campo]],
            "escolhidos": len(campos.get(nome, [])),
        }
        for campo, nome, rotulo in _CAMPOS_DE_PUBLICO
    ]
    origem = campos.get("origem") or (str(conclusoes[0].pk) if len(conclusoes) == 1 else "")
    return {
        "campos": campos, "listas": listas, "data_min": de.isoformat(), "data_max": ate.isoformat(),
        "dica_data": m.DICA_DATA.format(de=de.strftime("%d/%m/%Y"), ate=ate.strftime("%d/%m/%Y")),
        "publico_todos": campos.get("publico") == TODOS,
        "publico_formacoes": campos.get("publico") == FORMACOES,
        "origens": [{"valor": str(c.pk), "rotulo": formacao_em_texto(c),
                     "marcada": str(c.pk) == origem} for c in conclusoes],
    }


def formacao_em_texto(conclusao) -> str:
    partes = [conclusao.curso or "Formação", conclusao.unidade,
              str(conclusao.ano_conclusao) if conclusao.ano_conclusao else None]
    return " · ".join(p for p in partes if p)


def publico_em_texto(encontro) -> str:
    """O público em linguagem simples (FR-024; FR-006)."""
    if not encontro.tem_publico:
        return m.PUBLICO_TODOS
    partes = []
    for campo, _nome, rotulo in _CAMPOS_DE_PUBLICO:
        valores = getattr(encontro, campo)
        if valores:
            partes.append(f"{rotulo}: {'; '.join(valores)}")
    return ". ".join(partes)
