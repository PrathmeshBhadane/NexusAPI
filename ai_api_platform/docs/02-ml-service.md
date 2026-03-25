## 🤖 ML Service

*File: `ml-service/` (app/, Dockerfile, requirements.txt)*  
*Purpose: Train machine learning models and run predictions using scikit-learn*

### 🎯 What the ML Service Does

The ML Service handles machine learning model training and inference with support for multiple algorithms. It uses RabbitMQ for async job processing to handle long-running training tasks without blocking the API.

### 📋 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/ml/train` | Upload CSV + choose model type → starts training job |
| `GET` | `/ml/jobs/{id}` | Check if training is done + get status |
| `POST` | `/ml/predict` | Send data → get prediction from trained model |
| `GET` | `/ml/models` | List all your trained models |
| `GET` | `/ml/models/{id}` | Get model details, accuracy, features |
| `DELETE` | `/ml/models/{id}` | Delete a model |

### 🧠 Supported Model Types

- **Linear Regression** - For continuous prediction tasks
- **Random Forest Classifier** - For classification with complex patterns
- **Random Forest Regressor** - For regression with non-linear relationships
- **Logistic Regression** - For binary/multi-class classification
- **Decision Tree** - For interpretable classification/regression

### ⚙️ How ML Training Works

**The Async Training Pattern:**
```
User sends CSV + target column
→ ML service publishes job to RabbitMQ queue
→ Returns job_id immediately (50ms response time)
→ Background worker picks up job from queue
→ Trains model with scikit-learn on CPU/GPU
→ Saves trained .pkl file to persistent storage
→ Updates job status in PostgreSQL database
→ User polls GET /ml/jobs/{id} endpoint
→ Gets model_id when training completes
```

**Why Async Processing:**
- ML training can take 30 seconds to 5+ minutes
- Prevents HTTP timeouts and poor user experience
- Allows horizontal scaling of training workers
- Decouples API responsiveness from compute intensity

### 🔄 Training Workflow Example

```python
# User uploads CSV and requests training
POST /ml/train
{
  "dataset_id": "abc123",
  "target_column": "price",
  "model_type": "random_forest",
  "hyperparameters": {"n_estimators": 100}
}

# Immediate response (50ms)
{
  "job_id": "job_456",
  "status": "queued",
  "estimated_time": "2-3 minutes"
}

# User checks status (polling)
GET /ml/jobs/job_456
{
  "status": "completed",
  "model_id": "model_789",
  "accuracy": 0.87,
  "training_time": 145
}

# Use trained model for predictions
POST /ml/predict
{
  "model_id": "model_789",
  "data": {"feature1": 1.2, "feature2": 3.4}
}
# Returns: {"prediction": 45.67}
```

### 💾 Model Persistence

- **Storage**: Trained models saved as `.pkl` files using joblib
- **Location**: `./ml-service/saved_models/` (bind mount for persistence)
- **Metadata**: Model info stored in PostgreSQL (`ml_db`)
- **Cleanup**: Automatic deletion when models are removed via API

### 📊 Model Evaluation Metrics

Each trained model includes:
- **Accuracy Score** (classification) or **R² Score** (regression)
- **Feature Importance** rankings
- **Training Parameters** used
- **Dataset Statistics** (rows, columns, target distribution)

---

