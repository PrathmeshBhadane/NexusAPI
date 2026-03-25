## 📊 Data Service

*File: `data-service/` (app/, Dockerfile, requirements.txt)*  
*Port: 8004*  
*Purpose: Data upload, processing, transformation, cleaning*

### 🎯 Data Service Concepts Learned

| Concept | Icon | Implementation |
|---------|------|-----------------|
| **CSV File Upload** | 📤 | aiofiles for async file handling |
| **DataFrame Processing** | 🔧 | pandas + numpy for data manipulation |
| **Data Validation** | ✅ | Schema validation before processing |
| **Async I/O** | ⚡ | Non-blocking file and DB operations |
| **SQLAlchemy Models** | 🗄️ | Dataset metadata stored in PostgreSQL |
| **File Persistence** | 💾 | uploads/ folder (bind mount) for file storage |
| **Data Transformation** | 🔄 | Feature engineering, normalization |
| **Excel Support** | 📑 | openpyxl for Excel file handling |

### 🏗️ Data Service Architecture

```
┌──────────────────────────────┐
│   Data Service (FastAPI)     │
└────┬──────────────┬──────────┘
     │              │
     ▼              ▼
┌──────────────┐  ┌──────────────────┐
│ File Upload  │  │ Data Processing  │
│ (aiofiles)   │  │ (pandas, numpy)  │
└──────┬───────┘  └────────┬─────────┘
       │                   │
       ▼                   ▼
┌──────────────────────────────┐
│  uploads/ folder (persistent)│
│  • raw.csv                   │
│  • cleaned.csv               │
│  • transformed.csv           │
└──────────┬───────────────────┘
           │
           ▼
    ┌─────────────────┐
    │data_db (SQLAlch │
    │ Dataset tables  │
    └─────────────────┘
```

### 📤 Data Processing Pipeline

```
1. Upload CSV
   POST /data/upload (multipart/form-data)
   → Save to uploads/{dataset_id}.csv
   → Extract columns metadata
   → Store in data_db
   
2. Validate Data
   → Check column types
   → Find missing values
   → Detect outliers
   
3. Clean Data
   POST /data/clean/{dataset_id}
   → Drop NaN values
   → Remove duplicates
   → Standardize formats
   → Save to uploads/{dataset_id}_clean.csv
   
4. Transform Data
   POST /data/transform/{dataset_id}
   → Apply feature engineering
   → Normalization/Scaling
   → Encoding categorical variables
   
5. Analyze Data
   GET /data/analyze/{dataset_id}
   → Statistical summary
   → Distribution analysis
   → Correlation matrix
```

### 💾 Requirements Analysis

```
fastapi==0.111.0
uvicorn[standard]==0.29.0
sqlalchemy==2.0.30
asyncpg==0.29.0
pydantic-settings==2.2.1
redis==5.0.4
pandas==2.2.2                 ← Data frame operations
numpy==1.26.4                 ← Numerical computing
httpx==0.27.0
python-multipart==0.0.9      ← Form data parsing
aiofiles==23.2.1              ← Async file operations
openpyxl==3.1.2               ← Excel file support
```

---

