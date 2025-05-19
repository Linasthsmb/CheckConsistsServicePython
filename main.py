from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict
import pytesseract
from PIL import Image
import io
import spacy
import re

app = FastAPI()
nlp = spacy.load("en_core_web_sm")

bad_patterns = {
    "silicones": [
        r"\w*cone\b", r"dimethi", r"\bsil", r"siloxane", r"silsesquioxane", r"silylate",
        r"botanisil", r"microsil"
    ],
    "waxes": [
        r"\bcera", r"\bcire", r"wax", r"petroleum", r"petrolatum", r"paraffin", r"mineral jelly"
    ],
    "sulfates": [
        r"\bsulfate\b", r"\bsulphate\b"
    ],
    "alcohols": [
        r"\balcohol\b", r"ethyl alcohol", r"isopropyl alcohol", r"propyl alcohol",
        r"sd alcohol", r"isopropanol", r"2-propanol"
    ],
    "soap": [
        r"saponified", r"soap", r"sodium palm", r"sodium carboxylate"
    ]
}

# Пояснения для категорий
category_reasons = {
    "silicones": "может накапливаться на волосах и требовать сильных шампуней для удаления",
    "waxes": "оставляют плёнку и тяжело смываются без сульфатов",
    "sulfates": "могут сушить волосы и кожу головы",
    "alcohols": "могут сушить волосы, особенно в больших количествах",
    "soap": "может вызывать накопление и пересушивать волосы, особенно в жёсткой воде"
}

exceptions = {
    "silicones": [
        "peg-12 dimethicone", "peg/ppg-18/18 dimethicone"
    ],
    "waxes": [
        "peg-8 beeswax", "emulsifying wax"
    ],
    "sulfates": [
        "behentrimonium methosulfate"
    ],
    "alcohols": [
        "cetyl alcohol", "stearyl alcohol", "cetearyl alcohol", "oleyl alcohol",
        "lauryl alcohol", "myristyl alcohol", "isostearyl alcohol", "lanolin alcohol",
        "tridecyl alcohol", "decyl alcohol", "coconut alcohol", "jojoba alcohol",
        "hydrogenated rapeseed alcohol"
    ]
}

def clean_text(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9\s\-\/]", " ", text.lower())

def extract_bad_ingredients_nlp(text: str) -> List[Dict[str, str]]:
    doc = nlp(clean_text(text))
    found = []

    for token in doc:
        word = token.text.lower()
        for category, patterns in bad_patterns.items():
            for pattern in patterns:
                if re.search(pattern, word):
                    is_exception = any(ex in word for ex in exceptions.get(category, []))
                    if not is_exception:
                        reason = category_reasons.get(category, "нежелательный ингредиент")
                        found.append({
                            "ingredient": word,
                            "category": category,
                            "reason": reason
                        })
    return found

@app.post("/analyze")
async def analyze(file: Optional[UploadFile] = File(None), text: Optional[str] = Form(None)):
    try:
        raw_text = ""

        if file:
            image_bytes = await file.read()
            image = Image.open(io.BytesIO(image_bytes))
            raw_text = pytesseract.image_to_string(image, lang='eng')

        if text:
            raw_text += f"\n{text}"

        if not raw_text.strip():
            return JSONResponse(content={"error": "Нет текста для анализа"}, status_code=400)

        bad_ingredients = extract_bad_ingredients_nlp(raw_text)

        if not bad_ingredients:
            return {
                "result": "Состав отличный!💚"
            }

        return {
            "result": "Некоторые ингредиенты могут не подойти",
            "issues": bad_ingredients,
        }

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    import numpy as np
    import random
    import math

    # Целевая функция (например, среднеквадратичная ошибка)
    # Здесь используется тестовая функция. Замените на вашу.
    def objective_function(x):
        # Пример: простая параболическая функция
        return (x[0] - 3) ** 2 + (x[1] + 1) ** 2

    # Генерация нового состояния в окрестности текущего
    def neighbor(current_state, step_size=0.1):
        return [x + random.uniform(-step_size, step_size) for x in current_state]

    # Имитация отжига
    def simulated_annealing(
            objective_function,
            initial_state,
            initial_temp=1000,
            cooling_rate=0.95,
            temp_min=1e-6,
            max_iter=1000,
            step_size=0.1
    ):
        current_state = initial_state
        current_value = objective_function(current_state)

        best_state = list(current_state)
        best_value = current_value

        temp = initial_temp
        iteration = 0

        while temp > temp_min and iteration < max_iter:
            new_state = neighbor(current_state, step_size)
            new_value = objective_function(new_state)

            delta = new_value - current_value

            if delta < 0 or random.random() < math.exp(-delta / temp):
                current_state = new_state
                current_value = new_value

                if current_value < best_value:
                    best_state = list(current_state)
                    best_value = current_value

            temp *= cooling_rate
            iteration += 1

        return best_state, best_value

    # Пример использования
    initial_state = [random.uniform(-10, 10), random.uniform(-10, 10)]
    best_solution, best_score = simulated_annealing(objective_function, initial_state)

    print("Лучшее найденное решение:", best_solution)
    print("Значение целевой функции:", best_score)

