from pydantic import BaseModel, Field

class SentimentRequest(BaseModel):
    text: str = Field(
        ..., 
        min_length=1, 
        description="The raw review text to analyze",
        json_schema_extra={"example": "Great application overall, but load times could be faster."}
    )

class SentimentResponse(BaseModel):
    text: str = Field(..., description="The original review text analyzed")
    stars: int = Field(..., ge=1, le=5, description="Predicted star rating from 1 to 5")
    sentiment: str = Field(..., description="Mapped sentiment label (Negative, Neutral, Positive)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model classification confidence score")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Great application overall, but load times could be faster.",
                "stars": 4,
                "sentiment": "Positive",
                "confidence": 0.9412
            }
        }