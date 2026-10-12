# ruff: noqa: E501 — HTML e CSS embutidos em linhas longas (protótipo).
"""Protótipo estático: conclusão e confirmação da pesquisa (auditoria de 2026-10-12).

Conceitual. Cada tela usa o shell e as folhas **reais** da jornada (`estilo.css`, `jornada.css`,
assinatura), incluídos inline como em `interface/base.html`. "atual-*" reproduz o HTML de
`conclusao.html` e `concluida.html` de hoje; "proposta-*" troca só o conteúdo principal, com
uma folha própria feita só de tokens existentes. Sem JavaScript (023 FR-035). Os dados são da
persona fictícia Ana (TADS, Serra, 2022), no percurso "trabalha e estuda" (9 partes).

Nada aqui é importado pela aplicação, e as telas servidas não mudam: não é implementação.

Uso, na raiz do repositório (não precisa de banco nem de `.env`):

    uv run python docs/prototipos/2026-10-12-conclusao/gerar.py
"""

from html import escape
from pathlib import Path

PASTA = Path(__file__).resolve().parent
RAIZ = PASTA.parents[2]
INTERFACE = RAIZ / "trajetoria/interface/templates/interface"

CURSO = "Tecnologia em Análise e Desenvolvimento de Sistemas"
RESUMO = f"{CURSO} · Serra · 2022"
CONTEXTO = [
    ("Curso", CURSO),
    ("Unidade", "Serra"),
    ("Data de conclusão", "16/12/2022"),
    ("Nível", "Graduação"),
    ("Modalidade", "Presencial"),
]
# Percurso de Ana na Versão 2024: os títulos são os da Versão; a Seção 13 do original não
# tem título (inventário, E-11) e vira "Parte 9" (023 FR-015).
SECOES = [
    "Termos e condições",
    "Informações Pessoais",
    "Informações do curso",
    "Graduação",
    "Avaliação",
    "Egresso que trabalha",
    "Estudo",
    "Egresso que estuda",
    None,
]
ENCERRAMENTO = [
    "Este formulário chegou ao fim!",
    "Agradecemos imensamente a atenção dispensada e a participação na pesquisa.",
]
NAVEGACAO = ["Início", "Minha trajetória", "Oportunidades", "Encontros", "Participação"]


def e(t) -> str:
    return escape(str(t), quote=True)


CSS_PROPOSTA = """
/* Protótipo 2026-10-12 — só tokens de estilo.css; nada é comunicado só por cor. */
.prototipo { background: #1b1b1b; color: #fff; padding: .5rem 1rem; margin: 0; font-size: .875rem;
  line-height: 1.4; text-align: center; }
.prototipo strong { color: #ffdd00; }

/* Conclusão: contexto → revisão (recolhida) → decisão. */
.etapa { margin: 0 0 var(--espaco-1); font-size: var(--fonte-5); color: var(--cor-texto-suave); }
.contexto-compacto { margin-bottom: var(--espaco-5); }
details.revisao {
  border-top: var(--borda-fina) solid var(--cor-borda-suave);
  border-bottom: var(--borda-fina) solid var(--cor-borda-suave);
  margin: 0 0 var(--espaco-5);
}
/* Resumo com o marcador nativo (list-item), alvo de 44 px pelo preenchimento. */
details.revisao summary {
  cursor: pointer; color: var(--cor-acao); font-weight: var(--peso-medio);
  padding: var(--espaco-3) 0; min-height: var(--alvo);
}
details.revisao summary .quantas { color: var(--cor-texto-suave); font-weight: var(--peso-normal);
  font-size: var(--fonte-5); }
details.revisao > p { margin: 0 0 var(--espaco-3); font-size: var(--fonte-5); color: var(--cor-texto-suave); }
.lista-revisao { list-style: none; margin: 0 0 var(--espaco-3); padding: 0;
  display: grid; grid-template-columns: repeat(auto-fill, minmax(min(15rem, 100%), 1fr)); gap: 0 var(--espaco-5); }
.lista-revisao li { border-top: var(--borda-fina) solid var(--cor-borda-suave);
  display: flex; flex-direction: column; justify-content: center; padding: var(--espaco-1) 0; }
.lista-revisao a { display: flex; align-items: center; min-height: var(--alvo); }
.lista-revisao .numero { font-size: var(--fonte-5); color: var(--cor-texto-suave); padding-top: var(--espaco-1); }

.decisao { margin: 0; }
.decisao > p { margin: 0 0 var(--espaco-3); }
.decisao .acoes { margin-top: 0; }

/* Confirmação: registro → encerramento da Versão → continuidade no Portal. */
.continuidade { margin: var(--espaco-6) 0 var(--espaco-5); padding-top: var(--espaco-5);
  border-top: var(--borda-fina) solid var(--cor-borda-suave); }
.continuidade h2 { margin: 0 0 var(--espaco-3); font-size: var(--fonte-3, 1.125rem); }
a.botao { display: inline-flex; align-items: center; justify-content: center; min-height: var(--alvo);
  padding: var(--espaco-2) var(--espaco-5); border-radius: var(--raio); background: var(--cor-acao);
  color: var(--cor-fundo); font-weight: var(--peso-forte); text-decoration: none; }
a.botao:hover { background: var(--cor-acao-forte); color: var(--cor-fundo); }
.continuidade .nota { margin-top: var(--espaco-4); }
@media (max-width: 30em) { a.botao { width: 100%; } }
"""


