// Template trajetoria-v1 (Feature 022; contracts/template-video.md).
//
// Só decide QUANDO e COMO cada parte da composição entra. Não mede, não quebra, não corta,
// não formata e não gera texto: a marcação SVG de cada parte vem pronta do card da 021
// (trajetoria/narrativa/composicao.py). O último quadro é o card.
import React, {useState} from 'react';
import {
  AbsoluteFill,
  cancelRender,
  continueRender,
  delayRender,
  Easing,
  interpolate,
  staticFile,
  useCurrentFrame,
} from 'remotion';

type Zona = {chave: string; partes: string[]; y1?: number; y2?: number; paradas?: number[]};
export type Composicao = {template: string; zonas: Zona[]};

const QUADROS_BASE = 240; // 8,0 s a 30 fps
const EXTRA_COM_QUATRO_NOS = 18; // +0,6 s só na linha do tempo (spec FR-011)
const SUBIDA = 24; // translação máxima de texto, de baixo para cima (FR-017)

const zona = (c: Composicao, chave: string) => c.zonas.find((z) => z.chave === chave);
const extraDe = (c: Composicao) =>
  (zona(c, 'nos')?.partes.length ?? 0) === 4 ? EXTRA_COM_QUATRO_NOS : 0;

export const duracaoEmQuadros = (c: Composicao) => QUADROS_BASE + extraDe(c);

