import aio_pika
import json
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.job import Job
from app.models.ml_model import MLModel
from app.services.trainer import train_model
import logging

logger = logging.getLogger(__name__)

async def process_training_job(message: aio_pika.IncomingMessage):
    async with message.process():
        try:
            data = json.loads(message.body.decode())
            job_id = data["job_id"]
            model_id = data["model_id"]
            user_id = data["user_id"]
            train_data = data["data"]
            target_column = data["target_column"]
            model_type = data["model_type"]
            model_name = data["model_name"]

            logger.info(f"Processing training job: {job_id}")

            async with AsyncSessionLocal() as db:
                # update job status to running
                result = await db.execute(select(Job).where(Job.id == job_id))
                job = result.scalar_one_or_none()
                if job:
                    job.status = "running"
                    await db.commit()

            # run training in thread pool (CPU bound)
            loop = asyncio.get_event_loop()
            train_result = await loop.run_in_executor(
                None,
                train_model,
                train_data,
                target_column,
                model_type,
                model_id
            )

            async with AsyncSessionLocal() as db:
                # update model
                result = await db.execute(select(MLModel).where(MLModel.id == model_id))
                model = result.scalar_one_or_none()
                if model:
                    model.status = "ready"
                    model.file_path = train_result["file_path"]
                    model.features = train_result["features"]
                    model.accuracy = train_result["accuracy"]
                    model.metrics = train_result["metrics"]
                    await db.commit()

                # update job status to completed
                result = await db.execute(select(Job).where(Job.id == job_id))
                job = result.scalar_one_or_none()
                if job:
                    job.status = "completed"
                    job.result = {
                        "model_id": str(model_id),
                        "accuracy": train_result["accuracy"],
                        "metrics": train_result["metrics"]
                    }
                    await db.commit()

            logger.info(f"Training job completed: {job_id}")

        except Exception as e:
            logger.error(f"Training job failed: {e}")
            async with AsyncSessionLocal() as db:
                result = await db.execute(select(Job).where(Job.id == data.get("job_id")))
                job = result.scalar_one_or_none()
                if job:
                    job.status = "failed"
                    job.error = str(e)
                    await db.commit()

                result = await db.execute(select(MLModel).where(MLModel.id == data.get("model_id")))
                model = result.scalar_one_or_none()
                if model:
                    model.status = "failed"
                    await db.commit()

async def start_worker():
    while True:
        try:
            connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
            channel = await connection.channel()
            await channel.set_qos(prefetch_count=1)
            queue = await channel.declare_queue("ml.train", durable=True)
            await queue.consume(process_training_job)
            logger.info("ML Worker started — waiting for jobs")
            await asyncio.Future()
        except Exception as e:
            logger.error(f"Worker connection failed: {e} — retrying in 5s")
            await asyncio.sleep(5)