from pathlib import Path
from transformers import (
    DistilBertForSequenceClassification,
    DistilBertTokenizerFast,
    Trainer,
    TrainingArguments
)
from datasets import Dataset
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from datasets import DatasetDict


csv_spam_path = Path("db") / "data" / "spam.csv"
model_save_path = Path("ml_models") / "models_data" / "premium_spam_model"


def load_and_prepare_data():
    df = pd.read_csv(csv_spam_path, encoding="latin-1")[["v1", "v2"]]
    df.columns = ["label", "text"]
    df["label"] = df["label"].map({"ham": 0, "spam": 1})
    
    train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)
    
    train_dataset = Dataset.from_pandas(train_df)
    test_dataset = Dataset.from_pandas(test_df)
    
    return DatasetDict({
        "train": train_dataset,
        "test": test_dataset
    })

def tokenize_dataset(dataset, tokenizer):
    return dataset.map(
        lambda x: tokenizer(x["text"], padding="max_length", truncation=True),
        batched=True
    )

def compute_metrics(pred):
    labels = pred.label_ids
    preds = np.argmax(pred.predictions, axis=1)
    return {"accuracy": accuracy_score(labels, preds)}

def train_model():
    dataset = load_and_prepare_data()
    tokenizer = DistilBertTokenizerFast.from_pretrained("distilbert-base-uncased")
    
    tokenized_dataset = dataset.map(
        lambda x: tokenizer(x["text"], padding="max_length", truncation=True),
        batched=True
    )
    
    model = DistilBertForSequenceClassification.from_pretrained(
        "distilbert-base-uncased",
        num_labels=2
    )
    
    training_args = TrainingArguments(
        output_dir=model_save_path,
        num_train_epochs=3,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        eval_strategy="epoch",
        logging_dir=model_save_path / "logs",
        save_strategy="epoch",
        load_best_model_at_end=True
    )
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset["train"],
        eval_dataset=tokenized_dataset["test"],
        compute_metrics=compute_metrics
    )
    
    trainer.train()
    model.save_pretrained(model_save_path)
    tokenizer.save_pretrained(model_save_path)

if __name__ == "__main__":
    train_model()
