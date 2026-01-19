"""
Диалог "О программе".
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from version import __version__


class AboutDialog(QDialog):
    """Диалог с информацией о программе."""
    
    def __init__(self, parent=None):
        """
        Инициализация диалога.
        
        Args:
            parent: Родительское окно
        """
        super().__init__(parent)
        self.setWindowTitle("О программе")
        self.setGeometry(300, 300, 500, 400)
        self.setModal(True)
        
        self.init_ui()
    
    def init_ui(self):
        """Инициализация интерфейса."""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Название программы
        title_label = QLabel("ChatList")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Подзаголовок
        subtitle_label = QLabel("Сравнение ответов нейросетей")
        subtitle_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle_label)
        
        layout.addSpacing(20)
        
        # Информация о программе
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setPlainText("""
ChatList — это Python-приложение для сравнения ответов различных AI-моделей.

Основные возможности:
• Отправка одного промта в несколько нейросетей одновременно
• Сравнение ответов в удобной таблице
• Сохранение выбранных результатов в базу данных
• Поиск и фильтрация сохраненных промтов и результатов
• Экспорт результатов в Markdown и JSON
• Управление моделями (OpenAI, DeepSeek, Groq, OpenRouter и др.)
• AI-ассистент для улучшения промтов
• Настройка темы и размера шрифта

Технологии:
• Python 3.11+
• PyQt5 для пользовательского интерфейса
• SQLite для хранения данных
• Поддержка различных AI API

Версия: {__version__}
        """.format(__version__=__version__).strip())
        layout.addWidget(info_text)
        
        layout.addSpacing(10)
        
        # Кнопка закрытия
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(self.accept)
        buttons_layout.addWidget(close_button)
        
        layout.addLayout(buttons_layout)

