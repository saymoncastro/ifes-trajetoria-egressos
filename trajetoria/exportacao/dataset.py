"""Dataset lógico da exportação (data-model; contracts/exportacao.md).

Três tabelas — Dados, Dicionário, Metadados — de valores Python tipados: `None` (ausência),
`bool`, `int`, `date`, `datetime` com fuso e `str`. O tipo Python decide a representação em
cada formato (research R3); os formatos só serializam, sem decidir valor.

**Fonte** (research R1): a fronteira de leitura da 012 (`linhas_do_dataset`, que recebe o
conteúdo já lido para não relê-lo), o conteúdo imutável da Versão (002) e os campos da
Campanha fixados na abertura. As contagens dos Metadados derivam das próprias linhas. A
única leitura da 001 é a referência Conclusão → Pessoa, para o pseudônimo (spec FR-028).
Nunca: contexto atual, população atual, `encerrada_em`, nome da Pesquisa.

**Colunas de Pergunta** (data-model §1.2): derivam só da Versão — Perguntas sem Resposta têm
as mesmas colunas —, com chave técnica pelo identificador local à Versão, nunca pelo texto
(spec FR-031). **Aplicabilidade** (spec FR-047): pertença ao percurso calculado pela 006 e
entregue pela 012 (`perguntas_do_percurso`); valor só aparece com aplicabilidade verdadeira.

**Nada grava** (spec FR-005, FR-114): nem banco, nem disco, nem log.
"""

from dataclasses import dataclass
from datetime import datetime

from django.utils import timezone

from trajetoria.analitico.consultas import linhas_do_dataset
from trajetoria.analitico.models import RegistroDoSnapshot, SnapshotAnalitico
from trajetoria.exportacao.contrato import (
    CABECALHO_DICIONARIO,
    CABECALHO_METADADOS,
    COLUNAS_BASE,
    DESCRICAO_APLICABILIDADE,
    DESCRICAO_COMPLEMENTO,
    DESCRICAO_OPCAO,
    DESCRICAO_VALOR,
    DESCRICAO_VALOR_POSSIVEL,
    ESQUEMA_PSEUDONIMIZACAO,
    NOTAS,
    TIPOS_DE_PERGUNTA,
    VERSAO_CONTRATO,
)
from trajetoria.exportacao.pseudonimos import chave_de_pseudonimizacao, pseudonimo
from trajetoria.exportacao.regras import ExportacaoInconsistente, ExportacaoRecusada, Motivo
from trajetoria.instrumento.conteudo import conteudo_da_versao
from trajetoria.instrumento.models import EstadoVersao, TipoPergunta

__all__ = ["DatasetExportado", "Tabela", "dataset_exportado"]


@dataclass(frozen=True)
class Tabela:
    cabecalho: tuple[str, ...]
    linhas: tuple[tuple, ...]


@dataclass(frozen=True)
class DatasetExportado:
    dados: Tabela
    dicionario: Tabela
    metadados: Tabela
    capturado_em: datetime  # momento da captura, na timezone institucional (também nos Metadados)


