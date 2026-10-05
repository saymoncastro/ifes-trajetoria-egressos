"""O arquivo de vídeo real (022 US2, porta de decisão; FR-009, FR-010, FR-018, SC-001,
SC-006; research R11, R13, R14)."""

import pytest

from tests.video import midia
from tests.video.construcao import NOME

pytestmark = pytest.mark.precisa_renderizador

CASOS_DE_MIDIA = [("maria", NOME, 240), ("ana", None, 240), ("quatro_curtos", None, 258)]


@pytest.mark.parametrize(("caso", "nome", "quadros"), CASOS_DE_MIDIA)
def test_formato_do_arquivo(caso, nome, quadros, tmp_path):
    dados, _ = midia.video(caso, nome)
    info = midia.ffprobe(dados, tmp_path)
    assert len(info["streams"]) == 1, "nenhuma faixa além do vídeo (sem áudio)"
    stream = info["streams"][0]
    assert stream["codec_type"] == "video"
    assert stream["codec_name"] == "h264"
    assert stream["pix_fmt"] == "yuv420p"
    assert stream["color_space"] == "bt709"
    assert (stream["width"], stream["height"]) == (1080, 1920)
    assert stream["r_frame_rate"] == "30/1"
    assert int(stream["nb_frames"]) == quadros
    assert abs(float(info["format"]["duration"]) - quadros / 30) <= 1 / 30


@pytest.mark.parametrize(("caso", "nome", "quadros"), CASOS_DE_MIDIA)
def test_contêiner_mp4_com_faststart(caso, nome, quadros):
    dados, _ = midia.video(caso, nome)
    assert dados[4:8] == b"ftyp"
    assert 0 < dados.find(b"moov") < dados.find(b"mdat")


def test_mesmo_arquivo_no_mesmo_ambiente():
    dados, _ = midia.video("maria", NOME)
    assert midia.video_novo("maria", NOME) == dados


@pytest.mark.parametrize(("caso", "nome", "quadros"), CASOS_DE_MIDIA)
def test_pronto_em_menos_de_um_minuto(caso, nome, quadros):
    _, segundos = midia.video(caso, nome)
    print(f"render {caso}: {segundos:.1f} s")
    assert segundos < 60
