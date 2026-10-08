"""Rotas: a interface de demonstração da Feature 008 (adaptador e jornada), o editor
institucional do instrumento da Feature 009 (`/editor/`), o acompanhamento operacional da
coleta da Feature 011 (`/acompanhamento/`), a devolutiva da Feature 021
(`/minha-trajetoria/`), o vídeo da Feature 022 (`/minha-trajetoria/video…`), a página de
e-mail da Feature 020 (`/meu-email/`) e o Portal do Egresso da Feature 024 (`/`, `/entrar/`,
`/inicio/`). Com o modo de demonstração desligado, toda requisição é 404
(`ModoDemonstracaoMiddleware`).

O Portal entra antes da interface, para que a raiz seja a entrada do Portal; desligado
(`TRAJETORIA_PORTAL=0`), suas rotas não existem e a raiz volta a ser a da 008 (024 FR-005,
FR-027; research R8)."""

from django.conf import settings

from config.rotas import rotas

urlpatterns = rotas(settings.TRAJETORIA_PORTAL)