def dataset_exportado(snapshot: SnapshotAnalitico) -> DatasetExportado:
    """O dataset lógico do snapshot recebido (contracts/exportacao.md, "Passos")."""
    if not isinstance(snapshot, SnapshotAnalitico):
        raise TypeError(f"snapshot deve ser SnapshotAnalitico, não {type(snapshot).__name__}")
    gravado = (
        SnapshotAnalitico.objects.select_related("campanha__versao").filter(pk=snapshot.pk).first()
        if snapshot.pk is not None
        else None
    )
    if gravado is None:
        raise ExportacaoRecusada(Motivo.SNAPSHOT_NAO_GRAVADO)
    chave = chave_de_pseudonimizacao()  # antes de qualquer leitura de linha
    snapshot, campanha = gravado, gravado.campanha
    conteudo = conteudo_da_versao(campanha.versao)
    if conteudo.estado != EstadoVersao.PUBLICADA:
        raise ExportacaoInconsistente(f"snapshot {snapshot.pk}: a Versão não está publicada")

    grupos = tuple(
        _Grupo(snapshot.pk, secao, pergunta)
        for secao in conteudo.secoes
        for pergunta in secao.perguntas
    )
    colunas = _colunas_base() + tuple(c for g in grupos for c in g.colunas)
    _exigir_nomes_unicos(snapshot, colunas)

    pessoas = dict(
        RegistroDoSnapshot.objects.filter(snapshot=snapshot).values_list(
            "conclusao_id", "conclusao__pessoa_id"
        )
    )
    montagem = _Montagem(snapshot.pk, grupos, pessoas, chave)
    linhas = tuple(
        montagem.linha(linha) for linha in linhas_do_dataset(snapshot, conteudo=conteudo)
    )

    return DatasetExportado(
        dados=Tabela(tuple(c.nome for c in colunas), linhas),
        dicionario=Tabela(CABECALHO_DICIONARIO, _dicionario(conteudo, colunas)),
        metadados=Tabela(
            CABECALHO_METADADOS,
            _metadados(snapshot, conteudo, montagem, len(colunas)),
        ),
        capturado_em=timezone.localtime(snapshot.capturado_em),
    )


# --- Colunas -----------------------------------------------------------------------------------


@dataclass(frozen=True)
class _Coluna:
    """Uma coluna de Dados e o que o Dicionário diz dela. `papel`: `base`, `aplicabilidade`,
    `valor`, `opcao` ou `complemento`."""

    nome: str
    papel: str
    tipo_valor: str
    proveniencia: str
    descricao: str
    secao: object = None  # ConteudoSecao
    pergunta: object = None  # ConteudoPergunta
    opcao: object = None  # ConteudoOpcao


def _colunas_base() -> tuple:
    return tuple(
        _Coluna(b.nome, "base", b.tipo_valor, b.proveniencia, b.descricao) for b in COLUNAS_BASE
    )


def _exigir_nomes_unicos(snapshot, colunas) -> None:
    nomes = [c.nome for c in colunas]
    if len(set(nomes)) != len(nomes):
        raise ExportacaoInconsistente(f"snapshot {snapshot.pk}: nome de coluna repetido")


