# GUI Mockup

```text
+--------------------------------------+
| LinMic                               |
|                                      |
| Streaming                            |
| USB device: active                   |
|                                      |
| Input level                          |
| [####################          ]     |
|                                      |
| Input volume                         |
| [----------o---------------] 100%    |
|                                      |
| [ Connect ] [ Disconnect ]           |
|                                      |
| [ ] Noise suppression                |
| [ ] Echo cancellation                |
+--------------------------------------+
```

The first implementation is intentionally compact:

- Large session state for quick scanning.
- USB device status below the state.
- Stable input meter and volume slider.
- Tray icon with show and quit actions.
- Dark mode stylesheet by default.

Noise suppression and echo cancellation controls are visible but disabled until native DSP backends are wired.
