"""
Модуль для экспорта данных в различные форматы.
"""
import json
from datetime import datetime
from typing import List, Dict, Optional
from db import Database


class ExportManager:
    """Класс для управления экспортом данных."""
    
    def __init__(self, db: Database):
        """
        Инициализация менеджера экспорта.
        
        Args:
            db: Экземпляр базы данных
        """
        self.db = db
    
    def export_results_to_markdown(self, results: List[Dict], 
                                   prompt_text: Optional[str] = None,
                                   include_metadata: bool = True) -> str:
        """
        Экспорт результатов в Markdown формат.
        
        Args:
            results: Список результатов для экспорта
            prompt_text: Текст промта (опционально)
            include_metadata: Включать ли метаданные
            
        Returns:
            Строка в формате Markdown
        """
        md_lines = []
        
        if include_metadata:
            md_lines.append("# Результаты сравнения моделей\n")
            md_lines.append(f"**Дата экспорта:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            if prompt_text:
                md_lines.append(f"**Промт:** {prompt_text}\n")
            md_lines.append("\n---\n\n")
        
        for i, result in enumerate(results, 1):
            model_name = result.get('model_name', 'Неизвестная модель')
            response_text = result.get('response_text', '')
            
            md_lines.append(f"## {i}. {model_name}\n\n")
            md_lines.append(f"{response_text}\n\n")
            md_lines.append("---\n\n")
        
        return "".join(md_lines)
    
    def export_results_to_json(self, results: List[Dict],
                              prompt_text: Optional[str] = None,
                              include_metadata: bool = True) -> str:
        """
        Экспорт результатов в JSON формат.
        
        Args:
            results: Список результатов для экспорта
            prompt_text: Текст промта (опционально)
            include_metadata: Включать ли метаданные
            
        Returns:
            JSON строка
        """
        export_data = {}
        
        if include_metadata:
            export_data['metadata'] = {
                'export_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'prompt': prompt_text,
                'results_count': len(results)
            }
        
        export_data['results'] = results
        
        return json.dumps(export_data, ensure_ascii=False, indent=2)
    
    def export_saved_results(self, prompt_id: Optional[int] = None,
                             model_id: Optional[int] = None,
                             format: str = "markdown") -> str:
        """
        Экспорт сохраненных результатов из БД.
        
        Args:
            prompt_id: ID промта (если None - все промты)
            model_id: ID модели (если None - все модели)
            format: Формат экспорта (markdown или json)
            
        Returns:
            Экспортированные данные в выбранном формате
        """
        results = self.db.get_all_results(prompt_id=prompt_id, model_id=model_id)
        
        # Получение информации о моделях и промтах
        models = {m['id']: m['name'] for m in self.db.get_all_models()}
        prompts = {p['id']: p for p in self.db.get_all_prompts()}
        
        # Форматирование результатов для экспорта
        export_results = []
        for result in results:
            prompt_data = prompts.get(result['prompt_id'], {})
            model_name = models.get(result['model_id'], 'Неизвестная модель')
            
            export_results.append({
                'model_name': model_name,
                'response_text': result['response_text'],
                'prompt': prompt_data.get('prompt', ''),
                'saved_date': result['saved_date'],
                'tags': prompt_data.get('tags', '')
            })
        
        prompt_text = prompts.get(prompt_id, {}).get('prompt') if prompt_id else None
        
        if format.lower() == "json":
            return self.export_results_to_json(export_results, prompt_text)
        else:
            return self.export_results_to_markdown(export_results, prompt_text)

