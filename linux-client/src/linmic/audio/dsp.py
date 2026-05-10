from __future__ import annotations

import audioop
import logging

LOGGER = logging.getLogger(__name__)


class DspChain:
    def __init__(self) -> None:
        self.volume = 1.0
        self.noise_suppression_enabled = False
        self.echo_cancellation_enabled = False

    def process(self, pcm: bytes) -> bytes:
        if self.noise_suppression_enabled:
            LOGGER.debug("RNNoise requested but native binding is not installed yet")
        if self.echo_cancellation_enabled:
            LOGGER.debug("Echo cancellation requested but backend is not installed yet")
        if self.volume == 1.0:
            return pcm
        return audioop.mul(pcm, 2, self.volume)
