// Único ponto de entrada do renderizador de vídeo (Feature 022; contracts/renderizador.md).
//
//   node renderizar.mjs <entrada.json> <saida.mp4>
//   node renderizar.mjs <entrada.json> <diretorio> --quadros 30,120,fim
//
// Só o Python chama este script (trajetoria/video/renderizador.py). Ele não aplica regra de
// dado: valida a entrada, anima a composição e codifica. Nenhum acesso à rede; o navegador
// precisa estar provisionado (`npm run garantir-navegador`) e nunca é baixado aqui.
//
// Códigos de saída: 0 sucesso; 1 erro de renderização; 2 entrada inválida; 3 sem navegador.

import {bundle} from '@remotion/bundler';
import {openBrowser, renderMedia, renderStill, selectComposition} from '@remotion/renderer';
import {createHash} from 'node:crypto';
import {existsSync, mkdirSync, readdirSync, readFileSync, renameSync, rmSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const AQUI = path.dirname(fileURLToPath(import.meta.url));
const TEMPLATE = 'trajetoria-v1';
const VERSAO_CONTRATO = 1;
const FONTES = path.join(AQUI, '..', 'trajetoria', 'narrativa', 'fontes');
const NAVEGADOR_PROVISIONADO = path.join(AQUI, 'node_modules', '.remotion', 'chrome-headless-shell');
// Bundles prontos, um por versão do template (código, dependências e fontes): o webpack só
// roda quando algo muda, não a cada render.
const BUNDLES = path.join(AQUI, '.bundle');

const arquivosDe = (pasta) =>
  readdirSync(pasta, {withFileTypes: true, recursive: true})
    .filter((e) => e.isFile())
    .map((e) => path.join(e.parentPath ?? e.path, e.name))
    .sort();

const assinatura = () => {
  const hash = createHash('sha256');
  for (const arquivo of [...arquivosDe(path.join(AQUI, 'src')), path.join(AQUI, 'package-lock.json'),
    ...arquivosDe(FONTES)]) {
    hash.update(path.relative(AQUI, arquivo));
    hash.update(readFileSync(arquivo));
  }
  return hash.digest('hex').slice(0, 16);
};

const bundlePronto = async () => {
  const nome = `${TEMPLATE}-${assinatura()}`;
  const destino = path.join(BUNDLES, nome);
  if (existsSync(path.join(destino, 'index.html'))) return destino;
  mkdirSync(BUNDLES, {recursive: true});
  // Gera ao lado e troca por renomeação (atômica no mesmo diretório): dois processos
  // simultâneos nunca leem um bundle pela metade.
  const temporario = path.join(BUNDLES, `.gerando-${process.pid}-${Date.now()}`);
  await bundle({entryPoint: path.join(AQUI, 'src', 'index.ts'), publicDir: FONTES, outDir: temporario});
  try {
    renameSync(temporario, destino);
  } catch {
    rmSync(temporario, {recursive: true, force: true}); // outro processo chegou antes
  }
  for (const antigo of readdirSync(BUNDLES)) {
    if (antigo !== nome && antigo.startsWith(`${TEMPLATE}-`)) {
      rmSync(path.join(BUNDLES, antigo), {recursive: true, force: true});
    }
  }
  return destino;
};

class EntradaInvalida extends Error {}

const sair = (codigo, motivo) => {
  // Sem conteúdo da composição: só o motivo técnico.
  process.stderr.write(`renderizar: ${motivo}\n`);
  process.exit(codigo);
};

const [entrada, saida, opcao, listaDeQuadros] = process.argv.slice(2);
if (!entrada || !saida || (opcao && (opcao !== '--quadros' || !listaDeQuadros))) {
  sair(2, 'uso: renderizar.mjs <entrada.json> <saida> [--quadros 30,120,fim]');
}

let composicao;
try {
  composicao = JSON.parse(readFileSync(entrada, 'utf8'));
} catch {
  sair(2, 'entrada não é JSON válido');
}
if (composicao?.versao_contrato !== VERSAO_CONTRATO) sair(2, 'versão do contrato desconhecida');
if (composicao?.template !== TEMPLATE) sair(2, 'template desconhecido');
if (!Array.isArray(composicao?.zonas)) sair(2, 'composição sem zonas');

const navegador = process.env.TRAJETORIA_VIDEO_NAVEGADOR || null;
if (navegador ? !existsSync(navegador) : !existsSync(NAVEGADOR_PROVISIONADO)) {
  sair(3, 'navegador não provisionado');
}
const concorrencia = Number(process.env.TRAJETORIA_VIDEO_CONCORRENCIA ?? 2) || 2;

try {
  const serveUrl = await bundlePronto();
  const inputProps = {composicao};
  const browser = await openBrowser('chrome', {browserExecutable: navegador});
  try {
    const composition = await selectComposition({
      serveUrl, id: TEMPLATE, inputProps, puppeteerInstance: browser, browserExecutable: navegador,
    });
    if (opcao === '--quadros') {
      for (const pedido of listaDeQuadros.split(',')) {
        const frame = pedido === 'fim' ? composition.durationInFrames - 1 : Number(pedido);
        if (!Number.isInteger(frame) || frame < 0 || frame >= composition.durationInFrames) {
          throw new EntradaInvalida(`quadro fora do vídeo: ${pedido}`);
        }
        await renderStill({
          composition, serveUrl, inputProps, frame, puppeteerInstance: browser,
          output: path.join(saida, `quadro-${pedido}.png`),
        });
      }
    } else {
      await renderMedia({
        composition, serveUrl, inputProps, outputLocation: saida, puppeteerInstance: browser,
        codec: 'h264', pixelFormat: 'yuv420p', colorSpace: 'bt709', muted: true,
        concurrency: concorrencia,
      });
    }
  } finally {
    await browser.close({silent: true});
  }
} catch (erro) {
  if (erro instanceof EntradaInvalida) sair(2, erro.message);
  sair(1, `falha na renderização (${erro?.name ?? 'erro'})`);
}
