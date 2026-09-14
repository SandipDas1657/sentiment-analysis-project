import os
import re
import pandas as pd

def redact_pii(text: str) -> str:
    """Strips emails and phone numbers from review text."""
    if not isinstance(text, str):
        return ""
    text = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[REDACTED_EMAIL]', text)
    text = re.sub(r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b', '[REDACTED_PHONE]', text)
    return text.strip()

def map_score_to_sentiment(score: int) -> str:
    """Maps 1-5 rating scores to 3-class sentiment labels."""
    if score <= 2:
        return "Negative"
    elif score == 3:
        return "Neutral"
    else:
        return "Positive"

def process_raw_reviews():
    raw_path = os.path.join("data", "raw", "training_reviews.csv")
    processed_dir = os.path.join("data", "processed")
    os.makedirs(processed_dir, exist_ok=True)

    print(f"Loading raw data from {raw_path}...")
    df = pd.read_csv(raw_path)

    text_col = 'content' if 'content' in df.columns else ('text' if 'text' in df.columns else None)
    score_col = 'score' if 'score' in df.columns else ('stars' if 'stars' in df.columns else None)

    if not text_col or not score_col:
        raise KeyError(f"Missing required text or score columns. Available columns: {list(df.columns)}")

    df['review_id'] = df['reviewId'] if 'reviewId' in df.columns else range(1, len(df) + 1)
    df['text'] = df[text_col]
    df['score'] = df[score_col].astype(int)
    df['timestamp'] = df['at'] if 'at' in df.columns else None

    df = df[['review_id', 'text', 'score', 'timestamp']].copy()
    df.dropna(subset=['text'], inplace=True)

    print("Scrubbing PII from review text...")
    df['text'] = df['text'].apply(redact_pii)
    df['sentiment'] = df['score'].apply(map_score_to_sentiment)

    output_csv = os.path.join(processed_dir, "cleaned_reviews.csv")
    output_parquet = os.path.join(processed_dir, "cleaned_reviews.parquet")

    df.to_csv(output_csv, index=False)
    print(f"Saved CSV records to: {output_csv}")

    try:
        df.to_parquet(output_parquet, index=False)
        print(f"Saved Parquet export to: {output_parquet}")
    except ImportError:
        print("Skipped Parquet output (install 'pyarrow' to enable Parquet exports).")

    print(f"Processing complete! Cleaned {len(df)} total records.")

if __name__ == "__main__":
    process_raw_reviews()