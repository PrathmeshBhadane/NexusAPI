from pydantic import BaseModel
from typing import Any
import uuid
from datetime import datetime

class TrainRequest(BaseModel):
    name: str
    model_type: str
    target_column: str
    data: list[dict[str, Any]]

class TrainResponse(BaseModel):
    job_id: str
    status: str
    message: str

class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    result: dict | None = None
    error: str | None = None
    created_at: datetime

class PredictRequest(BaseModel):
    model_id: str
    data: list[dict[str, Any]]

class PredictResponse(BaseModel):
    model_id: str
    predictions: list[Any]

class ModelResponse(BaseModel):
    id: uuid.UUID
    name: str
    model_type: str
    target_column: str
    features: list[str] | None
    accuracy: float | None
    metrics: dict | None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True