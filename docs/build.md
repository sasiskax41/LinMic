# Build Instructions

## Linux Client

```bash
cd linux-client
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
linmic
```

Runtime dependencies:

- `pipewire`
- `pipewire-pulse`
- `pactl` from `pulseaudio-utils` or distro equivalent
- `adb` from Android platform tools

Check the virtual microphone after connecting:

```bash
pactl list short sources | grep linmic
```

## Android App

Open `android-app/` in Android Studio and run the app on a physical Android device.

With a local Gradle installation:

```bash
cd android-app
gradle assembleDebug
```

Enable USB debugging before connecting from Linux:

```bash
adb devices
adb forward tcp:38473 tcp:38473
```

The Linux client runs the `adb forward` command automatically during connection.
