"""Política determinística de escolha do contato (Feature 020, FR-008; data-model §1).

Ordem: (1) o `EGRESSO` mais recente; (2) senão, a observação `FONTE_ACADEMICA` mais recente,
o de menor posição; (3) senão, nenhum. Registro cujo valor não passa na normalização é
pulado para o próximo candidato da mesma ordem. Sem aleatoriedade, score ou combinação.
"""

from trajetoria.contato.endereco import email_valido
from trajetoria.contato.models import ContatoDaPessoa, Origem


def contato_utilizavel(pessoa_id, agora) -> ContatoDaPessoa | None:
    registros = ContatoDaPessoa.objects.filter(pessoa_id=pessoa_id, obtido_em__lte=agora)
    for registro in registros.filter(origem=Origem.EGRESSO).order_by("-obtido_em", "-pk"):
        if email_valido(registro.valor):
            return registro
    importados = registros.filter(origem=Origem.FONTE_ACADEMICA)
    ultima = importados.order_by("-obtido_em").values_list("obtido_em", flat=True).first()
    if ultima is None:
        return None
    for registro in importados.filter(obtido_em=ultima).order_by("posicao", "fonte", "pk"):
        if email_valido(registro.valor):
            return registro
    return None
