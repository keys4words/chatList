"""
Модуль для работы с моделями нейросетей.
Содержит классы для различных типов API.
"""
import os
from abc import ABC, abstractmethod
from typing import Dict, Optional, List
from dotenv import load_dotenv
from db import Database

# Загрузка переменных окружения
load_dotenv()


class BaseModel(ABC):
    """Базовый класс для работы с моделями."""
    
    def __init__(self, model_data: Dict, db: Database):
        """
        Инициализация модели.
        
        Args:
            model_data: Словарь с данными модели из БД
            db: Экземпляр базы данных
        """
        self.id = model_data["id"]
        self.name = model_data["name"]
        self.api_id = model_data["api_id"]
        self.is_active = model_data["is_active"]
        self.model_type = model_data["model_type"]
        self.db = db
        self.api_key = self._get_api_key()
        # api_url должен быть получен после инициализации, так как зависит от model_type
        self.api_url = self._get_api_url(model_data["api_url"])
        # Имя модели для API из БД (может быть None)
        self.api_model_name = model_data.get("api_model_name")
    
    def _get_api_key(self) -> Optional[str]:
        """Получение API-ключа из переменных окружения."""
        return os.getenv(self.api_id)
    
    def _get_api_url(self, default_url: str) -> str:
        """
        Получение API URL с поддержкой OPENAI_BASE_URL.
        Если OPENAI_BASE_URL задан в .env и модель использует openai-compatible тип, использует его.
        
        Args:
            default_url: URL по умолчанию из базы данных
        """
        openai_base_url = os.getenv("OPENAI_BASE_URL")
        if openai_base_url and self.model_type.lower() in ["openai-compatible", "olmo", "mistral"]:
            # Убираем trailing slash если есть
            base_url = openai_base_url.rstrip('/')
            # Проверяем, содержит ли базовый URL уже путь /v1 или /openrouter/v1
            if '/v1' in base_url or '/openrouter/v1' in base_url:
                # Если уже есть /v1 или /openrouter/v1, просто добавляем /chat/completions
                return f"{base_url}/chat/completions"
            else:
                # Если нет /v1, добавляем полный путь
                return f"{base_url}/v1/chat/completions"
        return default_url
    
    @abstractmethod
    def format_request(self, prompt: str) -> Dict:
        """
        Форматирование запроса для конкретного API.
        
        Args:
            prompt: Текст промта
            
        Returns:
            Словарь с данными для HTTP-запроса
        """
        pass
    
    @abstractmethod
    def parse_response(self, response_data: Dict) -> str:
        """
        Парсинг ответа от API.
        
        Args:
            response_data: Данные ответа от API
            
        Returns:
            Текст ответа модели
        """
        pass


