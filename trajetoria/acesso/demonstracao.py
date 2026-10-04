"""Dados exclusivamente fictícios, lidos do cenário e nunca do banco."""

from collections import Counter

from trajetoria.fonte_academica.cenarios import CONCLUIDA, PESSOAS, REGISTROS


def painel():
    cpfs = Counter(p.cpf for p in PESSOAS if p.cpf)
    concluidas = {r.id_pessoa for r in REGISTROS if r.situacao == CONCLUIDA}
    linhas = []
    for p in PESSOAS:
        notas = []
        if not p.cpf:
            notas.append("Sem CPF")
        if not p.data_nascimento:
            notas.append("Sem data")
        if p.cpf and cpfs[p.cpf] > 1:
            notas.append("CPF compartilhado")
        if p.id_externo not in concluidas:
            notas.append("Sem formação concluída")
        cpf = p.cpf
        linhas.append(
            {
                "nome": p.nome or "Pessoa fictícia sem nome informado",
                "cpf": f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}" if cpf else "",
                "nascimento": p.data_nascimento.strftime("%d/%m/%Y") if p.data_nascimento else "",
                "nota": "; ".join(notas),
            }
        )
    return linhas
