# USB Audio Protocol

The first protocol is a simple framed PCM stream over TCP through ADB forwarding.

Frame header:

```text
uint32_le payload_size
uint64_le sequence
byte[payload_size] pcm_s16le_48000_mono
```

The Android app is the server. The Linux client is the TCP client. If the socket closes, the Linux client attempts to reconnect.

Future versions should add:

- Hello message with protocol version and device name.
- Format negotiation.
- Codec negotiation for Opus.
- Keepalive and latency telemetry.
- Control channel for gain and mute.
