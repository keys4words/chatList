"""
Модуль для логирования запросов и ответов.
"""
import logging
import os
from datetime import datetime
from typing import Dict, Optional
from db import Database


class AppLogger:
    """Класс для управления логированием."""
    
    def __init__(self, db: Optional[Database] = None, log_to_file: bool = True):
        """
        Инициализация логгера.
        
        Args:
            db: Экземпляр базы данных (опционально, для сохранения в БД)
            log_to_file: Сохранять ли логи в файл
        """
        self.db = db
        self.log_to_file = log_to_file
        
        # Настройка файлового логирования
        if log_to_file:
            log_dir = "logs"
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            log_file = os.path.join(log_dir, f"chatlist_{datetime.now().strftime('%Y%m%d')}.log")
            
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(log_file, encoding='utf-8'),
                    logging.StreamHandler()
                ]
            )
        else:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[logging.StreamHandler()]
            )
        
        self.logger = logging.getLogger('ChatList')
    
    def log_request(self, prompt: str, model_name: str, success: bool,
                   response: Optional[str] = None, error: Optional[str] = None):
        """
        Логирование запроса к модели.
        
        Args:
            prompt: Текст промта
            model_name: Название модели
            success: Успешность запроса
            response: Текст ответа (если успешно)
            error: Текст ошибки (если неуспешно)
        """
        log_message = f"Запрос к {model_name}: {'Успешно' if success else 'Ошибка'}"
        if error:
            log_message += f" - {error}"
        
        if success:
            self.logger.info(log_message)
            if response:
                self.logger.debug(f"Ответ: {response[:200]}...")  # Первые 200 символов
        else:
            self.logger.error(log_message)
        
        # Сохранение в БД, если доступно
        if self.db:
            try:
                # Можно добавить таблицу logs в БД, если нужно
                # Пока просто логируем в файл
                pass
            except Exception as e:
                self.logger.warning(f"Не удалось сохранить лог в БД: {str(e)}")
    
    def log_batch_request(self, prompt: str, results: list):
        """
        Логирование пакетного запроса.
        
        Args:
            prompt: Текст промта
            results: Список результатов от всех моделей
        """
        success_count = sum(1 for r in results if r.get('success', False))
        total_count = len(results)
        
        self.logger.info(f"Пакетный запрос: {success_count}/{total_count} успешных")
        for result in results:
            self.log_request(
                prompt,
                result.get('model_name', 'Unknown'),
                result.get('success', False),
                result.get('response'),
                result.get('error')
            )

