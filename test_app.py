"""
Базовые тесты для проверки функциональности приложения.
"""
import os
import sys
from db import Database
from models import ModelFactory
from export import ExportManager


def test_database():
    """Тестирование работы с базой данных."""
    print("Тестирование базы данных...")
    
    db = Database("test_chatlist.db")
    
    # Тест создания промта
    prompt_id = db.create_prompt("Тестовый промт", "тест")
    assert prompt_id > 0, "Ошибка создания промта"
    print(f"✓ Промт создан с ID: {prompt_id}")
    
    # Тест получения промта
    prompt = db.get_prompt(prompt_id)
    assert prompt is not None, "Ошибка получения промта"
    assert prompt['prompt'] == "Тестовый промт", "Неверный текст промта"
    print("✓ Промт получен корректно")
    
    # Тест поиска промтов
    prompts = db.get_all_prompts(search="Тестовый")
    assert len(prompts) > 0, "Ошибка поиска промтов"
    print("✓ Поиск промтов работает")
    
    # Тест создания модели
    model_id = db.create_model(
        "Test Model",
        "https://api.test.com/v1/chat/completions",
        "TEST_API_KEY",
        "openai",
        1
    )
    assert model_id > 0, "Ошибка создания модели"
    print(f"✓ Модель создана с ID: {model_id}")
    
    # Тест получения активных моделей
    active_models = db.get_active_models()
    assert len(active_models) > 0, "Нет активных моделей"
    print("✓ Получение активных моделей работает")
    
    # Тест создания результата
    result_id = db.create_result(prompt_id, model_id, "Тестовый ответ")
    assert result_id > 0, "Ошибка создания результата"
    print(f"✓ Результат создан с ID: {result_id}")
    
    # Тест получения результатов
    results = db.get_all_results(prompt_id=prompt_id)
    assert len(results) > 0, "Ошибка получения результатов"
    print("✓ Получение результатов работает")
    
    # Очистка тестовой БД
    db.delete_prompt(prompt_id)
    db.delete_model(model_id)
    db.close()
    
    # Удаление тестового файла БД
    if os.path.exists("test_chatlist.db"):
        os.remove("test_chatlist.db")
    
    print("✓ Все тесты базы данных пройдены успешно\n")


def test_models():
    """Тестирование работы с моделями."""
    print("Тестирование модуля моделей...")
    
    db = Database("test_chatlist.db")
    
    # Создание тестовой модели
    model_data = {
        "id": 1,
        "name": "test-model",
        "api_url": "https://api.test.com/v1/chat/completions",
        "api_id": "TEST_API_KEY",
        "is_active": 1,
        "model_type": "openai"
    }
    
    # Тест создания модели через фабрику
    model = ModelFactory.create_model(model_data, db)
    assert model is not None, "Ошибка создания модели"
    assert model.name == "test-model", "Неверное имя модели"
    print("✓ Модель создана через фабрику")
    
    # Тест форматирования запроса
    request = model.format_request("Тестовый промт")
    assert "messages" in request, "Ошибка форматирования запроса"
    assert request["messages"][0]["content"] == "Тестовый промт", "Неверный контент запроса"
    print("✓ Форматирование запроса работает")
    
    db.close()
    if os.path.exists("test_chatlist.db"):
        os.remove("test_chatlist.db")
    
    print("✓ Все тесты моделей пройдены успешно\n")


def test_export():
    """Тестирование экспорта."""
    print("Тестирование экспорта...")
    
    db = Database("test_chatlist.db")
    export_manager = ExportManager(db)
    
    # Тестовые данные
    test_results = [
        {
            "model_name": "Test Model 1",
            "response_text": "Тестовый ответ 1"
        },
        {
            "model_name": "Test Model 2",
            "response_text": "Тестовый ответ 2"
        }
    ]
    
    # Тест экспорта в Markdown
    md_content = export_manager.export_results_to_markdown(test_results, "Тестовый промт")
    assert "# Результаты сравнения моделей" in md_content, "Ошибка экспорта в Markdown"
    assert "Test Model 1" in md_content, "Отсутствует название модели в Markdown"
    print("✓ Экспорт в Markdown работает")
    
    # Тест экспорта в JSON
    json_content = export_manager.export_results_to_json(test_results, "Тестовый промт")
    assert "results" in json_content, "Ошибка экспорта в JSON"
    assert "Test Model 1" in json_content, "Отсутствует название модели в JSON"
    print("✓ Экспорт в JSON работает")
    
    db.close()
    if os.path.exists("test_chatlist.db"):
        os.remove("test_chatlist.db")
    
    print("✓ Все тесты экспорта пройдены успешно\n")


def run_all_tests():
    """Запуск всех тестов."""
    print("=" * 50)
    print("Запуск тестов ChatList")
    print("=" * 50 + "\n")
    
    try:
        test_database()
        test_models()
        test_export()
        
        print("=" * 50)
        print("Все тесты пройдены успешно!")
        print("=" * 50)
        return True
    except AssertionError as e:
        print(f"\n❌ Ошибка теста: {str(e)}")
        return False
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

