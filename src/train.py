import os
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score

def train_and_export_model():
    processed_path = os.path.join("data", "processed", "cleaned_reviews.csv")
    print(f"Loading dataset from {processed_path}...")
    df = pd.read_csv(processed_path)

    df = df.dropna(subset=['text', 'score'])

    X = df['text'].astype(str)
    y = df['score'].astype(int)  # 1 to 5 stars

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("Training balanced 5-star sentiment pipeline...")
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(
            max_features=10000,
            ngram_range=(1, 2),
            stop_words='english',
            sublinear_tf=True
        )),
        ('clf', LogisticRegression(
            max_iter=1000,
            C=1.0,
            class_weight='balanced'  # Fixes majority class 5-star bias
        ))
    ])

    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    print(f"\nAccuracy Score: {accuracy_score(y_test, y_pred):.4f}\n")
    print(classification_report(y_test, y_pred))

    backend_model_dir = os.path.join("backend", "models")
    os.makedirs(backend_model_dir, exist_ok=True)

    joblib_path = os.path.join(backend_model_dir, "sentiment_pipeline.joblib")
    joblib.dump(pipeline, joblib_path)
    print(f"Model saved to: {joblib_path}")

if __name__ == "__main__":
    train_and_export_model()