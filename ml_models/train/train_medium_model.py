from pathlib import Path
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib


csv_spam_path = Path("db") / "data" / "spam.csv"
model_path = Path("ml_models") / "models_data" / "medium_model.joblib"
vectorizer_path = Path("ml_models") / "models_data" / "tfidf_vectorizer.joblib"

df = pd.read_csv(csv_spam_path, encoding="latin-1")[["v1", "v2"]]
df.columns = ["label", "text"]

df["label"] = df["label"].map({"ham": 0, "spam": 1})

vectorizer = TfidfVectorizer(max_features=5000, stop_words="english")
X = vectorizer.fit_transform(df["text"])
y = df["label"]

model = RandomForestClassifier(n_estimators=150, random_state=42)
model.fit(X, y)

joblib.dump(model, model_path)
joblib.dump(vectorizer, vectorizer_path)
