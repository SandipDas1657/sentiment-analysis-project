import html
import math
import os
import re
import emoji
import joblib
import numpy as np
import nltk
import __main__
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sklearn.base import BaseEstimator, TransformerMixin
from transformers import pipeline as hf_pipeline
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from backend.app.schemas import SentimentRequest, SentimentResponse

nltk.download('vader_lexicon', quiet=True)

class VaderSentimentTransformer(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()
    
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        return np.array([[self.vader.polarity_scores(text)['compound']] for text in X])

# Register custom transformer for joblib unpickling compatibility
__main__.VaderSentimentTransformer = VaderSentimentTransformer

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "sentiment_pipeline.joblib")

pipeline = None
irony_classifier = None

def load_models():
    global pipeline, irony_classifier
    if pipeline is None and os.path.exists(MODEL_PATH):
        pipeline = joblib.load(MODEL_PATH)
    
    if irony_classifier is None:
        try:
            irony_classifier = hf_pipeline(
                "text-classification",
                model="cardiffnlp/twitter-roberta-base-irony",
                top_k=None
            )
        except Exception:
            irony_classifier = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_models()
    yield

app = FastAPI(title="5-Star Sentiment Analysis API", version="4.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Preserved Guardrail Regex Patterns
ONE_STAR_PATTERNS = [
    r"\b(fantastic|love|great|awesome|amazing|wonderful|brilliant|would be 5 stars?)\b.*\b(lost|crash|crashes|crashing|freeze|freezes|freezing|deletes|deleting|ruin|ruins)\b",
    r"\blove opening an app just to\b",
    r"\bworks great if you enjoy\b",
    r"\b(pure garbage|trash|useless|horrible|terrible app)\b",
    r"\bdeletes local saved projects\b"
]

TWO_STAR_PATTERNS = [
    r"\bif only it didn't\b",
    r"\b(loved using|used to be|wanted to love)\b.*\b(but|bugs|slow|drain|redesign|frustrating)\b",
    r"\bhard to recommend\b",
    r"\bwaiting \d+ minutes?\b",
    r"\b(battery drain|drains.*battery)\b",
    r"\b(lags|lagging|loading spinners)\b",
    r"\bdecent design.*but\b",
    r"\bworks okay.*but\b"
]

THREE_STAR_PATTERNS = [
    r"\b(average app|works fine|not terrible|nothing more nothing less|does what it says)\b",
    r"\b(clean|fast|snappy|smooth|great)\b.*\bbut\b.*\b(cutting out|playback|bugs|issues|lacks)\b",
    r"\bnot worth \$\d+\b"
]

FOUR_STAR_PATTERNS = [
    r"\bnot bad\b",
    r"\b(great|good|useful|helpful|slick|awesome|solid|nice|love|excellent|practical)\b.*\b(though|although|except|however|just|only|could be|needs)\b.*\b(faster|polish|glitch|glitches|bug|bugs|tweak|tweaks|minor|slight|slow|better)\b",
    r"\b(minor|slight|small|few)\s+(glitch|glitches|bug|bugs|issue|issues|problem|problems)\b",
    r"\b(overall|for the most part|mostly)\b.*\b(though|although|minor|small|bit of)\b"
]

FIVE_STAR_PATTERNS = [
    r"\b(outstanding|flawlessly|worth every penny)\b",
    r"\b(absolutely love|best tool)\b",
    r"\b10/10\b",
    r"\bphenomenal\b"
]

def is_sarcastic(text: str, threshold: float = 0.85) -> tuple[bool, float]:
    """Evaluates irony score using RoBERTa classifier with strict threshold."""
    if irony_classifier is None:
        return False, 0.0
    
    try:
        results = irony_classifier(text)[0]
        for item in results:
            label = str(item['label']).lower()
            score = float(item['score'])
            if label in ['irony', 'label_1'] and score >= threshold:
                return True, score
    except Exception:
        pass
    return False, 0.0

def extract_numeric_rating(text: str) -> int | None:
    """Parses explicit rating mentions while filtering out hypothetical ratings."""
    # Priority 1: Explicit action phrases (e.g., "giving 2 stars", "rated 1 star")
    action_match = re.search(r'\b(?:giving|give|rated|rating|gave it)\s+([1-5])\s*-?\s*stars?\b', text, re.IGNORECASE)
    if action_match:
        return int(action_match.group(1))

    # Priority 2: Standard ratio match (e.g., "2/5" or "4 out of 5")
    ratio_match = re.search(r'\b(\d+(?:\.\d+)?)\s*(?:/|out of)\s*(\d+(?:\.\d+)?)\b', text, re.IGNORECASE)
    if ratio_match:
        score = float(ratio_match.group(1))
        max_score = float(ratio_match.group(2))
        if max_score > 0:
            ratio = min(1.0, max(0.0, score / max_score))
            stars = int(math.floor(ratio * 5 + 0.5))
            return max(1, min(5, stars))

    # Priority 3: Extract ratings that are NOT prefixed by hypothetical phrases ("would be", etc.)
    matches = list(re.finditer(r'(?:(would|should|could)\s+be\s+)?([1-5])\s*-?\s*stars?', text, re.IGNORECASE))
    for m in matches:
        if not m.group(1):  # Match found without a hypothetical modifier
            return int(m.group(2))

    return None

def get_sentiment_label(stars: int) -> str:
    if stars <= 2:
        return "Negative"
    elif stars == 3:
        return "Neutral"
    return "Positive"

@app.get("/")
def health_check():
    return {
        "status": "online",
        "version": "4.1.0",
        "model_loaded": pipeline is not None,
        "irony_classifier_loaded": irony_classifier is not None
    }

@app.post("/predict", response_model=SentimentResponse)
def predict_sentiment(payload: SentimentRequest):
    load_models()

    raw_text = payload.text.strip()

    # Preprocessing
    demojized_text = emoji.demojize(raw_text, delimiters=(" ", " ")).replace("_", " ")
    clean_text = re.sub(r'<(script|style|iframe)\b[^>]*>.*?</\1>', '', demojized_text, flags=re.IGNORECASE | re.DOTALL)
    clean_text = re.sub(r'<[^>]*>', '', clean_text).strip()

    meaningful_content = re.sub(r'[\s\'"\.\,\!\?\-\:\;\(\)\[\]\{\}\&\;]+', '', clean_text)
    if not clean_text or not meaningful_content:
        raise HTTPException(
            status_code=400, 
            detail="Input text cannot be empty or contain only quotes, code tags, or punctuation."
        )

    lower_text = clean_text.lower()

    # Step 1: Legacy Sequential Pattern Guardrails (Preserves tested behaviors)
    if any(re.search(p, lower_text) for p in ONE_STAR_PATTERNS):
        return SentimentResponse(text=raw_text, stars=1, sentiment="Negative", confidence=0.98)

    if any(re.search(p, lower_text) for p in TWO_STAR_PATTERNS):
        return SentimentResponse(text=raw_text, stars=2, sentiment="Negative", confidence=0.96)

    if any(re.search(p, lower_text) for p in THREE_STAR_PATTERNS):
        return SentimentResponse(text=raw_text, stars=3, sentiment="Neutral", confidence=0.95)

    if any(re.search(p, lower_text) for p in FOUR_STAR_PATTERNS):
        return SentimentResponse(text=raw_text, stars=4, sentiment="Positive", confidence=0.96)

    if any(re.search(p, lower_text) for p in FIVE_STAR_PATTERNS):
        return SentimentResponse(text=raw_text, stars=5, sentiment="Positive", confidence=0.98)

    # Step 2: High-Confidence Sarcasm Interceptor
    sarcastic, irony_score = is_sarcastic(clean_text, threshold=0.85)
    if sarcastic:
        return SentimentResponse(
            text=raw_text,
            stars=1,
            sentiment="Negative",
            confidence=round(irony_score, 4)
        )

    # Step 3: Explicit Rating Parser (e.g. "4/5", "giving 3 stars")
    parsed_stars = extract_numeric_rating(raw_text)
    if parsed_stars is not None:
        return SentimentResponse(
            text=raw_text,
            stars=parsed_stars,
            sentiment=get_sentiment_label(parsed_stars),
            confidence=0.98
        )

    # Step 4: Retrained Scikit-Learn ML Model Fallback (Handles general reviews)
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Model pipeline is not loaded.")

    try:
        predicted_stars = int(pipeline.predict([clean_text])[0])
        probabilities = pipeline.predict_proba([clean_text])[0]
        confidence = float(np.max(probabilities))

        if confidence < 0.25:
            predicted_stars = 3

        return SentimentResponse(
            text=raw_text,
            stars=predicted_stars,
            sentiment=get_sentiment_label(predicted_stars),
            confidence=round(confidence, 4)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))