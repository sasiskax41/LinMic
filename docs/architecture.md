# LinMic Architecture

## Linux Client

The Linux client is split into four layers:

- `transport`: discovers and connects to phone audio streams.
- `audio`: owns sample format, DSP, buffering, and virtual microphone output.
- `services`: coordinates lifecycle, reconnect, logging, and device status.
- `ui`: PySide6 widgets and tray actions.

The transport layer emits raw PCM frames. The audio layer applies local gain and optional DSP, then writes frames into the selected backend. The default backend creates a PipeWire-visible source with PipeWire-Pulse's `module-pipe-source`.

## USB Mode

Initial USB support uses ADB forwarding:

```bash
adb forward tcp:38473 tcp:38473
```

The Android app runs a local TCP server. The Linux client connects to `127.0.0.1:38473`, receives length-prefixed PCM frames, and reconnects if the device drops.

This approach keeps the first version shippable. A future direct USB transport can use Android Open Accessory or a custom USB class behind the same `FrameTransport` interface.

## Audio Format

Version 0 uses:

- PCM signed 16-bit little endian
- 48,000 Hz
- Mono
- 10 ms frame target, 480 samples per frame

Future Opus support should negotiate codec settings in a small control handshake before audio frames start.

## Virtual Microphone

The default backend creates a FIFO and loads:

```bash
pactl load-module module-pipe-source source_name=linmic file=/tmp/linmic/linmic.pcm format=s16le rate=48000 channels=1
```

With PipeWire-Pulse running, this source is visible to PipeWire-native and PulseAudio-compatible applications.
