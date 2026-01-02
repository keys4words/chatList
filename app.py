import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Minimal PyQt App")
        self.setGeometry(100, 100, 400, 300)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Add a label
        self.label = QLabel("Hello, PyQt!")
        self.label.setStyleSheet("font-size: 18px; padding: 20px;")
        layout.addWidget(self.label)
        
        # Add a button
        self.button = QPushButton("Нажми меня")
        self.button.clicked.connect(self.on_button_click)
        layout.addWidget(self.button)
        
    def on_button_click(self):
        self.label.setText("Минимальная программа на Python")


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

