import os
import re
import pandas as pd

def redact_pii(text: str) -> str:
    """Strips emails and phone numbers from review text."""
    if not isinstance(text, str):
        return ""
    # Redact email addresses
    text = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[REDACTED_EMAIL]', text)
    # Redact phone numbers
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
    raw_path = os.path.join("data", "raw", "raw_reviews.csv")
    processed_dir = os.path.join("data", "processed")
    os.makedirs(processed_dir, exist_ok=True)

    print(f"Loading raw data from {raw_path}...")
    df = pd.read_csv(raw_path)

    # Select core columns
    df = df[['reviewId', 'content', 'score', 'at']].copy()
    df.rename(columns={'reviewId': 'review_id', 'content': 'text', 'at': 'timestamp'}, inplace=True)

    # Drop missing review text
    df.dropna(subset=['text'], inplace=True)

    # Redact PII
    print("Scrubbing PII from review text...")
    df['text'] = df['text'].apply(redact_pii)

    # Assign sentiment target variable
    df['sentiment'] = df['score'].apply(map_score_to_sentiment)

    # Save clean dataset
    output_csv = os.path.join(processed_dir, "cleaned_reviews.csv")
    output_parquet = os.path.join(processed_dir, "cleaned_reviews.parquet")

    df.to_csv(output_csv, index=False)
    df.to_parquet(output_parquet, index=False)

    print(f"Processing complete! Saved {len(df)} cleaned records to:")
    print(f" - {output_csv}")
    print(f" - {output_parquet}")

if __name__ == "__main__":
    process_raw_reviews()