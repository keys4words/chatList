"""
Диалог для улучшения промтов с помощью AI.
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton,
    QComboBox, QListWidget, QListWidgetItem, QMessageBox, QProgressBar,
    QGroupBox, QSplitter, QScrollArea, QWidget
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from typing import Optional, Dict, List
from models import BaseModel
from prompt_improver import PromptImprover
import asyncio


class ImprovementThread(QThread):
    """Поток для выполнения улучшения промта."""
    
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, improver: PromptImprover, model: BaseModel, prompt: str, scenario: str = "general"):
        super().__init__()
        self.improver = improver
        self.model = model
        self.prompt = prompt
        self.scenario = scenario
    
    def run(self):
        """Выполнение улучшения в отдельном потоке."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                self.improver.improve_prompt_async(self.model, self.prompt, self.scenario)
            )
            loop.close()
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class PromptImproverDialog(QDialog):
    """Диалог для улучшения промтов."""
    
    def __init__(self, improver: PromptImprover, models: List[BaseModel], original_prompt: str, parent=None):
        """
        Инициализация диалога.
        
        Args:
            improver: Экземпляр PromptImprover
            models: Список доступных моделей
            original_prompt: Исходный промт для улучшения
            parent: Родительское окно
        """
        super().__init__(parent)
        self.improver = improver
        self.models = models
        self.original_prompt = original_prompt
        self.selected_prompt = None
        self.improvement_thread = None
        
        self.setWindowTitle("Улучшение промта")
        self.setGeometry(200, 100, 1000, 700)
        self.setModal(True)
        
        self.init_ui()
    
    def init_ui(self):
        """Инициализация интерфейса."""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Выбор модели и сценария
        controls_layout = QHBoxLayout()
        
        controls_layout.addWidget(QLabel("Модель для улучшения:"))
        self.model_combo = QComboBox()
        for model in self.models:
            self.model_combo.addItem(model.name, model)
        controls_layout.addWidget(self.model_combo)
        
        controls_layout.addWidget(QLabel("Сценарий:"))
        self.scenario_combo = QComboBox()
        self.scenario_combo.addItems([
            "Общее улучшение",
            "Улучшение ясности",
            "Для программирования",
            "Для анализа данных",
            "Для креативных задач"
        ])
        controls_layout.addWidget(self.scenario_combo)
        
        self.improve_button = QPushButton("Улучшить промт")
        self.improve_button.clicked.connect(self.start_improvement)
        self.improve_button.setStyleSheet("font-weight: bold; padding: 5px;")
        controls_layout.addWidget(self.improve_button)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Индикатор загрузки
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Разделитель для областей
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Левая панель: исходный промт
        left_group = QGroupBox("Исходный промт")
        left_layout = QVBoxLayout()
        left_group.setLayout(left_layout)
        
        self.original_text = QTextEdit()
        self.original_text.setPlainText(self.original_prompt)
        self.original_text.setReadOnly(True)
        self.original_text.setMaximumHeight(200)
        left_layout.addWidget(self.original_text)
        
        splitter.addWidget(left_group)
        
        # Правая панель: результаты улучшения
        right_group = QGroupBox("Результаты улучшения")
        right_layout = QVBoxLayout()
        right_group.setLayout(right_layout)
        
        # Улучшенная версия
        improved_label = QLabel("Улучшенная версия:")
        improved_label.setFont(QFont("Arial", 10, QFont.Bold))
        right_layout.addWidget(improved_label)
        
        self.improved_text = QTextEdit()
        self.improved_text.setReadOnly(True)
        self.improved_text.setMaximumHeight(150)
        right_layout.addWidget(self.improved_text)
        
        # Кнопка подстановки улучшенной версии
        self.use_improved_button = QPushButton("Подставить улучшенную версию")
        self.use_improved_button.clicked.connect(lambda: self.use_prompt(self.improved_text.toPlainText()))
        self.use_improved_button.setEnabled(False)
        right_layout.addWidget(self.use_improved_button)
        
        # Альтернативные варианты
        alternatives_label = QLabel("Альтернативные варианты:")
        alternatives_label.setFont(QFont("Arial", 10, QFont.Bold))
        right_layout.addWidget(alternatives_label)
        
        self.alternatives_list = QListWidget()
        self.alternatives_list.setMaximumHeight(150)
        self.alternatives_list.itemDoubleClicked.connect(self.on_alternative_double_clicked)
        right_layout.addWidget(self.alternatives_list)
        
        # Адаптации
        adaptations_label = QLabel("Адаптации для разных задач:")
        adaptations_label.setFont(QFont("Arial", 10, QFont.Bold))
        right_layout.addWidget(adaptations_label)
        
        adaptations_scroll = QScrollArea()
        adaptations_widget = QWidget()
        adaptations_layout = QVBoxLayout()
        adaptations_widget.setLayout(adaptations_layout)
        
        self.coding_text = QTextEdit()
        self.coding_text.setReadOnly(True)
        self.coding_text.setMaximumHeight(80)
        self.coding_text.setPlaceholderText("Адаптация для программирования")
        adaptations_layout.addWidget(QLabel("Для программирования:"))
        adaptations_layout.addWidget(self.coding_text)
        self.use_coding_button = QPushButton("Подставить")
        self.use_coding_button.clicked.connect(lambda: self.use_prompt(self.coding_text.toPlainText()))
        self.use_coding_button.setEnabled(False)
        adaptations_layout.addWidget(self.use_coding_button)
        
        self.analysis_text = QTextEdit()
        self.analysis_text.setReadOnly(True)
        self.analysis_text.setMaximumHeight(80)
        self.analysis_text.setPlaceholderText("Адаптация для анализа данных")
        adaptations_layout.addWidget(QLabel("Для анализа данных:"))
        adaptations_layout.addWidget(self.analysis_text)
        self.use_analysis_button = QPushButton("Подставить")
        self.use_analysis_button.clicked.connect(lambda: self.use_prompt(self.analysis_text.toPlainText()))
        self.use_analysis_button.setEnabled(False)
        adaptations_layout.addWidget(self.use_analysis_button)
        
        self.creative_text = QTextEdit()
        self.creative_text.setReadOnly(True)
        self.creative_text.setMaximumHeight(80)
        self.creative_text.setPlaceholderText("Адаптация для креативных задач")
        adaptations_layout.addWidget(QLabel("Для креативных задач:"))
        adaptations_layout.addWidget(self.creative_text)
        self.use_creative_button = QPushButton("Подставить")
        self.use_creative_button.clicked.connect(lambda: self.use_prompt(self.creative_text.toPlainText()))
        self.use_creative_button.setEnabled(False)
        adaptations_layout.addWidget(self.use_creative_button)
        
        adaptations_scroll.setWidget(adaptations_widget)
        adaptations_scroll.setWidgetResizable(True)
        right_layout.addWidget(adaptations_scroll)
        
        splitter.addWidget(right_group)
        splitter.setSizes([300, 700])
        
        # Кнопки внизу
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        copy_button = QPushButton("Копировать улучшенную версию")
        copy_button.clicked.connect(self.copy_improved)
        copy_button.setEnabled(False)
        self.copy_button = copy_button
        buttons_layout.addWidget(copy_button)
        
        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(self.accept)
        buttons_layout.addWidget(close_button)
        
        layout.addLayout(buttons_layout)
    
    def start_improvement(self):
        """Запуск процесса улучшения промта."""
        if not self.models:
            QMessageBox.warning(self, "Предупреждение", "Нет доступных моделей для улучшения!")
            return
        
        model = self.model_combo.currentData()
        if not model:
            QMessageBox.warning(self, "Предупреждение", "Выберите модель!")
            return
        
        scenario_map = {
            "Общее улучшение": "general",
            "Улучшение ясности": "clarity",
            "Для программирования": "coding",
            "Для анализа данных": "analysis",
            "Для креативных задач": "creative"
        }
        scenario = scenario_map.get(self.scenario_combo.currentText(), "general")
        
        # Отключаем кнопку и показываем прогресс
        self.improve_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Неопределенный прогресс
        
        # Очищаем предыдущие результаты
        self.clear_results()
        
        # Запускаем поток улучшения
        self.improvement_thread = ImprovementThread(
            self.improver, 
            model, 
            self.original_prompt, 
            scenario
        )
        self.improvement_thread.finished.connect(self.on_improvement_finished)
        self.improvement_thread.error.connect(self.on_improvement_error)
        self.improvement_thread.start()
    
    def on_improvement_finished(self, result: Dict):
        """Обработка завершения улучшения."""
        self.progress_bar.setVisible(False)
        self.improve_button.setEnabled(True)
        
        if not result.get("success"):
            error_msg = result.get("error", "Неизвестная ошибка")
            QMessageBox.critical(self, "Ошибка", f"Ошибка при улучшении промта:\n{error_msg}")
            return
        
        # Отображаем результаты
        improved = result.get("improved", "")
        if improved:
            self.improved_text.setPlainText(improved)
            self.use_improved_button.setEnabled(True)
            self.copy_button.setEnabled(True)
        
        # Альтернативные варианты
        alternatives = result.get("alternatives", [])
        self.alternatives_list.clear()
        for i, alt in enumerate(alternatives, 1):
            item = QListWidgetItem(f"Вариант {i}: {alt[:100]}...")
            item.setData(Qt.UserRole, alt)
            item.setToolTip(alt)
            self.alternatives_list.addItem(item)
        
        # Адаптации
        adaptations = result.get("adaptations", {})
        coding = adaptations.get("coding", "")
        analysis = adaptations.get("analysis", "")
        creative = adaptations.get("creative", "")
        
        if coding:
            self.coding_text.setPlainText(coding)
            self.use_coding_button.setEnabled(True)
        if analysis:
            self.analysis_text.setPlainText(analysis)
            self.use_analysis_button.setEnabled(True)
        if creative:
            self.creative_text.setPlainText(creative)
            self.use_creative_button.setEnabled(True)
    
    def on_improvement_error(self, error_msg: str):
        """Обработка ошибки при улучшении."""
        self.progress_bar.setVisible(False)
        self.improve_button.setEnabled(True)
        QMessageBox.critical(self, "Ошибка", f"Ошибка при улучшении промта:\n{error_msg}")
    
    def on_alternative_double_clicked(self, item: QListWidgetItem):
        """Обработка двойного клика по альтернативному варианту."""
        prompt = item.data(Qt.UserRole)
        if prompt:
            self.use_prompt(prompt)
    
    def use_prompt(self, prompt: str):
        """Подстановка промта в главное окно."""
        if prompt:
            self.selected_prompt = prompt
            self.accept()
    
    def copy_improved(self):
        """Копирование улучшенной версии в буфер обмена."""
        improved_text = self.improved_text.toPlainText()
        if improved_text:
            from PyQt5.QtWidgets import QApplication
            QApplication.clipboard().setText(improved_text)
            QMessageBox.information(self, "Успех", "Улучшенная версия скопирована в буфер обмена!")
    
    def clear_results(self):
        """Очистка результатов."""
        self.improved_text.clear()
        self.alternatives_list.clear()
        self.coding_text.clear()
        self.analysis_text.clear()
        self.creative_text.clear()
        self.use_improved_button.setEnabled(False)
        self.use_coding_button.setEnabled(False)
        self.use_analysis_button.setEnabled(False)
        self.use_creative_button.setEnabled(False)
        self.copy_button.setEnabled(False)
    
    def get_selected_prompt(self) -> Optional[str]:
        """Получение выбранного промта."""
        return self.selected_prompt

