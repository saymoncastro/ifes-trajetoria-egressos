"""Como um encontro aparece nas telas (031; protótipos p2 a p10, o4 a o9, m1 a m4).

Só formatação: nada consulta o banco além do que recebe e nada grava. O link entra no
resultado apenas quando `mostrar_link` é verdadeiro, decidido por `regras.mostra_link`
(FR-021; plan, "Riscos").
"""

from django.utils import timezone

from trajetoria.portal.encontros import mensagens as m
from trajetoria.portal.encontros.formularios import publico_em_texto
from trajetoria.portal.encontros.governanca import INSTITUCIONAL, responsavel
from trajetoria.portal.oportunidades import mensagens as m_oportunidades
from trajetoria.portal.oportunidades.regras import origem_do_site

SEMANA = ("segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira",
          "sábado", "domingo")
MESES = ("janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto",
         "setembro", "outubro", "novembro", "dezembro")


def hora(momento) -> str:
    local = timezone.localtime(momento)
    return f"{local.hour}h" + (f"{local.minute:02d}" if local.minute else "")


def data(momento) -> str:
    return timezone.localtime(momento).strftime("%d/%m/%Y")


def quem_moderou(escopo: str | None) -> str:
    """Do escopo gravado na decisão (analyze F1): "CPAEG" ou "CSAEG <unidade>"."""
    if not escopo or escopo == INSTITUCIONAL:
        return "CPAEG"
    return f"CSAEG {escopo}"


def quem_analisa(encontro) -> str:
    """Antes da decisão, quem é responsável pelo público (FR-016)."""
    return quem_moderou(responsavel(encontro.publico_unidades))


def origem(encontro) -> str:
    partes = [encontro.origem_curso, encontro.origem_unidade,
              str(encontro.origem_ano) if encontro.origem_ano else ""]
    return " · ".join(p for p in partes if p)


def origem_curta(encontro) -> str:
    dados = ", ".join(p for p in (encontro.origem_unidade,
                                  str(encontro.origem_ano) if encontro.origem_ano else "") if p)
    return f"{encontro.origem_curso} ({dados})" if dados else encontro.origem_curso


def apresentar(encontro, *, mostrar_link: bool = False) -> dict:
    inicio = timezone.localtime(encontro.inicio)
    dados = {
        "id": encontro.pk,
        "titulo": encontro.titulo,
        "descricao": encontro.descricao,
        "dia": f"{inicio.day:02d}",
        "mes_curto": MESES[inicio.month - 1][:3],
        "semana": SEMANA[inicio.weekday()],
        "data_longa": f"{inicio.day} de {MESES[inicio.month - 1]} de {inicio.year}",
        "data_curta": f"{SEMANA[inicio.weekday()].capitalize()}, {inicio:%d/%m}",
        "data_completa": f"{SEMANA[inicio.weekday()].capitalize()}, {inicio:%d/%m/%Y}",
        "data": data(encontro.inicio),
        "horario": f"{hora(encontro.inicio)} às {hora(encontro.termino)}",
        "nome": encontro.nome_apresentacao,
        "inicial": encontro.nome_apresentacao[:1].upper(),
        "origem": origem(encontro),
        "origem_curta": origem_curta(encontro),
        "publico": publico_em_texto(encontro),
        "moderado_por": m.MODERADO_POR.format(quem=quem_moderou(encontro.publicado_por_escopo))
        if encontro.publicado_em else "",
    }
    if mostrar_link:
        do_ifes, dominio = origem_do_site(encontro.link)
        dados["link"] = {
            "endereco": encontro.link,
            "texto": encontro.link.removeprefix("https://"),
            "nota": m.LINK_NOTA.format(
                origem=m_oportunidades.SITE_DO_IFES if do_ifes else m_oportunidades.SITE_EXTERNO,
                dominio=dominio,
            ),
        }
    return dados


def confirmacoes(n: int) -> str:
    return m.CONFIRMACOES.get(n) or m.CONFIRMACOES_VARIAS.format(n=n)