class OpenAIModel(BaseModel):
    """Класс для работы с OpenAI API."""
    
    def format_request(self, prompt: str) -> Dict:
        """Форматирование запроса для OpenAI API."""
        return {
            "model": self.name,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
    
    def parse_response(self, response_data: Dict) -> str:
        """Парсинг ответа от OpenAI API."""
        try:
            if response_data is None:
                return "Ошибка: ответ от API пустой (None)"
            if "choices" in response_data and len(response_data["choices"]) > 0:
                return response_data["choices"][0]["message"]["content"]
            return "Ошибка: пустой ответ от API"
        except (KeyError, IndexError, TypeError) as e:
            return f"Ошибка парсинга ответа: {str(e)}"


class DeepSeekModel(BaseModel):
    """Класс для работы с DeepSeek API."""
    
    def format_request(self, prompt: str) -> Dict:
        """Форматирование запроса для DeepSeek API."""
        return {
            "model": self.name,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
    
    def parse_response(self, response_data: Dict) -> str:
        """Парсинг ответа от DeepSeek API."""
        try:
            if response_data is None:
                return "Ошибка: ответ от API пустой (None)"
            if "choices" in response_data and len(response_data["choices"]) > 0:
                return response_data["choices"][0]["message"]["content"]
            return "Ошибка: пустой ответ от API"
        except (KeyError, IndexError, TypeError) as e:
            return f"Ошибка парсинга ответа: {str(e)}"


class GroqModel(BaseModel):
    """Класс для работы с Groq API."""
    
    def format_request(self, prompt: str) -> Dict:
        """Форматирование запроса для Groq API."""
        return {
            "model": self.name,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
    
    def parse_response(self, response_data: Dict) -> str:
        """Парсинг ответа от Groq API."""
        try:
            if response_data is None:
                return "Ошибка: ответ от API пустой (None)"
            if "choices" in response_data and len(response_data["choices"]) > 0:
                return response_data["choices"][0]["message"]["content"]
            return "Ошибка: пустой ответ от API"
        except (KeyError, IndexError, TypeError) as e:
            return f"Ошибка парсинга ответа: {str(e)}"


class OpenRouterModel(BaseModel):
    """Класс для работы с OpenRouter API."""
    
    # Дефолтный URL для всех OpenRouter моделей
    DEFAULT_API_URL = "https://openrouter.ai/api/v1/chat/completions"
    
    def __init__(self, model_data: Dict, db: Database):
        """Инициализация с использованием дефолтного URL и OPENROUTER_API_KEY."""
        super().__init__(model_data, db)
        # Переопределяем API URL на дефолтный для OpenRouter
        self.api_url = self.DEFAULT_API_URL
        # Переопределяем API ключ на OPENROUTER_API_KEY
        self.api_key = self._get_api_key()
    
    def _get_api_key(self) -> Optional[str]:
        """Получение API-ключа из переменных окружения (всегда OPENROUTER_API_KEY)."""
        return os.getenv("OPENROUTER_API_KEY")
    
    def _get_api_url(self, default_url: str) -> str:
        """Всегда возвращает дефолтный URL для OpenRouter."""
        return self.DEFAULT_API_URL
    
    def format_request(self, prompt: str) -> Dict:
        """Форматирование запроса для OpenRouter API."""
        # Используем api_model_name если задано, иначе используем name
        model_name = self.api_model_name if self.api_model_name else self.name
        return {
            "model": model_name,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
    
    def parse_response(self, response_data: Dict) -> str:
        """Парсинг ответа от OpenRouter API."""
        try:
            if response_data is None:
                return "Ошибка: ответ от API пустой (None)"
            if "choices" in response_data and len(response_data["choices"]) > 0:
                return response_data["choices"][0]["message"]["content"]
            return "Ошибка: пустой ответ от API"
        except (KeyError, IndexError, TypeError) as e:
            return f"Ошибка парсинга ответа: {str(e)}"


class OpenAICompatibleModel(BaseModel):
    """Класс для работы с OpenAI-совместимыми API (OLMO, Mistral, DeepSeek через OPENAI_BASE_URL)."""
    
    def __init__(self, model_data: Dict, db: Database):
        """Инициализация с поддержкой маппинга имен моделей из .env."""
        super().__init__(model_data, db)
        # Маппинг коротких имен на полные имена моделей для API (по умолчанию)
        self.model_name_mapping = {
            "olmo-3.1": "meta-llama/llama-3.1-405b-instruct",
            "mistral": "mistralai/mistral-medium-3",
            "deepseek": "deepseek/deepseek-chat"
        }
        # Получение имени модели из .env или использование маппинга/имени из БД
        self.api_model_name = self._get_model_name_from_env()
    
    def _get_model_name_from_env(self) -> str:
        """
        Получение имени модели для API.
        Приоритет: БД -> .env -> маппинг -> имя из БД
        """
        # Сначала проверяем, есть ли имя модели в БД
        if hasattr(self, 'api_model_name') and self.api_model_name:
            return self.api_model_name
        
        # Если в БД нет, проверяем .env
        # Формируем имя переменной окружения для имени модели
        # Заменяем _API_KEY на _MODEL_NAME
        model_name_env = self.api_id.replace("_API_KEY", "_MODEL_NAME")
        
        # Пытаемся получить имя модели из .env
        env_model_name = os.getenv(model_name_env)
        if env_model_name:
            return env_model_name.strip()
        
        # Если переменная не задана, используем маппинг или имя из БД
        return self.model_name_mapping.get(self.name.lower(), self.name)
    
    def format_request(self, prompt: str) -> Dict:
        """
        Форматирование запроса для OpenAI-совместимого API.
        Использует полное имя модели из маппинга или имя из БД.
        """
        return {
            "model": self.api_model_name,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
    
    def parse_response(self, response_data: Dict) -> str:
        """Парсинг ответа от OpenAI-совместимого API."""
        try:
            if response_data is None:
                return "Ошибка: ответ от API пустой (None)"
            if "choices" in response_data and len(response_data["choices"]) > 0:
                return response_data["choices"][0]["message"]["content"]
            return "Ошибка: пустой ответ от API"
        except (KeyError, IndexError, TypeError) as e:
            return f"Ошибка парсинга ответа: {str(e)}"


class ModelFactory:
    """Фабрика для создания экземпляров моделей."""
    
    @staticmethod
    def create_model(model_data: Dict, db: Database) -> BaseModel:
        """
        Создание экземпляра модели по типу.
        
        Args:
            model_data: Данные модели из БД
            db: Экземпляр базы данных
            
        Returns:
            Экземпляр соответствующего класса модели
        """
        model_type = model_data.get("model_type", "").lower()
        
        if model_type == "openai":
            return OpenAIModel(model_data, db)
        elif model_type == "deepseek":
            return DeepSeekModel(model_data, db)
        elif model_type == "groq":
            return GroqModel(model_data, db)
        elif model_type == "openrouter":
            return OpenRouterModel(model_data, db)
        elif model_type in ["openai-compatible", "olmo", "mistral"]:
            return OpenAICompatibleModel(model_data, db)
        else:
            # По умолчанию используем OpenAI формат
            return OpenAIModel(model_data, db)
    
    @staticmethod
    def get_active_models(db: Database) -> List[BaseModel]:
        """
        Получение списка активных моделей.
        
        Args:
            db: Экземпляр базы данных
            
        Returns:
            Список экземпляров активных моделей
        """
        models_data = db.get_active_models()
        return [ModelFactory.create_model(model_data, db) for model_data in models_data]

