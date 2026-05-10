from __future__ import annotations

import asyncio
import logging
import sys
import threading

from PySide6.QtCore import QObject, Qt, Signal, Slot
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QProgressBar,
    QPushButton,
    QSlider,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

from linmic.config import AppConfig
from linmic.services.session import LinMicSession
from linmic.utils.logging import setup_logging

LOGGER = logging.getLogger(__name__)


class SessionWorker(QObject):
    status_changed = Signal(str)
    failed = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._loop: asyncio.AbstractEventLoop | None = None
        self._session: LinMicSession | None = None
        self._thread: threading.Thread | None = None
        self._stop_requested: asyncio.Event | None = None

    @Slot()
    def start_session(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._thread_main, name="linmic-audio", daemon=True)
        self._thread.start()

    @Slot()
    def stop_session(self) -> None:
        if self._loop is not None and self._stop_requested is not None:
            self._loop.call_soon_threadsafe(self._stop_requested.set)

    @Slot(int)
    def set_volume(self, value: int) -> None:
        if self._session is not None:
            self._session.set_volume(value / 100)

    def _thread_main(self) -> None:
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_until_complete(self._run_session())
        except Exception as exc:  # UI boundary
            LOGGER.exception("Session error")
            self.failed.emit(str(exc))
        finally:
            self._loop.close()
            self._loop = None
            self._session = None
            self.status_changed.emit("Disconnected")

    async def _run_session(self) -> None:
        self._stop_requested = asyncio.Event()
        self._session = LinMicSession(AppConfig(), self.status_changed.emit)
        await self._session.start()
        try:
            await self._stop_requested.wait()
        finally:
            await self._session.stop()


class MainWindow(QMainWindow):
    start_requested = Signal()
    stop_requested = Signal()
    volume_changed = Signal(int)

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("LinMic")
        self.setMinimumSize(420, 320)

        self.status_label = QLabel("Disconnected")
        self.status_label.setObjectName("statusLabel")
        self.device_label = QLabel("USB device: waiting")
        self.level = QProgressBar()
        self.level.setRange(0, 100)
        self.level.setValue(0)
        self.level.setTextVisible(False)

        self.connect_button = QPushButton("Connect")
        self.disconnect_button = QPushButton("Disconnect")
        self.disconnect_button.setEnabled(False)

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 200)
        self.volume_slider.setValue(100)

        self.noise_checkbox = QCheckBox("Noise suppression")
        self.echo_checkbox = QCheckBox("Echo cancellation")
        self.noise_checkbox.setEnabled(False)
        self.echo_checkbox.setEnabled(False)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("LinMic"))
        layout.addWidget(self.status_label)
        layout.addWidget(self.device_label)
        layout.addWidget(QLabel("Input level"))
        layout.addWidget(self.level)
        layout.addWidget(QLabel("Input volume"))
        layout.addWidget(self.volume_slider)

        buttons = QHBoxLayout()
        buttons.addWidget(self.connect_button)
        buttons.addWidget(self.disconnect_button)
        layout.addLayout(buttons)
        layout.addWidget(self.noise_checkbox)
        layout.addWidget(self.echo_checkbox)
        layout.addStretch(1)

        root = QWidget()
        root.setLayout(layout)
        self.setCentralWidget(root)
        self._apply_dark_mode()

        self.connect_button.clicked.connect(self._connect_clicked)
        self.disconnect_button.clicked.connect(self._disconnect_clicked)
        self.volume_slider.valueChanged.connect(self.volume_changed.emit)

    @Slot(str)
    def set_status(self, status: str) -> None:
        self.status_label.setText(status)
        self.device_label.setText("USB device: active" if status == "Streaming" else "USB device: waiting")
        self.connect_button.setEnabled(status in {"Disconnected", "Reconnecting"})
        self.disconnect_button.setEnabled(status != "Disconnected")

    @Slot(str)
    def show_error(self, message: str) -> None:
        self.status_label.setText(f"Error: {message}")
        self.connect_button.setEnabled(True)
        self.disconnect_button.setEnabled(False)

    def _connect_clicked(self) -> None:
        self.connect_button.setEnabled(False)
        self.status_label.setText("Starting")
        self.start_requested.emit()

    def _disconnect_clicked(self) -> None:
        self.disconnect_button.setEnabled(False)
        self.stop_requested.emit()

    def _apply_dark_mode(self) -> None:
        self.setStyleSheet(
            """
            QWidget { background: #15171a; color: #f4f5f6; font-size: 14px; }
            QLabel#statusLabel { font-size: 22px; font-weight: 700; padding: 12px 0; }
            QPushButton {
                background: #2f7d5c; border: 0; border-radius: 6px; padding: 10px 14px;
            }
            QPushButton:disabled { background: #3b3f45; color: #9ba1aa; }
            QProgressBar {
                background: #252932; border: 1px solid #343a44; border-radius: 4px; min-height: 12px;
            }
            QProgressBar::chunk { background: #3bb273; border-radius: 4px; }
            QSlider::groove:horizontal { height: 6px; background: #343a44; border-radius: 3px; }
            QSlider::handle:horizontal { background: #f4f5f6; width: 18px; margin: -6px 0; border-radius: 9px; }
            """
        )


def run() -> int:
    setup_logging()
    app = QApplication(sys.argv)
    app.setApplicationName("LinMic")
    app.setQuitOnLastWindowClosed(False)

    window = MainWindow()
    worker = SessionWorker()

    window.start_requested.connect(worker.start_session)
    window.stop_requested.connect(worker.stop_session)
    window.volume_changed.connect(worker.set_volume)
    worker.status_changed.connect(window.set_status)
    worker.failed.connect(window.show_error)

    tray = QSystemTrayIcon(QIcon.fromTheme("audio-input-microphone"), app)
    show_action = QAction("Show LinMic")
    quit_action = QAction("Quit")
    show_action.triggered.connect(window.show)
    quit_action.triggered.connect(app.quit)
    tray_menu = QMenu()
    tray_menu.addAction(show_action)
    tray_menu.addAction(quit_action)
    tray.setContextMenu(tray_menu)
    tray.show()

    window.show()
    exit_code = app.exec()
    worker.stop_session()
    return exit_code
