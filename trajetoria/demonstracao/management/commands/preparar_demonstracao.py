from django.core.management.base import BaseCommand, CommandError

from trajetoria.demonstracao.cenario import PreparoRecusado, preparar


class Command(BaseCommand):
    help = (
        "Prepara o cenário de demonstração local (dados fictícios). Só com "
        "TRAJETORIA_DEMONSTRACAO=1 e num banco sem dados de outra fonte."
    )

    def handle(self, *args, **options):
        try:
            resumo = preparar()
        except PreparoRecusado as erro:
            raise CommandError(str(erro)) from None
        self.stdout.write("Cenário de demonstração pronto. Pessoas fictícias:")
        for linha in resumo.linhas:
            self.stdout.write(f"  {linha}")
