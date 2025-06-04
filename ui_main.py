from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QProgressBar, QTextEdit, QDialog
)
from PyQt5.QtGui import QFont, QIcon, QPixmap, QPalette, QColor
from PyQt5.QtCore import Qt, QPropertyAnimation, pyqtSlot, QThread, pyqtSignal
from PyQt5.QtWidgets import QGraphicsDropShadowEffect
import time
import threading
import json
import os

# Dummy backend for test mode
class DummyDownloader(QThread):
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    done = pyqtSignal()

    def __init__(self, url, directory):
        super().__init__()
        self.url = url
        self.directory = directory
        self._cancel = False

    def run(self):
        self.status.emit(f"Starting download for: {self.url}")
        for i in range(1, 101):
            if self._cancel:
                self.status.emit("Download cancelled.")
                return
            self.progress.emit(i)
            self.status.emit(f"Progress: {i}%")
            time.sleep(0.03)
        self.status.emit("Download complete!")
        self.done.emit()

    def cancel(self):
        self._cancel = True

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Spotify API Settings")
        self.setFixedSize(400, 220)
        layout = QVBoxLayout(self)
        label = QLabel("Enter your Spotify API credentials:")
        label.setFont(QFont("Segoe UI", 11))
        layout.addWidget(label)
        self.client_id_input = QLineEdit()
        self.client_id_input.setPlaceholderText("Client ID")
        layout.addWidget(self.client_id_input)
        self.client_secret_input = QLineEdit()
        self.client_secret_input.setPlaceholderText("Client Secret")
        layout.addWidget(self.client_secret_input)
        self.save_btn = QPushButton("Save")
        self.save_btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.save_btn.clicked.connect(self.save)
        layout.addWidget(self.save_btn)
        self.load_existing()

    def load_existing(self):
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    self.client_id_input.setText(config.get('client_id', ''))
                    self.client_secret_input.setText(config.get('client_secret', ''))
            except Exception:
                pass

    def save(self):
        config = {
            'client_id': self.client_id_input.text().strip(),
            'client_secret': self.client_secret_input.text().strip()
        }
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        with open(config_path, 'w') as f:
            json.dump(config, f)
        self.accept()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ipodfiller")
        self.setFixedSize(600, 560)
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f6fbff, stop:1 #eaf6fb);
            }
        """)
        self.downloader = None
        self.init_ui()
        self.fade_in_card()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)

        # Card
        self.card = QWidget()
        self.card.setStyleSheet("""
            background: white;
            border-radius: 24px;
            padding: 32px;
        """)
        card_layout = QVBoxLayout(self.card)
        card_layout.setSpacing(18)

        # Add drop shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(32)
        shadow.setXOffset(0)
        shadow.setYOffset(8)
        shadow.setColor(QColor(0, 0, 0, 40))
        self.card.setGraphicsEffect(shadow)

        # Title
        title = QLabel("<span style='font-size:32px; vertical-align:middle;'>🎵</span> <b>ipodfiller</b>")
        title.setFont(QFont("Segoe UI", 22))
        title.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title)

        subtitle = QLabel("Fill your digital music library with ease")
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(subtitle)

        # Playlist URL
        url_label = QLabel("Spotify Playlist URL")
        url_label.setFont(QFont("Segoe UI", 10))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://open.spotify.com/playlist/...")
        self.url_input.setStyleSheet("border-radius: 16px; padding: 10px; border: 1px solid #e0e0e0; background: #f8fbfd;")

        card_layout.addWidget(url_label)
        card_layout.addWidget(self.url_input)

        # Download Directory
        dir_label = QLabel("Download Directory")
        dir_label.setFont(QFont("Segoe UI", 10))
        self.dir_input = QLineEdit()
        self.dir_input.setPlaceholderText("C:\\Music\\Downloads")
        self.dir_input.setStyleSheet("border-radius: 16px; padding: 10px; border: 1px solid #e0e0e0; background: #f8fbfd;")
        self.dir_btn = QPushButton("📁")
        self.dir_btn.setFixedSize(36, 36)
        self.dir_btn.setStyleSheet("border-radius: 18px; background: #f6fbff; font-size: 18px;")
        self.dir_btn.clicked.connect(self.choose_directory)

        dir_layout = QHBoxLayout()
        dir_layout.addWidget(self.dir_input)
        dir_layout.addWidget(self.dir_btn)
        card_layout.addWidget(dir_label)
        card_layout.addLayout(dir_layout)

        # Start Button
        self.start_btn = QPushButton("Start Download")
        self.start_btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.start_btn.setStyleSheet("""
            QPushButton {
                border-radius: 18px;
                padding: 14px 0;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1ca3b5, stop:1 #3a8dde);
                color: white;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3a8dde, stop:1 #1ca3b5);
            }
        """)
        self.start_btn.clicked.connect(self.start_download)
        card_layout.addWidget(self.start_btn)

        # Progress Bar
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(16)
        self.progress.setStyleSheet("""
            QProgressBar {
                border-radius: 8px;
                background: #f8fbfd;
            }
            QProgressBar::chunk {
                border-radius: 8px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1ca3b5, stop:1 #3a8dde);
            }
        """)
        card_layout.addWidget(self.progress)

        # Status Log
        self.status_log = QTextEdit()
        self.status_log.setReadOnly(True)
        self.status_log.setFixedHeight(60)
        self.status_log.setStyleSheet("border-radius: 12px; background: #f8fbfd; border: 1px solid #e0e0e0; font-size: 11pt;")
        card_layout.addWidget(self.status_log)

        # Cancel Button (appears during download)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setFont(QFont("Segoe UI", 10))
        self.cancel_btn.setStyleSheet("border-radius: 12px; background: #e3f1fa; color: #1ca3b5;")
        self.cancel_btn.setVisible(False)
        self.cancel_btn.clicked.connect(self.cancel_download)
        card_layout.addWidget(self.cancel_btn)

        main_layout.addWidget(self.card, alignment=Qt.AlignCenter)

        # Settings Button below the card
        self.settings_btn = QPushButton("⚙️ Settings")
        self.settings_btn.setFont(QFont("Segoe UI", 11))
        self.settings_btn.setStyleSheet("border-radius: 16px; background: #f6fbff; font-size: 15px; padding: 8px 18px;")
        self.settings_btn.clicked.connect(self.open_settings)
        main_layout.addWidget(self.settings_btn, alignment=Qt.AlignCenter)

    def fade_in_card(self):
        self.card.setWindowOpacity(0)
        self.anim = QPropertyAnimation(self.card, b"windowOpacity")
        self.anim.setDuration(700)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.start()

    def choose_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Download Directory")
        if dir_path:
            self.dir_input.setText(dir_path)

    def start_download(self):
        url = self.url_input.text().strip()
        directory = self.dir_input.text().strip()
        if not url or not directory:
            self.status_log.append("Please enter both a playlist URL and a download directory.")
            return
        self.status_log.clear()
        self.progress.setValue(0)
        self.start_btn.setEnabled(False)
        self.cancel_btn.setVisible(True)
        # Use DummyDownloader for test mode; replace with real backend for production
        self.downloader = DummyDownloader(url, directory)
        self.downloader.progress.connect(self.progress.setValue)
        self.downloader.status.connect(self.status_log.append)
        self.downloader.done.connect(self.download_done)
        self.downloader.start()

    def cancel_download(self):
        if self.downloader:
            self.downloader.cancel()
        self.start_btn.setEnabled(True)
        self.cancel_btn.setVisible(False)
        self.status_log.append("Download cancelled by user.")

    @pyqtSlot()
    def download_done(self):
        self.start_btn.setEnabled(True)
        self.cancel_btn.setVisible(False)
        self.status_log.append("Ready for another download!")

    def open_settings(self):
        dlg = SettingsDialog(self)
        dlg.exec_() 