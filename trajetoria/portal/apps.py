from django.apps import AppConfig
from django.conf import settings


class PortalConfig(AppConfig):
    name = "trajetoria.portal"
    verbose_name = "Portal do Egresso em demonstração (024, 025)"

    def ready(self):
        """Usa só os pontos neutros do núcleo (025 research R3, R4): o destino `curadoria` da
        escolha de operador, ativo só com o Portal ligado (relido a cada pedido), e o
        catálogo fictício carregado pelo sinal do cenário."""
        from trajetoria.demonstracao.sinais import cenario_preparado
        from trajetoria.demonstracao.views import registrar_destino
        from trajetoria.portal.oportunidades.demonstracao import carregar_catalogo

        registrar_destino(
            "curadoria", "/curadoria/oportunidades/", ativo=lambda: settings.TRAJETORIA_PORTAL
        )
        cenario_preparado.connect(carregar_catalogo, dispatch_uid="portal-catalogo-025")
