from PySide6.QtWidgets import QMainWindow, QWidget, QGridLayout, QSpinBox, QPushButton, QFileDialog, QHBoxLayout, QVBoxLayout, QMessageBox, QGroupBox, QProgressBar
from PySide6.QtGui import QIcon
from video_panel import VideoPanel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Synchronizer")
        self.setGeometry(100, 100, 800, 600)
        
        # Главный контейнер с вертикальной компоновкой
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # Верхняя панель с кнопкой открытия
        top_panel = QHBoxLayout()
        self.open_button = QPushButton("Открыть видео")
        self.open_button.setStyleSheet("background-color: #2196F3; color: white; padding: 8px 16px; border-radius: 4px;")
        self.open_button.clicked.connect(self.open_videos)
        top_panel.addWidget(self.open_button)
        top_panel.addStretch()
        main_layout.addLayout(top_panel)
        
        # Сетка для видео
        self.video_grid = QGridLayout()
        self.video_grid.setColumnStretch(0, 1)
        self.video_grid.setColumnStretch(1, 1)
        self.video_grid.setRowStretch(0, 1)
        self.video_grid.setRowStretch(1, 1)
        main_layout.addLayout(self.video_grid)
        
        # Нижняя панель управления
        bottom_panel = QVBoxLayout()
        
        # Группа элементов управления
        control_group = QGroupBox("Общие настройки")
        control_layout = QHBoxLayout()
        
        # Кнопки навигации
        self.back_button = QPushButton("Назад")
        self.back_button.setIcon(QIcon("path/to/back_arrow.png"))
        self.back_button.setStyleSheet("background-color: #ff5722; color: white;")
        self.back_button.clicked.connect(lambda: self.navigate_frames(-1))
        
        # Виджет для выбора интервала (используем QSpinBox вместо QLineEdit)
        self.interval_input = QSpinBox()  # Используем QSpinBox
        self.interval_input.setRange(1, 9999)  # Устанавливаем минимальное значение 1
        self.interval_input.setValue(1)  # Значение по умолчанию
        
        self.next_button = QPushButton("Вперёд")
        self.next_button.setIcon(QIcon("path/to/forward_arrow.png"))
        self.next_button.setStyleSheet("background-color: #4CAF50; color: white;")
        self.next_button.clicked.connect(lambda: self.navigate_frames(1))
        
        control_layout.addWidget(self.back_button)
        control_layout.addWidget(self.interval_input)
        control_layout.addWidget(self.next_button)
        control_group.setLayout(control_layout)
        bottom_panel.addWidget(control_group)
        
        # Прогресс-бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        bottom_panel.addWidget(self.progress_bar)
        
        main_layout.addLayout(bottom_panel)

    def open_videos(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Выберите видео файлы", "", "Видео (*.mp4 *.avi *.mov)")
        
        # Очистка предыдущих видео
        for i in reversed(range(self.video_grid.count())):
            widget = self.video_grid.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Добавление новых панелей
        self.video_panels = []
        for i, path in enumerate(paths[:4]):
            try:
                panel = VideoPanel(path)
                row = i // 2
                col = i % 2
                self.video_grid.addWidget(panel, row, col)
                self.video_panels.append(panel)
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))
    
    def navigate_frames(self, direction):
        interval = self.interval_input.value()  # Получаем значение из QSpinBox
        for panel in self.video_panels:
            new_frame = panel.current_frame + (direction * interval)
            if 0 <= new_frame < panel.total_frames:
                panel.jump_to_frame(new_frame)
                self.update_progress(panel)
    
    def update_progress(self, panel):
        progress = (panel.current_frame / panel.total_frames) * 100
        self.progress_bar.setValue(int(progress))
