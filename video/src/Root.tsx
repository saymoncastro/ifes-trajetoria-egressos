// Composição única do MVP (FR-040): trajetoria-v1, 1080 × 1920, 30 fps.
import React from 'react';
import {Composition} from 'remotion';
import {Composicao, duracaoEmQuadros, TrajetoriaV1} from './TrajetoriaV1';

const VAZIA: Composicao = {template: 'trajetoria-v1', zonas: []};

export const Root: React.FC = () => (
  <Composition
    id="trajetoria-v1"
    component={TrajetoriaV1}
    width={1080}
    height={1920}
    fps={30}
    durationInFrames={240}
    defaultProps={{composicao: VAZIA}}
    calculateMetadata={({props}) => ({durationInFrames: duracaoEmQuadros(props.composicao)})}
  />
);
