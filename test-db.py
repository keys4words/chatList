"""
Тестовая программа для просмотра и редактирования SQLite баз данных.
Позволяет открыть файл БД, просмотреть список таблиц, 
отобразить данные с пагинацией и выполнить CRUD операции.
"""
import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem, QFileDialog,
    QListWidget, QListWidgetItem, QMessageBox, QDialog, QFormLayout,
    QLineEdit, QTextEdit, QDialogButtonBox, QSpinBox, QGroupBox
)
from PyQt5.QtCore import Qt
from typing import Optional, List, Dict, Any


class DatabaseViewer(QMainWindow):
    """Главное окно для просмотра и редактирования SQLite БД."""
    
    def __init__(self):
        super().__init__()
        self.db_path: Optional[str] = None
        self.conn: Optional[sqlite3.Connection] = None
        self.current_table: Optional[str] = None
        self.current_page: int = 1
        self.rows_per_page: int = 50
        self.total_rows: int = 0
        self.init_ui()
    
    def init_ui(self):
        """Инициализация интерфейса."""
        self.setWindowTitle("Просмотр SQLite базы данных")
        self.setGeometry(100, 100, 1200, 800)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Верхняя панель: выбор файла
        file_layout = QHBoxLayout()
        self.file_label = QLabel("Файл БД не выбран")
        self.file_label.setStyleSheet("font-weight: bold; padding: 5px;")
        file_layout.addWidget(self.file_label)
        
        self.open_file_btn = QPushButton("Выбрать файл БД")
        self.open_file_btn.clicked.connect(self.open_database)
        file_layout.addWidget(self.open_file_btn)
        
        main_layout.addLayout(file_layout)
        
        # Группа: список таблиц
        tables_group = QGroupBox("Таблицы")
        tables_layout = QVBoxLayout()
        
        self.tables_list = QListWidget()
        self.tables_list.itemClicked.connect(self.on_table_selected)
        tables_layout.addWidget(self.tables_list)
        
        self.open_table_btn = QPushButton("Открыть таблицу")
        self.open_table_btn.clicked.connect(self.open_selected_table)
        self.open_table_btn.setEnabled(False)
        tables_layout.addWidget(self.open_table_btn)
        
        tables_group.setLayout(tables_layout)
        main_layout.addWidget(tables_group)
        
        # Группа: данные таблицы
        data_group = QGroupBox("Данные таблицы")
        data_layout = QVBoxLayout()
        
        # Информация о таблице
        info_layout = QHBoxLayout()
        self.table_info_label = QLabel("Таблица не выбрана")
        info_layout.addWidget(self.table_info_label)
        
        # Настройки пагинации
        pagination_settings = QHBoxLayout()
        pagination_settings.addWidget(QLabel("Строк на странице:"))
        self.rows_per_page_spin = QSpinBox()
        self.rows_per_page_spin.setMinimum(10)
        self.rows_per_page_spin.setMaximum(1000)
        self.rows_per_page_spin.setValue(50)
        self.rows_per_page_spin.valueChanged.connect(self.on_rows_per_page_changed)
        pagination_settings.addWidget(self.rows_per_page_spin)
        pagination_settings.addStretch()
        
        info_layout.addLayout(pagination_settings)
        data_layout.addLayout(info_layout)
        
        # Таблица данных
        self.data_table = QTableWidget()
        self.data_table.setAlternatingRowColors(True)
        self.data_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.data_table.setEditTriggers(QTableWidget.NoEditTriggers)
        data_layout.addWidget(self.data_table)
        
        # Панель пагинации
        pagination_layout = QHBoxLayout()
        
        self.prev_page_btn = QPushButton("◄ Предыдущая")
        self.prev_page_btn.clicked.connect(self.prev_page)
        self.prev_page_btn.setEnabled(False)
        pagination_layout.addWidget(self.prev_page_btn)
        
        self.page_label = QLabel("Страница: 0 / 0")
        pagination_layout.addWidget(self.page_label)
        
        self.next_page_btn = QPushButton("Следующая ►")
        self.next_page_btn.clicked.connect(self.next_page)
        self.next_page_btn.setEnabled(False)
        pagination_layout.addWidget(self.next_page_btn)
        
        pagination_layout.addStretch()
        
        # Кнопки CRUD
        crud_layout = QHBoxLayout()
        
        self.create_btn = QPushButton("➕ Создать")
        self.create_btn.clicked.connect(self.create_record)
        self.create_btn.setEnabled(False)
        crud_layout.addWidget(self.create_btn)
        
        self.update_btn = QPushButton("✏️ Редактировать")
        self.update_btn.clicked.connect(self.update_record)
        self.update_btn.setEnabled(False)
        crud_layout.addWidget(self.update_btn)
        
        self.delete_btn = QPushButton("🗑️ Удалить")
        self.delete_btn.clicked.connect(self.delete_record)
        self.delete_btn.setEnabled(False)
        crud_layout.addWidget(self.delete_btn)
        
        self.refresh_btn = QPushButton("🔄 Обновить")
        self.refresh_btn.clicked.connect(self.refresh_table)
        self.refresh_btn.setEnabled(False)
        crud_layout.addWidget(self.refresh_btn)
        
        pagination_layout.addLayout(crud_layout)
        data_layout.addLayout(pagination_layout)
        
        data_group.setLayout(data_layout)
        main_layout.addWidget(data_group)
    
    def open_database(self):
        """Открытие файла базы данных."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл SQLite базы данных",
            "",
            "SQLite Database (*.db *.sqlite *.sqlite3);;All Files (*)"
        )
        
        if file_path:
            try:
                # Закрываем предыдущее соединение, если есть
                if self.conn:
                    self.conn.close()
                
                # Открываем новое соединение
                self.db_path = file_path
                self.conn = sqlite3.connect(file_path)
                self.conn.row_factory = sqlite3.Row  # Для доступа к колонкам по имени
                
                self.file_label.setText(f"Файл: {file_path}")
                self.load_tables()
                
                QMessageBox.information(self, "Успех", "База данных успешно открыта!")
                
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось открыть базу данных:\n{str(e)}")
                self.conn = None
                self.db_path = None
    
    def load_tables(self):
        """Загрузка списка таблиц из БД."""
        if not self.conn:
            return
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)
            
            tables = cursor.fetchall()
            self.tables_list.clear()
            
            for table in tables:
                item = QListWidgetItem(table[0])
                self.tables_list.addItem(item)
            
            if tables:
                self.open_table_btn.setEnabled(True)
            else:
                self.open_table_btn.setEnabled(False)
                
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке таблиц:\n{str(e)}")
    
    def on_table_selected(self, item: QListWidgetItem):
        """Обработка выбора таблицы в списке."""
        self.open_table_btn.setEnabled(True)
    
    def open_selected_table(self):
        """Открытие выбранной таблицы."""
        selected_items = self.tables_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Предупреждение", "Выберите таблицу из списка")
            return
        
        if not self.conn:
            QMessageBox.warning(self, "Предупреждение", "База данных не открыта")
            return
        
        self.current_table = selected_items[0].text()
        self.current_page = 1
        self.load_table_data()
    
    def load_table_data(self):
        """Загрузка данных таблицы с пагинацией."""
        if not self.conn or not self.current_table:
            return
        
        try:
            cursor = self.conn.cursor()
            
            # Получаем общее количество строк
            cursor.execute(f"SELECT COUNT(*) FROM {self.current_table}")
            self.total_rows = cursor.fetchone()[0]
            
            # Получаем информацию о колонках
            cursor.execute(f"PRAGMA table_info({self.current_table})")
            columns_info = cursor.fetchall()
            column_names = [col[1] for col in columns_info]
            
            # Вычисляем пагинацию
            total_pages = (self.total_rows + self.rows_per_page - 1) // self.rows_per_page if self.total_rows > 0 else 1
            offset = (self.current_page - 1) * self.rows_per_page
            
            # Загружаем данные с пагинацией
            cursor.execute(f"""
                SELECT * FROM {self.current_table}
                LIMIT ? OFFSET ?
            """, (self.rows_per_page, offset))
            
            rows = cursor.fetchall()
            
            # Настраиваем таблицу
            self.data_table.setColumnCount(len(column_names))
            self.data_table.setHorizontalHeaderLabels(column_names)
            self.data_table.setRowCount(len(rows))
            
            # Заполняем таблицу
            for row_idx, row in enumerate(rows):
                for col_idx, value in enumerate(row):
                    item = QTableWidgetItem(str(value) if value is not None else "")
                    self.data_table.setItem(row_idx, col_idx, item)
            
            # Обновляем информацию и кнопки
            self.table_info_label.setText(
                f"Таблица: {self.current_table} | Всего строк: {self.total_rows} | "
                f"Страница {self.current_page} из {total_pages}"
            )
            self.page_label.setText(f"Страница: {self.current_page} / {total_pages}")
            
            self.prev_page_btn.setEnabled(self.current_page > 1)
            self.next_page_btn.setEnabled(self.current_page < total_pages)
            
            # Включаем кнопки CRUD
            self.create_btn.setEnabled(True)
            self.update_btn.setEnabled(True)
            self.delete_btn.setEnabled(True)
            self.refresh_btn.setEnabled(True)
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке данных:\n{str(e)}")
    
    def on_rows_per_page_changed(self, value: int):
        """Обработка изменения количества строк на странице."""
        self.rows_per_page = value
        self.current_page = 1
        if self.current_table:
            self.load_table_data()
    
    def prev_page(self):
        """Переход на предыдущую страницу."""
        if self.current_page > 1:
            self.current_page -= 1
            self.load_table_data()
    
    def next_page(self):
        """Переход на следующую страницу."""
        total_pages = (self.total_rows + self.rows_per_page - 1) // self.rows_per_page if self.total_rows > 0 else 1
        if self.current_page < total_pages:
            self.current_page += 1
            self.load_table_data()
    
    def refresh_table(self):
        """Обновление данных таблицы."""
        if self.current_table:
            self.load_table_data()
    
    def get_column_info(self) -> List[Dict[str, Any]]:
        """Получение информации о колонках текущей таблицы."""
        if not self.conn or not self.current_table:
            return []
        
        cursor = self.conn.cursor()
        cursor.execute(f"PRAGMA table_info({self.current_table})")
        columns = cursor.fetchall()
        
        return [
            {
                "name": col[1],
                "type": col[2],
                "notnull": col[3],
                "default": col[4],
                "pk": col[5]
            }
            for col in columns
        ]
    
    def create_record(self):
        """Создание новой записи."""
        if not self.conn or not self.current_table:
            return
        
        columns_info = self.get_column_info()
        if not columns_info:
            return
        
        dialog = RecordDialog(columns_info, self)
        if dialog.exec_() == QDialog.Accepted:
            values = dialog.get_values()
            try:
                cursor = self.conn.cursor()
                column_names = [col["name"] for col in columns_info if not col["pk"] or values.get(col["name"])]
                placeholders = ", ".join(["?" for _ in column_names])
                column_names_str = ", ".join(column_names)
                values_list = [values.get(col) for col in column_names]
                
                cursor.execute(f"INSERT INTO {self.current_table} ({column_names_str}) VALUES ({placeholders})", values_list)
                self.conn.commit()
                
                QMessageBox.information(self, "Успех", "Запись успешно создана!")
                self.refresh_table()
                
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при создании записи:\n{str(e)}")
                self.conn.rollback()
    
    def update_record(self):
        """Редактирование выбранной записи."""
        selected_rows = self.data_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Предупреждение", "Выберите строку для редактирования")
            return
        
        if not self.conn or not self.current_table:
            return
        
        row_idx = selected_rows[0].row()
        
        # Получаем полные данные записи (с учетом пагинации)
        offset = (self.current_page - 1) * self.rows_per_page
        cursor = self.conn.cursor()
        cursor.execute(f"""
            SELECT * FROM {self.current_table}
            LIMIT 1 OFFSET ?
        """, (offset + row_idx,))
        
        row_data = cursor.fetchone()
        if not row_data:
            return
        
        columns_info = self.get_column_info()
        column_names = [col["name"] for col in columns_info]
        
        # Создаем словарь значений
        current_values = {col: str(row_data[col]) if row_data[col] is not None else "" for col in column_names}
        
        dialog = RecordDialog(columns_info, self, current_values)
        if dialog.exec_() == QDialog.Accepted:
            new_values = dialog.get_values()
            
            # Находим первичный ключ
            pk_columns = [col["name"] for col in columns_info if col["pk"]]
            if not pk_columns:
                QMessageBox.warning(self, "Предупреждение", "Таблица не имеет первичного ключа")
                return
            
            try:
                cursor = self.conn.cursor()
                set_clause = ", ".join([f"{col} = ?" for col in column_names if col not in pk_columns])
                where_clause = " AND ".join([f"{pk} = ?" for pk in pk_columns])
                set_values = [new_values.get(col) for col in column_names if col not in pk_columns]
                where_values = [current_values[pk] for pk in pk_columns]
                
                cursor.execute(
                    f"UPDATE {self.current_table} SET {set_clause} WHERE {where_clause}",
                    set_values + where_values
                )
                self.conn.commit()
                
                QMessageBox.information(self, "Успех", "Запись успешно обновлена!")
                self.refresh_table()
                
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при обновлении записи:\n{str(e)}")
                self.conn.rollback()
    
    def delete_record(self):
        """Удаление выбранной записи."""
        selected_rows = self.data_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Предупреждение", "Выберите строку для удаления")
            return
        
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            "Вы уверены, что хотите удалить выбранную запись?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        if not self.conn or not self.current_table:
            return
        
        row_idx = selected_rows[0].row()
        
        # Получаем полные данные записи
        offset = (self.current_page - 1) * self.rows_per_page
        cursor = self.conn.cursor()
        cursor.execute(f"""
            SELECT * FROM {self.current_table}
            LIMIT 1 OFFSET ?
        """, (offset + row_idx,))
        
        row_data = cursor.fetchone()
        if not row_data:
            return
        
        columns_info = self.get_column_info()
        pk_columns = [col["name"] for col in columns_info if col["pk"]]
        
        if not pk_columns:
            # Если нет PK, используем все колонки для WHERE
            pk_columns = [col["name"] for col in columns_info]
        
        try:
            where_clause = " AND ".join([f"{pk} = ?" for pk in pk_columns])
            where_values = [row_data[pk] for pk in pk_columns]
            
            cursor.execute(f"DELETE FROM {self.current_table} WHERE {where_clause}", where_values)
            self.conn.commit()
            
            QMessageBox.information(self, "Успех", "Запись успешно удалена!")
            self.refresh_table()
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении записи:\n{str(e)}")
            self.conn.rollback()
    
    def closeEvent(self, event):
        """Закрытие соединения с БД при закрытии приложения."""
        if self.conn:
            self.conn.close()
        event.accept()


class RecordDialog(QDialog):
    """Диалог для создания/редактирования записи."""
    
    def __init__(self, columns_info: List[Dict[str, Any]], parent=None, current_values: Optional[Dict[str, str]] = None):
        super().__init__(parent)
        self.columns_info = columns_info
        self.current_values = current_values or {}
        self.inputs: Dict[str, QLineEdit] = {}
        self.init_ui()
    
    def init_ui(self):
        """Инициализация интерфейса диалога."""
        self.setWindowTitle("Редактирование записи" if self.current_values else "Создание записи")
        self.setModal(True)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        form_layout = QFormLayout()
        
        for col_info in self.columns_info:
            col_name = col_info["name"]
            col_type = col_info["type"].upper()
            is_pk = col_info["pk"]
            is_notnull = col_info["notnull"]
            default_val = col_info["default"]
            
            # Пропускаем автоинкрементные PK при создании
            if is_pk and "INTEGER" in col_type and not self.current_values:
                continue
            
            label_text = col_name
            if is_pk:
                label_text += " (PK)"
            if is_notnull:
                label_text += " *"
            
            # Определяем тип поля ввода
            if "TEXT" in col_type or "VARCHAR" in col_type or "CHAR" in col_type:
                input_widget = QTextEdit()
                input_widget.setMaximumHeight(100)
                if col_name in self.current_values:
                    input_widget.setPlainText(self.current_values[col_name])
                elif default_val:
                    input_widget.setPlainText(str(default_val))
            else:
                input_widget = QLineEdit()
                if col_name in self.current_values:
                    input_widget.setText(self.current_values[col_name])
                elif default_val:
                    input_widget.setText(str(default_val))
            
            if is_pk and self.current_values:
                input_widget.setReadOnly(True)
                input_widget.setStyleSheet("background-color: #f0f0f0;")
            
            self.inputs[col_name] = input_widget
            form_layout.addRow(label_text, input_widget)
        
        layout.addLayout(form_layout)
        
        # Кнопки
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_values(self) -> Dict[str, Any]:
        """Получение значений из полей ввода."""
        values = {}
        for col_name, input_widget in self.inputs.items():
            if isinstance(input_widget, QTextEdit):
                value = input_widget.toPlainText().strip()
            else:
                value = input_widget.text().strip()
            
            # Преобразуем пустые строки в None для полей, которые могут быть NULL
            if not value:
                col_info = next((c for c in self.columns_info if c["name"] == col_name), None)
                if col_info and not col_info["notnull"]:
                    value = None
                else:
                    value = value if value else None
            
            values[col_name] = value
        
        return values


def main():
    """Главная функция."""
    app = QApplication(sys.argv)
    window = DatabaseViewer()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

