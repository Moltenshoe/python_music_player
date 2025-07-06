import sys
import os
import pygame
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QLabel, QFrame, QSlider, QFileDialog,
    QGraphicsBlurEffect
)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import (
    QColor, QPalette, QFont, QPixmap, QBrush, QPainter, 
    QIcon, QLinearGradient
)

# Initialize Pygame Mixer
pygame.mixer.init()

class Song:
    def __init__(self, title, artist, album, duration, file_path):
        self.title = title
        self.artist = artist
        self.album = album
        self.duration = duration
        self.file_path = file_path

class Playlist:
    def __init__(self, name):
        self.name = name
        self.songs = []

    def add_song(self, song):
        self.songs.append(song)
        
    def add_songs_from_folder(self, folder_path):
        for file in os.listdir(folder_path):
            if file.endswith(('.wav', '.mp3', '.ogg', '.flac')):
                song = Song(
                    title=os.path.splitext(file)[0],
                    artist="Unknown Artist",
                    album="Unknown Album",
                    duration="0:00",
                    file_path=os.path.join(folder_path, file)
                )
                self.add_song(song)

class MusicPlayer:
    def __init__(self):
        self.playlist = None
        self.current_song_index = 0
        self.is_playing = False
        self.is_paused = False

    def load_playlist(self, playlist):
        self.playlist = playlist

    def play(self):
        if not self.playlist or not self.playlist.songs:
            return "No playlist loaded"
        
        if self.current_song_index >= len(self.playlist.songs):
            self.current_song_index = 0
            
        song = self.playlist.songs[self.current_song_index]
        try:
            pygame.mixer.music.load(song.file_path)
            pygame.mixer.music.play()
            self.is_playing = True
            self.is_paused = False
            return f"{song.title} - {song.artist}"
        except Exception as e:
            return f"Error: {str(e)}"

    def pause(self):
        if not self.is_playing:
            return "Not playing"
            
        if self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
            return "Resumed"
        else:
            pygame.mixer.music.pause()
            self.is_paused = True
            return "Paused"

    def stop(self):
        pygame.mixer.music.stop()
        self.is_playing = False
        self.is_paused = False

    def next_song(self):
        if not self.playlist or not self.playlist.songs:
            return "No playlist loaded"
            
        self.current_song_index = (self.current_song_index + 1) % len(self.playlist.songs)
        return self.play()

    def previous_song(self):
        if not self.playlist or not self.playlist.songs:
            return "No playlist loaded"
            
        self.current_song_index = (self.current_song_index - 1) % len(self.playlist.songs)
        return self.play()

class BlurredBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.background = QPixmap("data/music-player-2951399_1280.webp")
        if self.background.isNull():
            # Create a gradient fallback
            self.background = QPixmap(1000, 650)
            self.background.fill(Qt.black)
            painter = QPainter(self.background)
            gradient = QLinearGradient(0, 0, 0, 650)
            gradient.setColorAt(0, QColor(30, 30, 50))
            gradient.setColorAt(1, QColor(10, 10, 20))
            painter.fillRect(self.background.rect(), gradient)
            painter.end()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        scaled_bg = self.background.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        painter.drawPixmap(0, 0, scaled_bg)
        painter.setOpacity(0.85)
        painter.fillRect(self.rect(), QColor(20, 20, 30, 220))

class MusicPlayerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Harmony Player")
        self.setGeometry(100, 100, 1000, 650)
        self.setMinimumSize(800, 500)
        
        # Set up background
        self.background = BlurredBackground()
        self.setCentralWidget(self.background)
        
        # Main content widget
        self.main_widget = QWidget()
        self.main_widget.setStyleSheet("background: transparent;")
        
        # Custom icons and font
        self.font = QFont("Futura", 12)
        self.bold_font = QFont("Futura", 14, QFont.Bold)
        
        # Initialize playlist and player
        self.playlist = Playlist("My Playlist")
        self.music_player = MusicPlayer()
        self.music_player.load_playlist(self.playlist)
        
        # Main layout
        self.main_layout = QHBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Setup UI
        self.setup_sidebar()
        self.setup_separator()
        self.setup_main_content()
        
        # Add main widget to background
        layout = QVBoxLayout(self.background)
        layout.addWidget(self.main_widget)
        
        # Timer for progress updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(100)
        
        # Set dark theme by default
        self.set_dark_theme()

    def setup_sidebar(self):
        """Left sidebar with albums"""
        self.sidebar = QFrame()
        self.sidebar.setFrameShape(QFrame.StyledPanel)
        self.sidebar.setStyleSheet("""
            background: rgba(25, 25, 35, 220);
            border: none;
            border-radius: 0px;
        """)
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(15, 20, 15, 20)
        sidebar_layout.setSpacing(15)
        
        # Albums header with icon
        albums_header = QHBoxLayout()
        icon_label = QLabel()
        icon_pixmap = QPixmap("data/music-player-icon-png-11552246944dtgsj5obcg.png")
        if icon_pixmap.isNull():
            icon_pixmap = QPixmap(30, 30)
            icon_pixmap.fill(Qt.transparent)
        icon_pixmap = icon_pixmap.scaled(28, 28, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        icon_label.setPixmap(icon_pixmap)
        
        albums_label = QLabel("LIBRARY")
        albums_label.setFont(self.bold_font)
        albums_label.setStyleSheet("color: #5bc0de;")
        
        albums_header.addWidget(icon_label)
        albums_header.addWidget(albums_label)
        albums_header.addStretch()
        sidebar_layout.addLayout(albums_header)
        
        # Album list
        self.album_list = QListWidget()
        self.album_list.setFont(self.font)
        self.album_list.addItems(["All Songs", "Recently Added", "Favorites", "+ Add Folder"])
        self.album_list.setStyleSheet("""
            QListWidget {
                background: rgba(40, 40, 50, 120);
                border: none;
                border-radius: 8px;
                color: white;
            }
            QListWidget::item {
                padding: 12px 15px;
                border-bottom: 1px solid rgba(60, 60, 70, 100);
            }
            QListWidget::item:hover {
                background: rgba(60, 60, 70, 150);
            }
            QListWidget::item:selected {
                background: rgba(80, 80, 90, 180);
                border-left: 3px solid #5bc0de;
            }
        """)
        sidebar_layout.addWidget(self.album_list, 1)
        
        # Player stats at bottom
        stats_label = QLabel(f"{len(self.playlist.songs)} songs")
        stats_label.setFont(QFont("Futura", 10))
        stats_label.setStyleSheet("color: rgba(200, 200, 200, 150);")
        stats_label.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(stats_label)
        
        self.main_layout.addWidget(self.sidebar, 1)  # 25% width

    def setup_separator(self):
        """Vertical separator line"""
        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.VLine)
        self.separator.setLineWidth(1)
        self.separator.setStyleSheet("background: rgba(100, 100, 120, 80);")
        self.main_layout.addWidget(self.separator)

    def setup_main_content(self):
        """Right side with songs and controls"""
        self.content = QWidget()
        self.content.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout(self.content)
        content_layout.setContentsMargins(25, 25, 25, 25)
        content_layout.setSpacing(20)
        
        # Songs list
        self.song_list = QListWidget()
        self.song_list.setFont(self.font)
        self.song_list.setStyleSheet("""
            QListWidget {
                background: rgba(40, 40, 50, 120);
                border: none;
                border-radius: 10px;
                color: white;
            }
            QListWidget::item {
                padding: 14px 20px;
                border-bottom: 1px solid rgba(60, 60, 70, 100);
            }
            QListWidget::item:hover {
                background: rgba(60, 60, 70, 150);
            }
            QListWidget::item:selected {
                background: rgba(80, 80, 90, 180);
            }
        """)
        content_layout.addWidget(self.song_list, 1)
        
        # Now playing info
        now_playing_layout = QVBoxLayout()
        now_playing_layout.setSpacing(5)
        
        self.song_title = QLabel("No song selected")
        self.song_title.setFont(QFont("Futura", 16, QFont.Bold))
        self.song_title.setStyleSheet("color: white;")
        self.song_title.setAlignment(Qt.AlignCenter)
        
        self.song_artist = QLabel("")
        self.song_artist.setFont(QFont("Futura", 12))
        self.song_artist.setStyleSheet("color: rgba(200, 200, 200, 180);")
        self.song_artist.setAlignment(Qt.AlignCenter)
        
        now_playing_layout.addWidget(self.song_title)
        now_playing_layout.addWidget(self.song_artist)
        content_layout.addLayout(now_playing_layout)
        
        # Progress bar
        self.progress = QSlider(Qt.Horizontal)
        self.progress.setRange(0, 100)
        self.progress.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 6px;
                background: rgba(70, 70, 80, 150);
                border-radius: 3px;
            }
            QSlider::sub-page:horizontal {
                background: #5bc0de;
                border-radius: 3px;
            }
            QSlider::add-page:horizontal {
                background: rgba(70, 70, 80, 150);
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: white;
                width: 16px;
                height: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }
        """)
        content_layout.addWidget(self.progress)
        
        # Time labels
        time_layout = QHBoxLayout()
        self.time_elapsed = QLabel("0:00")
        self.time_elapsed.setFont(QFont("Futura", 10))
        self.time_elapsed.setStyleSheet("color: rgba(200, 200, 200, 150);")
        
        self.time_remaining = QLabel("-0:00")
        self.time_remaining.setFont(QFont("Futura", 10))
        self.time_remaining.setStyleSheet("color: rgba(200, 200, 200, 150);")
        self.time_remaining.setAlignment(Qt.AlignRight)
        
        time_layout.addWidget(self.time_elapsed)
        time_layout.addWidget(self.time_remaining)
        content_layout.addLayout(time_layout)
        
        # Controls
        controls = QHBoxLayout()
        controls.setSpacing(20)
        
        # Create control buttons with custom icons
        self.prev_btn = self.create_control_button("⏮", "Previous")
        self.play_btn = self.create_control_button("▶", "Play", larger=True)
        self.next_btn = self.create_control_button("⏭", "Next")
        
        controls.addStretch()
        controls.addWidget(self.prev_btn)
        controls.addWidget(self.play_btn)
        controls.addWidget(self.next_btn)
        controls.addStretch()
        
        content_layout.addLayout(controls)
        
        self.main_layout.addWidget(self.content, 3)  # 75% width
        
        # Connect signals
        self.play_btn.clicked.connect(self.toggle_play)
        self.prev_btn.clicked.connect(self.play_previous)
        self.next_btn.clicked.connect(self.play_next)
        self.song_list.itemDoubleClicked.connect(self.play_selected_song)
        self.album_list.itemClicked.connect(self.handle_album_selection)

    def create_control_button(self, symbol, tooltip, larger=False):
        """Create styled control button with symbol"""
        btn = QPushButton(symbol)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setToolTip(tooltip)
        
        font_size = 16 if larger else 14
        btn.setFont(QFont("Futura", font_size))
        
        btn.setStyleSheet("""
            QPushButton {
                background: rgba(60, 60, 70, 180);
                color: white;
                border: none;
                border-radius: 30px;
                min-width: 50px;
                min-height: 50px;
            }
            QPushButton:hover {
                background: rgba(80, 80, 90, 200);
            }
            QPushButton:pressed {
                background: rgba(40, 40, 50, 180);
            }
        """)
        
        if larger:
            btn.setFixedSize(70, 70)
            btn.setStyleSheet(btn.styleSheet() + """
                QPushButton {
                    min-width: 60px;
                    min-height: 60px;
                }
            """)
        else:
            btn.setFixedSize(60, 60)
            
        return btn

    def update_song_list(self):
        """Populate song list from playlist"""
        self.song_list.clear()
        for song in self.playlist.songs:
            self.song_list.addItem(f"{song.title} - {song.artist} ({song.duration})")

    def toggle_play(self):
        """Toggle between play and pause"""
        if not self.music_player.is_playing:
            self.play_selected_song()
        else:
            status = self.music_player.pause()
            self.play_btn.setText("▶" if self.music_player.is_paused else "⏸")
            self.update_now_playing(status)

    def play_selected_song(self, item=None):
        """Play the selected song"""
        if item is not None:
            selected_row = self.song_list.row(item)
            self.music_player.current_song_index = selected_row
        elif self.song_list.currentRow() >= 0:
            self.music_player.current_song_index = self.song_list.currentRow()
        
        status = self.music_player.play()
        self.play_btn.setText("⏸")
        self.update_now_playing(status)
        self.song_list.setCurrentRow(self.music_player.current_song_index)

    def update_now_playing(self, status):
        """Update the now playing display"""
        if self.music_player.playlist and self.music_player.current_song_index < len(self.music_player.playlist.songs):
            song = self.music_player.playlist.songs[self.music_player.current_song_index]
            self.song_title.setText(song.title)
            self.song_artist.setText(song.artist)
        else:
            self.song_title.setText("No song selected")
            self.song_artist.setText("")

    def play_previous(self):
        """Play previous song"""
        status = self.music_player.previous_song()
        self.play_btn.setText("⏸")
        self.update_now_playing(status)
        self.song_list.setCurrentRow(self.music_player.current_song_index)

    def play_next(self):
        """Play next song"""
        status = self.music_player.next_song()
        self.play_btn.setText("⏸")
        self.update_now_playing(status)
        self.song_list.setCurrentRow(self.music_player.current_song_index)

    def handle_album_selection(self, item):
        """Handle album selection"""
        if item.text() == "+ Add Folder":
            folder = QFileDialog.getExistingDirectory(self, "Select Music Folder")
            if folder:
                self.playlist.add_songs_from_folder(folder)
                self.update_song_list()
                album_name = os.path.basename(folder)
                self.album_list.insertItem(self.album_list.count()-1, album_name)

    def update_progress(self):
        """Update progress bar and time labels"""
        if self.music_player.is_playing and not self.music_player.is_paused:
            pos_ms = pygame.mixer.music.get_pos()
            if pos_ms >= 0:  # -1 means no song playing
                pos_sec = pos_ms / 1000
                duration = self.get_current_duration()
                if duration > 0:
                    progress = int((pos_sec / duration) * 100)
                    self.progress.setValue(progress)
                    
                    # Update time labels
                    mins, secs = divmod(int(pos_sec), 60)
                    self.time_elapsed.setText(f"{mins}:{secs:02d}")
                    
                    remaining = duration - pos_sec
                    mins, secs = divmod(int(remaining), 60)
                    self.time_remaining.setText(f"-{mins}:{secs:02d}")
                    
                    # Auto-play next song when current ends
                    if progress >= 99:
                        self.play_next()

    def get_current_duration(self):
        """Get duration of current song in seconds"""
        if (self.music_player.playlist and 
            self.music_player.current_song_index < len(self.music_player.playlist.songs)):
            mins, secs = map(int, self.playlist.songs[self.music_player.current_song_index].duration.split(':'))
            return mins * 60 + secs
        return 0

    def set_dark_theme(self):
        """Apply dark theme"""
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(30, 30, 40))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(20, 20, 30))
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(50, 50, 60))
        palette.setColor(QPalette.ButtonText, Qt.white)
        self.setPalette(palette)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Set default font
    font = QFont("Futura", 13)
    app.setFont(font)
    
    # Create and show player
    player = MusicPlayerApp()
    player.show()
    
    sys.exit(app.exec_())