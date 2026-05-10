from __future__ import annotations

import asyncio
import logging
import struct
import time
from typing import AsyncIterator

from linmic.audio.types import AudioFrame
from linmic.config import UsbConfig

LOGGER = logging.getLogger(__name__)
HEADER = struct.Struct("<IQ")


class AdbUsbTransport:
    """USB transport using adb forward to reach the Android local TCP server."""

    def __init__(self, config: UsbConfig) -> None:
        self.config = config
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None

    async def connect(self) -> None:
        await self._adb("forward", f"tcp:{self.config.port}", f"tcp:{self.config.port}")
        self._reader, self._writer = await asyncio.open_connection(self.config.host, self.config.port)
        LOGGER.info("Connected to Android audio stream over ADB USB forwarding")

    async def frames(self) -> AsyncIterator[AudioFrame]:
        if self._reader is None:
            raise RuntimeError("USB transport is not connected")

        while True:
            header = await self._reader.readexactly(HEADER.size)
            payload_size, sequence = HEADER.unpack(header)
            pcm = await self._reader.readexactly(payload_size)
            yield AudioFrame(pcm=pcm, sequence=sequence, timestamp_ns=time.time_ns())

    async def close(self) -> None:
        if self._writer is not None:
            self._writer.close()
            await self._writer.wait_closed()
            self._writer = None
        self._reader = None

    async def _adb(self, *args: str) -> None:
        process = await asyncio.create_subprocess_exec(
            self.config.adb_path,
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            raise RuntimeError(
                f"adb {' '.join(args)} failed: {stderr.decode().strip() or stdout.decode().strip()}"
            )
