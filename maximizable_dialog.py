"""
Базовый класс для диалогов с возможностью разворачивания на весь экран.
"""
from PyQt5.QtWidgets import QDialog, QToolButton, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt


class MaximizableDialog(QDialog):
    """Базовый класс для диалогов с возможностью разворачивания на весь экран."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.normal_geometry = None
        self.is_maximized = False
    
    def add_maximize_button_to_header(self, header_layout: QHBoxLayout, header_label: QLabel = None):
        """
        Добавление кнопки разворачивания в заголовок.
        
        Args:
            header_layout: Layout заголовка
            header_label: Label заголовка (для обработки двойного клика)
        """
        header_layout.addStretch()
        
        # Иконка разворачивания на весь экран
        self.maximize_icon_button = QToolButton()
        self.maximize_icon_button.setToolTip("Развернуть на весь экран (двойной клик)")
        self.maximize_icon_button.setText("⛶")  # Unicode символ для разворачивания
        self.maximize_icon_button.setStyleSheet("""
            QToolButton {
                font-size: 18px;
                border: none;
                background: transparent;
                padding: 5px;
            }
            QToolButton:hover {
                background: #e0e0e0;
                border-radius: 3px;
            }
        """)
        self.maximize_icon_button.clicked.connect(self.toggle_maximize)
        header_layout.addWidget(self.maximize_icon_button)
        
        # Обработка двойного клика по заголовку
        if header_label:
            header_label.mouseDoubleClickEvent = lambda e: self.toggle_maximize()
    
    def toggle_maximize(self):
        """Переключение между обычным и полноэкранным режимом."""
        if self.is_maximized:
            self.showNormal()
            if self.normal_geometry:
                self.setGeometry(self.normal_geometry)
            if hasattr(self, 'maximize_icon_button'):
                self.maximize_icon_button.setText("⛶")
                self.maximize_icon_button.setToolTip("Развернуть на весь экран (двойной клик)")
            self.is_maximized = False
        else:
            self.normal_geometry = self.geometry()
            self.showMaximized()
            if hasattr(self, 'maximize_icon_button'):
                self.maximize_icon_button.setText("⛶")
                self.maximize_icon_button.setToolTip("Восстановить размер (двойной клик)")
            self.is_maximized = True
    
    def showEvent(self, event):
        """Сохранение исходной геометрии при первом показе."""
        if self.normal_geometry is None:
            self.normal_geometry = self.geometry()
        super().showEvent(event)

