import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QLabel
import subprocess

class StreamApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setGeometry(100, 100, 400, 300)
        self.setWindowTitle('Simple Streamer')
        
        self.label = QLabel('Select a video file', self)
        self.label.move(20, 20)
        
        self.btn = QPushButton('Browse', self)
        self.btn.move(20, 50)
        self.btn.clicked.connect(self.showDialog)
        
        self.start_btn = QPushButton('Start Streaming', self)
        self.start_btn.move(20, 100)
        self.start_btn.clicked.connect(self.startStreaming)
        
        self.video_path = None
    
    def showDialog(self):
        options = QFileDialog.Options()
        self.video_path, _ = QFileDialog.getOpenFileName(self, "Select Video File", "", "All Files (*);;MP4 Files (*.mp4)", options=options)
        if self.video_path:
            self.label.setText(self.video_path)
    
    def startStreaming(self):
        if self.video_path:
            stream_url = "rtmp://a.rtmp.youtube.com/live2/cs2f-ev2w-m9z9-qg9y-erqk"
            ffmpeg_path = r"C:/ffmpeg/bin/ffmpeg.exe"  # Replace with the correct path
            command = [
                ffmpeg_path, '-re', '-i', self.video_path, '-c:v', 'libx264', '-preset', 'veryfast', 
                '-maxrate', '3000k', '-bufsize', '6000k', '-pix_fmt', 'yuv420p', '-g', '50', '-c:a', 'aac', 
                '-b:a', '128k', '-ar', '44100', '-f', 'flv', stream_url
            ]
            subprocess.run(command, check=True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = StreamApp()
    ex.show()
    sys.exit(app.exec_())
