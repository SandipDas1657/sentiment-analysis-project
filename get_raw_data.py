import os
import json
import pandas as pd
from google_play_scraper import reviews, Sort

def fetch_and_save_raw_data(app_id: str = "com.spotify.music", count: int = 2000):
    # Ensure raw directory exists
    raw_dir = os.path.join("data", "raw")
    os.makedirs(raw_dir, exist_ok=True)

    print(f"Fetching {count} raw reviews for app: {app_id}...")
    
    # Extract raw data stream
    scraped_data, _ = reviews(
        app_id,
        lang="en",
        country="us",
        sort=Sort.NEWEST,
        count=count
    )

    # Save as raw JSON payload
    json_path = os.path.join(raw_dir, "raw_reviews.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(scraped_data, f, indent=4, default=str)

    # Save as raw CSV
    csv_path = os.path.join(raw_dir, "raw_reviews.csv")
    df = pd.DataFrame(scraped_data)
    df.to_csv(csv_path, index=False)

    print(f"Saved {len(scraped_data)} raw records to:")
    print(f" - {json_path}")
    print(f" - {csv_path}")

if __name__ == "__main__":
    fetch_and_save_raw_data()