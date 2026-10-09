"""Catálogo fictício de oportunidades da demonstração (025 FR-042; research R4;
contracts/pertinencia.md, "Catálogo fictício").

Carregado pelo sinal `cenario_preparado`, dentro da transação do preparo, só pelas
operações (único caminho de escrita). Idempotente: identificadores `uuid5` fixos; o que já
existe não é tocado. As datas são relativas a `D`, o dia local do preparo. Os endereços usam
o domínio reservado para exemplos, para nunca levar a uma página real como se fosse oficial.
"""

import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta

from django.utils import timezone

from trajetoria.demonstracao.operador import OPERADORES_FICTICIOS
from trajetoria.governanca.regras import EscopoDeAcompanhamento
from trajetoria.portal.models import Categoria, Oportunidade
from trajetoria.portal.oportunidades import operacoes

_NAMESPACE = uuid.UUID("0a1b2c3d-0250-4025-8025-000000000025")
_DOMINIO = "https://oportunidades.example/"
OPERADOR_A, OPERADOR_B = (o.identificador for o in OPERADORES_FICTICIOS[:2])
_ESCOPO_A = EscopoDeAcompanhamento(institucional=True, unidades=frozenset())
_ESCOPO_B = EscopoDeAcompanhamento(institucional=False, unidades=frozenset({"Vitória"}))
TADS = "Tecnologia em Análise e Desenvolvimento de Sistemas"
REDES = "Tecnologia em Redes de Computadores"


@dataclass(frozen=True)
class Item:
    chave: str
    titulo: str
    resumo: str
    categoria: str
    unidade: str
    inicio: int  # dias a partir de D
    fim: int
    publico: dict = field(default_factory=dict)
    publicar_em: int | None = None  # dias a partir de D; None = rascunho
    retirar_em: int | None = None
    operador_b: bool = False


CATALOGO = (
    Item("O1", "Curso de extensão a distância em Ciência de Dados",
         "Curso livre, gratuito e a distância, com certificado do Ifes. Vagas e prazos na "
         "página oficial.", Categoria.CURSOS, "", -7, 60, publicar_em=-7),
    Item("O2", "Especialização em Segurança da Informação",
         "Pós-graduação lato sensu presencial na Serra, com aulas no período noturno.",
         Categoria.CURSOS, "Serra", -3, 45, {"publico_cursos": [REDES, TADS]}, publicar_em=-3),
    Item("O3", "Mestrado Profissional em Educação: seleção aberta",
         "Seleção para o mestrado profissional, com linhas de pesquisa em ensino e formação "
         "docente.", Categoria.CURSOS, "Vitória", -5, 30,
         {"publico_niveis": ["Pós-graduação"]}, publicar_em=-5, operador_b=True),
    Item("O4", "Encontro de egressos das engenharias e edificações",
         "Tarde de conversa com egressos e professores, no campus.", Categoria.EVENTOS,
         "Vitória", -2, 20, {"publico_unidades": ["Vitória"]}, publicar_em=-2, operador_b=True),
    Item("O5", "Programa de mentoria em pesquisa aplicada",
         "Mentoria para projetos de pesquisa aplicada com grupos da unidade.",
         Categoria.PESQUISA_EXTENSAO, "Serra", -6, 40,
         {"publico_niveis": ["Pós-graduação"], "publico_unidades": ["Serra"]}, publicar_em=-6),
    Item("O6", "Programa de estágio em laboratórios parceiros",
         "Estágio supervisionado em laboratórios parceiros da unidade.", Categoria.CARREIRA,
         "Vila Velha", -4, 25,
         {"publico_niveis": ["Técnico"], "publico_unidades": ["Vila Velha"]}, publicar_em=-4),
    Item("O7", "Feira de empreendedorismo e inovação",
         "Feira com projetos de egressos e estudantes, aberta ao público.",
         Categoria.EMPREENDEDORISMO, "", 10, 40, publicar_em=0),
    Item("O8", "Ciclo de palestras de carreira 2026",
         "Palestras sobre carreira e empregabilidade.", Categoria.CARREIRA, "", -40, -1,
         publicar_em=-40),
    Item("O9", "Curso livre de fotografia", "Curso livre de curta duração.", Categoria.OUTRAS,
         "Vitória", -10, 10, publicar_em=-10, retirar_em=-2, operador_b=True),
    Item("O10", "Oficina de currículo (rascunho)", "Oficina prática de currículo.",
         Categoria.CARREIRA, "Vitória", -1, 30, operador_b=True),
)


def identificador(chave: str) -> uuid.UUID:
    return uuid.uuid5(_NAMESPACE, chave)


def _momento(dia: date) -> datetime:
    return timezone.make_aware(datetime.combine(dia, time(9, 0)))


def carregar_catalogo(sender, data: date, **kwargs) -> None:
    """Receptor de `cenario_preparado` (research R4)."""
    for item in CATALOGO:
        pk = identificador(item.chave)
        if Oportunidade.objects.filter(pk=pk).exists():
            continue
        operador, escopo = (OPERADOR_B, _ESCOPO_B) if item.operador_b else (OPERADOR_A, _ESCOPO_A)
        dados = {
            "titulo": item.titulo, "resumo": item.resumo, "categoria": item.categoria,
            "unidade_responsavel": item.unidade,
            "endereco": f"{_DOMINIO}{item.chave.lower()}",
            "inicio": data + timedelta(days=item.inicio),
            "fim": data + timedelta(days=item.fim),
            **item.publico,
        }
        dia_do_cadastro = data + timedelta(days=min(item.publicar_em or 0, 0))
        operacoes.cadastrar(dados, operador=operador, escopo=escopo, hoje=dia_do_cadastro, id=pk)
        if item.publicar_em is not None:
            operacoes.publicar(pk, operador=operador, escopo=escopo,
                               agora=_momento(data + timedelta(days=item.publicar_em)))
        if item.retirar_em is not None:
            operacoes.retirar(pk, operador=operador, escopo=escopo,
                              agora=_momento(data + timedelta(days=item.retirar_em)))
