import os
from dotenv import load_dotenv
import google.generativeai as genai

# Загружаем переменные из .env файла
load_dotenv()

# Получаем API ключ
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY не найден в .env файле")

# Конфигурируем API
genai.configure(api_key=api_key)

def list_available_models():
    """Выводит список доступных моделей"""
    print("Доступные модели:")
    for model in genai.list_models():
        if "generateContent" in model.supported_generation_methods:
            print(f"  - {model.name}")

# Получаем первую доступную модель
available_models = [m for m in genai.list_models() if "generateContent" in m.supported_generation_methods]
if not available_models:
    raise ValueError("Нет доступных моделей для generateContent")

model = genai.GenerativeModel(available_models[0].name)
print(f"Используется модель: {available_models[0].name}\n")

def ask_gemini(question: str) -> str:
    """Отправляет вопрос в Gemini и возвращает ответ"""
    response = model.generate_content(question)
    return response.text

if __name__ == "__main__":
    # Пример использования
    question = "Как я могу использовать Gemini API в своём коде?"
    print(f"Вопрос: {question}")
    print(f"Ответ: {ask_gemini(question)}")
