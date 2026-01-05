"""
Диалог для просмотра полного ответа модели.
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QToolButton
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor, QFont, QIcon
from response_viewer_text_edit import ResponseTextEdit


class ResponseViewerDialog(QDialog):
    """Диалог для просмотра полного ответа модели."""
    
    def __init__(self, model_name: str, response_text: str, parent=None):
        """
        Инициализация диалога.
        
        Args:
            model_name: Название модели
            response_text: Полный текст ответа
            parent: Родительское окно
        """
        super().__init__(parent)
        self.setWindowTitle(f"Ответ модели: {model_name}")
        # Окно перемещено выше и будет открываться на весь экран
        self.setGeometry(200, 50, 900, 700)
        self.setModal(False)  # Не блокирующий диалог
        
        # Сохраняем исходный размер для восстановления
        self.normal_geometry = self.geometry()
        self.is_maximized = False
        
        self.init_ui(model_name, response_text)
    
    def init_ui(self, model_name: str, response_text: str):
        """Инициализация интерфейса."""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Заголовок с названием модели и иконкой разворачивания
        header_layout = QHBoxLayout()
        header_label = QLabel(f"<b>Модель:</b> {model_name}")
        header_label.setStyleSheet("font-size: 14px; padding: 5px;")
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        
        # Иконка разворачивания на весь экран
        self.maximize_icon_button = QToolButton()
        self.maximize_icon_button.setToolTip("Развернуть на весь экран (двойной клик)")
        # Используем стандартную иконку или текст
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
        
        layout.addLayout(header_layout)
        
        # Обработка двойного клика по заголовку окна
        self.header_label = header_label
        original_double_click = header_label.mouseDoubleClickEvent
        def on_header_double_click(event):
            self.toggle_maximize()
            if original_double_click:
                original_double_click(event)
        header_label.mouseDoubleClickEvent = on_header_double_click
        
        # Текстовое поле с ответом (кастомное для обработки двойного клика)
        self.text_edit = ResponseTextEdit(self)
        self.text_edit.setReadOnly(True)
        self.text_edit.setPlainText(response_text)
        self.text_edit.setFont(QFont("Consolas", 10))  # Моноширинный шрифт для лучшей читаемости
        self.text_edit.setLineWrapMode(QTextEdit.WidgetWidth)
        layout.addWidget(self.text_edit)
        
        # Информация о длине текста
        char_count = len(response_text)
        word_count = len(response_text.split())
        info_label = QLabel(f"Символов: {char_count:,} | Слов: {word_count:,}")
        info_label.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(info_label)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        # Кнопка копирования
        copy_button = QPushButton("Копировать")
        copy_button.clicked.connect(self.copy_to_clipboard)
        buttons_layout.addWidget(copy_button)
        
        # Кнопка развернуть/свернуть
        self.toggle_maximize_button = QPushButton("На весь экран")
        self.toggle_maximize_button.clicked.connect(self.toggle_maximize)
        buttons_layout.addWidget(self.toggle_maximize_button)
        
        # Кнопка закрытия
        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(self.accept)
        buttons_layout.addWidget(close_button)
        
        layout.addLayout(buttons_layout)
    
    def copy_to_clipboard(self):
        """Копирование текста в буфер обмена."""
        clipboard = self.text_edit.textCursor().selectedText()
        if not clipboard:
            clipboard = self.text_edit.toPlainText()
        
        from PyQt5.QtWidgets import QApplication
        QApplication.clipboard().setText(clipboard)
    
    def toggle_maximize(self):
        """Переключение между обычным и полноэкранным режимом."""
        if self.is_maximized:
            self.showNormal()
            self.setGeometry(self.normal_geometry)
            self.toggle_maximize_button.setText("На весь экран")
            self.maximize_icon_button.setText("⛶")  # Иконка разворачивания
            self.maximize_icon_button.setToolTip("Развернуть на весь экран (двойной клик)")
            self.is_maximized = False
        else:
            self.normal_geometry = self.geometry()
            self.showMaximized()
            self.toggle_maximize_button.setText("Восстановить")
            self.maximize_icon_button.setText("⛶")  # Иконка восстановления (можно использовать другой символ)
            self.maximize_icon_button.setToolTip("Восстановить размер (двойной клик)")
            self.is_maximized = True
    

