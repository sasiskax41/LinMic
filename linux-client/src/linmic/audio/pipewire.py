from __future__ import annotations

import asyncio
import logging
import os
import shutil
import tempfile
from pathlib import Path

from linmic.config import AudioConfig

LOGGER = logging.getLogger(__name__)


class PipeWireVirtualMicrophone:
    """PipeWire virtual microphone using PipeWire-Pulse's module-pipe-source."""

    def __init__(
        self,
        audio_config: AudioConfig,
        source_name: str = "linmic",
        source_description: str = "LinMic Phone Microphone",
    ) -> None:
        self.audio_config = audio_config
        self.source_name = source_name
        self.source_description = source_description
        self.runtime_dir = Path(tempfile.gettempdir()) / "linmic"
        self.fifo_path = self.runtime_dir / "linmic.pcm"
        self._module_id: str | None = None
        self._writer: asyncio.StreamWriter | None = None

    async def start(self) -> None:
        if not shutil.which("pactl"):
            raise RuntimeError("pactl is required. Install pipewire-pulse or pulseaudio-utils.")

        self.runtime_dir.mkdir(parents=True, exist_ok=True)
        if self.fifo_path.exists():
            self.fifo_path.unlink()
        os.mkfifo(self.fifo_path, 0o600)

        cmd = [
            "pactl",
            "load-module",
            "module-pipe-source",
            f"source_name={self.source_name}",
            f"file={self.fifo_path}",
            f"format={self.audio_config.sample_format}",
            f"rate={self.audio_config.sample_rate}",
            f"channels={self.audio_config.channels}",
            f"source_properties=device.description={self.source_description}",
        ]
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            if self.fifo_path.exists():
                self.fifo_path.unlink()
            raise RuntimeError(f"Failed to create virtual microphone: {stderr.decode().strip()}")

        self._module_id = stdout.decode().strip()
        LOGGER.info("Created PipeWire virtual source module %s", self._module_id)
        self._writer = await self._open_fifo_writer()

    async def write(self, pcm: bytes) -> None:
        if self._writer is None:
            return
        self._writer.write(pcm)
        await self._writer.drain()

    async def stop(self) -> None:
        if self._writer is not None:
            self._writer.close()
            await self._writer.wait_closed()
            self._writer = None

        if self._module_id:
            process = await asyncio.create_subprocess_exec(
                "pactl",
                "unload-module",
                self._module_id,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            await process.communicate()
            LOGGER.info("Unloaded PipeWire virtual source module %s", self._module_id)
            self._module_id = None

        if self.fifo_path.exists():
            self.fifo_path.unlink()

    async def _open_fifo_writer(self) -> asyncio.StreamWriter:
        loop = asyncio.get_running_loop()
        fd = await loop.run_in_executor(None, os.open, self.fifo_path, os.O_WRONLY)
        pipe = os.fdopen(fd, "wb", buffering=0)
        transport, protocol = await loop.connect_write_pipe(asyncio.streams.FlowControlMixin, pipe)
        return asyncio.StreamWriter(transport, protocol, None, loop)
