"""Processador de pedidos de vídeo (Feature 022; research R7).

Um render por vez. Em laço, com pausa de 1 s quando não há trabalho; `--uma-vez` processa no
máximo um pedido e termina (testes e cron). Sem renderizador, avisa e continua: a limpeza
marca os pedidos esquecidos como `sem_processador` depois de 10 min.
"""

import time

from django.core.management.base import BaseCommand

from trajetoria.video import operacoes, renderizador


class Command(BaseCommand):
    help = "Processa os pedidos de vídeo da Minha trajetória (Feature 022)."

    def add_arguments(self, parser):
        parser.add_argument("--uma-vez", action="store_true",
                            help="processa no máximo um pedido e termina")

    def handle(self, *args, uma_vez=False, **opcoes):
        if uma_vez:
            operacoes.processar_proximo()
            return
        self.stdout.write("Processador de vídeos (Feature 022) — Ctrl+C para sair")
        if not renderizador.disponivel():
            self.stderr.write(
                "Renderizador indisponível: rode `npm ci --prefix video` e "
                "`npm --prefix video run garantir-navegador`."
            )
        try:
            while True:
                if not operacoes.processar_proximo():
                    time.sleep(1)
        except KeyboardInterrupt:
            self.stdout.write("Processador encerrado.")