def pagina(titulo: str, conteudo: str, *, portal: bool = False, aviso: str = "") -> str:
    estilo = (INTERFACE / "estilo.css").read_text()
    jornada = (INTERFACE / "jornada.css").read_text()
    assinatura = (INTERFACE / "assinatura.svg").read_text()
    if portal:
        produto = '<span class="nome">Portal do Egresso</span> <span class="subtitulo">Instituto Federal do Espírito Santo</span>'
        itens = "".join(
            f'<li><a href="#" data-rotulo="{e(r)}"{" aria-current=\"page\"" if r == "Participação" else ""}>{e(r)}</a></li>'
            for r in NAVEGACAO
        )
        navegacao = f'<nav class="navegacao" aria-label="Portal do Egresso"><div class="coluna"><ul>{itens}</ul></div></nav>'
    else:
        produto = '<span class="nome">Trajetória Ifes</span> <span class="subtitulo">Acompanhamento de egressos</span>'
        navegacao = ""
    faixa = f'<p class="prototipo"><strong>Protótipo</strong> — {e(aviso)}</p>' if aviso else ""
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titulo)} — Trajetória Ifes (demonstração) — protótipo 2026-10-12</title>
<style>{estilo}
{jornada}
{CSS_PROPOSTA}</style>
</head>
<body>
{faixa}
<a class="pular" href="#conteudo">Pular para o conteúdo</a>
<div class="faixa-demonstracao" role="note">
  <div class="coluna">
    <p><strong>Ambiente de demonstração.</strong> Todos os dados são fictícios. A confirmação usa CPF e data de nascimento fictícios e não é autenticação forte.</p>
    <p class="pessoa">Pessoa fictícia: Ana Exemplo</p>
    <form><button type="button">Sair</button></form>
  </div>
</div>
<header class="produto">
  <div class="coluna">
    <span class="assinatura" role="img" aria-label="Instituto Federal do Espírito Santo">
{assinatura}
    </span>
    <p class="produto-nome">{produto}</p>
  </div>
</header>{navegacao}
<main id="conteudo" tabindex="-1">
  <div class="coluna">
{conteudo}
  </div>
</main>
<footer class="rodape">
  <div class="coluna">
    <p>Instituto Federal do Espírito Santo</p>
    <p class="ambiente">Trajetória Ifes — demonstração local com dados fictícios.</p>
  </div>
</footer>
</body>
</html>
"""


def contexto_completo() -> str:
    linhas = "".join(f"<dt>{e(r)}</dt><dd>{e(v)}</dd>" for r, v in CONTEXTO)
    return f'<section class="contexto" aria-labelledby="titulo-contexto"><h2 id="titulo-contexto">Sobre a sua formação</h2><dl>{linhas}</dl></section>'


def contexto_compacto() -> str:
    return f'<section class="contexto contexto-compacto" aria-labelledby="titulo-contexto"><p><strong id="titulo-contexto">Você está respondendo sobre:</strong> {e(RESUMO)}</p></section>'


# --- Hoje (reprodução de conclusao.html e concluida.html) ------------------------------------


def atual_conclusao() -> str:
    itens = "".join(
        f'<li><a href="#">{e(t or f"Parte {n}")}</a></li>' for n, t in enumerate(SECOES, 1)
    )
    return f"""<h1>Concluir a pesquisa</h1>
