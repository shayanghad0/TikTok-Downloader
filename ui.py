import sys
import os
import re
import yt_dlp
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QListWidget, QListWidgetItem, QLabel,
    QProgressBar, QFileDialog, QMessageBox, QInputDialog
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt

# ---------- Worker thread for downloading ----------
class DownloadWorker(QThread):
    progress_signal = pyqtSignal(str)        # status message
    link_finished = pyqtSignal()             # one link completely done
    all_done = pyqtSignal()                  # everything finished

    def __init__(self, download_list, folder="tdownload"):
        """
        download_list: list of tuples (url, limit)
            limit = 1  -> single video
            limit = -1 -> all videos from profile
            limit > 1  -> exact number from profile
        """
        super().__init__()
        self.download_list = download_list
        self.folder = folder
        self._cancel = False

    def cancel(self):
        self._cancel = True

    def run(self):
        os.makedirs(self.folder, exist_ok=True)
        video_counter = 1

        for url, limit in self.download_list:
            if self._cancel:
                self.progress_signal.emit("⏹️ Download cancelled.")
                break

            username = self._is_profile(url)
            if username:
                # profile link
                self.progress_signal.emit(f"🔍 Scanning @{username}...")
                try:
                    videos = self._fetch_video_urls(url, limit)
                except Exception as e:
                    self.progress_signal.emit(f"❌ Failed to scan @{username}: {e}")
                    self.link_finished.emit()
                    continue

                if not videos:
                    self.progress_signal.emit(f"⚠️ No videos found for @{username}.")
                    self.link_finished.emit()
                    continue

                total = len(videos)
                self.progress_signal.emit(f"📥 Downloading {total} video(s) from @{username}...")
                for vid_url in videos:
                    if self._cancel: break
                    filename = f"video{video_counter}.mp4"
                    try:
                        self._download_video(vid_url, filename)
                        self.progress_signal.emit(f"✅ {filename} downloaded.")
                    except Exception as e:
                        self.progress_signal.emit(f"❌ {filename} failed: {e}")
                    finally:
                        video_counter += 1
                self.link_finished.emit()
            else:
                # single video
                filename = f"video{video_counter}.mp4"
                self.progress_signal.emit(f"⬇️ Downloading {filename}...")
                try:
                    self._download_video(url, filename)
                    self.progress_signal.emit(f"✅ {filename} downloaded.")
                except Exception as e:
                    self.progress_signal.emit(f"❌ {filename} failed: {e}")
                finally:
                    video_counter += 1
                self.link_finished.emit()

        self.all_done.emit()

    def _is_profile(self, url):
        pattern = r'https?://(?:www\.)?tiktok\.com/@([A-Za-z0-9_.]+)/?(?:\?.*)?(?:#.*)?$'
        match = re.match(pattern, url.strip())
        return match.group(1) if match else None

    def _fetch_video_urls(self, profile_url, limit):
        """Return a list of direct video URLs from a profile."""
        ydl_opts = {
            'extract_flat': True,
            'quiet': True,
            'no_warnings': True,
        }
        if limit != -1:  # if limit is not 'all'
            ydl_opts['playlistend'] = limit

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(profile_url, download=False)

        entries = info.get('entries', [])
        video_urls = []
        username = self._is_profile(profile_url)
        for entry in entries:
            vid_url = entry.get('url') or entry.get('webpage_url')
            if not vid_url:
                vid_id = entry.get('id')
                if vid_id and username:
                    vid_url = f"https://www.tiktok.com/@{username}/video/{vid_id}"
                else:
                    continue
            video_urls.append(vid_url)
        return video_urls

    def _download_video(self, url, filename):
        ydl_opts = {
            'outtmpl': os.path.join(self.folder, filename),
            'format': 'mp4/best',
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
            'merge_output_format': 'mp4',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

# ---------- Main UI ----------
class TikTokDownloaderUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TikTok Downloader")
        self.setMinimumSize(650, 500)
        self.setup_ui()
        self.apply_stylesheet()

        self.download_list = []      # each item: (url, limit)
        self.worker = None

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(12)

        # --- Input row ---
        input_row = QHBoxLayout()
        self.link_input = QLineEdit()
        self.link_input.setPlaceholderText("Paste TikTok link (video or profile)...")
        self.link_input.returnPressed.connect(self.add_link)
        input_row.addWidget(self.link_input)

        add_btn = QPushButton("➕ Add Link")
        add_btn.clicked.connect(self.add_link)
        input_row.addWidget(add_btn)

        file_btn = QPushButton("📂 Select File")
        file_btn.clicked.connect(self.load_file)
        input_row.addWidget(file_btn)

        layout.addLayout(input_row)

        # --- Link list ---
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        # --- Buttons row ---
        btn_row = QHBoxLayout()
        clear_btn = QPushButton("🗑️ Clear List")
        clear_btn.clicked.connect(self.clear_list)
        btn_row.addWidget(clear_btn)

        self.download_btn = QPushButton("⬇️ Download All")
        self.download_btn.clicked.connect(self.start_download)
        btn_row.addWidget(self.download_btn)

        cancel_btn = QPushButton("⏹️ Cancel")
        cancel_btn.clicked.connect(self.cancel_download)
        btn_row.addWidget(cancel_btn)

        layout.addLayout(btn_row)

        # --- Progress ---
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Ready.")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

    def apply_stylesheet(self):
        style = """
        QMainWindow {
            background-color: #2b2b2b;
        }
        QWidget {
            color: #eeeeee;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 13px;
        }
        QLineEdit {
            background-color: #3c3f41;
            border: 1px solid #555;
            border-radius: 6px;
            padding: 8px;
            color: #fff;
        }
        QPushButton {
            background-color: #007acc;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            color: white;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #0098ff;
        }
        QPushButton:pressed {
            background-color: #005f99;
        }
        QPushButton:disabled {
            background-color: #4a4a4a;
            color: #aaa;
        }
        QListWidget {
            background-color: #313335;
            border: 1px solid #555;
            border-radius: 6px;
            padding: 4px;
            color: #ddd;
        }
        QListWidget::item {
            padding: 6px;
            border-bottom: 1px solid #444;
        }
        QListWidget::item:selected {
            background-color: #264f78;
        }
        QProgressBar {
            border: 1px solid #555;
            border-radius: 6px;
            text-align: center;
            background-color: #3c3f41;
            color: white;
        }
        QProgressBar::chunk {
            background-color: #007acc;
            border-radius: 5px;
        }
        QLabel {
            color: #ccc;
        }
        """
        self.setStyleSheet(style)

    # ---------- Add / Load links ----------
    def add_link(self):
        url = self.link_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Warning", "Please enter a TikTok link.")
            return

        limit = 1   # default single video
        username = self._profile_username(url)
        if username:
            limit = self._ask_profile_limit(username)
            if limit is None:   # user cancelled dialog
                return

        self.download_list.append((url, limit))
        display = self._make_display_text(url, limit, username)
        self.list_widget.addItem(display)
        self.link_input.clear()

    def _profile_username(self, url):
        pattern = r'https?://(?:www\.)?tiktok\.com/@([A-Za-z0-9_.]+)/?(?:\?.*)?(?:#.*)?$'
        match = re.match(pattern, url.strip())
        return match.group(1) if match else None

    def _ask_profile_limit(self, username):
        """Ask the user how many videos to download from a profile."""
        text, ok = QInputDialog.getText(
            self, f"Profile @{username}",
            "How many videos?\nType 'all' or a number:",
            text="all"
        )
        if not ok:
            return None
        if text.strip().lower() == "all":
            return -1
        try:
            num = int(text)
            if num > 0:
                return num
            else:
                QMessageBox.warning(self, "Invalid", "Number must be positive.")
                return None
        except ValueError:
            QMessageBox.warning(self, "Invalid", "Please type 'all' or a positive number.")
            return None

    def _make_display_text(self, url, limit, username=None):
        if limit == -1:
            return f"@{username} – All videos"
        elif limit == 1:
            if username:  # shouldn't happen for profile, but just in case
                return f"@{username} – 1 video"
            else:
                # show shortened url
                short = url if len(url) < 50 else url[:47] + "..."
                return f"Video: {short}"
        else:
            return f"@{username} – {limit} videos"

    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Text File", "", "Text Files (*.txt);;All Files (*)"
        )
        if not file_path:
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not read file:\n{e}")
            return

        if not lines:
            QMessageBox.information(self, "Info", "The file is empty.")
            return

        # Check if file contains any profile links, ask global limit
        has_profile = any(self._profile_username(l) for l in lines)
        global_limit = 1
        if has_profile:
            choice, ok = QInputDialog.getText(
                self, "Profile Videos",
                "For ALL profile links in this file,\nhow many videos? (all / number):",
                text="all"
            )
            if not ok:
                return
            choice = choice.strip().lower()
            if choice == "all":
                global_limit = -1
            else:
                try:
                    global_limit = int(choice)
                    if global_limit <= 0:
                        raise ValueError
                except ValueError:
                    QMessageBox.warning(self, "Invalid", "Using 'all' as default.")
                    global_limit = -1

        # Add all lines to the list
        for url in lines:
            username = self._profile_username(url)
            if username:
                limit = global_limit
            else:
                limit = 1
            self.download_list.append((url, limit))
            display = self._make_display_text(url, limit, username)
            self.list_widget.addItem(display)

    def clear_list(self):
        self.download_list.clear()
        self.list_widget.clear()
        self.status_label.setText("List cleared.")

    # ---------- Download logic ----------
    def start_download(self):
        if not self.download_list:
            QMessageBox.information(self, "Info", "No links to download.")
            return

        if self.worker and self.worker.isRunning():
            QMessageBox.warning(self, "Busy", "A download is already in progress.")
            return

        self.progress_bar.setMaximum(len(self.download_list))
        self.progress_bar.setValue(0)
        self.status_label.setText("Starting...")

        self.download_btn.setEnabled(False)
        self.list_widget.setEnabled(False)

        self.worker = DownloadWorker(self.download_list[:])  # copy
        self.worker.progress_signal.connect(self.update_status)
        self.worker.link_finished.connect(self.on_link_finished)
        self.worker.all_done.connect(self.on_download_finished)
        self.worker.start()

    def cancel_download(self):
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.status_label.setText("Cancelling...")

    def update_status(self, msg):
        self.status_label.setText(msg)

    def on_link_finished(self):
        self.progress_bar.setValue(self.progress_bar.value() + 1)

    def on_download_finished(self):
        self.progress_bar.setValue(self.progress_bar.maximum())
        self.status_label.setText("✅ All downloads completed!")
        self.download_btn.setEnabled(True)
        self.list_widget.setEnabled(True)
        self.worker = None

# ---------- Run the app ----------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TikTokDownloaderUI()
    window.show()
    sys.exit(app.exec_())