import sys
from PySide6.QtWidgets import QApplication
from main_window import MainWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
        
    app.setStyleSheet("""
        QWidget {
            background-color: #2b2b2b;
            color: #ffffff;
        }

        QPushButton {
            background-color: #4CAF50;
            border: none;
            color: white;
            padding: 8px 16px;
            text-align: center;
            font-size: 14px;
            border-radius: 4px;
        }

        QPushButton:hover {
            background-color: #45a049;
        }

        QLineEdit {
            background-color: #333333;
            color: white;
            border: 1px solid #555555;
            padding: 4px;
            border-radius: 4px;
        }

        QProgressBar {
            background-color: #333333;
            color: white;
            border: none;
            border-radius: 5px;
            text-align: center;
        }

        QProgressBar::chunk {
            background-color: #4CAF50;
            width: 10px;
            margin: 0.5px;
        }
    """)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
