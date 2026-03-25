import aio_pika
import json
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.config import settings
from app.models.ml_model import MLModel
from app.models.job import Job
from app.schemas.ml import TrainRequest, TrainResponse, JobStatusResponse, PredictRequest, PredictResponse, ModelResponse
from app.services.trainer import predict
import redis.asyncio as redis

router = APIRouter(prefix="/ml", tags=["ml"])

async def get_redis():
    return redis.from_url(settings.REDIS_URL, decode_responses=True)

async def get_rabbitmq():
    connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
    channel = await connection.channel()
    return connection, channel

@router.post("/train", response_model=TrainResponse)
async def train(
    payload: TrainRequest,
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    model_id = str(uuid.uuid4())
    job_id = str(uuid.uuid4())

    ml_model = MLModel(
        id=model_id,
        user_id=user_id,
        name=payload.name,
        model_type=payload.model_type,
        target_column=payload.target_column,
        status="queued"
    )
    db.add(ml_model)

    job = Job(
        id=job_id,
        user_id=user_id,
        job_type="ml_training",
        status="queued"
    )
    db.add(job)
    await db.commit()

    connection, channel = await get_rabbitmq()
    try:
        await channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps({
                    "job_id": job_id,
                    "model_id": model_id,
                    "user_id": user_id,
                    "model_name": payload.name,
                    "model_type": payload.model_type,
                    "target_column": payload.target_column,
                    "data": payload.data
                }).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            ),
            routing_key="ml.train"
        )
    finally:
        await connection.close()

    return TrainResponse(
        job_id=job_id,
        status="queued",
        message=f"Training job queued. Poll GET /ml/jobs/{job_id} for status."
    )

@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobStatusResponse(
        job_id=str(job.id),
        status=job.status,
        result=job.result,
        error=job.error,
        created_at=job.created_at
    )

@router.post("/predict", response_model=PredictResponse)
async def run_predict(
    payload: PredictRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(MLModel).where(
            MLModel.id == payload.model_id,
            MLModel.status == "ready"
        )
    )
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found or not ready")

    try:
        predictions = predict(payload.model_id, payload.data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return PredictResponse(model_id=payload.model_id, predictions=predictions)

@router.get("/models", response_model=list[ModelResponse])
async def list_models(user_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(MLModel).where(MLModel.user_id == user_id)
    )
    return result.scalars().all()

@router.get("/models/{model_id}", response_model=ModelResponse)
async def get_model(model_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MLModel).where(MLModel.id == model_id))
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model

@router.delete("/models/{model_id}")
async def delete_model(model_id: str, user_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(MLModel).where(MLModel.id == model_id, MLModel.user_id == user_id)
    )
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    model.status = "deleted"
    await db.commit()
    return {"message": "Model deleted"}

@router.get("/health")
async def ml_router_health():
    return {"status": "ok", "service": "ml-router"}