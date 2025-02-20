import cv2
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QSpinBox, QHBoxLayout
from PySide6.QtGui import QImage, QPixmap, Qt
from PySide6.QtCore import QThread, Signal


class FrameLoader(QThread):
    frame_loaded = Signal(object)

    def __init__(self, cap, frame_number):
        super().__init__()
        self.cap = cap
        self.frame_number = frame_number
        self.running = True  # Флаг для управления состоянием потока

    def run(self):
        if not self.running:
            return
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.frame_number)
        ret, frame = self.cap.read()
        if ret and self.running:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.frame_loaded.emit(frame)

    def stop(self):
        """Остановка потока"""
        self.running = False
        self.wait()  # Ждём завершения работы потока


class VideoPanel(QWidget):
    def __init__(self, video_path):
        super().__init__()
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            raise ValueError(f"Не удалось открыть видео: {video_path}")
        
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.duration = self.total_frames / self.fps if self.fps > 0 else 0
        
        self.current_frame = 0
        self.frame_cache = {}
        self.loader = None  # Ссылка на текущий поток загрузки
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Информация о видео
        info_text = (f"Файл: {self.video_path.split('/')[-1]}\n"
                     f"Размер: {self.width}x{self.height}\n"
                     f"FPS: {self.fps:.2f}\n"
                     f"Кадры: {self.total_frames}\n"
                     f"Длительность: {self.duration:.2f} сек")
        self.info_label = QLabel(info_text)
        layout.addWidget(self.info_label)
        
        # Виджет для отображения видео
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setMinimumSize(320, 240)
        self.video_label.setScaledContents(True)
        layout.addWidget(self.video_label)
        
        # Панель управления
        control_layout = QHBoxLayout()
        
        # Кнопка сброса к 0 кадру
        self.reset_button = QPushButton("Сброс")
        self.reset_button.setStyleSheet("background-color: #A60000; color: white;")
        self.reset_button.clicked.connect(self.reset_to_start)
        control_layout.addWidget(self.reset_button)
        
        # Стрелки для выбора кадра
        self.frame_spinbox = QSpinBox()
        self.frame_spinbox.setMinimum(0)
        self.frame_spinbox.setMaximum(self.total_frames - 1)
        self.frame_spinbox.setValue(self.current_frame)
        self.frame_spinbox.valueChanged.connect(self.jump_to_frame)
        control_layout.addWidget(self.frame_spinbox)
        
        layout.addLayout(control_layout)
        self.setLayout(layout)

    def show_frame(self):
        if self.loader:  # Остановка предыдущего потока, если он существует
            self.loader.stop()
        if self.current_frame in self.frame_cache:
            frame = self.frame_cache[self.current_frame]
            self.display_frame(frame)
        else:
            self.loader = FrameLoader(self.cap, self.current_frame)
            self.loader.frame_loaded.connect(self.display_frame)
            self.loader.start()

    def display_frame(self, frame):
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(q_img))
        self.frame_cache[self.current_frame] = frame

    def jump_to_frame(self, frame):
        if 0 <= frame < self.total_frames:
            self.current_frame = frame
            self.frame_spinbox.setValue(self.current_frame)
            self.show_frame()

    def reset_to_start(self):
        self.jump_to_frame(0)

    def cleanup(self):
        """Метод для очистки ресурсов"""
        if self.loader:
            self.loader.stop()  # Остановка текущего потока
        if self.cap.isOpened():
            self.cap.release()  # Закрытие видеопотока