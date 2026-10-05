"""Cenário de demonstração (contracts/demonstracao.md; research R17; FR-012 a FR-018).

Preparado por um passo **explícito e local** (`manage.py preparar_demonstracao`), nunca por
migração ou automaticamente. Usa só as operações existentes: incorporação pela fonte
simulada (001), materialização da baseline (003), cópia e publicação de Versão (002),
criação, configuração e abertura de Campanha (004). Nunca cria Participação nem Resposta.

Também registra os vínculos de governança dos operadores fictícios do editor (010): A atua
pela CPAEG, B pela CSAEG da unidade Vitória e C não tem vínculo. São fictícios e não
representam designação institucional real (DP-1002).

Para o acompanhamento da coleta (011), acrescenta uma Campanha fictícia **nunca aberta e sem
período**, com a Versão de referência em rascunho e sem critério. Nunca aberta, ela não admite
Participação (004 FR-053) e não entra em `campanhas_em_coleta_para`.

A "coleta ampla" não tem critério; a "coleta sobreposta" é o único cenário com abrangência
restrita (pós-graduação de Vila Velha) e mantém a ambiguidade operacional da 007 (ADR 0004).

A publicação da cópia é técnica e local, como nos testes das 005–007; a baseline continua em
RASCUNHO e nada disso é publicação institucional (002/DP-001). Idempotente: repetir não
duplica nada. Recomeçar do zero é recriar o banco local — não existe operação para remover
Participações (005 FR-017) nem para reabrir Campanha (004/DP-405).

Depois da incorporação, carrega o contexto da trajetória da 021 (P2) pela fonte simulada de
contexto, separada da fonte acadêmica: cada Pessoa num *savepoint* próprio, e uma falha não
interrompe o preparo nem desfaz a incorporação (021 FR-071). Depois, do mesmo modo, os
contatos fictícios da 020 pela fonte de contatos, também separada da fonte acadêmica.
"""

import logging
from dataclasses import dataclass
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from trajetoria.academico.models import Pessoa
from trajetoria.acesso.chaves import ChavesInvalidas, chaves_de_acesso
from trajetoria.acesso.material import incorporar_com_material
from trajetoria.campanha import operacoes as op_campanha
from trajetoria.campanha.consultas import EstadoCampanha, estado
from trajetoria.campanha.models import Campanha
from trajetoria.campanha.regras import CampanhaRejeitada
from trajetoria.contato.carga import carregar_contatos
from trajetoria.contexto_trajetoria.carga import carregar_contexto
from trajetoria.demonstracao.base import base_somente_simulada
from trajetoria.demonstracao.operador import OPERADORES_FICTICIOS
from trajetoria.fonte_academica import cenarios
from trajetoria.fonte_academica.contatos_simulados import ContatosSimulados
from trajetoria.fonte_academica.contexto_simulado import ContextoSimulado
from trajetoria.fonte_academica.simulada import FonteSimulada
from trajetoria.formulario_2024 import materializar
from trajetoria.formulario_2024.materializacao import MaterializacaoRecusada
from trajetoria.governanca import operacoes as op_governanca
from trajetoria.governanca.consultas import vinculos_ativos
from trajetoria.governanca.models import Papel, VinculoDeGovernanca
from trajetoria.instrumento import operacoes as op_instrumento
from trajetoria.instrumento.models import Versao
from trajetoria.instrumento.regras import OperacaoRejeitada
from trajetoria.participacao.entrada import ResolucaoDaEntrada, situacao_de_entrada

logger = logging.getLogger("trajetoria.demonstracao")

DESIGNACAO_DEMONSTRACAO = "Demonstração — cópia da referência 2024"
VINCULOS = (
    ("demonstracao:operador-a", Papel.CPAEG, ""),
    ("demonstracao:operador-b", Papel.CSAEG, "Vitória"),
)
DURACAO = timedelta(days=180)
# Critério de Campanha é abrangência do instrumento, nunca foco de mobilização (ADR 0004).
# Fora de `CAMPANHAS`: nunca é aberta, então `_exigir_campanhas_em_coleta` não a verifica.
CAMPANHA_ACOMPANHAMENTO = ("Demonstração — rodada em preparação", {})
CAMPANHAS = {
    # Ampla de fato: sem critério, admite qualquer Conclusão Acadêmica.
    "Demonstração — coleta ampla": {},
    # O único cenário restrito: um instrumento que só se aplica à pós-graduação de Vila Velha.
    "Demonstração — coleta sobreposta": {
        "unidades": ["Vila Velha"],
        "niveis": ["Pós-graduação"],
    },
}

_DESCRICAO = {
    ResolucaoDaEntrada.SEM_FORMACAO: "nenhuma formação",
    ResolucaoDaEntrada.SEM_PESQUISA: "sem pesquisa disponível",
    ResolucaoDaEntrada.SEM_ENTRADA_PENDENTE: "nenhuma pesquisa pendente",
    ResolucaoDaEntrada.ENTRADA_RESOLVIDA: "1 formação com pesquisa pendente",
    ResolucaoDaEntrada.SELECAO_NECESSARIA: "escolha entre formações com pesquisa pendente",
}


class PreparoRecusado(Exception):
    """Nada foi alterado."""


@dataclass(frozen=True)
class Resumo:
    linhas: tuple[str, ...]  # "Nome — situação", sem identificadores


