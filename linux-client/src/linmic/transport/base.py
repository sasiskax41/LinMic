from __future__ import annotations

from typing import AsyncIterator, Protocol

from linmic.audio.types import AudioFrame


class FrameTransport(Protocol):
    async def connect(self) -> None:
        ...

    async def frames(self) -> AsyncIterator[AudioFrame]:
        ...

    async def close(self) -> None:
        ...
