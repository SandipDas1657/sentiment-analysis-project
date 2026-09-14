import os
import time
import pandas as pd
from google_play_scraper import reviews, Sort

APPS = [
    "com.spotify.music",
    "com.whatsapp",
    "com.netflix.mediaclient",
    "com.instagram.android",
    "com.duolingo",
    "com.twitter.android",
    "com.adobe.reader",
    "com.uber.m3"
]

def fetch_large_dataset(target_per_app: int = 10000):
    raw_dir = os.path.join("data", "raw")
    os.makedirs(raw_dir, exist_ok=True)
    
    all_reviews = []
    
    for app_id in APPS:
        print(f"Fetching {target_per_app} reviews for app: {app_id}...")
        try:
            scraped, _ = reviews(
                app_id,
                lang="en",
                country="us",
                sort=Sort.NEWEST,
                count=target_per_app
            )
            all_reviews.extend(scraped)
            print(f"Successfully collected {len(scraped)} items from {app_id}.")
            time.sleep(1.5)  # Pause to avoid IP rate limits
        except Exception as e:
            print(f"Failed to scrape {app_id}: {e}")
            
    df = pd.DataFrame(all_reviews)
    df = df[['content', 'score']].dropna()
    df.rename(columns={'content': 'text', 'score': 'stars'}, inplace=True)
    
    output_path = os.path.join(raw_dir, "training_reviews.csv")
    df.to_csv(output_path, index=False, encoding="utf-8")
    print(f"\nSaved total dataset of {len(df)} labeled reviews to: {output_path}")

if __name__ == "__main__":
    fetch_large_dataset(target_per_app=10000)