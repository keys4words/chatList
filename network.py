"""
Модуль для отправки сетевых запросов к API моделей.
"""
import requests
import asyncio
import aiohttp
from typing import List, Dict, Optional
from datetime import datetime
from models import BaseModel


class NetworkManager:
    """Класс для управления сетевыми запросами."""
    
    def __init__(self, timeout: Optional[int] = None, retry_on_429: bool = True, max_retries: int = 3):
        """
        Инициализация менеджера сетевых запросов.
        
        Args:
            timeout: Таймаут для запросов в секундах (если None, берется из настроек или 120 по умолчанию)
            retry_on_429: Автоматически повторять запросы при ошибке 429
            max_retries: Максимальное количество повторных попыток
        """
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        if timeout is None:
            # Пытаемся получить таймаут из .env
            env_timeout = os.getenv("REQUEST_TIMEOUT")
            if env_timeout:
                try:
                    self.timeout = int(env_timeout)
                except ValueError:
                    self.timeout = 120  # По умолчанию 120 секунд
            else:
                self.timeout = 120  # По умолчанию 120 секунд (увеличено с 30)
        else:
            self.timeout = timeout
        
        self.retry_on_429 = retry_on_429
        self.max_retries = max_retries
        self.session = None
    
    async def _create_session(self):
        """Создание aiohttp сессии."""
        if self.session is None:
            self.session = aiohttp.ClientSession()
    
    async def _close_session(self):
        """Закрытие aiohttp сессии."""
        if self.session:
            await self.session.close()
            self.session = None
    
    def send_request_sync(self, model: BaseModel, prompt: str) -> Dict:
        """
        Синхронная отправка запроса к API модели.
        
        Args:
            model: Экземпляр модели
            prompt: Текст промта
            
        Returns:
            Словарь с результатом: {"success": bool, "model_name": str, "response": str, "error": str}
        """
        if not model.api_key:
            return {
                "success": False,
                "model_name": model.name,
                "response": "",
                "error": f"API ключ не найден для {model.api_id}"
            }
        
        try:
            request_data = model.format_request(prompt)
            headers = {
                "Authorization": f"Bearer {model.api_key}",
                "Content-Type": "application/json"
            }
            
            # Дополнительные заголовки для OpenRouter (опционально)
            if model.model_type.lower() == "openrouter":
                headers["HTTP-Referer"] = "https://github.com/yourusername/chatlist"
                headers["X-Title"] = "ChatList"
            
            response = requests.post(
                model.api_url,
                json=request_data,
                headers=headers,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            try:
                response_data = response.json()
            except Exception as e:
                return {
                    "success": False,
                    "model_name": model.name,
                    "response": "",
                    "error": f"Ошибка парсинга JSON ответа: {str(e)}"
                }
            
            if response_data is None:
                return {
                    "success": False,
                    "model_name": model.name,
                    "response": "",
                    "error": "Ответ от API пустой (None)"
                }
            
            response_text = model.parse_response(response_data)
            
            return {
                "success": True,
                "model_name": model.name,
                "response": response_text,
                "error": None
            }
            
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "model_name": model.name,
                "response": "",
                "error": "Таймаут запроса"
            }
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            # Улучшенная обработка ошибок HTTP
            if hasattr(e, 'response') and e.response is not None:
                status_code = e.response.status_code
                
                # Пытаемся извлечь детальное сообщение об ошибке из JSON
                error_detail = None
                try:
                    error_json = e.response.json()
                    if isinstance(error_json, dict):
                        if "error" in error_json:
                            if isinstance(error_json["error"], dict) and "message" in error_json["error"]:
                                error_detail = error_json["error"]["message"]
                            elif isinstance(error_json["error"], str):
                                error_detail = error_json["error"]
                        elif "message" in error_json:
                            error_detail = error_json["message"]
                except:
                    pass  # Если не удалось распарсить, используем общее сообщение
                
                if status_code == 400:
                    if error_detail:
                        error_msg = f"400 Bad Request - {error_detail}. Проверьте правильность имени модели '{model.name}' в настройках."
                    else:
                        error_msg = f"400 Bad Request - Некорректный запрос. Проверьте правильность имени модели '{model.name}' и параметров запроса."
                elif status_code == 404:
                    if error_detail:
                        error_msg = f"404 Not Found - {error_detail}. Модель '{model.name}' не найдена."
                    else:
                        error_msg = f"404 Not Found - Модель '{model.name}' не найдена. Проверьте правильность имени модели в настройках."
                elif status_code == 401:
                    error_msg = f"401 Unauthorized - Неверный API ключ для {model.api_id}"
                elif status_code == 402:
                    error_msg = f"402 Payment Required - Недостаточно средств на счету"
                elif status_code == 429:
                    error_msg = f"429 Too Many Requests - Превышен лимит запросов"
                else:
                    if error_detail:
                        error_msg = f"Ошибка запроса ({status_code}): {error_detail}"
                    else:
                        error_msg = f"Ошибка запроса ({status_code}): {str(e)}"
            else:
                error_msg = f"Ошибка запроса: {str(e)}"
            
            return {
                "success": False,
                "model_name": model.name,
                "response": "",
                "error": error_msg
            }
        except Exception as e:
            return {
                "success": False,
                "model_name": model.name,
                "response": "",
                "error": f"Неожиданная ошибка: {str(e)}"
            }
    
    async def send_request_async(self, model: BaseModel, prompt: str, retry_count: int = 0) -> Dict:
        """
        Асинхронная отправка запроса к API модели с поддержкой повторных попыток.
        
        Args:
            model: Экземпляр модели
            prompt: Текст промта
            retry_count: Текущее количество попыток
            
        Returns:
            Словарь с результатом
        """
        if not model.api_key:
            return {
                "success": False,
                "model_name": model.name,
                "response": "",
                "error": f"API ключ не найден для {model.api_id}"
            }
        
        await self._create_session()
        
        try:
            request_data = model.format_request(prompt)
            headers = {
                "Authorization": f"Bearer {model.api_key}",
                "Content-Type": "application/json"
            }
            
            # Дополнительные заголовки для OpenRouter (опционально)
            if model.model_type.lower() == "openrouter":
                headers["HTTP-Referer"] = "https://github.com/yourusername/chatlist"
                headers["X-Title"] = "ChatList"
            
            async with self.session.post(
                model.api_url,
                json=request_data,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                # Проверка статуса перед парсингом
                if response.status != 200:
                    error_text = await response.text()
                    status_code = response.status
                    
                    # Обработка ошибки 429 с повторной попыткой
                    if status_code == 429 and self.retry_on_429 and retry_count < self.max_retries:
                        # Экспоненциальная задержка: 2^retry_count секунд
                        delay = 2 ** retry_count
                        await asyncio.sleep(delay)
                        # Повторная попытка
                        return await self.send_request_async(model, prompt, retry_count + 1)
                    
                    # Пытаемся распарсить JSON ошибки для более детального сообщения
                    error_detail = None
                    try:
                        import json
                        error_json = json.loads(error_text)
                        if isinstance(error_json, dict):
                            if "error" in error_json:
                                if isinstance(error_json["error"], dict) and "message" in error_json["error"]:
                                    error_detail = error_json["error"]["message"]
                                elif isinstance(error_json["error"], str):
                                    error_detail = error_json["error"]
                            elif "message" in error_json:
                                error_detail = error_json["message"]
                    except:
                        pass  # Если не удалось распарсить, используем общее сообщение
                    
                    if status_code == 400:
                        if error_detail:
                            error_msg = f"400 Bad Request - {error_detail}. Проверьте правильность имени модели '{model.name}' в настройках."
                        else:
                            error_msg = f"400 Bad Request - Некорректный запрос. Проверьте правильность имени модели '{model.name}' и параметров запроса."
                    elif status_code == 404:
                        if error_detail:
                            error_msg = f"404 Not Found - {error_detail}. Модель '{model.name}' не найдена."
                        else:
                            error_msg = f"404 Not Found - Модель '{model.name}' не найдена. Проверьте правильность имени модели в настройках."
                    elif status_code == 401:
                        error_msg = f"401 Unauthorized - Неверный API ключ для {model.api_id}"
                    elif status_code == 402:
                        error_msg = f"402 Payment Required - Недостаточно средств на счету"
                    elif status_code == 429:
                        error_msg = f"429 Too Many Requests - Превышен лимит запросов (попыток: {retry_count + 1})"
                    else:
                        if error_detail:
                            error_msg = f"Ошибка запроса ({status_code}): {error_detail}"
                        else:
                            error_msg = f"Ошибка запроса ({status_code}): {error_text[:200]}"
                    
                    return {
                        "success": False,
                        "model_name": model.name,
                        "response": "",
                        "error": error_msg
                    }
                
                try:
                    response_data = await response.json()
                except Exception as e:
                    return {
                        "success": False,
                        "model_name": model.name,
                        "response": "",
                        "error": f"Ошибка парсинга JSON ответа: {str(e)}"
                    }
                
                if response_data is None:
                    return {
                        "success": False,
                        "model_name": model.name,
                        "response": "",
                        "error": "Ответ от API пустой (None)"
                    }
                
                response_text = model.parse_response(response_data)
                
                return {
                    "success": True,
                    "model_name": model.name,
                    "response": response_text,
                    "error": None
                }
                
        except asyncio.TimeoutError:
            return {
                "success": False,
                "model_name": model.name,
                "response": "",
                "error": "Таймаут запроса"
            }
        except aiohttp.ClientError as e:
            error_msg = str(e)
            # Улучшенная обработка ошибок HTTP для асинхронных запросов
            if hasattr(e, 'status'):
                status_code = e.status
                if status_code == 404:
                    error_msg = f"404 Not Found - Модель '{model.name}' не найдена. Проверьте правильность имени модели в настройках."
                elif status_code == 401:
                    error_msg = f"401 Unauthorized - Неверный API ключ для {model.api_id}"
                elif status_code == 402:
                    error_msg = f"402 Payment Required - Недостаточно средств на счету"
                elif status_code == 429:
                    error_msg = f"429 Too Many Requests - Превышен лимит запросов"
                else:
                    error_msg = f"Ошибка запроса ({status_code}): {str(e)}"
            else:
                error_msg = f"Ошибка запроса: {str(e)}"
            
            return {
                "success": False,
                "model_name": model.name,
                "response": "",
                "error": error_msg
            }
        except Exception as e:
            return {
                "success": False,
                "model_name": model.name,
                "response": "",
                "error": f"Неожиданная ошибка: {str(e)}"
            }
    
    async def send_to_all_models_async(self, models: List[BaseModel], prompt: str, delay_between_requests: float = 0.0) -> List[Dict]:
        """
        Асинхронная отправка промта во все модели с возможной задержкой между запросами.
        
        Args:
            models: Список экземпляров моделей
            prompt: Текст промта
            delay_between_requests: Задержка между запросами в секундах (для избежания rate limiting)
            
        Returns:
            Список результатов от всех моделей
        """
        async def send_with_delay(model, delay):
            """Отправка запроса с задержкой."""
            if delay > 0:
                await asyncio.sleep(delay)
            return await self.send_request_async(model, prompt)
        
        # Создаем задачи с задержками
        tasks = []
        for i, model in enumerate(models):
            delay = i * delay_between_requests if delay_between_requests > 0 else 0
            tasks.append(send_with_delay(model, delay))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Обработка исключений
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "success": False,
                    "model_name": models[i].name,
                    "response": "",
                    "error": f"Исключение: {str(result)}"
                })
            else:
                processed_results.append(result)
        
        await self._close_session()
        return processed_results
    
    def send_to_all_models_sync(self, models: List[BaseModel], prompt: str) -> List[Dict]:
        """
        Синхронная отправка промта во все модели (для совместимости).
        
        Args:
            models: Список экземпляров моделей
            prompt: Текст промта
            
        Returns:
            Список результатов от всех моделей
        """
        results = []
        for model in models:
            result = self.send_request_sync(model, prompt)
            results.append(result)
        return results


