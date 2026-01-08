"""
Диалог настроек приложения.
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QSpinBox, QGroupBox, QMessageBox
)
from PyQt5.QtCore import Qt
from db import Database


class SettingsDialog(QDialog):
    """Диалог настроек приложения."""
    
    def __init__(self, db: Database, parent=None):
        """
        Инициализация диалога настроек.
        
        Args:
            db: Экземпляр базы данных
            parent: Родительское окно
        """
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Настройки")
        self.setGeometry(300, 300, 400, 250)
        self.setModal(True)
        
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """Инициализация интерфейса."""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Группа "Внешний вид"
        appearance_group = QGroupBox("Внешний вид")
        appearance_layout = QVBoxLayout()
        appearance_group.setLayout(appearance_layout)
        
        # Выбор темы
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Тема:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Светлая", "Темная"])
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        appearance_layout.addLayout(theme_layout)
        
        # Размер шрифта
        font_size_layout = QHBoxLayout()
        font_size_layout.addWidget(QLabel("Размер шрифта:"))
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setMinimum(8)
        self.font_size_spin.setMaximum(24)
        self.font_size_spin.setValue(10)
        self.font_size_spin.setSuffix(" pt")
        font_size_layout.addWidget(self.font_size_spin)
        font_size_layout.addStretch()
        appearance_layout.addLayout(font_size_layout)
        
        layout.addWidget(appearance_group)
        
        layout.addStretch()
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(self.save_settings)
        buttons_layout.addWidget(save_button)
        
        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)
        
        layout.addLayout(buttons_layout)
    
    def load_settings(self):
        """Загрузка текущих настроек из БД."""
        # Загрузка темы
        theme = self.db.get_setting("theme")
        if theme == "dark":
            self.theme_combo.setCurrentIndex(1)
        else:
            self.theme_combo.setCurrentIndex(0)
        
        # Загрузка размера шрифта
        font_size = self.db.get_setting("font_size")
        if font_size:
            try:
                self.font_size_spin.setValue(int(font_size))
            except ValueError:
                self.font_size_spin.setValue(10)
        else:
            self.font_size_spin.setValue(10)
    
    def save_settings(self):
        """Сохранение настроек в БД."""
        # Сохранение темы
        theme = "dark" if self.theme_combo.currentIndex() == 1 else "light"
        self.db.set_setting("theme", theme)
        
        # Сохранение размера шрифта
        font_size = str(self.font_size_spin.value())
        self.db.set_setting("font_size", font_size)
        
        QMessageBox.information(
            self, 
            "Настройки сохранены", 
            "Настройки сохранены. Изменения вступят в силу после перезапуска приложения."
        )
        
        self.accept()

