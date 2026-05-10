# LinMic

LinMic is a Linux-first open-source alternative to WO Mic. It turns an Android phone microphone into a Linux microphone source that apps such as Discord, OBS, browsers, and games can discover automatically through PipeWire.

## Goals

- Android microphone capture with `AudioRecord`
- USB-first streaming through ADB port forwarding
- Linux virtual microphone exposed through PipeWire/PipeWire-Pulse
- Low-latency PCM pipeline with room for Opus later
- PySide6 desktop UI with tray integration and dark mode
- Clean, modular Python client architecture
- Kotlin Android app with a foreground microphone service

## Architecture

```text
Android AudioRecord
  -> foreground streaming service
  -> localhost TCP server on Android
  -> ADB port forward over USB
  -> Linux asyncio USB transport
  -> optional DSP chain: volume, RNNoise, echo cancellation
  -> PipeWire virtual microphone backend
  -> Discord / OBS / games
```

The first Linux backend uses `pactl load-module module-pipe-source` against PipeWire-Pulse. On modern Linux desktops this creates a real PipeWire source while staying cross-distro and simple to package. A native `libpipewire` backend can be added behind the same `AudioSink` interface.

## Repository Layout

```text
LinMic/
  linux-client/          Python + PySide6 Linux client
  android-app/           Kotlin Android starter app
  packaging/             Arch and Debian package metadata
  docs/                  Architecture and development notes
  scripts/               Helper scripts
```

## Linux Quick Start

Dependencies:

- Python 3.11+
- PipeWire and PipeWire-Pulse
- `pactl`
- Android platform tools: `adb`

```bash
cd linux-client
python -m venv .venv
source .venv/bin/activate
pip install -e .
linmic
```

Connect an Android phone over USB, enable USB debugging, start the LinMic Android app, then press **Connect** in the Linux client.

## Android Quick Start

Open `android-app/` in Android Studio and run the `app` configuration on a device. The starter service captures 48 kHz mono PCM16 audio and serves framed packets on `127.0.0.1:38473` for ADB forwarding.

CLI build:

```bash
cd android-app
./gradlew assembleDebug
```

## Packaging

Arch:

```bash
cd packaging/arch
makepkg -si
```

Debian:

```bash
cd packaging/debian
dpkg-buildpackage -us -uc
```

## Roadmap

- Native PipeWire backend
- RNNoise integration
- Echo cancellation through WebRTC Audio Processing or PipeWire filter-chain
- Wi-Fi mode with QR pairing
- Bluetooth mode
- Opus codec
- Multi-device routing

## License

MIT
