"""
Модуль для работы с базой данных SQLite.
Инкапсулирует все операции с БД.
"""
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple

# Импортируем утилиту для определения путей
try:
    from app_paths import get_db_path
except ImportError:
    # Если app_paths не доступен (старая версия), используем текущую директорию
    def get_db_path():
        return "chatlist.db"


class Database:
    """Класс для работы с базой данных."""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Инициализация подключения к БД.
        
        Args:
            db_path: Путь к файлу базы данных (если None, определяется автоматически)
        """
        if db_path is None:
            db_path = get_db_path()
        
        # Создаем директорию для базы данных, если нужно
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        
        self.db_path = db_path
        self.conn = None
        self.connect()
        self.create_tables()
        self.init_default_settings()
    
    def connect(self):
        """Установка соединения с БД."""
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
        except sqlite3.OperationalError as e:
            # Если не удается создать БД, пробуем в текущей директории
            if "unable to open database file" in str(e).lower():
                fallback_path = os.path.join(os.getcwd(), "chatlist.db")
                if fallback_path != self.db_path:
                    self.db_path = fallback_path
                    self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
                    self.conn.row_factory = sqlite3.Row
                else:
                    raise
            else:
                raise
    
    def close(self):
        """Закрытие соединения с БД."""
        if self.conn:
            self.conn.close()
    
    def create_tables(self):
        """Создание всех необходимых таблиц в БД."""
        cursor = self.conn.cursor()
        
        # Таблица prompts
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prompts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                prompt TEXT NOT NULL,
                tags TEXT
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_prompts_date ON prompts(date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_prompts_tags ON prompts(tags)")
        
        # Таблица models
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                api_url TEXT NOT NULL,
                api_id TEXT NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1,
                model_type TEXT NOT NULL,
                api_model_name TEXT
            )
        """)
        # Добавление поля api_model_name, если таблица уже существует
        try:
            cursor.execute("ALTER TABLE models ADD COLUMN api_model_name TEXT")
        except sqlite3.OperationalError:
            pass  # Поле уже существует
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_models_is_active ON models(is_active)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_models_name ON models(name)")
        
        # Таблица results
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt_id INTEGER NOT NULL,
                model_id INTEGER NOT NULL,
                response_text TEXT NOT NULL,
                saved_date TEXT NOT NULL,
                FOREIGN KEY (prompt_id) REFERENCES prompts(id) ON DELETE CASCADE,
                FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE RESTRICT
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_results_prompt_id ON results(prompt_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_results_model_id ON results(model_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_results_saved_date ON results(saved_date)")
        
        # Таблица settings
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT NOT NULL UNIQUE,
                value TEXT
            )
        """)
        
        self.conn.commit()
    
    def init_default_settings(self):
        """Инициализация настроек по умолчанию."""
        default_settings = {
            "default_timeout": "120",
            "request_timeout": "120",
            "max_results_per_page": "50",
            "export_format": "markdown",
            "log_level": "INFO",
            "retry_on_429": "true",
            "max_retries": "3",
            "delay_between_requests": "0.5",
            "theme": "light",
            "font_size": "10"
        }
        
        cursor = self.conn.cursor()
        for key, value in default_settings.items():
            cursor.execute(
                "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
                (key, value)
            )
        self.conn.commit()
    
    # ========== CRUD операции для prompts ==========
    
    def create_prompt(self, prompt: str, tags: Optional[str] = None) -> int:
        """
        Создание нового промта.
        
        Args:
            prompt: Текст промта
            tags: Теги (разделенные запятыми)
            
        Returns:
            ID созданного промта
        """
        cursor = self.conn.cursor()
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO prompts (date, prompt, tags) VALUES (?, ?, ?)",
            (date, prompt, tags)
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def get_prompt(self, prompt_id: int) -> Optional[Dict]:
        """Получение промта по ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM prompts WHERE id = ?", (prompt_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_all_prompts(self, search: Optional[str] = None, 
                       sort_by: str = "date", 
                       order: str = "DESC") -> List[Dict]:
        """
        Получение всех промтов с возможностью поиска и сортировки.
        
        Args:
            search: Поисковый запрос (по тексту промта или тегам)
            sort_by: Поле для сортировки (date, prompt, tags)
            order: Порядок сортировки (ASC, DESC)
        """
        cursor = self.conn.cursor()
        query = "SELECT * FROM prompts"
        params = []
        
        if search:
            query += " WHERE prompt LIKE ? OR tags LIKE ?"
            search_term = f"%{search}%"
            params = [search_term, search_term]
        
        if sort_by in ["date", "prompt", "tags"]:
            query += f" ORDER BY {sort_by} {order}"
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def update_prompt(self, prompt_id: int, prompt: str, tags: Optional[str] = None):
        """Обновление промта."""
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE prompts SET prompt = ?, tags = ? WHERE id = ?",
            (prompt, tags, prompt_id)
        )
        self.conn.commit()
    
    def delete_prompt(self, prompt_id: int):
        """Удаление промта."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM prompts WHERE id = ?", (prompt_id,))
        self.conn.commit()
    
    # ========== CRUD операции для models ==========
    
    def create_model(self, name: str, api_url: str, api_id: str, 
                    model_type: str, is_active: int = 1, api_model_name: Optional[str] = None) -> int:
        """Создание новой модели."""
        cursor = self.conn.cursor()
        cursor.execute(
            """INSERT INTO models (name, api_url, api_id, model_type, is_active, api_model_name) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            (name, api_url, api_id, model_type, is_active, api_model_name)
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def get_model(self, model_id: int) -> Optional[Dict]:
        """Получение модели по ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM models WHERE id = ?", (model_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_all_models(self, active_only: bool = False, 
                      search: Optional[str] = None) -> List[Dict]:
        """
        Получение всех моделей.
        
        Args:
            active_only: Только активные модели
            search: Поиск по названию
        """
        cursor = self.conn.cursor()
        query = "SELECT * FROM models WHERE 1=1"
        params = []
        
        if active_only:
            query += " AND is_active = 1"
        
        if search:
            query += " AND name LIKE ?"
            params.append(f"%{search}%")
        
        query += " ORDER BY name"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def get_active_models(self) -> List[Dict]:
        """Получение списка активных моделей."""
        return self.get_all_models(active_only=True)
    
    def update_model(self, model_id: int, name: Optional[str] = None,
                    api_url: Optional[str] = None, api_id: Optional[str] = None,
                    is_active: Optional[int] = None, model_type: Optional[str] = None,
                    api_model_name: Optional[str] = None):
        """Обновление модели."""
        cursor = self.conn.cursor()
        updates = []
        params = []
        
        if name is not None:
            updates.append("name = ?")
            params.append(name)
        if api_url is not None:
            updates.append("api_url = ?")
            params.append(api_url)
        if api_id is not None:
            updates.append("api_id = ?")
            params.append(api_id)
        if is_active is not None:
            updates.append("is_active = ?")
            params.append(is_active)
        if model_type is not None:
            updates.append("model_type = ?")
            params.append(model_type)
        if api_model_name is not None:
            updates.append("api_model_name = ?")
            params.append(api_model_name)
        
        if updates:
            params.append(model_id)
            query = f"UPDATE models SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            self.conn.commit()
    
    def delete_model(self, model_id: int):
        """Удаление модели."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM models WHERE id = ?", (model_id,))
        self.conn.commit()
    
    # ========== CRUD операции для results ==========
    
    def create_result(self, prompt_id: int, model_id: int, response_text: str) -> int:
        """Создание результата."""
        cursor = self.conn.cursor()
        saved_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            """INSERT INTO results (prompt_id, model_id, response_text, saved_date) 
               VALUES (?, ?, ?, ?)""",
            (prompt_id, model_id, response_text, saved_date)
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def get_result(self, result_id: int) -> Optional[Dict]:
        """Получение результата по ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM results WHERE id = ?", (result_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_all_results(self, prompt_id: Optional[int] = None,
                       model_id: Optional[int] = None,
                       search: Optional[str] = None,
                       sort_by: str = "saved_date",
                       order: str = "DESC") -> List[Dict]:
        """
        Получение всех результатов с фильтрацией и сортировкой.
        """
        cursor = self.conn.cursor()
        query = "SELECT * FROM results WHERE 1=1"
        params = []
        
        if prompt_id:
            query += " AND prompt_id = ?"
            params.append(prompt_id)
        
        if model_id:
            query += " AND model_id = ?"
            params.append(model_id)
        
        if search:
            query += " AND response_text LIKE ?"
            params.append(f"%{search}%")
        
        if sort_by in ["saved_date", "prompt_id", "model_id"]:
            query += f" ORDER BY {sort_by} {order}"
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def delete_result(self, result_id: int):
        """Удаление результата."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM results WHERE id = ?", (result_id,))
        self.conn.commit()
    
    # ========== Операции для settings ==========
    
    def get_setting(self, key: str) -> Optional[str]:
        """Получение настройки по ключу."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row["value"] if row else None
    
    def set_setting(self, key: str, value: str):
        """Установка настройки."""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            (key, value)
        )
        self.conn.commit()
    
    def get_all_settings(self) -> Dict[str, str]:
        """Получение всех настроек."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT key, value FROM settings")
        return {row["key"]: row["value"] for row in cursor.fetchall()}

