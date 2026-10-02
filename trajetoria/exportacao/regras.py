"""Vocabulário de erro da exportação (contracts/exportacao.md, "Vocabulário de erro").

Mesmo padrão de `trajetoria/analitico/regras.py`. Nada é devolvido nem gravado quando
qualquer uma destas exceções é levantada: não existe arquivo parcial nem estado de
exportação. As mensagens citam motivo, identificadores técnicos de snapshot, Pergunta ou
Opção, nome de coluna, número de linha e contagens — nunca valor acadêmico, conteúdo de
Resposta, identificador interno de Pessoa ou Conclusão, pseudônimo nem a chave (spec FR-093).
"""

from enum import Enum


class Motivo(Enum):
    SNAPSHOT_NAO_GRAVADO = "snapshot_nao_gravado"  # spec FR-090
    CHAVE_AUSENTE = "chave_ausente"  # spec FR-027, FR-090
    CHAVE_INADEQUADA = "chave_inadequada"  # spec FR-027 (hipótese: < 32 ou = SECRET_KEY)


_TEXTO = {
    Motivo.SNAPSHOT_NAO_GRAVADO: "o snapshot informado não está gravado",
    Motivo.CHAVE_AUSENTE: "a chave de pseudonimização analítica não está configurada",
    Motivo.CHAVE_INADEQUADA: (
        "a chave de pseudonimização analítica é curta demais ou igual ao segredo da aplicação"
    ),
}


class ExportacaoRecusada(Exception):
    """A exportação não pode começar: snapshot ou configuração inadequados."""

    def __init__(self, motivo: Motivo):
        self.motivo = motivo
        super().__init__(f"{motivo.name}: {_TEXTO[motivo]}")


class ExportacaoInconsistente(Exception):
    """Inconsistência estrutural inesperada na representação (spec FR-092). Só ocorre com
    dado escrito fora das operações de domínio (ADR 0002); não é decisão de domínio."""


class ValorNaoRepresentavel(ExportacaoInconsistente):
    """Um valor que o formato não consegue gravar sem alteração (spec FR-091)."""

    def __init__(self, *, formato: str, tabela: str, coluna: str, linha: int):
        self.formato = formato
        self.tabela = tabela
        self.coluna = coluna
        self.linha = linha
        super().__init__(
            f"{formato}: valor da tabela {tabela}, coluna {coluna}, linha {linha} não é "
            "representável sem alteração"
        )