class _Grupo:
    """As colunas de uma Pergunta (aplicabilidade, valor ou Opções, complemento) e a leitura
    de uma Resposta nelas, com validação de forma (research R7). Sem hierarquia de tipos: um
    `if` por tipo, só os quatro existentes (spec FR-030)."""

    def __init__(self, snapshot_id, secao, pergunta):
        if pergunta.tipo not in TIPOS_DE_PERGUNTA:
            raise ExportacaoInconsistente(
                f"snapshot {snapshot_id}: Pergunta {pergunta.id} de tipo desconhecido"
            )
        self.snapshot_id, self.secao, self.pergunta = snapshot_id, secao, pergunta
        self.com_complemento = any(o.complemento_textual for o in pergunta.opcoes)
        base = f"pergunta_{pergunta.id.hex}"
        colunas = [
            self._coluna(
                f"{base}__aplicavel",
                "aplicabilidade",
                "booleano",
                "derivado",
                DESCRICAO_APLICABILIDADE,
            )
        ]
        if pergunta.tipo == TipoPergunta.ESCOLHA_MULTIPLA:
            colunas += [
                self._coluna(
                    f"{base}__opcao_{o.id.hex}",
                    "opcao",
                    "booleano",
                    "declarado",
                    DESCRICAO_OPCAO,
                    o,
                )
                for o in pergunta.opcoes
            ]
        else:
            tipo = "inteiro" if pergunta.tipo == TipoPergunta.ESCALA else "texto"
            colunas.append(self._coluna(base, "valor", tipo, "declarado", DESCRICAO_VALOR))
        if self.com_complemento:
            outro = next(o for o in pergunta.opcoes if o.complemento_textual)
            colunas.append(
                self._coluna(
                    f"{base}__complemento",
                    "complemento",
                    "texto",
                    "declarado",
                    DESCRICAO_COMPLEMENTO,
                    outro,
                )
            )
        self.colunas = tuple(colunas)

    def _coluna(self, nome, papel, tipo_valor, proveniencia, descricao, opcao=None) -> _Coluna:
        return _Coluna(
            nome, papel, tipo_valor, proveniencia, descricao, self.secao, self.pergunta, opcao
        )

    def vazio(self) -> list:
        return [None] * len(self.colunas)

    def valores(self, aplicavel: bool, resposta) -> list:
        if not aplicavel or resposta is None:
            return [aplicavel] + [None] * (len(self.colunas) - 1)
        tipo = self.pergunta.tipo
        if tipo == TipoPergunta.ESCOLHA_UNICA:
            self._exigir(resposta.opcao is not None and not resposta.opcoes, "sem uma Opção")
            self._exigir(resposta.texto is None and resposta.escala is None, "forma incompatível")
            self._exigir_da_pergunta(resposta.opcao)
            valores = [resposta.opcao.texto]
            escolhidas = (resposta.opcao,)
        elif tipo == TipoPergunta.ESCOLHA_MULTIPLA:
            self._exigir(bool(resposta.opcoes) and resposta.opcao is None, "sem Opções")
            self._exigir(resposta.texto is None and resposta.escala is None, "forma incompatível")
            for opcao in resposta.opcoes:
                self._exigir_da_pergunta(opcao)
            ids = {o.pk for o in resposta.opcoes}
            valores = [o.id in ids for o in self.pergunta.opcoes]
            escolhidas = resposta.opcoes
        else:
            campo, outro = (
                ("escala", "texto") if tipo == TipoPergunta.ESCALA else ("texto", "escala")
            )
            valor = getattr(resposta, campo)
            self._exigir(
                valor is not None and getattr(resposta, outro) is None, "forma incompatível"
            )
            self._exigir(resposta.opcao_id is None and not resposta.opcoes, "forma incompatível")
            self._exigir(resposta.complemento is None, "complemento não admitido")
            return [True, valor]
        if resposta.complemento is not None:
            admitido = any(o.complemento_textual for o in escolhidas)
            self._exigir(self.com_complemento and admitido, "complemento não admitido")
        complemento = [resposta.complemento] if self.com_complemento else []
        return [True, *valores, *complemento]

    def _exigir(self, condicao: bool, motivo: str) -> None:
        if not condicao:
            raise ExportacaoInconsistente(
                f"snapshot {self.snapshot_id}: Resposta à Pergunta {self.pergunta.id}: {motivo}"
            )

    def _exigir_da_pergunta(self, opcao) -> None:
        if opcao.pergunta_id != self.pergunta.id:
            raise ExportacaoInconsistente(
                f"snapshot {self.snapshot_id}: Opção {opcao.pk} não é da Pergunta "
                f"{self.pergunta.id}"
            )


# --- Dados -----------------------------------------------------------------------------------


