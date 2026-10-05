# ruff: noqa: E501 -- esboço arquivado da auditoria, não é código do produto.
"""Protótipo ESTÁTICO da nova direção visual do card (auditoria de convergência da 021).

Não é o renderer: é um esboço descartável para revisão. Ilustração vetorial fictícia,
dados fictícios da fonte simulada. Gera PNGs 1080 x 1920.
"""

import re
import sys
from pathlib import Path

RAIZ = Path(sys.argv[1])
SAIDA = Path(sys.argv[2])
sys.path.insert(0, str(RAIZ))

import resvg_py  # noqa: E402

from trajetoria.narrativa import metricas  # noqa: E402

FONTES = [str(RAIZ / "trajetoria/narrativa/fontes" / f) for f in
          ("OpenSans-Regular.ttf", "OpenSans-Bold.ttf")]
F = "Open Sans"
W, H = 1080, 1920
TOPO, BASE = 270, 1650          # área segura proposta (diretriz Meta: ~14% topo e base)
X0, X1 = 90, 990

C = {
    "creme": "#f6f2e8", "profundo": "#0e3b23", "marca": "#2f9e41", "texto": "#1b1b1b",
    "suave": "#4a5058", "branco": "#ffffff", "tinta": "#e3f1e6", "ceu1": "#bfe0f0",
    "ceu2": "#eaf4ea",
}

ASSINATURA = (RAIZ / "trajetoria/interface/templates/interface/assinatura.svg").read_text()
ASSINATURA = re.sub(r"<\?xml[^>]*\?>", "", ASSINATURA)


def larg(t, s, b=False):
    tab = metricas.NEGRITO if b else metricas.REGULAR
    mx = metricas.MAXIMA_NEGRITO if b else metricas.MAXIMA_REGULAR
    return sum(tab.get(c, mx) for c in t) * s


def quebrar(t, s, b, lim):
    linhas, atual = [], ""
    for p in t.split():
        c = f"{atual} {p}" if atual else p
        if atual and larg(c, s, b) > lim:
            linhas.append(atual)
            atual = p
        else:
            atual = c
    return linhas + ([atual] if atual else [])


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;")


def texto(x, y, t, s, cor, b=False, anchor="start", extra=""):
    peso = ' font-weight="700"' if b else ""
    return (f'<text x="{x}" y="{y}" font-family="{F}" font-size="{s}"{peso} fill="{cor}" '
            f'text-anchor="{anchor}" {extra}>{esc(t)}</text>')


def ilustracao(altura):
    """Campus fictício e genérico, vetorial: decorativo, sem afirmar período."""
    h = altura
    p = [f'<defs><linearGradient id="ceu" x1="0" y1="0" x2="0" y2="1">'
         f'<stop offset="0" stop-color="{C["ceu1"]}"/><stop offset="1" stop-color="{C["ceu2"]}"/>'
         f'</linearGradient></defs>',
         f'<rect width="{W}" height="{h}" fill="url(#ceu)"/>',
         f'<circle cx="860" cy="{h*0.30:.0f}" r="70" fill="#fff6d6" opacity="0.9"/>']
    chao = h * 0.80
    # prédio principal
    px, py, pw, ph = 250, chao - 300, 640, 300
    p.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" fill="#fbfbf8"/>')
    p.append(f'<rect x="{px}" y="{py}" width="{pw}" height="34" fill="{C["marca"]}"/>')
    for linha in range(3):
        for col in range(9):
            p.append(f'<rect x="{px+30+col*68}" y="{py+60+linha*72}" width="44" height="46" '
                     f'rx="3" fill="#a9c7d6"/>')
    p.append(f'<rect x="{px+pw/2-50}" y="{chao-110}" width="100" height="110" fill="{C["profundo"]}"/>')
    # ala lateral
    p.append(f'<rect x="80" y="{chao-190}" width="200" height="190" fill="#f0efe9"/>')
    for col in range(3):
        p.append(f'<rect x="{105+col*58}" y="{chao-150}" width="36" height="40" rx="3" fill="#a9c7d6"/>')
    # palmeiras
    for cx, alt in ((140, 330), (960, 360), (1030, 280)):
        p.append(f'<rect x="{cx-7}" y="{chao-alt}" width="14" height="{alt}" fill="#7a5b3a"/>')
        for ang in (-60, -25, 10, 45, 80, 120, 160):
            p.append(f'<ellipse cx="{cx}" cy="{chao-alt}" rx="95" ry="20" fill="#3f8f4a" '
                     f'transform="rotate({ang} {cx} {chao-alt})" opacity="0.92"/>')
    # gramado e árvores
    p.append(f'<rect y="{chao}" width="{W}" height="{h-chao}" fill="#6fae5c"/>')
    for cx in (330, 520, 760):
        p.append(f'<circle cx="{cx}" cy="{chao+10}" r="46" fill="#4f9a4f"/>')
    # borda inferior em onda para o fundo creme
    p.append(f'<path d="M0 {h-60} C 270 {h-130} 640 {h+10} {W} {h-90} L {W} {h} L 0 {h} Z" '
             f'fill="{C["creme"]}"/>')
    return "\n".join(p)


