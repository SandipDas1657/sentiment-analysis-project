import os
import re
import joblib
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.app.schemas import SentimentRequest, SentimentResponse

app = FastAPI(title="5-Star Sentiment Analysis API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "sentiment_pipeline.joblib")

# Abusive guardrail words (Force 1-Star)
ABUSIVE_WORDS = {
    'fuck', 'fucking', 'fucker', 'motherfucker', 'shit', 'bitch',
    'asshole', 'bastard', 'cunt', 'dick', 'sucks', 'crap', 'garbage',
    'trash', 'rubbish', 'worst', 'terrible', 'horrible', 'pathetic'
}

# Neutral guardrail words (Force 3-Stars)
NEUTRAL_WORDS = {
    'average', 'avarage', 'ok', 'okay', 'fine', 'decent', 'mediocre',
    'so-so', 'normal', 'fair', 'moderate', 'acceptable'
}

pipeline = None

@app.on_event("startup")
def load_model():
    global pipeline
    if os.path.exists(MODEL_PATH):
        pipeline = joblib.load(MODEL_PATH)

def get_sentiment_label(stars: int) -> str:
    if stars <= 2:
        return "Negative"
    elif stars == 3:
        return "Neutral"
    return "Positive"

@app.post("/predict", response_model=SentimentResponse)
def predict_sentiment(payload: SentimentRequest):
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Model is not loaded.")

    clean_text = payload.text.strip()
    if not clean_text:
        raise HTTPException(status_code=400, detail="Input text cannot be empty.")

    tokens = set(re.findall(r'\b\w+\b', clean_text.lower()))

    # Guardrail 1: Abusive words -> 1-Star Negative
    if tokens.intersection(ABUSIVE_WORDS):
        return SentimentResponse(
            text=clean_text,
            stars=1,
            sentiment="Negative",
            confidence=0.99
        )

    # Guardrail 2: Neutral words (handles typos like 'avarage') -> 3-Star Neutral
    if tokens.intersection(NEUTRAL_WORDS):
        return SentimentResponse(
            text=clean_text,
            stars=3,
            sentiment="Neutral",
            confidence=0.95
        )

    try:
        predicted_stars = int(pipeline.predict([clean_text])[0])
        probabilities = pipeline.predict_proba([clean_text])[0]
        confidence = float(np.max(probabilities))

        # Guardrail 3: Low confidence prediction fallback -> 3-Star Neutral
        if confidence < 0.35:
            return SentimentResponse(
                text=clean_text,
                stars=3,
                sentiment="Neutral",
                confidence=round(confidence, 4)
            )

        return SentimentResponse(
            text=clean_text,
            stars=predicted_stars,
            sentiment=get_sentiment_label(predicted_stars),
            confidence=round(confidence, 4)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))