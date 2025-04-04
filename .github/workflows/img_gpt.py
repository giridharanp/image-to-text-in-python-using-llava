import os
import sys
import ollama
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QFileDialog, QVBoxLayout, QWidget, QTextEdit
from PyQt5.QtGui import QPixmap, QIcon

class Worker(QThread):
    result_ready = pyqtSignal(str)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def run(self):
        res = ollama.chat(
            model='llava',
            messages=[{
                'role': 'user',
                'content': 'Describe this image',
                'images': [self.file_path]
            }]
        )
        result_text = res['message']['content']
        self.result_ready.emit(result_text)

class ImageInputApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('IMG2TXT')

        # Set the window icon
        icon_path = os.path.join(os.path.dirname(__file__), 'luffy.ico')
        self.setWindowIcon(QIcon(icon_path))

        # Create a central widget and set a layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # QLabel to display the image
        self.image_label = QLabel('No image selected', self)
        self.image_label.setScaledContents(True)
        layout.addWidget(self.image_label)

        # QTextEdit for text input below the QLabel
        self.text_edit = QTextEdit(self)
        layout.addWidget(self.text_edit)

        # QPushButton to browse for an image
        self.browse_button = QPushButton('Browse', self)
        self.browse_button.clicked.connect(self.browse_image)
        layout.addWidget(self.browse_button)

        # QPushButton to trigger the image to text conversion
        self.go_btn = QPushButton('GO', self)
        self.go_btn.clicked.connect(self.img2text)
        layout.addWidget(self.go_btn)

        self.setGeometry(300, 300, 350, 450)

    def browse_image(self):
        options = QFileDialog.Options()
        self.file_path, _ = QFileDialog.getOpenFileName(self, "Select an Image", "",
                                                        "Image Files (*.png *.jpg *.bmp);;All Files (*)",
                                                        options=options)
        if self.file_path:
            self.image_label.setPixmap(QPixmap(self.file_path))
            self.browse_button.setDisabled(True)

    def img2text(self):
        self.go_btn.setDisabled(True)
        self.text_edit.setText("")
        self.text_edit.setDisabled(True)

        # Create and start the worker thread
        self.worker = Worker(self.file_path)
        self.worker.result_ready.connect(self.display_result)
        self.worker.start()

    def display_result(self, result_text):
        self.text_edit.setText(result_text)
        self.browse_button.setDisabled(False)
        self.go_btn.setDisabled(False)
        self.text_edit.setDisabled(False)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageInputApp()
    ex.show()
    sys.exit(app.exec_())