# Medidas únicas: a mesma tabela mede e desenha (nada se sobrepõe).
T_TITULO, L_TITULO = 84, 92          # corpo e entrelinha do título (2 linhas)
T_ANO, T_CURSO, L_CURSO, T_DET = 44, 44, 52, 36
G_ITEM, G_BLOCO = 28, 36
ALT_STATS, ALT_FECHO, ALT_RODAPE = 200, 70, 74


def card(caso):
    nome, unidade, formacoes, mais, stats, apuracao, marca = (
        caso["nome"], caso["unidade"], caso["formacoes"], caso["mais"], caso["stats"],
        caso.get("apuracao"), caso["marca"],
    )
    def medir(formacoes, mais, stats):
        itens = []
        for ano, curso, detalhe in formacoes:
            linhas = quebrar(curso, T_CURSO, True, X1 - X0 - 90)
            itens.append((ano, linhas, detalhe,
                          T_ANO + 14 + len(linhas) * L_CURSO + T_DET + 10 + G_ITEM))
        alt_tl = sum(i[3] for i in itens) + (56 if mais else 0)
        alt_titulo = 2 * L_TITULO + 16 + (58 if nome else 0)
        conteudo = (alt_titulo + G_BLOCO + alt_tl + (G_BLOCO + ALT_STATS if stats else 0)
                    + G_BLOCO + ALT_FECHO + ALT_RODAPE)
        return itens, (BASE - TOPO) - conteudo

    # Composição adaptativa: primeiro some o destaque; depois as formações viram "e mais N".
    extras = int(mais.split()[2]) if mais else 0
    itens, livre = medir(formacoes, mais, stats)
    if livre < 150 and stats:
        stats = []
        itens, livre = medir(formacoes, mais, stats)
    while livre < 150 and len(formacoes) > 1:
        formacoes = formacoes[:-1]
        extras += 1
        mais = f"e mais {extras} formações registradas"
        itens, livre = medir(formacoes, mais, stats)
    # A ilustração absorve o espaço livre; abaixo de 260 px úteis, aplica a composição
    # adaptativa já aprovada (aqui o protótipo só registra).
    hero = TOPO + max(150, min(620, livre))
    partes = [f'<rect width="{W}" height="{H}" fill="{C["creme"]}"/>', ilustracao(hero)]
    if marca:
        partes.append(f'<rect x="{X0-20}" y="{TOPO+6}" width="390" height="116" rx="18" '
                      f'fill="{C["branco"]}" opacity="0.96"/>')
        partes.append(f'<svg x="{X0-5}" y="{TOPO+14}" width="360" height="100" viewBox="0 0 709 284">'
                      f'{ASSINATURA.split(">",1)[1].rsplit("</svg>",1)[0]}</svg>')
    else:
        partes.append(f'<rect x="{X0-20}" y="{TOPO+6}" width="300" height="80" rx="18" '
                      f'fill="{C["branco"]}" opacity="0.96"/>')
        partes.append(texto(X0, TOPO+58, "Instituto Federal", 34, C["profundo"], True))
    leg = f"Unidade {unidade} · ilustração" if unidade else "Ifes · ilustração"
    lw = larg(leg, 30) + 44
    partes.append(f'<rect x="{X1-lw+22}" y="{hero-128}" width="{lw:.0f}" height="52" rx="26" '
                  f'fill="{C["profundo"]}" opacity="0.88"/>')
    partes.append(texto(X1, hero-92, leg, 30, C["branco"], anchor="end"))
    y = hero
    partes.append(texto(X0, y + L_TITULO - 14, "Minha trajetória", T_TITULO, C["profundo"], True))
    partes.append(texto(X0, y + 2 * L_TITULO - 14, "no Ifes", T_TITULO, C["marca"], True))
    y += 2 * L_TITULO + 16
    if nome:
        partes.append(texto(X0, y + 42, nome, 44, C["suave"]))
        y += 58
    y += G_BLOCO
    centros = []
    nos = []
    for ano, linhas, detalhe, alt in itens:
        cy = y + T_ANO - 14
        centros.append(cy)
        nos.append(f'<circle cx="{X0+24}" cy="{cy}" r="22" fill="{C["marca"]}"/>'
                   f'<circle cx="{X0+24}" cy="{cy}" r="9" fill="{C["creme"]}"/>')
        partes.append(texto(X0 + 74, y + T_ANO, ano or "", T_ANO, C["marca"], True))
        ly = y + T_ANO + 14 + L_CURSO - 10
        for linha in linhas:
            partes.append(texto(X0 + 74, ly, linha, T_CURSO, C["texto"], True))
            ly += L_CURSO
        partes.append(texto(X0 + 74, ly - 6, detalhe, T_DET, C["suave"]))
        y += alt
    if len(centros) > 1:
        partes.append(f'<line x1="{X0+24}" y1="{centros[0]}" x2="{X0+24}" y2="{centros[-1]}" '
                      f'stroke="{C["marca"]}" stroke-width="6"/>')
    partes += nos
    if mais:
        partes.append(texto(X0 + 74, y + 30, mais, 38, C["suave"], True))
        y += 56
    if stats:
        y += G_BLOCO - G_ITEM
        largura = (X1 - X0 - 30) / 2 if len(stats) == 2 else X1 - X0
        for i, (numero, rotulo) in enumerate(stats):
            x = X0 + i * (largura + 30)
            partes.append(f'<rect x="{x:.0f}" y="{y}" width="{largura:.0f}" height="{ALT_STATS}" '
                          f'rx="24" fill="{C["branco"]}"/>')
            partes.append(f'<rect x="{x:.0f}" y="{y+24}" width="8" height="{ALT_STATS-48}" rx="4" '
                          f'fill="{C["marca"]}"/>')
            partes.append(texto(x + 36, y + 96, numero, 88, C["profundo"], True))
            for j, r in enumerate(rotulo):
                partes.append(texto(x + 36, y + 138 + j * 34, r, 30, C["suave"]))
        y += ALT_STATS
    partes.append(texto(X0, BASE - ALT_RODAPE - 16, "Essa história também é minha.", 46,
                        C["profundo"], True))
    rod = "Instituto Federal do Espírito Santo · Demonstração — dados fictícios"
    partes.append(texto(X0, BASE - 38, rod, 28, C["suave"]))
    if apuracao:
        partes.append(texto(X0, BASE - 4, apuracao, 26, C["suave"]))
    partes.append(f'<rect y="{BASE+30}" width="{W}" height="{H-BASE-30}" fill="{C["profundo"]}"/>')
    for i in range(0, W, 60):
        partes.append(f'<rect x="{i+18}" y="{BASE+70}" width="24" height="24" rx="4" '
                      f'fill="{C["marca"]}" opacity="0.35"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
            f'viewBox="0 0 {W} {H}">' + "\n".join(partes) + "</svg>")