class TemporaryResults:
    """Класс для работы с временной таблицей результатов (в памяти)."""
    
    def __init__(self):
        """Инициализация временной таблицы."""
        self.results: List[Dict] = []
    
    def clear(self):
        """Очистка временной таблицы."""
        self.results = []
    
    def add_result(self, model_name: str, response_text: str, error: Optional[str] = None):
        """
        Добавление результата во временную таблицу.
        
        Args:
            model_name: Название модели
            response_text: Текст ответа
            error: Текст ошибки (если есть)
        """
        result = {
            "model_name": model_name,
            "response_text": response_text if not error else f"Ошибка: {error}",
            "selected": False,
            "error": error
        }
        self.results.append(result)
    
    def update_from_network_results(self, network_results: List[Dict]):
        """
        Обновление временной таблицы из результатов сетевых запросов.
        
        Args:
            network_results: Список результатов от NetworkManager
        """
        self.clear()
        for result in network_results:
            if result["success"]:
                self.add_result(result["model_name"], result["response"])
            else:
                self.add_result(result["model_name"], "", result["error"])
    
    def get_selected_results(self) -> List[Dict]:
        """Получение выбранных результатов."""
        return [r for r in self.results if r.get("selected", False)]
    
    def toggle_selection(self, index: int):
        """Переключение выбора результата по индексу."""
        if 0 <= index < len(self.results):
            self.results[index]["selected"] = not self.results[index].get("selected", False)
    
    def get_all_results(self) -> List[Dict]:
        """Получение всех результатов."""
        return self.results

