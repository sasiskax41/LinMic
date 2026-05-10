from dataclasses import dataclass, field


@dataclass(frozen=True)
class AudioConfig:
    sample_rate: int = 48_000
    channels: int = 1
    sample_format: str = "s16le"
    frame_ms: int = 10

    @property
    def bytes_per_sample(self) -> int:
        return 2

    @property
    def frame_bytes(self) -> int:
        samples = self.sample_rate * self.frame_ms // 1000
        return samples * self.channels * self.bytes_per_sample


@dataclass(frozen=True)
class UsbConfig:
    adb_path: str = "adb"
    host: str = "127.0.0.1"
    port: int = 38_473
    reconnect_delay_seconds: float = 1.5


@dataclass(frozen=True)
class AppConfig:
    audio: AudioConfig = field(default_factory=AudioConfig)
    usb: UsbConfig = field(default_factory=UsbConfig)
    source_name: str = "linmic"
    source_description: str = "LinMic Phone Microphone"
