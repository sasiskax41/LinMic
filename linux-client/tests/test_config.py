from linmic.config import AppConfig


def test_default_frame_size_is_10ms_pcm16_mono() -> None:
    assert AppConfig().audio.frame_bytes == 960
