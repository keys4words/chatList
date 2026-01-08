"""
Главный модуль приложения ChatList.
Реализует пользовательский интерфейс на PyQt5.
"""
import sys
import asyncio
from datetime import datetime
from typing import Optional
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QTableWidget, QTableWidgetItem, QComboBox,
    QLabel, QCheckBox, QLineEdit, QMessageBox, QProgressBar, QSplitter,
    QHeaderView, QGroupBox, QMenuBar, QAction, QFileDialog, QDialog
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor, QIcon, QPalette
import os

from db import Database
from response_viewer import ResponseViewerDialog
from models import ModelFactory
from network import NetworkManager, TemporaryResults
from export import ExportManager
from logger import AppLogger
from models_dialog import ModelsDialog
from prompt_improver import PromptImprover
from prompt_improver_dialog import PromptImproverDialog
from settings_dialog import SettingsDialog
from about_dialog import AboutDialog


class RequestThread(QThread):
    """Поток для выполнения асинхронных запросов к API."""
    
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    
    def __init__(self, network_manager, models, prompt, db=None):
        super().__init__()
        self.network_manager = network_manager
        self.models = models
        self.prompt = prompt
        self.db = db
    
    def run(self):
        """Выполнение запросов в отдельном потоке."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            # Получение задержки между запросами из настроек
            delay = 0.5  # По умолчанию
            if self.db:
                delay_setting = self.db.get_setting("delay_between_requests")
                if delay_setting:
                    try:
                        delay = float(delay_setting)
                    except ValueError:
                        delay = 0.5
            
            results = loop.run_until_complete(
                self.network_manager.send_to_all_models_async(self.models, self.prompt, delay)
            )
            loop.close()
            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """Главное окно приложения."""
    
    def __init__(self):
        super().__init__()
        self.db = Database()
        # Получение настроек из БД
        timeout_setting = self.db.get_setting("request_timeout")
        timeout = int(timeout_setting) if timeout_setting else None
        
        retry_on_429_setting = self.db.get_setting("retry_on_429")
        retry_on_429 = retry_on_429_setting.lower() == "true" if retry_on_429_setting else True
        
        max_retries_setting = self.db.get_setting("max_retries")
        max_retries = int(max_retries_setting) if max_retries_setting else 3
        
        self.network_manager = NetworkManager(
            timeout=timeout,
            retry_on_429=retry_on_429,
            max_retries=max_retries
        )
        self.temp_results = TemporaryResults()
        self.export_manager = ExportManager(self.db)
        self.logger = AppLogger(self.db, log_to_file=True)
        self.prompt_improver = PromptImprover(self.network_manager)
        self.current_prompt_id: Optional[int] = None
        
        self.init_ui()
        self.apply_settings()
        self.load_prompts()
        self.load_models_info()
    
    def init_ui(self):
        """Инициализация пользовательского интерфейса."""
        self.setWindowTitle("ChatList - Сравнение ответов нейросетей")
        self.setGeometry(100, 100, 1200, 800)
        
        # Установка иконки приложения
        icon_path = os.path.join(os.path.dirname(__file__), "app.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Разделитель для разделения областей
        splitter = QSplitter(Qt.Vertical)
        main_layout.addWidget(splitter)
        
        # ========== Область ввода промта ==========
        prompt_group = QGroupBox("Ввод промта")
        prompt_layout = QVBoxLayout()
        prompt_group.setLayout(prompt_layout)
        
        # Выбор сохраненного промта и поиск
        saved_prompts_layout = QHBoxLayout()
        saved_prompts_layout.addWidget(QLabel("Сохраненные промты:"))
        self.prompts_combo = QComboBox()
        self.prompts_combo.currentIndexChanged.connect(self.on_prompt_selected)
        saved_prompts_layout.addWidget(self.prompts_combo)
        
        self.search_prompt_input = QLineEdit()
        self.search_prompt_input.setPlaceholderText("Поиск по промтам...")
        self.search_prompt_input.textChanged.connect(self.filter_prompts)
        saved_prompts_layout.addWidget(QLabel("Поиск:"))
        saved_prompts_layout.addWidget(self.search_prompt_input)
        prompt_layout.addLayout(saved_prompts_layout)
        
        # Поле ввода нового промта
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("Введите ваш промт здесь...")
        self.prompt_input.setMaximumHeight(100)
        prompt_layout.addWidget(self.prompt_input)
        
        # Поле для тегов
        tags_layout = QHBoxLayout()
        tags_layout.addWidget(QLabel("Теги:"))
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("тег1, тег2, тег3")
        tags_layout.addWidget(self.tags_input)
        prompt_layout.addLayout(tags_layout)
        
        # Кнопки управления промтом
        buttons_layout = QHBoxLayout()
        self.send_button = QPushButton("Отправить запрос")
        self.send_button.clicked.connect(self.send_requests)
        self.send_button.setStyleSheet("font-weight: bold; padding: 5px;")
        buttons_layout.addWidget(self.send_button)
        
        self.improve_prompt_button = QPushButton("Улучшить промт")
        self.improve_prompt_button.clicked.connect(self.improve_prompt)
        self.improve_prompt_button.setToolTip("Улучшить промт с помощью AI")
        buttons_layout.addWidget(self.improve_prompt_button)
        
        self.save_prompt_button = QPushButton("Сохранить промт")
        self.save_prompt_button.clicked.connect(self.save_prompt)
        buttons_layout.addWidget(self.save_prompt_button)
        
        buttons_layout.addStretch()
        prompt_layout.addLayout(buttons_layout)
        
        splitter.addWidget(prompt_group)
        
        # ========== Таблица результатов ==========
        results_group = QGroupBox("Результаты")
        results_layout = QVBoxLayout()
        results_group.setLayout(results_layout)
        
        # Кнопки управления результатами
        results_buttons_layout = QHBoxLayout()
        self.save_results_button = QPushButton("Сохранить выбранные")
        self.save_results_button.clicked.connect(self.save_selected_results)
        self.save_results_button.setEnabled(False)
        results_buttons_layout.addWidget(self.save_results_button)
        
        self.export_button = QPushButton("Экспорт")
        self.export_button.clicked.connect(self.export_current_results)
        results_buttons_layout.addWidget(self.export_button)
        
        self.clear_button = QPushButton("Очистить")
        self.clear_button.clicked.connect(self.clear_results)
        results_buttons_layout.addWidget(self.clear_button)
        
        results_buttons_layout.addStretch()
        
        # Индикатор загрузки
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        results_buttons_layout.addWidget(self.progress_bar)
        
        results_layout.addLayout(results_buttons_layout)
        
        # Таблица результатов
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(3)
        self.results_table.setHorizontalHeaderLabels(["Модель", "Ответ", "Выбрать"])
        self.results_table.horizontalHeader().setStretchLastSection(False)
        self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.results_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        results_layout.addWidget(self.results_table)
        
        splitter.addWidget(results_group)
        
        # Установка пропорций разделителя
        splitter.setSizes([200, 600])
        
        # Создание меню
        self.create_menu()
        
        # Статусная строка
        self.statusBar().showMessage("Готово")
    
    def create_menu(self):
        """Создание меню приложения."""
        menubar = self.menuBar()
        
        # Меню "Файл"
        file_menu = menubar.addMenu("Файл")
        
        export_action = QAction("Экспорт результатов...", self)
        export_action.triggered.connect(self.export_results)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Меню "Модели"
        models_menu = menubar.addMenu("Модели")
        
        manage_models_action = QAction("Управление моделями...", self)
        manage_models_action.triggered.connect(self.manage_models)
        models_menu.addAction(manage_models_action)
        
        # Меню "Промты"
        prompts_menu = menubar.addMenu("Промты")
        
        search_prompts_action = QAction("Поиск промтов...", self)
        search_prompts_action.triggered.connect(self.search_prompts)
        prompts_menu.addAction(search_prompts_action)
        
        # Меню "Результаты"
        results_menu = menubar.addMenu("Результаты")
        
        search_results_action = QAction("Поиск результатов...", self)
        search_results_action.triggered.connect(self.search_results)
        results_menu.addAction(search_results_action)
        
        # Меню "Справка"
        help_menu = menubar.addMenu("Справка")
        
        settings_action = QAction("Настройки...", self)
        settings_action.triggered.connect(self.show_settings)
        help_menu.addAction(settings_action)
        
        help_menu.addSeparator()
        
        about_action = QAction("О программе...", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def load_prompts(self):
        """Загрузка сохраненных промтов в выпадающий список."""
        self.prompts_combo.clear()
        self.prompts_combo.addItem("-- Новый промт --", None)
        
        prompts = self.db.get_all_prompts(sort_by="date", order="DESC")
        for prompt in prompts:
            display_text = f"{prompt['date']}: {prompt['prompt'][:50]}..."
            self.prompts_combo.addItem(display_text, prompt['id'])
    
    def load_models_info(self):
        """Загрузка информации о моделях."""
        models = self.db.get_all_models(active_only=True)
        if not models:
            self.statusBar().showMessage("Внимание: нет активных моделей. Добавьте модели в настройках.")
    
    def on_prompt_selected(self, index):
        """Обработка выбора сохраненного промта."""
        prompt_id = self.prompts_combo.itemData(index)
        if prompt_id:
            prompt_data = self.db.get_prompt(prompt_id)
            if prompt_data:
                self.prompt_input.setPlainText(prompt_data['prompt'])
                self.tags_input.setText(prompt_data.get('tags', ''))
                self.current_prompt_id = prompt_id
                # Очистка результатов при выборе нового промта
                self.clear_results()
    
    def save_prompt(self):
        """Сохранение промта в базу данных."""
        prompt_text = self.prompt_input.toPlainText().strip()
        if not prompt_text:
            QMessageBox.warning(self, "Предупреждение", "Введите текст промта!")
            return
        
        tags = self.tags_input.text().strip()
        tags = tags if tags else None
        
        try:
            if self.current_prompt_id:
                # Обновление существующего промта
                self.db.update_prompt(self.current_prompt_id, prompt_text, tags)
                QMessageBox.information(self, "Успех", "Промт обновлен!")
            else:
                # Создание нового промта
                self.current_prompt_id = self.db.create_prompt(prompt_text, tags)
                QMessageBox.information(self, "Успех", "Промт сохранен!")
            
            self.load_prompts()
            # Выбор сохраненного промта
            index = self.prompts_combo.findData(self.current_prompt_id)
            if index >= 0:
                self.prompts_combo.setCurrentIndex(index)
                
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения промта: {str(e)}")
    
    def send_requests(self):
        """Отправка запроса во все активные модели."""
        prompt_text = self.prompt_input.toPlainText().strip()
        if not prompt_text:
            QMessageBox.warning(self, "Предупреждение", "Введите текст промта!")
            return
        
        # Очистка предыдущих результатов
        self.clear_results()
        
        # Получение активных моделей
        models = ModelFactory.get_active_models(self.db)
        if not models:
            QMessageBox.warning(self, "Предупреждение", "Нет активных моделей!")
            return
        
        # Сохранение промта, если он новый
        if not self.current_prompt_id:
            tags = self.tags_input.text().strip()
            tags = tags if tags else None
            try:
                self.current_prompt_id = self.db.create_prompt(prompt_text, tags)
                self.load_prompts()
            except Exception as e:
                QMessageBox.warning(self, "Предупреждение", f"Не удалось сохранить промт: {str(e)}")
        
        # Показ индикатора загрузки
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Неопределенный прогресс
        self.send_button.setEnabled(False)
        self.statusBar().showMessage("Отправка запросов...")
        
        # Запуск запросов в отдельном потоке
        self.request_thread = RequestThread(self.network_manager, models, prompt_text, self.db)
        self.request_thread.finished.connect(self.on_requests_finished)
        self.request_thread.error.connect(self.on_request_error)
        self.request_thread.start()
    
    def on_requests_finished(self, results):
        """Обработка завершения запросов."""
        self.progress_bar.setVisible(False)
        self.send_button.setEnabled(True)
        
        # Логирование результатов
        prompt_text = self.prompt_input.toPlainText().strip()
        self.logger.log_batch_request(prompt_text, results)
        
        # Обновление временной таблицы
        self.temp_results.update_from_network_results(results)
        
        # Отображение результатов в таблице
        self.update_results_table()
        
        self.statusBar().showMessage(f"Получено ответов: {len([r for r in results if r['success']])}/{len(results)}")
    
    def on_request_error(self, error_msg):
        """Обработка ошибки при выполнении запросов."""
        self.progress_bar.setVisible(False)
        self.send_button.setEnabled(True)
        QMessageBox.critical(self, "Ошибка", f"Ошибка при отправке запросов: {error_msg}")
        self.statusBar().showMessage("Ошибка")
    
    def update_results_table(self):
        """Обновление таблицы результатов."""
        results = self.temp_results.get_all_results()
        self.results_table.setRowCount(len(results))
        
        for i, result in enumerate(results):
            # Колонка "Модель"
            model_item = QTableWidgetItem(result['model_name'])
            model_item.setFlags(model_item.flags() & ~Qt.ItemIsEditable)
            self.results_table.setItem(i, 0, model_item)
            
            # Колонка "Ответ" - показываем превью для длинных ответов
            full_text = result['response_text']
            MAX_PREVIEW_LENGTH = 300
            is_long = len(full_text) > MAX_PREVIEW_LENGTH
            
            if is_long:
                preview_text = full_text[:MAX_PREVIEW_LENGTH] + "..."
                display_text = f"{preview_text}\n\n[Нажмите дважды для просмотра полного ответа ({len(full_text):,} символов)]"
            else:
                display_text = full_text
            
            response_item = QTableWidgetItem(display_text)
            response_item.setFlags(response_item.flags() & ~Qt.ItemIsEditable)
            response_item.setTextAlignment(Qt.AlignTop | Qt.AlignLeft)
            
            # Сохраняем полный текст в данных элемента для доступа при клике
            response_item.setData(Qt.UserRole, full_text)
            response_item.setData(Qt.UserRole + 1, result['model_name'])
            
            # Выделение длинных ответов другим цветом
            if is_long:
                response_item.setBackground(QColor(255, 255, 240))  # Светло-желтый фон
            
            self.results_table.setItem(i, 1, response_item)
            
            # Колонка "Выбрать" (чекбокс)
            checkbox = QCheckBox()
            checkbox.setChecked(result.get('selected', False))
            checkbox.stateChanged.connect(lambda state, idx=i: self.temp_results.toggle_selection(idx))
            self.results_table.setCellWidget(i, 2, checkbox)
        
        # Подключение обработчика двойного клика для просмотра полного ответа
        self.results_table.cellDoubleClicked.connect(self.show_full_response)
        
        # Автоматическая высота строк (но ограничим максимальную высоту)
        self.results_table.resizeRowsToContents()
        # Ограничение максимальной высоты строки
        for i in range(self.results_table.rowCount()):
            height = self.results_table.rowHeight(i)
            if height > 200:
                self.results_table.setRowHeight(i, 200)
        
        self.save_results_button.setEnabled(len(results) > 0)
    
    def show_full_response(self, row: int, column: int):
        """Открытие диалога с полным ответом модели."""
        if column != 1:  # Только для колонки с ответами
            return
        
        item = self.results_table.item(row, column)
        if not item:
            return
        
        full_text = item.data(Qt.UserRole)
        model_name = item.data(Qt.UserRole + 1)
        
        if full_text and model_name:
            dialog = ResponseViewerDialog(model_name, full_text, self)
            dialog.show()
    
    def save_selected_results(self):
        """Сохранение выбранных результатов в базу данных."""
        if not self.current_prompt_id:
            QMessageBox.warning(self, "Предупреждение", "Сначала отправьте запрос!")
            return
        
        selected_results = self.temp_results.get_selected_results()
        if not selected_results:
            QMessageBox.warning(self, "Предупреждение", "Выберите результаты для сохранения!")
            return
        
        # Получение моделей для сопоставления имен с ID
        models = self.db.get_all_models()
        model_name_to_id = {model['name']: model['id'] for model in models}
        
        saved_count = 0
        for result in selected_results:
            model_id = model_name_to_id.get(result['model_name'])
            if model_id:
                try:
                    self.db.create_result(
                        self.current_prompt_id,
                        model_id,
                        result['response_text']
                    )
                    saved_count += 1
                except Exception as e:
                    QMessageBox.warning(self, "Ошибка", f"Ошибка сохранения результата: {str(e)}")
        
        if saved_count > 0:
            QMessageBox.information(self, "Успех", f"Сохранено результатов: {saved_count}")
            # Снятие выбора с сохраненных результатов
            for result in selected_results:
                result['selected'] = False
            self.update_results_table()
    
    def clear_results(self):
        """Очистка результатов."""
        self.temp_results.clear()
        self.results_table.setRowCount(0)
        self.save_results_button.setEnabled(False)
        self.statusBar().showMessage("Результаты очищены")
    
    def filter_prompts(self, text):
        """Фильтрация промтов по поисковому запросу."""
        search_text = text.strip()
        if not search_text:
            self.load_prompts()
            return
        
        prompts = self.db.get_all_prompts(search=search_text, sort_by="date", order="DESC")
        self.prompts_combo.clear()
        self.prompts_combo.addItem("-- Новый промт --", None)
        
        for prompt in prompts:
            display_text = f"{prompt['date']}: {prompt['prompt'][:50]}..."
            self.prompts_combo.addItem(display_text, prompt['id'])
    
    def export_current_results(self):
        """Экспорт текущих результатов из таблицы."""
        results = self.temp_results.get_all_results()
        if not results:
            QMessageBox.warning(self, "Предупреждение", "Нет результатов для экспорта!")
            return
        
        # Выбор формата
        format_dialog = QMessageBox(self)
        format_dialog.setWindowTitle("Выбор формата")
        format_dialog.setText("Выберите формат экспорта:")
        md_button = format_dialog.addButton("Markdown", QMessageBox.AcceptRole)
        json_button = format_dialog.addButton("JSON", QMessageBox.AcceptRole)
        cancel_button = format_dialog.addButton("Отмена", QMessageBox.RejectRole)
        format_dialog.exec_()
        
        if format_dialog.clickedButton() == cancel_button:
            return
        
        export_format = "markdown" if format_dialog.clickedButton() == md_button else "json"
        prompt_text = self.prompt_input.toPlainText().strip()
        
        if export_format == "markdown":
            content = self.export_manager.export_results_to_markdown(results, prompt_text)
            ext = "md"
        else:
            content = self.export_manager.export_results_to_json(results, prompt_text)
            ext = "json"
        
        # Сохранение файла
        filename, _ = QFileDialog.getSaveFileName(
            self, "Сохранить результаты", f"results.{ext}",
            f"{ext.upper()} Files (*.{ext})"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                QMessageBox.information(self, "Успех", f"Результаты экспортированы в {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка экспорта: {str(e)}")
    
    def export_results(self):
        """Экспорт сохраненных результатов из БД."""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Экспорт результатов")
        dialog.setModal(True)
        layout = QVBoxLayout()
        dialog.setLayout(layout)
        
        layout.addWidget(QLabel("Выберите формат:"))
        format_combo = QComboBox()
        format_combo.addItems(["Markdown", "JSON"])
        layout.addWidget(format_combo)
        
        buttons_layout = QHBoxLayout()
        export_button = QPushButton("Экспорт")
        cancel_button = QPushButton("Отмена")
        buttons_layout.addWidget(export_button)
        buttons_layout.addWidget(cancel_button)
        layout.addLayout(buttons_layout)
        
        export_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)
        
        if dialog.exec_() == QDialog.Accepted:
            export_format = format_combo.currentText().lower()
            content = self.export_manager.export_saved_results(format=export_format)
            
            ext = "md" if export_format == "markdown" else "json"
            filename, _ = QFileDialog.getSaveFileName(
                self, "Сохранить результаты", f"exported_results.{ext}",
                f"{ext.upper()} Files (*.{ext})"
            )
            
            if filename:
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(content)
                    QMessageBox.information(self, "Успех", f"Результаты экспортированы в {filename}")
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка", f"Ошибка экспорта: {str(e)}")
    
    def manage_models(self):
        """Открытие диалога управления моделями."""
        dialog = ModelsDialog(self.db, self)
        dialog.exec_()
        self.load_models_info()
    
    def improve_prompt(self):
        """Открытие диалога улучшения промта."""
        prompt_text = self.prompt_input.toPlainText().strip()
        
        if not prompt_text:
            QMessageBox.warning(self, "Предупреждение", "Введите промт для улучшения!")
            return
        
        # Получаем список активных моделей
        models = ModelFactory.get_active_models(self.db)
        
        if not models:
            QMessageBox.warning(self, "Предупреждение", "Нет активных моделей для улучшения промта!")
            return
        
        # Открываем диалог улучшения
        dialog = PromptImproverDialog(self.prompt_improver, models, prompt_text, self)
        
        if dialog.exec_() == QDialog.Accepted:
            selected_prompt = dialog.get_selected_prompt()
            if selected_prompt:
                # Подставляем выбранный промт в поле ввода
                self.prompt_input.setPlainText(selected_prompt)
                QMessageBox.information(self, "Успех", "Улучшенный промт подставлен в поле ввода!")
    
    def show_settings(self):
        """Открытие диалога настроек."""
        dialog = SettingsDialog(self.db, self)
        if dialog.exec_() == QDialog.Accepted:
            # Применяем настройки сразу
            self.apply_settings()
    
    def show_about(self):
        """Открытие диалога 'О программе'."""
        dialog = AboutDialog(self)
        dialog.exec_()
    
    def apply_settings(self):
        """Применение настроек темы и размера шрифта."""
        # Применение темы
        theme = self.db.get_setting("theme")
        if theme == "dark":
            self.apply_dark_theme()
        else:
            self.apply_light_theme()
        
        # Применение размера шрифта
        font_size = self.db.get_setting("font_size")
        if font_size:
            try:
                size = int(font_size)
                self.apply_font_size(size)
            except ValueError:
                self.apply_font_size(10)
        else:
            self.apply_font_size(10)
    
    def apply_light_theme(self):
        """Применение светлой темы."""
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(255, 255, 255))
        palette.setColor(QPalette.WindowText, QColor(0, 0, 0))
        palette.setColor(QPalette.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.AlternateBase, QColor(240, 240, 240))
        palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 220))
        palette.setColor(QPalette.ToolTipText, QColor(0, 0, 0))
        palette.setColor(QPalette.Text, QColor(0, 0, 0))
        palette.setColor(QPalette.Button, QColor(240, 240, 240))
        palette.setColor(QPalette.ButtonText, QColor(0, 0, 0))
        palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.Link, QColor(0, 0, 255))
        palette.setColor(QPalette.Highlight, QColor(0, 120, 215))
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        QApplication.setPalette(palette)
    
    def apply_dark_theme(self):
        """Применение темной темы."""
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.Base, QColor(35, 35, 35))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, QColor(0, 0, 0))
        palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
        palette.setColor(QPalette.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
        QApplication.setPalette(palette)
    
    def apply_font_size(self, size: int):
        """Применение размера шрифта ко всем виджетам."""
        font = QFont()
        font.setPointSize(size)
        QApplication.setFont(font)
    
    def search_prompts(self):
        """Поиск промтов."""
        from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget
        from PyQt5.QtCore import Qt
        from maximizable_dialog import MaximizableDialog
        
        dialog = MaximizableDialog(self)
        dialog.setWindowTitle("Поиск промтов")
        dialog.setGeometry(300, 300, 600, 400)
        layout = QVBoxLayout()
        dialog.setLayout(layout)
        
        # Заголовок с иконкой разворачивания
        header_layout = QHBoxLayout()
        header_label = QLabel("<b>Поиск промтов</b>")
        header_label.setStyleSheet("font-size: 14px; padding: 5px;")
        header_layout.addWidget(header_label)
        dialog.add_maximize_button_to_header(header_layout, header_label)
        layout.addLayout(header_layout)
        
        layout.addWidget(QLabel("Поисковый запрос:"))
        search_input = QLineEdit()
        result_list = QListWidget()
        
        def load_prompts_to_list(prompts):
            """Загрузка промптов в список результатов."""
            result_list.clear()
            for prompt in prompts:
                tags_text = f" [{prompt['tags']}]" if prompt.get('tags') else ""
                item_text = f"{prompt['date']}: {prompt['prompt'][:100]}{tags_text}"
                result_list.addItem(item_text)
        
        def update_prompts_search(text):
            """Обновление результатов поиска."""
            if text.strip():
                # Поиск с сортировкой по дате (DESC)
                prompts = self.db.get_all_prompts(search=text.strip(), sort_by="date", order="DESC")
            else:
                # Загрузка всей истории по умолчанию, отсортированной по дате (DESC)
                prompts = self.db.get_all_prompts(sort_by="date", order="DESC")
            load_prompts_to_list(prompts)
        
        # Обработка двойного клика по списку для разворачивания
        def on_list_double_click(item):
            dialog.toggle_maximize()
        result_list.itemDoubleClicked.connect(on_list_double_click)
        
        search_input.textChanged.connect(update_prompts_search)
        layout.addWidget(search_input)
        
        layout.addWidget(QLabel("Результаты:"))
        layout.addWidget(result_list)
        
        # Загрузка истории по умолчанию при открытии окна
        update_prompts_search("")
        
        buttons_layout = QHBoxLayout()
        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(dialog.accept)
        buttons_layout.addWidget(close_button)
        layout.addLayout(buttons_layout)
        
        dialog.exec_()
    
    def search_results(self):
        """Поиск сохраненных результатов."""
        from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget
        from maximizable_dialog import MaximizableDialog
        
        dialog = MaximizableDialog(self)
        dialog.setWindowTitle("Поиск результатов")
        dialog.setGeometry(300, 300, 700, 500)
        layout = QVBoxLayout()
        dialog.setLayout(layout)
        
        # Заголовок с иконкой разворачивания
        header_layout = QHBoxLayout()
        header_label = QLabel("<b>Поиск результатов</b>")
        header_label.setStyleSheet("font-size: 14px; padding: 5px;")
        header_layout.addWidget(header_label)
        dialog.add_maximize_button_to_header(header_layout, header_label)
        layout.addLayout(header_layout)
        
        layout.addWidget(QLabel("Поисковый запрос:"))
        search_input = QLineEdit()
        result_list = QListWidget()
        
        def update_search(text):
            result_list.clear()
            if text.strip():
                results = self.db.get_all_results(search=text.strip())
                models = {m['id']: m['name'] for m in self.db.get_all_models()}
                prompts = {p['id']: p for p in self.db.get_all_prompts()}
                
                for result in results:
                    model_name = models.get(result['model_id'], 'Unknown')
                    prompt_text = prompts.get(result['prompt_id'], {}).get('prompt', '')[:50]
                    result_list.addItem(f"{model_name}: {result['response_text'][:80]}... (Промт: {prompt_text})")
        
        # Обработка двойного клика по списку для разворачивания
        def on_list_double_click(item):
            dialog.toggle_maximize()
        result_list.itemDoubleClicked.connect(on_list_double_click)
        
        search_input.textChanged.connect(update_search)
        layout.addWidget(search_input)
        
        layout.addWidget(QLabel("Результаты:"))
        layout.addWidget(result_list)
        
        buttons_layout = QHBoxLayout()
        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(dialog.accept)
        buttons_layout.addWidget(close_button)
        layout.addLayout(buttons_layout)
        
        dialog.exec_()
    
    def closeEvent(self, event):
        """Обработка закрытия приложения."""
        self.db.close()
        event.accept()


def main():
    """Главная функция приложения."""
    app = QApplication(sys.argv)
    
    # Установка стиля приложения
    app.setStyle('Fusion')
    
    # Установка иконки приложения
    icon_path = os.path.join(os.path.dirname(__file__), "app.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

