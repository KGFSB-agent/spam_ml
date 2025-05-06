from transformers import pipeline, DistilBertForSequenceClassification, DistilBertTokenizer
from pathlib import Path
import torch


class PremiumSpamModel:
    def __init__(self):
        self.cost = 500
        model_path = Path("ml_models") / "models_data" / "premium_spam_model"
        
        self.model = DistilBertForSequenceClassification.from_pretrained(model_path)
        self.tokenizer = DistilBertTokenizer.from_pretrained(model_path)
        self.device = 0 if torch.cuda.is_available() else -1
    
    def predict(self, text: str) -> bool:
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        outputs = self.model(**inputs)
        pred = torch.argmax(outputs.logits).item()
        return bool(pred)  # 1 = спам, 0 = не спам
