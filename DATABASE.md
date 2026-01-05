# Схема базы данных ChatList

## Общая информация

База данных использует SQLite и состоит из четырех основных таблиц:
- `prompts` - хранение промтов (запросов пользователя)
- `models` - хранение информации о нейросетях
- `results` - хранение сохраненных результатов ответов моделей
- `settings` - хранение настроек программы

## Таблица: prompts

Хранит промты (запросы), которые пользователь отправляет в нейросети.

### Структура таблицы

| Поле | Тип | Описание | Ограничения |
|------|-----|----------|-------------|
| id | INTEGER | Первичный ключ | PRIMARY KEY AUTOINCREMENT |
| date | TEXT | Дата создания промта | NOT NULL, формат: ISO 8601 (YYYY-MM-DD HH:MM:SS) |
| prompt | TEXT | Текст промта | NOT NULL |
| tags | TEXT | Теги для категоризации | Может быть NULL, формат: разделенные запятыми |

### Пример данных

```
id: 1
date: "2024-01-15 10:30:00"
prompt: "Объясни квантовую физику простыми словами"
tags: "физика, образование"
```

### Индексы

- `idx_prompts_date` - индекс по полю `date` для быстрого поиска по дате
- `idx_prompts_tags` - индекс по полю `tags` для поиска по тегам

## Таблица: models

Хранит информацию о нейросетях (моделях), к которым можно отправлять запросы.

### Структура таблицы

| Поле | Тип | Описание | Ограничения |
|------|-----|----------|-------------|
| id | INTEGER | Первичный ключ | PRIMARY KEY AUTOINCREMENT |
| name | TEXT | Название модели | NOT NULL, UNIQUE |
| api_url | TEXT | URL API для отправки запросов | NOT NULL |
| api_id | TEXT | Имя переменной окружения с API-ключом | NOT NULL, например: "OPENAI_API_KEY" |
| is_active | INTEGER | Флаг активности модели | NOT NULL, 0 или 1 (BOOLEAN) |
| model_type | TEXT | Тип модели (openai, deepseek, groq) | NOT NULL |

### Пример данных

```
id: 1
name: "GPT-4"
api_url: "https://api.openai.com/v1/chat/completions"
api_id: "OPENAI_API_KEY"
is_active: 1
model_type: "openai"

id: 2
name: "DeepSeek Chat"
api_url: "https://api.deepseek.com/v1/chat/completions"
api_id: "DEEPSEEK_API_KEY"
is_active: 1
model_type: "deepseek"
```

### Индексы

- `idx_models_is_active` - индекс по полю `is_active` для быстрого получения активных моделей
- `idx_models_name` - индекс по полю `name` для поиска по названию

### Примечания

- API-ключи не хранятся в базе данных, а находятся в файле `.env`
- Поле `api_id` содержит имя переменной окружения, из которой нужно брать ключ
- Поле `is_active` определяет, будет ли модель использоваться при отправке запросов

## Таблица: results

Хранит сохраненные результаты ответов моделей на промты.

### Структура таблицы

| Поле | Тип | Описание | Ограничения |
|------|-----|----------|-------------|
| id | INTEGER | Первичный ключ | PRIMARY KEY AUTOINCREMENT |
| prompt_id | INTEGER | Ссылка на промт | NOT NULL, FOREIGN KEY (prompts.id) |
| model_id | INTEGER | Ссылка на модель | NOT NULL, FOREIGN KEY (models.id) |
| response_text | TEXT | Текст ответа модели | NOT NULL |
| saved_date | TEXT | Дата сохранения результата | NOT NULL, формат: ISO 8601 |

### Пример данных

```
id: 1
prompt_id: 1
model_id: 1
response_text: "Квантовая физика изучает поведение частиц на атомном уровне..."
saved_date: "2024-01-15 10:35:00"
```

### Индексы

- `idx_results_prompt_id` - индекс по полю `prompt_id` для быстрого поиска результатов по промту
- `idx_results_model_id` - индекс по полю `model_id` для поиска результатов по модели
- `idx_results_saved_date` - индекс по полю `saved_date` для сортировки по дате

### Связи

- `results.prompt_id` → `prompts.id` (ON DELETE CASCADE)
- `results.model_id` → `models.id` (ON DELETE RESTRICT)

## Таблица: settings

Хранит настройки программы.

### Структура таблицы

| Поле | Тип | Описание | Ограничения |
|------|-----|----------|-------------|
| id | INTEGER | Первичный ключ | PRIMARY KEY AUTOINCREMENT |
| key | TEXT | Ключ настройки | NOT NULL, UNIQUE |
| value | TEXT | Значение настройки | Может быть NULL |

### Пример данных

```
id: 1
key: "default_timeout"
value: "30"

id: 2
key: "max_results_per_page"
value: "50"

id: 3
key: "export_format"
value: "markdown"
```

### Стандартные настройки

- `default_timeout` - таймаут для HTTP-запросов (секунды)
- `max_results_per_page` - максимальное количество результатов на странице
- `export_format` - формат экспорта по умолчанию (markdown/json)
- `log_level` - уровень логирования (DEBUG/INFO/WARNING/ERROR)

## Диаграмма связей

```
prompts (1) ────< (N) results
                      │
                      │
models (1) ──────────< (N) results

settings (независимая таблица)
```

## SQL для создания таблиц

```sql
-- Таблица prompts
CREATE TABLE IF NOT EXISTS prompts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    prompt TEXT NOT NULL,
    tags TEXT
);

CREATE INDEX IF NOT EXISTS idx_prompts_date ON prompts(date);
CREATE INDEX IF NOT EXISTS idx_prompts_tags ON prompts(tags);

-- Таблица models
CREATE TABLE IF NOT EXISTS models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    api_url TEXT NOT NULL,
    api_id TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    model_type TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_models_is_active ON models(is_active);
CREATE INDEX IF NOT EXISTS idx_models_name ON models(name);

-- Таблица results
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt_id INTEGER NOT NULL,
    model_id INTEGER NOT NULL,
    response_text TEXT NOT NULL,
    saved_date TEXT NOT NULL,
    FOREIGN KEY (prompt_id) REFERENCES prompts(id) ON DELETE CASCADE,
    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_results_prompt_id ON results(prompt_id);
CREATE INDEX IF NOT EXISTS idx_results_model_id ON results(model_id);
CREATE INDEX IF NOT EXISTS idx_results_saved_date ON results(saved_date);

-- Таблица settings
CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL UNIQUE,
    value TEXT
);
```

## Примечания по реализации

1. **Временная таблица результатов**: Не хранится в БД, создается в памяти при получении ответов от моделей. Структура аналогична таблице `results`, но без полей `id` и `saved_date`, с добавлением поля `selected` (BOOLEAN).

2. **Формат даты**: Используется формат ISO 8601 (YYYY-MM-DD HH:MM:SS) для удобства сортировки и сравнения.

3. **API-ключи**: Хранятся в файле `.env` в формате:
   ```
   OPENAI_API_KEY=sk-...
   DEEPSEEK_API_KEY=sk-...
   GROQ_API_KEY=gsk_...
   ```

4. **Каскадное удаление**: При удалении промта автоматически удаляются связанные результаты (ON DELETE CASCADE). При удалении модели удаление результатов запрещено (ON DELETE RESTRICT) для сохранения истории.

