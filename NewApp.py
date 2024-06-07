import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QFileDialog, QLabel, QVBoxLayout, QMessageBox, QHBoxLayout, QLineEdit, QStyle)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
import subprocess
import threading

class StreamApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('Automated OBS Streaming Only for Youtube')

        self.status_label = QLabel(self)
        self.status_label.setFixedSize(20, 20)
        self.status_label.setStyleSheet("background-color: red; border-radius: 10px;")
        
        self.label = QLabel('Select a video file', self)
        self.label.setFont(QFont('Arial', 14))
        self.label.setAlignment(Qt.AlignCenter)

        self.key_label = QLabel('YouTube Streaming Key:', self)
        self.key_label.setFont(QFont('Arial', 12))

        self.key_input = QLineEdit(self)
        self.key_input.setFont(QFont('Arial', 12))
        
        self.btn = QPushButton('Browse', self)
        self.btn.setFont(QFont('Arial', 12))
        self.btn.clicked.connect(self.showDialog)
        
        self.start_btn = QPushButton('Start Streaming', self)
        self.start_btn.setFont(QFont('Arial', 12))
        self.start_btn.clicked.connect(self.startStreaming)

        self.stop_btn = QPushButton('Stop Streaming', self)
        self.stop_btn.setFont(QFont('Arial', 12))
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stopStreaming)
        
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

        hbox = QHBoxLayout()
        hbox.addWidget(self.status_label)
        hbox.addStretch(1)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(self.label)
        vbox.addWidget(self.key_label)
        vbox.addWidget(self.key_input)
        vbox.addWidget(self.btn)
        vbox.addWidget(self.start_btn)
        vbox.addWidget(self.stop_btn)
        vbox.addWidget(self.video_widget)
        
        video_control_box = QHBoxLayout()
        video_control_box.addWidget(self.play_btn)
        video_control_box.addWidget(self.stop_video_btn)
        vbox.addLayout(video_control_box)
        
        self.setLayout(vbox)
        
        self.video_path = None
        self.ffmpeg_process = None
    
    def showDialog(self):
        options = QFileDialog.Options()
        self.video_path, _ = QFileDialog.getOpenFileName(self, "Select Video File", "", "All Files (*);;MP4 Files (*.mp4)", options=options)
        if self.video_path:
            self.label.setText(f"Selected file: {self.video_path}")
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(self.video_path)))
            self.play_btn.setEnabled(True)
            self.stop_video_btn.setEnabled(True)
    
    def startStreaming(self):
        if self.video_path and self.key_input.text():
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.updateStatusLabel("green")
            threading.Thread(target=self.run_ffmpeg).start()
        else:
            self.showMessageBox("Error", "Please select a video file and enter the YouTube streaming key.")
    
    def run_ffmpeg(self):
        stream_key = self.key_input.text()
        stream_url = f"rtmp://a.rtmp.youtube.com/live2/{stream_key}"
        ffmpeg_path = r"C:/ffmpeg/bin/ffmpeg.exe"  # Replace with the correct path
        command = [
            ffmpeg_path, '-re', '-i', self.video_path, '-c:v', 'libx264', '-preset', 'veryfast', 
            '-maxrate', '3000k', '-bufsize', '6000k', '-pix_fmt', 'yuv420p', '-g', '50', '-c:a', 'aac', 
            '-b:a', '128k', '-ar', '44100', '-f', 'flv', stream_url
        ]
        print("Running command:", command)
        try:
            self.ffmpeg_process = subprocess.Popen(command)
            self.ffmpeg_process.wait()
        except FileNotFoundError as e:
            self.showMessageBox("File Not Found", f"FileNotFoundError: {e}")
        except Exception as e:
            self.showMessageBox("Error", f"An error occurred: {e}")
        finally:
            self.updateStatusLabel("red")
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
    
    def stopStreaming(self):
        if self.ffmpeg_process:
            self.ffmpeg_process.terminate()
            self.ffmpeg_process = None
            self.showMessageBox("Stopped", "Streaming stopped successfully!")
            self.updateStatusLabel("red")
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)

    def playVideo(self):
        self.media_player.play()
        self.play_btn.setEnabled(False)
        self.stop_video_btn.setEnabled(True)

    def stopVideo(self):
        self.media_player.stop()
        self.play_btn.setEnabled(True)
        self.stop_video_btn.setEnabled(False)
    
    def updateStatusLabel(self, color):
        self.status_label.setStyleSheet(f"background-color: {color}; border-radius: 10px;")
    
    def showMessageBox(self, title, message):
        QMessageBox.information(self, title, message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = StreamApp()
    ex.show()
    sys.exit(app.exec_())
