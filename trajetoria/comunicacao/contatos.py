"""Contato fictício zero/um; nunca atributo acadêmico ou inferência pelo nome."""

from trajetoria.fonte_academica.simulada import FonteSimulada

CONTATOS = {
    "SIM-P-0001": "sim-p-0001@example.invalid",
    "SIM-P-0002": "sim-p-0002@example.invalid",
    "SIM-P-0003": "sim-p-0003@example.invalid",
    "SIM-P-0004": "sim-p-0004@example.invalid",
    "SIM-P-0005": "sim-p-0005@example.invalid",
    "SIM-P-0006": "sim-p-0006@example.invalid",
    "SIM-P-0007": "sim-p-0007@example.invalid",
    "SIM-P-0008": "sim-p-0008@example.invalid",
    "SIM-P-0009": "sim-p-0009@example.invalid",
    "SIM-P-0010": None,
    "SIM-P-0011": "sim-p-0011@example.invalid",
}


def contato_ficticio(pessoa) -> str | None:
    if pessoa.fonte != FonteSimulada.codigo:
        return None
    return CONTATOS.get(pessoa.id_externo)
