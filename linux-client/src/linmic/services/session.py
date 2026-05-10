from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable

from linmic.audio.dsp import DspChain
from linmic.audio.pipewire import PipeWireVirtualMicrophone
from linmic.config import AppConfig
from linmic.transport.usb_adb import AdbUsbTransport

LOGGER = logging.getLogger(__name__)


StatusCallback = Callable[[str], None]


class LinMicSession:
    def __init__(self, config: AppConfig, status_callback: StatusCallback | None = None) -> None:
        self.config = config
        self.status_callback = status_callback or (lambda status: None)
        self.dsp = DspChain()
        self._task: asyncio.Task[None] | None = None
        self._stop = asyncio.Event()

    def set_volume(self, value: float) -> None:
        self.dsp.volume = max(0.0, min(value, 2.0))

    async def start(self) -> None:
        if self._task is not None:
            return
        self._stop.clear()
        self._task = asyncio.create_task(self._run(), name="linmic-session")

    async def stop(self) -> None:
        self._stop.set()
        if self._task is not None:
            await self._task
            self._task = None

    async def _run(self) -> None:
        sink = PipeWireVirtualMicrophone(
            self.config.audio,
            source_name=self.config.source_name,
            source_description=self.config.source_description,
        )
        await sink.start()
        try:
            while not self._stop.is_set():
                transport = AdbUsbTransport(self.config.usb)
                try:
                    self.status_callback("Connecting")
                    await transport.connect()
                    self.status_callback("Streaming")
                    async for frame in transport.frames():
                        if self._stop.is_set():
                            break
                        await sink.write(self.dsp.process(frame.pcm))
                except (asyncio.IncompleteReadError, ConnectionError, OSError, RuntimeError) as exc:
                    LOGGER.warning("USB stream interrupted: %s", exc)
                    self.status_callback("Reconnecting")
                    await asyncio.sleep(self.config.usb.reconnect_delay_seconds)
                finally:
                    await transport.close()
        finally:
            self.status_callback("Disconnected")
            await sink.stop()
