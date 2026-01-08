"""
Модуль для улучшения промтов с помощью AI-моделей.
"""
import asyncio
import json
import re
from typing import Dict, List, Optional, Tuple
from models import BaseModel
from network import NetworkManager


class PromptImprover:
    """Класс для улучшения промтов с помощью AI-моделей."""
    
    # Шаблоны системных промтов для разных сценариев
    SYSTEM_PROMPTS = {
        "general": """Ты - эксперт по формулировке промтов для AI-моделей. Твоя задача - улучшить данный промт, сделав его более четким, конкретным и эффективным.

Верни ответ в следующем JSON-формате:
{
    "improved": "улучшенная версия промта",
    "alternatives": [
        "вариант переформулировки 1",
        "вариант переформулировки 2",
        "вариант переформулировки 3"
    ],
    "adaptations": {
        "coding": "адаптация для задач программирования",
        "analysis": "адаптация для анализа данных",
        "creative": "адаптация для креативных задач"
    }
}

Важно: верни только валидный JSON, без дополнительного текста.""",
        
        "clarity": """Ты - эксперт по формулировке промтов. Улучши данный промт, сделав его максимально понятным и однозначным.

Верни ответ в JSON-формате:
{
    "improved": "улучшенная версия",
    "alternatives": ["вариант 1", "вариант 2", "вариант 3"]
}""",
        
        "coding": """Ты - эксперт по промтам для программирования. Адаптируй данный промт для задач кодирования, сделав его технически точным.

Верни ответ в JSON-формате:
{
    "improved": "адаптированная версия для кодирования",
    "alternatives": ["вариант 1", "вариант 2"]
}""",
        
        "analysis": """Ты - эксперт по промтам для анализа данных. Адаптируй данный промт для задач анализа, добавив конкретные требования к выводу.

Верни ответ в JSON-формате:
{
    "improved": "адаптированная версия для анализа",
    "alternatives": ["вариант 1", "вариант 2"]
}""",
        
        "creative": """Ты - эксперт по креативным промтам. Адаптируй данный промт для творческих задач, добавив детали для вдохновения.

Верни ответ в JSON-формате:
{
    "improved": "адаптированная версия для креативности",
    "alternatives": ["вариант 1", "вариант 2"]
}"""
    }
    
    def __init__(self, network_manager: NetworkManager):
        """
        Инициализация улучшателя промтов.
        
        Args:
            network_manager: Менеджер сетевых запросов
        """
        self.network_manager = network_manager
    
    def _get_system_prompt(self, scenario: str = "general") -> str:
        """
        Получение системного промта для указанного сценария.
        
        Args:
            scenario: Тип сценария (general, clarity, coding, analysis, creative)
            
        Returns:
            Системный промт
        """
        return self.SYSTEM_PROMPTS.get(scenario, self.SYSTEM_PROMPTS["general"])
    
    def _format_improvement_request(self, original_prompt: str, system_prompt: str) -> Dict:
        """
        Форматирование запроса для улучшения промта.
        
        Args:
            original_prompt: Исходный промт
            system_prompt: Системный промт
            
        Returns:
            Словарь с данными для запроса
        """
        return {
            "model": "gpt-4",  # Будет переопределено моделью
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Улучши следующий промт:\n\n{original_prompt}"}
            ],
            "temperature": 0.7
        }
    
    async def improve_prompt_async(
        self, 
        model: BaseModel, 
        original_prompt: str, 
        scenario: str = "general"
    ) -> Dict:
        """
        Асинхронное улучшение промта с помощью указанной модели.
        
        Args:
            model: Модель для улучшения
            original_prompt: Исходный промт
            scenario: Сценарий улучшения (general, clarity, coding, analysis, creative)
            
        Returns:
            Словарь с результатами:
            {
                "success": bool,
                "improved": str,
                "alternatives": List[str],
                "adaptations": Dict[str, str],
                "error": str (если success=False)
            }
        """
        if not original_prompt or not original_prompt.strip():
            return {
                "success": False,
                "error": "Исходный промт не может быть пустым"
            }
        
        if len(original_prompt) > 5000:
            return {
                "success": False,
                "error": "Промт слишком длинный (максимум 5000 символов)"
            }
        
        system_prompt = self._get_system_prompt(scenario)
        
        try:
            # Используем существующий метод NetworkManager для отправки запроса
            # Но нам нужно отправить кастомный запрос с системным промтом
            result = await self._send_custom_request(model, original_prompt, system_prompt)
            
            if not result.get("success"):
                return result
            
            response_text = result.get("response", "")
            if not response_text:
                return {
                    "success": False,
                    "error": "Модель не вернула ответ"
                }
            
            # Парсинг ответа
            parsed = self._parse_response(response_text)
            return parsed
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Ошибка при улучшении промта: {str(e)}"
            }
    
    async def _send_custom_request(
        self, 
        model: BaseModel, 
        user_prompt: str, 
        system_prompt: str
    ) -> Dict:
        """
        Отправка кастомного запроса с системным промтом.
        
        Args:
            model: Модель для запроса
            user_prompt: Пользовательский промт
            system_prompt: Системный промт
            
        Returns:
            Результат запроса
        """
        import aiohttp
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        
        if not model.api_key:
            return {
                "success": False,
                "error": f"API ключ не найден для {model.api_id}"
            }
        
        # Определяем имя модели для API
        if hasattr(model, 'api_model_name') and model.api_model_name:
            api_model_name = model.api_model_name
        elif hasattr(model, 'name'):
            api_model_name = model.name
        else:
            api_model_name = "gpt-4"  # Fallback
        
        request_data = {
            "model": api_model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Улучши следующий промт:\n\n{user_prompt}"}
            ],
            "temperature": 0.7
        }
        
        headers = {
            "Authorization": f"Bearer {model.api_key}",
            "Content-Type": "application/json"
        }
        
        # Дополнительные заголовки для OpenRouter
        if model.model_type.lower() == "openrouter":
            headers["HTTP-Referer"] = "https://github.com/yourusername/chatlist"
            headers["X-Title"] = "ChatList"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    model.api_url,
                    json=request_data,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=self.network_manager.timeout)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"Ошибка запроса ({response.status}): {error_text[:200]}"
                        }
                    
                    response_data = await response.json()
                    response_text = model.parse_response(response_data)
                    
                    return {
                        "success": True,
                        "response": response_text
                    }
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": "Превышено время ожидания ответа"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Ошибка сети: {str(e)}"
            }
    
    def _parse_response(self, response_text: str) -> Dict:
        """
        Парсинг ответа модели для извлечения улучшенного промта и вариантов.
        
        Args:
            response_text: Текст ответа от модели
            
        Returns:
            Словарь с распарсенными данными
        """
        # Пытаемся извлечь JSON из ответа
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        
        if json_match:
            try:
                json_str = json_match.group(0)
                data = json.loads(json_str)
                
                return {
                    "success": True,
                    "improved": data.get("improved", "").strip(),
                    "alternatives": [alt.strip() for alt in data.get("alternatives", []) if alt.strip()],
                    "adaptations": {
                        "coding": data.get("adaptations", {}).get("coding", "").strip(),
                        "analysis": data.get("adaptations", {}).get("analysis", "").strip(),
                        "creative": data.get("adaptations", {}).get("creative", "").strip()
                    }
                }
            except json.JSONDecodeError:
                pass  # Fallback к неструктурированному парсингу
        
        # Fallback: пытаемся извлечь информацию из неструктурированного текста
        return self._parse_unstructured_response(response_text)
    
    def _parse_unstructured_response(self, response_text: str) -> Dict:
        """
        Парсинг неструктурированного ответа (fallback).
        
        Args:
            response_text: Текст ответа
            
        Returns:
            Словарь с распарсенными данными
        """
        # Ищем улучшенную версию
        improved_match = re.search(
            r'(?:улучшенн[ая]*\s*версия|improved|улучшенный):\s*(.+?)(?:\n|$)', 
            response_text, 
            re.IGNORECASE | re.DOTALL
        )
        
        improved = improved_match.group(1).strip() if improved_match else response_text[:500].strip()
        
        # Ищем альтернативные варианты
        alternatives = []
        alt_patterns = [
            r'(?:вариант|alternative|альтернатив[ая]*)\s*\d*:?\s*(.+?)(?:\n|$)',
            r'(?:переформулировка|reformulation):\s*(.+?)(?:\n|$)',
            r'^\d+[\.\)]\s*(.+?)$'
        ]
        
        for pattern in alt_patterns:
            matches = re.findall(pattern, response_text, re.IGNORECASE | re.MULTILINE)
            alternatives.extend([m.strip() for m in matches if m.strip()])
        
        # Ограничиваем количество альтернатив
        alternatives = alternatives[:3]
        
        return {
            "success": True,
            "improved": improved,
            "alternatives": alternatives if alternatives else [improved],
            "adaptations": {
                "coding": "",
                "analysis": "",
                "creative": ""
            }
        }

