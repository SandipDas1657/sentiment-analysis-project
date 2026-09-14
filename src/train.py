import os
import re
import pandas as pd
import numpy as np
import joblib
import emoji
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.metrics import classification_report, accuracy_score

nltk.download('vader_lexicon', quiet=True)

class VaderSentimentTransformer(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()
    
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        return np.array([[self.vader.polarity_scores(text)['compound']] for text in X])

def preprocess_text(text: str) -> str:
    """Preprocess text with exact parity to main.py rules."""
    text = str(text)
    text = emoji.demojize(text, delimiters=(" ", " "))
    text = text.replace("_", " ")
    text = re.sub(r'<(script|style|iframe)\b[^>]*>.*?</\1>', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'<[^>]*>', '', text).strip()
    return text

def train_pipeline():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir) if os.path.basename(script_dir) == "src" else script_dir

    data_path = os.path.join(project_root, "data", "processed", "cleaned_reviews.csv")
    output_dir = os.path.join(project_root, "backend", "models")
    output_model_path = os.path.join(output_dir, "sentiment_pipeline.joblib")

    print(f"Loading dataset from: {data_path}")
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Dataset not found at {data_path}. Ensure data processing step is complete.")

    df = pd.read_csv(data_path)
    df = df.dropna(subset=['text', 'score'])

    print("Cleaning and demojizing training text...")
    X = df['text'].apply(preprocess_text)
    y = df['score'].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("Building hybrid pipeline (TF-IDF + VADER compound score)...")
    pipeline = Pipeline([
        ('features', FeatureUnion([
            ('tfidf', TfidfVectorizer(
                max_features=50000,
                ngram_range=(1, 3),
                stop_words=None,  # Retain negations & contrast terms (e.g., 'not', 'but', 'however')
                sublinear_tf=True
            )),
            ('vader', VaderSentimentTransformer())
        ])),
        ('clf', LogisticRegression(
            max_iter=1500,
            C=2.0,
            class_weight='balanced',
            solver='lbfgs'
        ))
    ])

    print("Training model across 1-5 star rating spectrum...")
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\nModel Accuracy: {acc:.4f}\n")
    print("Classification Report:")
    print(classification_report(y_test, y_pred, digits=4))

    os.makedirs(output_dir, exist_ok=True)
    joblib.dump(pipeline, output_model_path)
    print(f"Model saved to: {output_model_path}")

if __name__ == "__main__":
    train_pipeline()