from pydantic import BaseModel
from typing import Any
import uuid
from datetime import datetime

class DatasetResponse(BaseModel):
    id: uuid.UUID
    name: str
    file_size: int | None
    rows: int | None
    columns: int | None
    column_names: list[str] | None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class CleanRequest(BaseModel):
    drop_duplicates: bool = True
    drop_nulls: bool = False
    fill_nulls: str | None = None

class TransformRequest(BaseModel):
    normalize: bool = False
    encode_categoricals: bool = False
    columns: list[str] | None = None

class AnalysisResponse(BaseModel):
    dataset_id: str
    rows: int
    columns: int
    column_names: list[str]
    dtypes: dict[str, str]
    missing_values: dict[str, int]
    statistics: dict[str, Any]
    sample: list[dict]