class _Montagem:
    """Monta as linhas de Dados e conta as Participações com percurso não determinável."""

    def __init__(self, snapshot_id, grupos, pessoas: dict, chave: str):
        self.snapshot_id = snapshot_id
        self.grupos = grupos
        self.pessoas = pessoas  # conclusao_id → pessoa_id (só a referência)
        self.chave = chave
        self.nao_determinaveis = 0
        self.contagens = dict.fromkeys(
            (
                "registros",
                "elegiveis",
                "nao_elegiveis_com_participacao",
                "com_participacao",
                "concluidas",
            ),
            0,
        )

    def linha(self, linha) -> tuple:
        contexto = linha.contexto
        participacao = linha.participacao
        self._contar(linha.elegivel_no_snapshot, participacao)
        return (
            pseudonimo("conclusao", linha.conclusao_id, self.chave),
            pseudonimo("pessoa", self.pessoas[linha.conclusao_id], self.chave),
            linha.elegivel_no_snapshot,
            contexto.unidade,
            contexto.curso,
            contexto.nivel,
            contexto.modalidade,
            contexto.forma_oferta,
            contexto.ano_conclusao,
            contexto.data_conclusao,
            participacao is not None,
            *_estado(participacao),
            *self._perguntas(linha),
        )

    def _contar(self, elegivel: bool, participacao) -> None:
        """As contagens dos Metadados, sobre as próprias linhas: as mesmas definições da 012
        (iniciada = Participação existente; concluída inclusive por recusa)."""
        c = self.contagens
        c["registros"] += 1
        c["elegiveis"] += elegivel
        if participacao is not None:
            c["com_participacao"] += 1
            c["nao_elegiveis_com_participacao"] += not elegivel
            c["concluidas"] += participacao.concluida

    def _perguntas(self, linha) -> list:
        """Preenchimento de data-model §1.3."""
        percurso = linha.perguntas_do_percurso
        if linha.participacao is None:
            return [v for g in self.grupos for v in g.vazio()]
        if percurso is None:
            self._exigir(not linha.participacao.concluida, "concluída sem percurso determinável")
            self.nao_determinaveis += 1
            return [v for g in self.grupos for v in g.vazio()]
        if linha.participacao.concluida:
            self._exigir(
                set(linha.respostas) <= percurso, "concluída com Resposta fora do percurso"
            )
        return [
            valor
            for g in self.grupos
            for valor in g.valores(g.pergunta.id in percurso, linha.respostas.get(g.pergunta.id))
        ]

    def _exigir(self, condicao: bool, motivo: str) -> None:
        if not condicao:
            raise ExportacaoInconsistente(f"snapshot {self.snapshot_id}: {motivo}")


def _estado(participacao) -> tuple:
    """`participacao_concluida`, `participacao_iniciada_em`, `participacao_concluida_em`:
    fatos registrados, sem categoria inventada (spec FR-024). Datas civis na timezone
    institucional (spec FR-025)."""
    if participacao is None:
        return None, None, None
    concluida_em = participacao.concluida_em
    return (
        participacao.concluida,
        timezone.localtime(participacao.iniciada_em).date(),
        None if concluida_em is None else timezone.localtime(concluida_em).date(),
    )


# --- Dicionário ------------------------------------------------------------------------------


def _linha_do_dicionario(**campos) -> tuple:
    return tuple(campos.get(nome) for nome in CABECALHO_DICIONARIO)


def _dicionario(conteudo, colunas) -> tuple:
    """Uma linha `coluna` por coluna de Dados, na mesma ordem; após a coluna de valor de cada
    escolha única, uma linha `valor_possivel` por Opção (data-model §2). Regras e
    encaminhamentos pela **posição** da Seção de destino, resolvida no próprio conteúdo."""
    versao = str(conteudo.id)
    posicoes = {secao.id: secao.posicao for secao in conteudo.secoes}
    linhas = []
    for ordem, coluna in enumerate(colunas, start=1):
        comuns = dict(
            coluna=coluna.nome,
            ordem=ordem,
            tipo_valor=coluna.tipo_valor,
            proveniencia=coluna.proveniencia,
            versao=versao,
        )
        campos = dict(comuns, elemento="coluna", descricao=coluna.descricao)
        pergunta = coluna.pergunta
        if pergunta is not None:
            campos.update(_campos_da_pergunta(coluna.secao, pergunta, posicoes))
        if coluna.opcao is not None:
            campos.update(_campos_da_opcao(coluna.opcao, posicoes))
        linhas.append(_linha_do_dicionario(**campos))
        if coluna.papel == "valor" and pergunta.tipo == TipoPergunta.ESCOLHA_UNICA:
            linhas.extend(
                _linha_do_dicionario(
                    **comuns,
                    elemento="valor_possivel",
                    descricao=DESCRICAO_VALOR_POSSIVEL,
                    **_campos_da_pergunta(coluna.secao, pergunta, posicoes),
                    **_campos_da_opcao(opcao, posicoes),
                )
                for opcao in pergunta.opcoes
            )
    return tuple(linhas)


