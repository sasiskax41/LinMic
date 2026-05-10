from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class AudioFrame:
    pcm: bytes
    sequence: int
    timestamp_ns: int


class AudioSink(Protocol):
    async def start(self) -> None:
        ...

    async def write(self, pcm: bytes) -> None:
        ...

    async def stop(self) -> None:
        ...
