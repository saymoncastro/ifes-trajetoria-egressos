"""Comando `preparar_demonstracao` (008 US1; FR-012 a FR-018; research R17)."""

from datetime import timedelta
from io import StringIO

import pytest
from django.core.management import CommandError, call_command
from django.utils import timezone

from tests.interface import construcao_interface as ci
from tests.participacao import construcao_entrada as ce
from trajetoria.academico.models import ConclusaoAcademica, Pessoa
from trajetoria.campanha.consultas import EstadoCampanha, estado
from trajetoria.campanha.models import Campanha
from trajetoria.campanha.operacoes import encerrar
from trajetoria.formulario_2024.declaracao import DESIGNACAO
from trajetoria.instrumento.models import EstadoVersao, Versao
from trajetoria.participacao.entrada import (
    ResolucaoDaEntrada,
    SituacaoDaFormacao,
    situacao_de_entrada,
)
from trajetoria.participacao.models import Participacao, Resposta

pytestmark = pytest.mark.django_db

AMPLA = "Demonstração — coleta ampla"
SOBREPOSTA = "Demonstração — coleta sobreposta"


def preparar() -> str:
    saida = StringIO()
    call_command("preparar_demonstracao", stdout=saida)
    return saida.getvalue()


def contagens() -> dict:
    return {m.__name__: m.objects.count() for m in (Pessoa, ConclusaoAcademica, Versao, Campanha)}


def test_recusa_com_o_modo_desligado(settings):
    settings.TRAJETORIA_DEMONSTRACAO = False
    with pytest.raises(CommandError, match="modo de demonstração está desligado"):
        preparar()
    assert contagens() == {"Pessoa": 0, "ConclusaoAcademica": 0, "Versao": 0, "Campanha": 0}


@pytest.mark.parametrize("modelo", ["pessoa", "conclusao"])
def test_recusa_banco_com_dados_de_outra_fonte(modelo):
    pessoa = ce.pessoa()  # fonte "teste-entrada"
    if modelo == "conclusao":
        pessoa.fonte = "simulada"
        pessoa.save()
        ce.formacao(pessoa)  # Conclusão de fonte "teste-participacao"
    antes = contagens()
    with pytest.raises(CommandError, match="não são da fonte simulada"):
        preparar()
    assert contagens() == antes


def test_prepara_o_cenario_so_com_as_operacoes_existentes():
    saida = preparar()
    hoje = timezone.localdate()
    assert Pessoa.objects.filter(fonte="simulada").count() == 9
    assert not Pessoa.objects.filter(id_externo__in=["SIM-P-0006", "SIM-P-0008"]).exists()
    assert Versao.objects.get(designacao=DESIGNACAO).estado == EstadoVersao.RASCUNHO
    demo = Versao.objects.get(designacao="Demonstração — cópia da referência 2024")
    assert demo.estado == EstadoVersao.PUBLICADA
    ampla, sobreposta = Campanha.objects.get(nome=AMPLA), Campanha.objects.get(nome=SOBREPOSTA)
    for campanha in (ampla, sobreposta):
        assert campanha.versao == demo
        assert (campanha.inicio, campanha.fim) == (hoje, hoje + timedelta(days=180))
        assert estado(campanha) is EstadoCampanha.EM_COLETA
    assert ampla.ano_minimo == 2015 and ampla.ano_maximo is None
    # A 004 guarda o conjunto ordenado (research R11 da 004).
    unidades = ["Serra", "Cefor", "Vila Velha", "Alegre", "Cariacica", "Colatina"]
    assert ampla.unidades == sorted(unidades)
    assert ampla.niveis is None
    assert sobreposta.unidades == ["Vila Velha"] and sobreposta.niveis == ["Pós-graduação"]
    assert sobreposta.ano_minimo is None
    assert not Participacao.objects.exists() and not Resposta.objects.exists()
    assert "Ana Exemplo" in saida and ci.tecnicos_em(saida.replace(AMPLA, "")) == []


def _situacao(id_externo):
    return situacao_de_entrada(ce.pessoa_da_fonte(id_externo))


def _por_curso(situacao):
    return {f.conclusao.curso: f.situacao for f in situacao.formacoes}


def test_situacoes_da_tabela_r17():
    preparar()
    R, F = ResolucaoDaEntrada, SituacaoDaFormacao
    assert _situacao("SIM-P-0001").resolucao is R.ENTRADA_RESOLVIDA
    assert _situacao("SIM-P-0003").resolucao is R.SELECAO_NECESSARIA
    diego = _situacao("SIM-P-0004")
    assert diego.resolucao is R.ENTRADA_RESOLVIDA
    assert _por_curso(diego) == {
        "Técnico em Química": F.SEM_PESQUISA,
        "Licenciatura em Química": F.DISPONIVEL_PARA_INICIAR,
        "Mestrado Profissional em Química": F.AMBIGUIDADE_OPERACIONAL,
    }
    for id_externo in ("SIM-P-0002", "SIM-P-0010"):
        assert _situacao(id_externo).resolucao is R.SEM_PESQUISA
    for id_externo in ("SIM-P-0011", "SIM-P-0005", "SIM-P-0007", "SIM-P-0009"):
        assert _situacao(id_externo).resolucao is R.ENTRADA_RESOLVIDA


def test_idempotente():
    preparar()
    antes = contagens()
    preparar()
    assert contagens() == antes


def test_recusa_campanha_de_demonstracao_fora_de_coleta():
    preparar()
    encerrar(Campanha.objects.get(nome=AMPLA))
    antes = contagens()
    with pytest.raises(CommandError, match="Recrie o banco local"):
        preparar()
    assert contagens() == antes


def test_recusa_de_operacao_de_dominio_vira_mensagem(monkeypatch):
    from trajetoria.formulario_2024.materializacao import BaselineDivergente

    def recusa():
        raise BaselineDivergente("forma divergente")

    monkeypatch.setattr("trajetoria.demonstracao.cenario.materializar", recusa)
    with pytest.raises(CommandError, match="Recrie o banco local"):
        preparar()
    assert contagens() == {"Pessoa": 0, "ConclusaoAcademica": 0, "Versao": 0, "Campanha": 0}