<p>Você chegou ao fim da pesquisa. Depois de concluída, ela não poderá ser alterada.</p>
<form><div class="acoes"><button type="button" class="primario">Concluir pesquisa</button></div></form>
<p>Se quiser revisar alguma resposta antes de concluir, volte a uma das partes:</p>
<ul class="lista-secoes">{itens}</ul>
{contexto_completo()}"""


def atual_concluida() -> str:
    encerramento = "".join(f"<p>{e(p)}</p>" for p in ENCERRAMENTO)
    return f"""<div class="confirmacao">
<h1>Pesquisa concluída</h1>
<p>Suas respostas sobre {e(CURSO)} foram registradas.</p>
</div>
<div class="encerramento">{encerramento}</div>
<p><a href="#">Ver minha trajetória no Ifes</a></p>
<p class="nota convite-contato"><a href="#">Quer manter seu e-mail atualizado com o Ifes?</a></p>
{contexto_completo()}"""


# --- Proposta ---------------------------------------------------------------------------------


def proposta_conclusao(aberta: bool) -> str:
    itens = []
    for n, titulo in enumerate(SECOES, 1):
        if titulo:
            # O número fica fora do link: o nome acessível é só o título da Seção.
            itens.append(f'<li><span class="numero">Parte {n}</span><a href="#">{e(titulo)}</a></li>')
        else:
            # Sem título na Versão: "Parte X", como hoje (023 FR-015). O trecho da primeira
            # Pergunta foi descartado: o enunciado literal começa por "Indique o seu grau de
            # concordância com a afirmação…", igual ao de outras Perguntas (auditoria, D2).
            itens.append(f'<li><a href="#">Parte {n}</a></li>')
    return f"""<p class="etapa">Última etapa</p>
<h1>Concluir a pesquisa</h1>
<p>Você chegou ao fim da pesquisa. Falta só enviar suas respostas.</p>
{contexto_compacto()}
<details class="revisao"{" open" if aberta else ""}>
  <summary>Revisar respostas antes de enviar <span class="quantas">· {len(SECOES)} partes</span></summary>
  <p>Ao abrir uma parte, suas respostas aparecem como você deixou.</p>
  <ol class="lista-revisao">{"".join(itens)}</ol>
</details>
<div class="decisao">
  <p>Depois de concluída, a pesquisa não poderá ser alterada.</p>
  <form><div class="acoes"><button type="button" class="primario">Concluir pesquisa</button></div></form>
</div>"""


def proposta_concluida() -> str:
    encerramento = "".join(f"<p>{e(p)}</p>" for p in ENCERRAMENTO)
    return f"""<div class="confirmacao">
<h1>Pesquisa concluída</h1>
<p>Suas respostas sobre {e(CURSO)} foram registradas.</p>
</div>
<div class="encerramento">{encerramento}</div>
<section class="continuidade" aria-labelledby="titulo-continuidade">
  <h2 id="titulo-continuidade">No Portal do Egresso</h2>
  <p><a class="botao" href="#">Ver minha trajetória no Ifes</a></p>
  <p class="nota convite-contato"><a href="#">Quer manter seu e-mail atualizado com o Ifes?</a></p>
</section>"""


TELAS = {
    "atual-conclusao.html": ("Concluir a pesquisa", atual_conclusao(), False, "tela de hoje, reproduzida"),
    "proposta-conclusao.html": ("Concluir a pesquisa", proposta_conclusao(False), False, "proposta, revisão recolhida (não existe na aplicação)"),
    "proposta-conclusao-revisao.html": ("Concluir a pesquisa", proposta_conclusao(True), False, "proposta, revisão aberta (não existe na aplicação)"),
    "atual-concluida.html": ("Pesquisa concluída", atual_concluida(), True, "tela de hoje, reproduzida"),
    "proposta-concluida.html": ("Pesquisa concluída", proposta_concluida(), True, "proposta (não existe na aplicação)"),
}


def main() -> None:
    for nome, (titulo, conteudo, portal, aviso) in TELAS.items():
        (PASTA / nome).write_text(pagina(titulo, conteudo, portal=portal, aviso=aviso))
        print(PASTA / nome)


if __name__ == "__main__":
    main()
