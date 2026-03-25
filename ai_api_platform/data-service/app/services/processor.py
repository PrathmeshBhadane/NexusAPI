import pandas as pd
import numpy as np
import os
from app.core.config import settings

def load_dataframe(file_path: str) -> pd.DataFrame:
    if file_path.endswith(".csv"):
        return pd.read_csv(file_path)
    elif file_path.endswith((".xlsx", ".xls")):
        return pd.read_excel(file_path)
    else:
        raise ValueError("Unsupported file type")

def get_basic_info(df: pd.DataFrame) -> dict:
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()}
    }

def clean_dataframe(df: pd.DataFrame, drop_duplicates: bool, drop_nulls: bool, fill_nulls: str | None) -> pd.DataFrame:
    if drop_duplicates:
        df = df.drop_duplicates()
    if drop_nulls:
        df = df.dropna()
    elif fill_nulls is not None:
        if fill_nulls == "mean":
            df = df.fillna(df.mean(numeric_only=True))
        elif fill_nulls == "median":
            df = df.fillna(df.median(numeric_only=True))
        elif fill_nulls == "mode":
            df = df.fillna(df.mode().iloc[0])
        elif fill_nulls == "zero":
            df = df.fillna(0)
        else:
            df = df.fillna(fill_nulls)
    return df

def transform_dataframe(df: pd.DataFrame, normalize: bool, encode_categoricals: bool, columns: list[str] | None) -> pd.DataFrame:
    target_cols = columns if columns else list(df.columns)

    if encode_categoricals:
        for col in target_cols:
            if col in df.columns and df[col].dtype == object:
                df[col] = pd.Categorical(df[col]).codes

    if normalize:
        numeric_cols = df[target_cols].select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            col_min = df[col].min()
            col_max = df[col].max()
            if col_max != col_min:
                df[col] = (df[col] - col_min) / (col_max - col_min)

    return df

def analyze_dataframe(df: pd.DataFrame) -> dict:
    missing_values = {col: int(df[col].isnull().sum()) for col in df.columns}

    statistics = {}
    for col in df.columns:
        if df[col].dtype in [np.float64, np.int64, np.float32, np.int32]:
            statistics[col] = {
                "mean": float(df[col].mean()) if not df[col].isnull().all() else None,
                "std": float(df[col].std()) if not df[col].isnull().all() else None,
                "min": float(df[col].min()) if not df[col].isnull().all() else None,
                "max": float(df[col].max()) if not df[col].isnull().all() else None,
                "median": float(df[col].median()) if not df[col].isnull().all() else None,
            }
        else:
            value_counts = df[col].value_counts().head(5).to_dict()
            statistics[col] = {
                "unique_values": int(df[col].nunique()),
                "top_values": {str(k): int(v) for k, v in value_counts.items()}
            }

    sample = df.head(5).replace({np.nan: None}).to_dict(orient="records")

    return {
        "missing_values": missing_values,
        "statistics": statistics,
        "sample": sample
    }