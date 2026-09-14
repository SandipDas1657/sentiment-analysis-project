import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

TEST_CASES = [
    # 1-Star Cases (Severe Failures, Profanity, Sarcastic Crash/Data Loss)
    ("Fantastic, just lost 3 hours of unsaved work due to another freeze.", 1, "Negative"),
    ("Love opening an app just to watch it crash instantly.", 1, "Negative"),
    ("This update is pure garbage.", 1, "Negative"),
    ("Works great if you enjoy restarting your phone twice a day.", 1, "Negative"),
    ("Would be 5 stars, but exporting files deletes local saved projects.", 1, "Negative"),

    # 2-Star Cases (Regression, Churn, Moderate Complaints, Disappointment, Latency)
    ("Great app, if only it didn't log me out every 5 minutes.", 2, "Negative"),
    ("Loved using this for months, but recent updates introduced way too many bugs.", 2, "Negative"),
    ("Used to be a great tool, but now it's way too slow.", 2, "Negative"),
    ("App is snappy and lightweight, but the lack of cloud sync makes it hard to recommend.", 2, "Negative"),
    ("I wanted to love this, but the battery drain is insane.", 2, "Negative"),
    ("It eventually opens after waiting 3 minutes on the loading screen.", 2, "Negative"),

    # 3-Star Cases (Trade-offs, Neutral Qualifiers, Average Experience)
    ("UI looks clean and navigation is fast, but background playback keeps cutting out.", 3, "Neutral"),
    ("It's not terrible, but definitely not worth $20 a month.", 3, "Neutral"),
    ("Average app, works fine.", 3, "Neutral"),
    ("It does what it says on the tin, nothing more nothing less.", 3, "Neutral"),

    # 4-Star Cases (Positive Negations, Minor Qualifiers)
    ("Not bad at all for a free app.", 4, "Positive"),
    ("Great experience overall, though dark mode needs a bit of polish.", 4, "Positive"),

    # 5-Star Cases (Strong Superlatives, Flawless Feedback)
    ("Outstanding", 5, "Positive"),
    ("Absolutely love this app, works flawlessly!", 5, "Positive"),
    ("Easily the best tool in my workflow, worth every penny.", 5, "Positive"),
]

@pytest.mark.parametrize("text, expected_stars, expected_sentiment", TEST_CASES)
def test_sentiment_predictions(client, text, expected_stars, expected_sentiment):
    response = client.post("/predict", json={"text": text})
    assert response.status_code == 200
    data = response.json()
    assert data["stars"] == expected_stars, f"Failed on text: '{text}'. Expected {expected_stars}, got {data['stars']}"
    assert data["sentiment"] == expected_sentiment