## 📊 Data Models

### User + Auth Models
```python
# User Table (auth_db)
User:
  id: UUID
  email: str (unique)
  hashed_password: str (bcrypt)
  is_active: bool
  created_at: datetime
  
# API Key Table (auth_db)
APIKey:
  id: UUID
  user_id: FK(User)
  key: str (hashed)
  permissions: list
  is_active: bool
  created_at: datetime
  last_used: datetime
```

### ML Models
```python
# Job Table (ml_db)
MLJob:
  id: UUID
  user_id: UUID
  dataset_id: UUID
  model_type: str (enum)
  status: str (queued|training|completed|failed)
  created_at: datetime
  completed_at: datetime
  
# ML Model Table (ml_db)
MLModel:
  id: UUID
  user_id: UUID
  job_id: FK(MLJob)
  model_type: str
  accuracy: float
  features: list
  parameters: dict
  created_at: datetime
  filepath: str (saved_models/xxx.pkl)
```

### Data Service Models
```python
# Dataset Table (data_db)
Dataset:
  id: UUID
  user_id: UUID
  filename: str
  rows: int
  columns: int
  status: str (raw|cleaned|transformed)
  created_at: datetime
  filepath: str (uploads/xxx.csv)
  metadata: dict
```

---