def _campos_da_pergunta(secao, pergunta, posicoes) -> dict:
    campos = dict(
        secao_posicao=secao.posicao,
        secao_titulo=secao.titulo,
        secao_encaminhamento_destino=posicoes.get(secao.encaminhamento_id),
        pergunta_posicao=pergunta.posicao,
        pergunta_tipo=TIPOS_DE_PERGUNTA[pergunta.tipo],
        pergunta_texto=pergunta.texto,
        pergunta_texto_explicativo=pergunta.texto_explicativo,
        pergunta_obrigatoria=pergunta.obrigatoria,
    )
    if pergunta.escala is not None:
        campos.update(
            escala_inicio=pergunta.escala.inicio,
            escala_fim=pergunta.escala.fim,
            escala_rotulo_inicio=pergunta.escala.rotulo_inicio,
            escala_rotulo_fim=pergunta.escala.rotulo_fim,
        )
    return campos


def _campos_da_opcao(opcao, posicoes) -> dict:
    regra = opcao.regra
    return dict(
        opcao_posicao=opcao.posicao,
        opcao_texto=opcao.texto,
        opcao_admite_complemento=opcao.complemento_textual,
        opcao_regra_finaliza=regra is not None and regra.finaliza,
        opcao_regra_destino_secao=(
            None if regra is None or regra.finaliza else posicoes[regra.destino_secao_id]
        ),
    )


# --- Metadados -------------------------------------------------------------------------------


def _metadados(snapshot, conteudo, montagem, colunas: int) -> tuple:
    """As 27 linhas de data-model §3, todas fixas para o snapshot (spec FR-063): fatos do
    snapshot, da Campanha fixados na abertura e da Versão publicada, contagens derivadas das
    linhas montadas e constantes. Nunca o nome da Pesquisa (mutável), o encerramento
    explícito (pode ser gravado depois da captura) nem o momento da exportação."""
    campanha = snapshot.campanha
    local = timezone.localtime
    contagens = montagem.contagens
    linhas = [
        ("contrato_versao", VERSAO_CONTRATO, "inteiro"),
        ("pseudonimizacao_esquema", ESQUEMA_PSEUDONIMIZACAO, "texto"),
        ("finalidade", NOTAS["finalidade"], "texto"),
        ("snapshot", str(snapshot.pk), "texto"),
        ("capturado_em", local(snapshot.capturado_em), "momento"),
        ("campanha", str(campanha.pk), "texto"),
        ("campanha_nome", campanha.nome, "texto"),
        ("campanha_inicio", campanha.inicio, "data"),
        ("campanha_fim", campanha.fim, "data"),
        ("campanha_aberta_em", local(campanha.aberta_em), "momento"),
        ("versao", str(conteudo.id), "texto"),
        ("versao_designacao", conteudo.designacao, "texto"),
        ("versao_titulo", conteudo.titulo, "texto"),
        ("versao_publicada_em", local(conteudo.publicada_em), "momento"),
        ("registros", contagens["registros"], "inteiro"),
        ("elegiveis_no_snapshot", contagens["elegiveis"], "inteiro"),
        ("nao_elegiveis_com_participacao", contagens["nao_elegiveis_com_participacao"], "inteiro"),
        ("com_participacao", contagens["com_participacao"], "inteiro"),
        ("participacoes_concluidas", contagens["concluidas"], "inteiro"),
        ("participacoes_com_percurso_nao_determinavel", montagem.nao_determinaveis, "inteiro"),
        ("colunas_de_dados", colunas, "inteiro"),
    ]
    linhas += [(chave, texto, "texto") for chave, texto in NOTAS.items() if chave != "finalidade"]
    return tuple(linhas)
