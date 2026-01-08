"""
Скрипт для инициализации базы данных с примерами моделей.
Запустите этот скрипт один раз для создания начальных данных.
"""
from db import Database


def init_sample_models():
    """Добавление примеров моделей в базу данных."""
    db = Database()
    
    # Проверка, есть ли уже модели
    existing_models = db.get_all_models()
    if existing_models:
        print("Модели уже существуют в базе данных.")
        response = input("Хотите добавить примеры моделей? (y/n): ")
        if response.lower() != 'y':
            db.close()
            return
    
    # Получение OPENAI_BASE_URL из переменных окружения
    import os
    from dotenv import load_dotenv
    load_dotenv()
    openai_base_url = os.getenv("OPENAI_BASE_URL", "")
    
    # Примеры моделей
    sample_models = [
        {
            "name": "GPT-4",
            "api_url": "https://api.openai.com/v1/chat/completions",
            "api_id": "OPENAI_API_KEY",
            "model_type": "openai",
            "is_active": 1
        },
        {
            "name": "GPT-3.5-turbo",
            "api_url": "https://api.openai.com/v1/chat/completions",
            "api_id": "OPENAI_API_KEY",
            "model_type": "openai",
            "is_active": 1
        },
        {
            "name": "DeepSeek Chat",
            "api_url": "https://api.deepseek.com/v1/chat/completions",
            "api_id": "DEEPSEEK_API_KEY",
            "model_type": "deepseek",
            "is_active": 1
        },
        {
            "name": "Llama 3 (Groq)",
            "api_url": "https://api.groq.com/openai/v1/chat/completions",
            "api_id": "GROQ_API_KEY",
            "model_type": "groq",
            "is_active": 1
        },
        {
            "name": "openai/gpt-4",
            "api_url": "https://openrouter.ai/api/v1/chat/completions",
            "api_id": "OPENROUTER_API_KEY",
            "model_type": "openrouter",
            "is_active": 1,
            "api_model_name": "openai/gpt-4"
        }
    ]
    
    # Добавление моделей через OPENAI_BASE_URL, если он задан
    if openai_base_url:
        # Убираем trailing slash если есть
        base_url = openai_base_url.rstrip('/')
        # Проверяем, содержит ли базовый URL уже путь /v1 или /openrouter/v1
        if '/v1' in base_url or '/openrouter/v1' in base_url:
            # Если уже есть /v1 или /openrouter/v1, просто добавляем /chat/completions
            api_url_template = f"{base_url}/chat/completions"
        else:
            # Если нет /v1, добавляем полный путь
            api_url_template = f"{base_url}/v1/chat/completions"
        
        openai_compatible_models = [
            {
                "name": "olmo-3.1",
                "api_url": api_url_template,
                "api_id": "OLMO-3.1_API_KEY",
                "model_type": "openai-compatible",
                "is_active": 1
            },
            {
                "name": "mistral",
                "api_url": api_url_template,
                "api_id": "MISTRAL_API_KEY",
                "model_type": "openai-compatible",
                "is_active": 1
            },
            {
                "name": "deepseek",
                "api_url": api_url_template,
                "api_id": "DEEPSEEK_API_KEY",
                "model_type": "openai-compatible",
                "is_active": 1
            }
        ]
        
        print(f"\nДобавление моделей через OPENAI_BASE_URL: {openai_base_url}")
        print("\nИмена моделей можно задать в .env файле:")
        print("  OLMO-3.1_MODEL_NAME=meta-llama/llama-3.1-405b-instruct")
        print("  MISTRAL_MODEL_NAME=mistralai/mistral-medium-3")
        print("  DEEPSEEK_MODEL_NAME=deepseek/deepseek-chat")
        print("\nЕсли переменные не заданы, будут использованы значения по умолчанию.")
        sample_models.extend(openai_compatible_models)
    
    for model in sample_models:
        try:
            db.create_model(
                name=model["name"],
                api_url=model["api_url"],
                api_id=model["api_id"],
                model_type=model["model_type"],
                is_active=model["is_active"],
                api_model_name=model.get("api_model_name")
            )
            print(f"Добавлена модель: {model['name']}")
        except Exception as e:
            print(f"Ошибка при добавлении модели {model['name']}: {str(e)}")
    
    print("\nИнициализация завершена!")
    print("Не забудьте добавить API-ключи в файл .env")
    db.close()


if __name__ == "__main__":
    init_sample_models()

