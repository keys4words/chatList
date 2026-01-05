"""
Диалог для управления моделями.
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QCheckBox,
    QComboBox, QMessageBox, QHeaderView
)
from PyQt5.QtCore import Qt
from db import Database


class ModelsDialog(QDialog):
    """Диалог для управления моделями."""
    
    def __init__(self, db: Database, parent=None):
        """
        Инициализация диалога.
        
        Args:
            db: Экземпляр базы данных
            parent: Родительское окно
        """
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Управление моделями")
        # Уменьшена высота и окно перемещено выше
        self.setGeometry(200, 100, 800, 500)
        
        self.init_ui()
        self.load_models()
    
    def init_ui(self):
        """Инициализация интерфейса."""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Таблица моделей
        self.models_table = QTableWidget()
        self.models_table.setColumnCount(6)
        self.models_table.setHorizontalHeaderLabels([
            "ID", "Название", "API URL", "API ID", "Тип", "Активна"
        ])
        self.models_table.horizontalHeader().setStretchLastSection(False)
        self.models_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.models_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.models_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.models_table)
        
        # Кнопки управления
        buttons_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Добавить")
        self.add_button.clicked.connect(self.add_model)
        buttons_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("Редактировать")
        self.edit_button.clicked.connect(self.edit_model)
        buttons_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("Удалить")
        self.delete_button.clicked.connect(self.delete_model)
        buttons_layout.addWidget(self.delete_button)
        
        self.toggle_active_button = QPushButton("Активировать/Деактивировать")
        self.toggle_active_button.clicked.connect(self.toggle_active)
        buttons_layout.addWidget(self.toggle_active_button)
        
        buttons_layout.addStretch()
        
        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(self.accept)
        buttons_layout.addWidget(close_button)
        
        layout.addLayout(buttons_layout)
    
    def load_models(self):
        """Загрузка моделей в таблицу."""
        models = self.db.get_all_models()
        self.models_table.setRowCount(len(models))
        
        for i, model in enumerate(models):
            self.models_table.setItem(i, 0, QTableWidgetItem(str(model['id'])))
            self.models_table.setItem(i, 1, QTableWidgetItem(model['name']))
            self.models_table.setItem(i, 2, QTableWidgetItem(model['api_url']))
            self.models_table.setItem(i, 3, QTableWidgetItem(model['api_id']))
            self.models_table.setItem(i, 4, QTableWidgetItem(model['model_type']))
            
            checkbox = QCheckBox()
            checkbox.setChecked(bool(model['is_active']))
            checkbox.setEnabled(False)  # Только для отображения
            self.models_table.setCellWidget(i, 5, checkbox)
    
    def add_model(self):
        """Добавление новой модели."""
        dialog = ModelEditDialog(self.db, self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_models()
    
    def edit_model(self):
        """Редактирование выбранной модели."""
        selected_rows = self.models_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "Предупреждение", "Выберите модель для редактирования!")
            return
        
        model_id = int(self.models_table.item(selected_rows[0].row(), 0).text())
        model_data = self.db.get_model(model_id)
        
        if model_data:
            dialog = ModelEditDialog(self.db, self, model_data)
            if dialog.exec_() == QDialog.Accepted:
                self.load_models()
    
    def delete_model(self):
        """Удаление выбранной модели."""
        selected_rows = self.models_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "Предупреждение", "Выберите модель для удаления!")
            return
        
        model_id = int(self.models_table.item(selected_rows[0].row(), 0).text())
        model_name = self.models_table.item(selected_rows[0].row(), 1).text()
        
        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Удалить модель '{model_name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.db.delete_model(model_id)
                self.load_models()
                QMessageBox.information(self, "Успех", "Модель удалена!")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка удаления: {str(e)}")
    
    def toggle_active(self):
        """Переключение активности модели."""
        selected_rows = self.models_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "Предупреждение", "Выберите модель!")
            return
        
        model_id = int(self.models_table.item(selected_rows[0].row(), 0).text())
        model_data = self.db.get_model(model_id)
        
        if model_data:
            new_active = 0 if model_data['is_active'] else 1
            try:
                self.db.update_model(model_id, is_active=new_active)
                self.load_models()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка обновления: {str(e)}")


class ModelEditDialog(QDialog):
    """Диалог для добавления/редактирования модели."""
    
    def __init__(self, db: Database, parent=None, model_data=None):
        """
        Инициализация диалога.
        
        Args:
            db: Экземпляр базы данных
            parent: Родительское окно
            model_data: Данные модели для редактирования (None для новой)
        """
        super().__init__(parent)
        self.db = db
        self.model_data = model_data
        self.setWindowTitle("Редактировать модель" if model_data else "Добавить модель")
        self.setModal(True)
        
        self.init_ui()
        if model_data:
            self.load_model_data()
    
    def init_ui(self):
        """Инициализация интерфейса."""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Название
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Название:"))
        self.name_input = QLineEdit()
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # API URL
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("API URL:"))
        self.url_input = QLineEdit()
        url_layout.addWidget(self.url_input)
        layout.addLayout(url_layout)
        
        # API ID (имя переменной окружения)
        api_id_layout = QHBoxLayout()
        api_id_layout.addWidget(QLabel("API ID (имя переменной в .env):"))
        self.api_id_input = QLineEdit()
        api_id_layout.addWidget(self.api_id_input)
        layout.addLayout(api_id_layout)
        
        # Имя модели для API
        model_name_layout = QHBoxLayout()
        model_name_layout.addWidget(QLabel("Имя модели (для API):"))
        self.model_name_input = QLineEdit()
        self.model_name_input.setPlaceholderText("Оставьте пустым для использования из .env или значения по умолчанию")
        model_name_layout.addWidget(self.model_name_input)
        layout.addLayout(model_name_layout)
        
        # Тип модели
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Тип модели:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "openai", 
            "deepseek", 
            "groq", 
            "openrouter",
            "openai-compatible"
        ])
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)
        
        # Активна
        self.active_checkbox = QCheckBox("Активна")
        self.active_checkbox.setChecked(True)
        layout.addWidget(self.active_checkbox)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(self.save_model)
        buttons_layout.addWidget(save_button)
        
        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)
        
        layout.addLayout(buttons_layout)
    
    def load_model_data(self):
        """Загрузка данных модели в форму."""
        if self.model_data:
            self.name_input.setText(self.model_data['name'])
            self.url_input.setText(self.model_data['api_url'])
            self.api_id_input.setText(self.model_data['api_id'])
            
            # Загрузка имени модели для API (если задано)
            api_model_name = self.model_data.get('api_model_name', '')
            if api_model_name:
                self.model_name_input.setText(api_model_name)
            
            index = self.type_combo.findText(self.model_data['model_type'])
            if index >= 0:
                self.type_combo.setCurrentIndex(index)
            
            self.active_checkbox.setChecked(bool(self.model_data['is_active']))
    
    def save_model(self):
        """Сохранение модели."""
        name = self.name_input.text().strip()
        url = self.url_input.text().strip()
        api_id = self.api_id_input.text().strip()
        model_type = self.type_combo.currentText()
        is_active = 1 if self.active_checkbox.isChecked() else 0
        api_model_name = self.model_name_input.text().strip() or None
        
        if not all([name, url, api_id]):
            QMessageBox.warning(self, "Предупреждение", "Заполните все обязательные поля!")
            return
        
        try:
            if self.model_data:
                # Обновление
                self.db.update_model(
                    self.model_data['id'],
                    name=name,
                    api_url=url,
                    api_id=api_id,
                    model_type=model_type,
                    is_active=is_active,
                    api_model_name=api_model_name
                )
            else:
                # Создание
                self.db.create_model(name, url, api_id, model_type, is_active, api_model_name)
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения: {str(e)}")

