from pathlib import Path
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
import joblib


csv_spam_path = Path("db") / "data" / "spam.csv"
model_path = Path("ml_models") / "models_data" / "medium_model.joblib"
vectorizer_path = Path("ml_models") / "models_data" / "tfidf_vectorizer.joblib"

# 1. Загрузка данных
df = pd.read_csv(csv_spam_path, encoding="latin-1")[["v1", "v2"]]
df.columns = ["label", "text"]

# 2. Преобразование меток
df["label"] = df["label"].map({"ham": 0, "spam": 1})

# 3. Создание TF-IDF векторизатора
vectorizer = TfidfVectorizer(max_features=5000, stop_words="english")
X = vectorizer.fit_transform(df["text"])
y = df["label"]

# 4. Обучение модели
model = RandomForestClassifier(n_estimators=150, random_state=42)
model.fit(X, y)

# 5. Сохранение артефактов
joblib.dump(model, model_path)
joblib.dump(vectorizer, vectorizer_path)
