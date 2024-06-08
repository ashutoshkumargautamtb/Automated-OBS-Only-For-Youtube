import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QFileDialog, QLabel, QVBoxLayout, 
                             QMessageBox, QHBoxLayout, QLineEdit, QTimeEdit, QTextEdit)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QUrl, QTime, QTimer
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
import subprocess
import threading
import datetime

class StreamApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setGeometry(100, 100, 1000, 600)
        self.setWindowTitle('Automated OBS Streaming Only for Youtube')

        # Status label at the top center
        self.status_label = QLabel(self)
        self.status_label.setFont(QFont('Arial', 14))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.updateStatusLabel("red", "Streaming is off")

        self.label = QLabel('Select a video file', self)
        self.label.setFont(QFont('Arial', 14))
        self.label.setAlignment(Qt.AlignCenter)

        self.key_label = QLabel('YouTube Streaming Key:', self)
        self.key_label.setFont(QFont('Arial', 12))

        self.key_input = QLineEdit(self)
        self.key_input.setFont(QFont('Arial', 12))

        self.schedule_label = QLabel('Schedule Time (HH:MM):', self)
        self.schedule_label.setFont(QFont('Arial', 12))

        self.time_input = QTimeEdit(self)
        self.time_input.setDisplayFormat('HH:mm')
        self.time_input.setFont(QFont('Arial', 12))
        
        self.btn = QPushButton('Browse Video', self)
        self.btn.setFont(QFont('Arial', 12))
        self.btn.clicked.connect(self.showVideoDialog)

        self.ticker_btn = QPushButton('Browse Ticker Image', self)
        self.ticker_btn.setFont(QFont('Arial', 12))
        self.ticker_btn.clicked.connect(self.showTickerDialog)
        
        self.start_btn = QPushButton('Start Streaming', self)
        self.start_btn.setFont(QFont('Arial', 12))
        self.start_btn.clicked.connect(self.startStreaming)

        self.stop_btn = QPushButton('Stop Streaming', self)
        self.stop_btn.setFont(QFont('Arial', 12))
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stopStreaming)

        self.schedule_btn = QPushButton('Schedule Streaming', self)
        self.schedule_btn.setFont(QFont('Arial', 12))
        self.schedule_btn.clicked.connect(self.scheduleStreaming)
        
        self.play_btn = QPushButton('Play Video', self)
        self.play_btn.setFont(QFont('Arial', 12))
        self.play_btn.setEnabled(False)
        self.play_btn.clicked.connect(self.playVideo)
        
        self.stop_video_btn = QPushButton('Stop Video', self)
        self.stop_video_btn.setFont(QFont('Arial', 12))
        self.stop_video_btn.setEnabled(False)
        self.stop_video_btn.clicked.connect(self.stopVideo)

        self.video_widget = QVideoWidget(self)
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.media_player.setVideoOutput(self.video_widget)

        self.log_output = QTextEdit(self)
        self.log_output.setFont(QFont('Arial', 12))
        self.log_output.setReadOnly(True)
        
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.label)
        left_layout.addWidget(self.key_label)
        left_layout.addWidget(self.key_input)
        left_layout.addWidget(self.schedule_label)
        left_layout.addWidget(self.time_input)
        left_layout.addWidget(self.btn)
        left_layout.addWidget(self.ticker_btn)
        left_layout.addWidget(self.start_btn)
        left_layout.addWidget(self.schedule_btn)
        left_layout.addWidget(self.stop_btn)
        left_layout.addWidget(self.video_widget)
        
        video_control_box = QHBoxLayout()
        video_control_box.addWidget(self.play_btn)
        video_control_box.addWidget(self.stop_video_btn)
        left_layout.addLayout(video_control_box)
        
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.log_output)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.status_label)
        
        content_layout = QHBoxLayout()
        content_layout.addLayout(left_layout, 2)
        content_layout.addLayout(right_layout, 1)
        main_layout.addLayout(content_layout)

        self.setLayout(main_layout)

        self.video_path = None
        self.ticker_path = None
        self.ffmpeg_process = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_schedule)
        self.timer.start(1000)  # Check every second

    def log_message(self, message):
        self.log_output.append(message)
    
    def showVideoDialog(self):
        options = QFileDialog.Options()
        self.video_path, _ = QFileDialog.getOpenFileName(self, "Select Video File", "", "All Files (*);;MP4 Files (*.mp4)", options=options)
        if self.video_path:
            self.label.setText(f"Selected file: {self.video_path}")
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(self.video_path)))
            self.play_btn.setEnabled(True)
            self.stop_video_btn.setEnabled(True)
            self.log_message(f"Selected file: {self.video_path}")

    def showTickerDialog(self):
        options = QFileDialog.Options()
        self.ticker_path, _ = QFileDialog.getOpenFileName(self, "Select Ticker Image", "", "All Files (*);;PNG Files (*.png);;JPG Files (*.jpg)", options=options)
        if self.ticker_path:
            self.log_message(f"Selected ticker image: {self.ticker_path}")
    
    def startStreaming(self):
        if self.video_path and self.key_input.text() and self.ticker_path:
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.updateStatusLabel("green", "Streaming is on")
            self.log_message("Starting streaming...")
            threading.Thread(target=self.run_ffmpeg).start()
        else:
            self.showMessageBox("Error", "Please select a video file, ticker image, and enter the YouTube streaming key.")
    
    def run_ffmpeg(self):
        stream_key = self.key_input.text()
        stream_url = f"rtmp://a.rtmp.youtube.com/live2/{stream_key}"
        ffmpeg_path = r"C:/ffmpeg/bin/ffmpeg.exe"  # Replace with the correct path
        command = [
            ffmpeg_path, '-re', '-i', self.video_path, '-i', self.ticker_path,
            '-filter_complex', '[1:v]scale=iw:-1[ticker];[0:v][ticker]overlay=0:H-h',
            '-c:v', 'libx264', '-preset', 'veryfast', 
            '-maxrate', '3000k', '-bufsize', '6000k', '-pix_fmt', 'yuv420p', '-g', '50', '-c:a', 'aac', 
            '-b:a', '128k', '-ar', '44100', '-f', 'flv', stream_url
        ]
        self.log_message(f"Running command: {command}")
        try:
            self.ffmpeg_process = subprocess.Popen(command)
            self.ffmpeg_process.wait()
        except FileNotFoundError as e:
            self.showMessageBox("File Not Found", f"FileNotFoundError: {e}")
            self.log_message(f"FileNotFoundError: {e}")
        except Exception as e:
            self.showMessageBox("Error", f"An error occurred: {e}")
            self.log_message(f"An error occurred: {e}")
        finally:
            self.updateStatusLabel("red", "Streaming is off")
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.log_message("Streaming stopped.")
    
    def stopStreaming(self):
        if self.ffmpeg_process:
            self.ffmpeg_process.terminate()
            self.ffmpeg_process = None
            self.showMessageBox("Stopped", "Streaming stopped successfully!")
            self.updateStatusLabel("red", "Streaming is off")
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.log_message("Streaming stopped by user.")

    def playVideo(self):
        self.media_player.play()
        self.play_btn.setEnabled(False)
        self.stop_video_btn.setEnabled(True)
        self.log_message("Playing video.")

    def stopVideo(self):
        self.media_player.stop()
        self.play_btn.setEnabled(True)
        self.stop_video_btn.setEnabled(False)
        self.log_message("Stopped video.")
    
    def scheduleStreaming(self):
        self.scheduled_time = self.time_input.time().toString('HH:mm')
        self.showMessageBox("Scheduled", f"Streaming scheduled at {self.scheduled_time}")
        self.log_message(f"Streaming scheduled at {self.scheduled_time}")
    
    def check_schedule(self):
        current_time = datetime.datetime.now().strftime('%H:%M')
        if hasattr(self, 'scheduled_time') and self.scheduled_time == current_time:
            self.startStreaming()
            delattr(self, 'scheduled_time')  # Remove the attribute after starting streaming
    
    def updateStatusLabel(self, color, text):
        color_circle = f'<span style="color: {color}; font-size: 46px;">&#9679;</span>'
        self.status_label.setText(f"{color_circle} {text}")

    def showMessageBox(self, title, message):
        QMessageBox.information(self, title, message)
        self.log_message(message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = StreamApp()
    ex.show()
    sys.exit(app.exec_())
