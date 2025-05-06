import joblib
from pathlib import Path


class MediumSpamModel:
    def __init__(self):
        self.cost = 250  # Стоимость 250 кредитов
        model_path = Path("ml_models") / "models_data" / "medium_model.joblib"
        vectorizer_path = Path("ml_models") / "models_data" / "tfidf_vectorizer.joblib"

        # Проверка существования файлов
        if not (model_path.exists() and vectorizer_path.exists()):
            raise FileNotFoundError("Model artifacts not found. Train the model first!")
        
        self.model = joblib.load(model_path)
        self.vectorizer = joblib.load(vectorizer_path)
    
    def predict(self, text: str) -> bool:
        X = self.vectorizer.transform([text])
        prediction = self.model.predict(X)[0]
        return bool(prediction)  # Явное преобразование в bool