TADS = "Tecnologia em Análise e Desenvolvimento de Sistemas"
CASOS = {
    "proto-maria-2-formacoes-agregados": dict(
        nome="Maria Exemplo", unidade="Serra", marca=True, mais=None,
        formacoes=[("2022", TADS, "Serra · Graduação · Presencial"),
                   ("2025", "Especialização em Informática na Educação",
                    "Cefor · Pós-graduação · A distância")],
        stats=[("27", ["conclusões deste curso", "na unidade Serra em 2022"]),
               ("812", ["conclusões registradas", "na unidade Serra em 2022"])],
        apuracao="Dados institucionais apurados em 31/01/2026."),
    "proto-ana-1-formacao-agregados-sem-marca": dict(
        nome=None, unidade="Serra", marca=False, mais=None,
        formacoes=[("2022", TADS, "Serra · Graduação · Presencial")],
        stats=[("27", ["conclusões deste curso", "na unidade Serra em 2022"]),
               ("812", ["conclusões registradas", "na unidade Serra em 2022"])],
        apuracao="Dados institucionais apurados em 31/01/2026."),
    "proto-diego-3-formacoes-sem-agregados": dict(
        nome="Diego Exemplo", unidade="Vila Velha", marca=True, mais=None,
        formacoes=[("2012", "Técnico em Química", "Vila Velha · Técnico · Presencial"),
                   ("2017", "Licenciatura em Química", "Vila Velha · Graduação · Presencial"),
                   ("2020", "Mestrado Profissional em Química",
                    "Vila Velha · Pós-graduação · Presencial")],
        stats=[], apuracao=None),
    "proto-pior-caso-4-formacoes-e-mais": dict(
        nome="Maria Aparecida dos Santos Albuquerque", unidade=None, marca=True,
        mais="e mais 3 formações registradas",
        formacoes=[("2012", "Especialização em Práticas Pedagógicas para Professores da Educação Profissional", "Cachoeiro de Itapemirim · Pós-graduação"),
                   ("2015", TADS, "Cachoeiro de Itapemirim · Graduação"),
                   ("2018", "Mestrado Profissional em Educação Profissional e Tecnológica", "Vitória · Pós-graduação"),
                   ("2022", "Especialização em Educação Profissional e Tecnológica Inclusiva", "Vitória · Pós-graduação")],
        stats=[], apuracao=None),
}

SAIDA.mkdir(parents=True, exist_ok=True)
for nome, caso in CASOS.items():
    svg = card(caso)
    png = bytes(resvg_py.svg_to_bytes(svg_string=svg, font_files=FONTES, skip_system_fonts=True))
    (SAIDA / f"{nome}.png").write_bytes(png)
    print(nome, len(png))
