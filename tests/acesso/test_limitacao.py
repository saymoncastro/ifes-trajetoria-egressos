from datetime import timedelta

from tests.acesso.construcao import AGORA


def test_esperas_expiracao_e_zerar():
    from trajetoria.acesso.limitacao import em_espera, registrar, zerar

    agora = AGORA
    chave = "acesso:cpf:" + "a" * 64
    for _ in range(3):
        registrar("cpf", chave, agora)
        assert em_espera(chave, agora) is None
    for segundos in (5, 15, 45, 135, 300, 300):
        registrar("cpf", chave, agora)
        ate = agora + timedelta(seconds=segundos)
        assert em_espera(chave, agora) == ate
        registrar("cpf", chave, agora)
        assert em_espera(chave, agora) == ate
        agora = ate
    assert em_espera(chave, agora + timedelta(seconds=3600)) is None
    registrar("cpf", chave, agora)
    zerar(chave)
    assert em_espera(chave, agora) is None


def test_janela_fixa_nao_e_prolongada_por_trafego_continuo():
    """Revisão 018: tráfego contínuo da mesma origem não mantém a espera para sempre."""
    from trajetoria.acesso.limitacao import em_espera, registrar

    chave = "acesso:origem:" + "b" * 64
    inicio = AGORA
    for _ in range(31):
        registrar("origem", chave, inicio)
    assert em_espera(chave, inicio) is not None
    agora = inicio
    while agora < inicio + timedelta(seconds=900):
        if em_espera(chave, agora) is None:
            registrar("origem", chave, agora)
        agora += timedelta(seconds=100)
    # Fim da janela fixa: nova contagem, com 30 submissões livres de novo.
    for _ in range(30):
        registrar("origem", chave, agora)
        assert em_espera(chave, agora) is None


def test_estornar_e_travar():
    from django.core.cache import caches

    from trajetoria.acesso.limitacao import estornar, liberar, registrar, travar

    chave = "acesso:origem:" + "d" * 64
    estornar(chave)  # nada contado: sem efeito nem erro
    registrar("origem", chave, AGORA)
    estornar(chave)
    estornar(chave)
    assert caches["acesso"].get(chave + ":n") == 0
    assert travar(chave) is True
    assert travar(chave) is False
    liberar(chave)
    assert travar(chave) is True
