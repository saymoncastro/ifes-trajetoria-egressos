# Quickstart — Feature 024: Início do egresso e shell do Portal

Pré-requisito: o ambiente local de
[docs/desenvolvimento/ambiente-local.md](../../docs/desenvolvimento/ambiente-local.md), com o
banco preparado (`preparar_demonstracao`) e o servidor no ar com `source .env &&`. O Portal
vem ligado por padrão. Para desligar, use `TRAJETORIA_PORTAL=0`.

## Verificações automáticas

```bash
uv run pytest tests/portal tests/narrativa tests/interface tests/video tests/acesso
```

```bash
uv run python manage.py makemigrations --check --dry-run
```

As verificações completas do CI estão em [AGENTS.md](../../AGENTS.md).

## Roteiro manual (navegador a 375×812)

Personas da fonte simulada (painel "Usar estes dados"); casos esperados em [contracts/rotas.md](contracts/rotas.md):

1. **Caminho B (Portal).**
   - Abra `http://127.0.0.1:8000/` sem sessão. Você deve cair em `/entrar/`, com o rótulo
     "Entrada do Portal do Egresso".
   - Use "Usar estes dados" de Maria (duas formações). Você deve chegar a `/inicio/`.
   - Confira: o título e a síntese aparecem sem rolar; as duas formações vêm com "Registro
     do Ifes"; o convite aparece só no fim.
2. **Trajetória antes da pesquisa.** No Início, abra "Ver minha trajetória no Ifes", baixe o
   card e gere o vídeo, se o renderizador existir. Nada disso pede pesquisa.
3. **Navegação.**
   - Pela navegação, vá a "Pesquisa" (`/formacoes/`): ela não mostra "Ao final, você poderá
     ver…", e mostra "A pesquisa tem no máximo N partes.".
   - Volte ao Início pela navegação.
   - Comece a pesquisa: as Seções não têm navegação.
4. **Caminho A (convite).**
   - Clique em "Sair".
   - Abra `http://127.0.0.1:8000/acesso/` (o endereço do convite) e entre com Diego. Você
     deve chegar a `/formacoes/`, como antes desta feature.
   - Responda uma parte e conclua. Na confirmação aparece "Ver minha trajetória no Ifes" e a
     navegação.
5. **Sessão expirada no Portal.**
   - Com a inatividade reduzida a 1 minuto (`TRAJETORIA_SESSAO_INATIVIDADE=1`, só para o
     teste), espere e recarregue `/inicio/`.
   - Você deve voltar a `/entrar/` com o aviso genérico de sessão encerrada, sem a frase de
     envio guardado.
6. **Portal desligado.**
   - Reinicie o servidor com `TRAJETORIA_PORTAL=0`.
   - `/` deve se comportar como antes (vai para `/acesso/` sem sessão).
   - `/inicio/` e `/entrar/` devem responder 404.
   - Nenhuma tela deve ter navegação.
   - A trajetória continua abrindo antes da pesquisa.

## Checkpoint 1

O teste moderado usa este mesmo ambiente com o Portal ligado. Os critérios estão em
SC-008 a SC-016 da [spec](spec.md). O protocolo (participantes, limiar de "maioria", roteiro
de perguntas) é escrito antes do teste, numa evidência própria da feature.
