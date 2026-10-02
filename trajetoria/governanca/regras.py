"""As três capacidades da Feature 010 (spec FR-028 a FR-035; contracts/governanca.md).

Regras fixas e puras sobre os vínculos do operador: não leem banco, requisição, settings
nem o modo de demonstração. Um vínculo inativo não concede nada, mesmo se passado aqui.
Capacidade é a existência de **algum** vínculo ativo que a conceda; não há precedência nem
"papel ativo", e a unidade não participa (spec FR-017, FR-021).

Fundamentação: a elaboração do questionário cabe à CPAEG (PAEG Art. 21, VI); a CSAEG aplica
o questionário e reporta atualizações à CPAEG (Art. 22, IV), e por isso consulta o
instrumento publicado — interpretação operacional B6, não competência autônoma. Consultar
rascunho e elaborar são regras distintas da spec, hoje com o mesmo critério (DP-1004).
Publicar não é capacidade de ninguém (002/DP-001).
"""

from trajetoria.governanca.models import Papel

__all__ = ["pode_consultar_publicado", "pode_consultar_rascunho", "pode_elaborar_instrumento"]


def pode_consultar_publicado(vinculos) -> bool:
    return any(v.ativo for v in vinculos)


def pode_consultar_rascunho(vinculos) -> bool:
    return any(v.ativo and v.papel == Papel.CPAEG for v in vinculos)


def pode_elaborar_instrumento(vinculos) -> bool:
    return any(v.ativo and v.papel == Papel.CPAEG for v in vinculos)