def preparar(fonte_de_contexto=None, fonte_de_contatos=None) -> Resumo:
    if not settings.TRAJETORIA_DEMONSTRACAO:
        raise PreparoRecusado(
            "O modo de demonstração está desligado. Defina TRAJETORIA_DEMONSTRACAO=1 num "
            "ambiente local."
        )
    try:
        chaves_de_acesso()
    except ChavesInvalidas:
        raise PreparoRecusado(
            "As chaves de acesso não estão configuradas. Defina "
            "TRAJETORIA_CHAVE_ACESSO_LOCALIZACAO e TRAJETORIA_CHAVE_ACESSO_VERIFICACAO "
            "(valores distintos, com pelo menos 32 caracteres)."
        ) from None
    fonte = FonteSimulada()
    if not base_somente_simulada():
        raise PreparoRecusado(
            "O banco contém dados que não são da fonte simulada. O cenário de demonstração só "
            "é preparado num banco local com dados fictícios."
        )
    ficticios = [o.identificador for o in OPERADORES_FICTICIOS]
    if VinculoDeGovernanca.objects.exclude(identificador_operador__in=ficticios).exists():
        raise PreparoRecusado(
            "O banco contém vínculos de governança que não são fictícios. O cenário de "
            "demonstração só é preparado num banco local com dados fictícios."
        )
    _exigir_campanhas_em_coleta()
    try:
        with transaction.atomic():
            for pessoa in cenarios.PESSOAS:
                if pessoa.id_externo in cenarios.PESSOAS_NAO_PREPARADAS:
                    continue
                incorporar_com_material(fonte, pessoa.id_externo)
            _carregar_contextos(fonte_de_contexto or ContextoSimulado())
            _carregar_contatos(fonte_de_contatos or ContatosSimulados())
            baseline = materializar().versao
            versao = _versao_de_demonstracao(baseline)
            for nome, criterios in CAMPANHAS.items():
                if not Campanha.objects.filter(nome=nome).exists():
                    _abrir_campanha(nome, versao, criterios)
            _campanha_de_acompanhamento(baseline)
            _garantir_vinculos()
    except (
        MaterializacaoRecusada,
        OperacaoRejeitada,
        CampanhaRejeitada,
        op_governanca.VinculoRejeitado,
    ) as erro:
        # Recusa de uma operação de domínio: a transação foi desfeita; nada ficou gravado.
        raise PreparoRecusado(
            f"Uma operação do preparo foi recusada ({erro}). Recrie o banco local e execute o "
            "preparo de novo."
        ) from None
    return _resumo()


def _carregar_contextos(fonte_de_contexto) -> None:
    """021 P2: o contexto da trajetória vem depois da incorporação e à parte dela."""
    for pessoa in Pessoa.objects.filter(fonte=FonteSimulada.codigo).order_by("pk"):
        try:
            with transaction.atomic():
                carregar_contexto(fonte_de_contexto, pessoa)
        except Exception:
            # Sem dado pessoal; a incorporação já feita não é desfeita (FR-071).
            logger.warning("Falha ao carregar o contexto da trajetória no preparo")


def _carregar_contatos(fonte_de_contatos) -> None:
    """020: contatos fictícios depois da incorporação e à parte dela (contrato separado da
    fonte acadêmica). Uma falha não interrompe o preparo nem desfaz a incorporação."""
    for pessoa in Pessoa.objects.filter(fonte=FonteSimulada.codigo).order_by("pk"):
        try:
            with transaction.atomic():
                carregar_contatos(fonte_de_contatos, pessoa)
        except Exception:
            logger.warning("Falha ao carregar contatos no preparo")


def _exigir_campanhas_em_coleta() -> None:
    for campanha in Campanha.objects.filter(nome__in=CAMPANHAS):
        if estado(campanha) is not EstadoCampanha.EM_COLETA:
            raise PreparoRecusado(
                "As Campanhas de demonstração não estão mais em coleta. Recrie o banco local e "
                "execute o preparo de novo."
            )


def _versao_de_demonstracao(baseline: Versao) -> Versao:
    existente = Versao.objects.filter(
        pesquisa_id=baseline.pesquisa_id, designacao=DESIGNACAO_DEMONSTRACAO
    ).first()
    if existente is not None:
        return existente
    copia = op_instrumento.criar_versao_a_partir_de(baseline, DESIGNACAO_DEMONSTRACAO)
    op_instrumento.publicar(copia)
    copia.refresh_from_db()
    return copia


def _garantir_vinculos() -> None:
    """Registra só o que ainda não está ativo: repetir o preparo não muda nada."""
    for identificador, papel, unidade in VINCULOS:
        ativos = vinculos_ativos(identificador)
        if not any(v.papel == papel and v.unidade == unidade for v in ativos):
            op_governanca.registrar_vinculo(identificador, papel, unidade)


def _campanha_de_acompanhamento(baseline: Versao) -> None:
    """Só pelas operações da 004: criar e definir critérios. Sem período e sem abertura."""
    nome, criterios = CAMPANHA_ACOMPANHAMENTO
    if not Campanha.objects.filter(nome=nome).exists():
        campanha = op_campanha.criar_campanha(nome, baseline)
        op_campanha.definir_criterios(campanha, **criterios)


def _abrir_campanha(nome: str, versao: Versao, criterios: dict) -> None:
    hoje = timezone.localdate()
    campanha = op_campanha.criar_campanha(nome, versao)
    op_campanha.definir_periodo(campanha, hoje, hoje + DURACAO)
    op_campanha.definir_criterios(campanha, **criterios)
    op_campanha.abrir(campanha)


def _resumo() -> Resumo:
    linhas = []
    for pessoa in Pessoa.objects.filter(fonte=FonteSimulada.codigo).order_by("nome", "pk"):
        nome = pessoa.nome or "Pessoa fictícia sem nome informado"
        linhas.append(f"{nome} — {_DESCRICAO[situacao_de_entrada(pessoa).resolucao]}")
    return Resumo(tuple(linhas))
