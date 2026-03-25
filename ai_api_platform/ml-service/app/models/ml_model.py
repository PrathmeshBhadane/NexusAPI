from sqlalchemy import Column, String, Float, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import uuid
from datetime import datetime

class MLModel(Base):
    __tablename__ = "ml_models"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    model_type = Column(String, nullable=False)
    target_column = Column(String, nullable=False)
    features = Column(JSON, nullable=True)
    accuracy = Column(Float, nullable=True)
    metrics = Column(JSON, nullable=True)
    file_path = Column(String, nullable=True)
    status = Column(String, default="training")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)