const suave = Easing.bezier(0.22, 1, 0.36, 1);
const progresso = (quadro: number, inicio: number, fim: number) =>
  interpolate(quadro, [inicio, fim], [0, 1], {
    easing: suave,
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

const Parte: React.FC<{marcacao: string}> = ({marcacao}) => (
  <g dangerouslySetInnerHTML={{__html: marcacao}} />
);

// Opacidade e translação de baixo para cima; com p = 1 a parte está na posição do card.
const Entrada: React.FC<{p: number; subida?: number; children: React.ReactNode}> = ({
  p,
  subida = SUBIDA,
  children,
}) => (
  <g opacity={p} transform={subida ? `translate(0 ${((1 - p) * subida).toFixed(3)})` : undefined}>
    {children}
  </g>
);

const useFontes = () => {
  // Open Sans Regular e Bold, as mesmas do PNG; sem elas o render falha (nunca cai para a
  // fonte do sistema).
  const [espera] = useState(() => delayRender('Carregando Open Sans'));
  useState(() => {
    const fontes = [
      new FontFace('Open Sans', `url(${staticFile('OpenSans-Regular.ttf')})`, {weight: '400'}),
      new FontFace('Open Sans', `url(${staticFile('OpenSans-Bold.ttf')})`, {weight: '700'}),
    ];
    Promise.all(fontes.map((f) => f.load()))
      .then((carregadas) => {
        carregadas.forEach((f) => document.fonts.add(f));
        continueRender(espera);
      })
      .catch((erro) => cancelRender(erro));
    return null;
  });
};

export const TrajetoriaV1: React.FC<{composicao: Composicao}> = ({composicao}) => {
  useFontes();
  const q = useCurrentFrame();
  const c = composicao;
  const extra = extraDe(c);
  const partes = (chave: string) => zona(c, chave)?.partes ?? [];

  // Linha do tempo: 51 → 150 + extra, dividida entre os nós e o "e mais N".
  const nos = partes('nos');
  const mais = partes('mais');
  const vagas = Math.max(1, nos.length + (mais.length ? 1 : 0));
  const passo = (150 + extra - 51) / vagas;
  const duracaoDoNo = Math.min(passo, 18);
  const inicioDoNo = (i: number) => 51 + i * passo;
  // O traço desce trecho a trecho: do nó i ao nó i + 1 enquanto o nó i entra, chegando ao
  // centro do próximo nó no instante em que ele começa a entrar.
  const traco = zona(c, 'traco');
  const paradas = traco?.paradas ?? (traco ? [traco.y1 ?? 0, traco.y2 ?? 0] : []);
  let alturaDoTraco = paradas[0] ?? 0;
  for (let i = 0; i + 1 < paradas.length; i++) {
    alturaDoTraco += progresso(q, inicioDoNo(i), inicioDoNo(i + 1)) * (paradas[i + 1] - paradas[i]);
  }
  const destaques = 150 + extra;
  const fecho = 189 + extra;

  return (
    <AbsoluteFill style={{backgroundColor: '#f6f2e8'}}>
      <svg xmlns="http://www.w3.org/2000/svg" width={1080} height={1920} viewBox="0 0 1080 1920">
        {/* Estáticos do quadro 0 ao último: fundo, faixa inferior e rodapé (FR-015). */}
        {partes('fundo').map((m, i) => <Parte key={`fundo-${i}`} marcacao={m} />)}

        {/* Abertura: só a imagem escala (1,04 → 1,00), a partir do pé da abertura. */}
        <g opacity={progresso(q, 0, 21)}>
          <g
            style={{
              transform: `scale(${(1.04 - 0.04 * progresso(q, 0, 39)).toFixed(5)})`,
              transformBox: 'fill-box',
              transformOrigin: '50% 100%',
            }}
          >
            {partes('abertura').map((m, i) => <Parte key={`abertura-${i}`} marcacao={m} />)}
          </g>
        </g>
        <Entrada p={progresso(q, 4, 21)} subida={0}>
          {partes('marca').map((m, i) => <Parte key={`marca-${i}`} marcacao={m} />)}
        </Entrada>
        <Entrada p={progresso(q, 9, 21)} subida={12}>
          {partes('legenda').map((m, i) => <Parte key={`legenda-${i}`} marcacao={m} />)}
        </Entrada>

        <Entrada p={progresso(q, 21, 39)}>
          {partes('titulo').map((m, i) => <Parte key={`titulo-${i}`} marcacao={m} />)}
        </Entrada>
        <Entrada p={progresso(q, 33, 51)}>
          {partes('nome').map((m, i) => <Parte key={`nome-${i}`} marcacao={m} />)}
        </Entrada>

        {traco && traco.y1 !== undefined && traco.y2 !== undefined && (
          <>
            <defs>
              <clipPath id="revelacao-do-traco">
                <rect x={0} y={0} width={1080} height={alturaDoTraco} />
              </clipPath>
            </defs>
            <g clipPath="url(#revelacao-do-traco)">
              {traco.partes.map((m, i) => <Parte key={`traco-${i}`} marcacao={m} />)}
            </g>
          </>
        )}
        {nos.map((m, i) => (
          <Entrada key={`no-${i}`} p={progresso(q, inicioDoNo(i), inicioDoNo(i) + duracaoDoNo)}>
            <Parte marcacao={m} />
          </Entrada>
        ))}
        {mais.map((m, i) => (
          <Entrada
            key={`mais-${i}`}
            p={progresso(q, inicioDoNo(nos.length), inicioDoNo(nos.length) + duracaoDoNo)}
          >
            <Parte marcacao={m} />
          </Entrada>
        ))}

        {/* Destaques: números estáticos, sem contagem (E7). */}
        {partes('destaques').map((m, i) => (
          <Entrada key={`destaque-${i}`} p={progresso(q, destaques + 8 * i, destaques + 8 * i + 18)}>
            <Parte marcacao={m} />
          </Entrada>
        ))}
        <Entrada p={progresso(q, destaques, destaques + 18)} subida={0}>
          {partes('apuracao').map((m, i) => <Parte key={`apuracao-${i}`} marcacao={m} />)}
        </Entrada>

        {/* Fechamento: só opacidade, porque o rodapé visível está logo abaixo. */}
        <Entrada p={progresso(q, fecho, fecho + 18)} subida={0}>
          {partes('fechamento').map((m, i) => <Parte key={`fechamento-${i}`} marcacao={m} />)}
        </Entrada>

        {partes('rodape').map((m, i) => <Parte key={`rodape-${i}`} marcacao={m} />)}
      </svg>
    </AbsoluteFill>
  );
};
