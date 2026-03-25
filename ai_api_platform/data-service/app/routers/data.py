import os
import uuid
import aiofiles
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.config import settings
from app.models.dataset import Dataset
from app.schemas.data import DatasetResponse, CleanRequest, TransformRequest, AnalysisResponse
from app.services.processor import (
    load_dataframe, get_basic_info,
    clean_dataframe, transform_dataframe, analyze_dataframe
)

router = APIRouter(prefix="/data", tags=["data"])

@router.post("/upload", response_model=DatasetResponse)
async def upload_dataset(
    user_id: str = Query(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    if not file.filename.endswith((".csv", ".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Only CSV and Excel files are supported")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1]
    file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}{ext}")

    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    file_size = len(content)

    try:
        import pandas as pd
        if ext == ".csv":
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        info = get_basic_info(df)
    except Exception as e:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail=f"Could not parse file: {str(e)}")

    dataset = Dataset(
        user_id=user_id,
        name=file.filename,
        file_path=file_path,
        file_size=file_size,
        rows=info["rows"],
        columns=info["columns"],
        column_names=info["column_names"],
        dtypes=info["dtypes"]
    )
    db.add(dataset)
    await db.commit()
    await db.refresh(dataset)

    return dataset

@router.get("/datasets", response_model=list[DatasetResponse])
async def list_datasets(user_id: str = Query(...), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Dataset).where(Dataset.user_id == user_id)
    )
    return result.scalars().all()

@router.get("/datasets/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(dataset_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset

@router.post("/clean/{dataset_id}")
async def clean_dataset(
    dataset_id: str,
    payload: CleanRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    try:
        df = load_dataframe(dataset.file_path)
        original_rows = len(df)
        df = clean_dataframe(df, payload.drop_duplicates, payload.drop_nulls, payload.fill_nulls)

        clean_path = dataset.file_path.replace(".", "_clean.")
        df.to_csv(clean_path, index=False)

        return {
            "message": "Dataset cleaned successfully",
            "original_rows": original_rows,
            "cleaned_rows": len(df),
            "removed_rows": original_rows - len(df),
            "clean_file": clean_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/transform/{dataset_id}")
async def transform_dataset(
    dataset_id: str,
    payload: TransformRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    try:
        df = load_dataframe(dataset.file_path)
        df = transform_dataframe(df, payload.normalize, payload.encode_categoricals, payload.columns)

        transform_path = dataset.file_path.replace(".", "_transformed.")
        df.to_csv(transform_path, index=False)

        return {
            "message": "Dataset transformed successfully",
            "rows": len(df),
            "columns": list(df.columns),
            "transform_file": transform_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analyze/{dataset_id}", response_model=AnalysisResponse)
async def analyze_dataset(dataset_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    try:
        df = load_dataframe(dataset.file_path)
        analysis = analyze_dataframe(df)
        info = get_basic_info(df)

        return AnalysisResponse(
            dataset_id=dataset_id,
            rows=info["rows"],
            columns=info["columns"],
            column_names=info["column_names"],
            dtypes=info["dtypes"],
            missing_values=analysis["missing_values"],
            statistics=analysis["statistics"],
            sample=analysis["sample"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/datasets/{dataset_id}")
async def delete_dataset(dataset_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    if os.path.exists(dataset.file_path):
        os.remove(dataset.file_path)

    await db.delete(dataset)
    await db.commit()

    return {"message": "Dataset deleted successfully"}

@router.get("/health")
async def data_router_health():
    return {"status": "ok", "service": "data-router"}