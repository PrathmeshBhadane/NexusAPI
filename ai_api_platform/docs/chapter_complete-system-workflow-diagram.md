## 📈 Complete System Workflow Diagram

### 🌊 User Request Lifecycle (Full Journey)

```
STEP 1: User Request Arrives
┌─────────────────────────────────────────────────────────────┐
│ Browser: POST /ml/train                                     │
│ Headers: Authorization: Bearer <token>                      │
│ Body: {dataset_id: 123, model_type: "random_forest"}      │
└──────────────┬──────────────────────────────────────────────┘
               │
STEP 2: Nginx Reverse Proxy
┌──────────────▼──────────────────────────────────────────────┐
│ Nginx (port 80)                                             │
│ • Receives request                                          │
│ • Preserves headers (X-Real-IP, X-Forwarded-For)          │
│ • Forwards to gateway:8000                                 │
└──────────────┬──────────────────────────────────────────────┘
               │
STEP 3: Gateway Authentication 
┌──────────────▼──────────────────────────────────────────────┐
│ Gateway Service (port 8000)                                 │
│ 1. Extract token from Authorization header                │
│ 2. POST to auth-service:8001/auth/validate-token         │
│ 3. Auth-service checks JWT signature & expiration        │
│    → Connects to auth_db to verify user exists           │
│ 4. Returns {valid: true, user_id: 42, permissions: []} │
│ 5. Token valid ✅ Continue                               │
└──────────────┬──────────────────────────────────────────────┘
               │
STEP 4: Rate Limiting Check
┌──────────────▼──────────────────────────────────────────────┐
│ Rate Limiter (Redis)                                       │
│ 1. Get user's API key from request                        │
│ 2. Check Redis: requests_this_hour[api_key]              │
│ 3. If count < 100: increment and continue                │
│ 4. Else: return 429 Too Many Requests                    │
│ 5. Rate limit OK ✅ Continue                             │
└──────────────┬──────────────────────────────────────────────┘
               │
STEP 5: Service Discovery & Routing
┌──────────────▼──────────────────────────────────────────────┐
│ Gateway Routes Request                                      │
│ 1. Path = /ml/train → route to ML service               │
│ 2. Check service registry in Redis                       │
│    redis.hgetall("registry:ml-service")                  │
│ 3. Verify last_seen timestamp < 30 seconds              │
│ 4. If not found or stale: return 503 Service Unavailable│
│ 5. Service available ✅Continue                         │
└──────────────┬──────────────────────────────────────────────┘
               │
STEP 6: Forward to ML Service
┌──────────────▼──────────────────────────────────────────────┐
│ ML Service (port 8002)                                      │
│ 1. Receives training request                              │
│ 2. Extract dataset_id from request body                   │
│ 3. Validate dataset exists in data_db                     │
│ 4. Create training job record in ml_db                    │
│    {job_id: "abc123", status: "queued", user_id: 42}    │
│ 5. Publish to RabbitMQ queue:                           │
│    {job_id: "abc123", dataset_id: 123, model: "rf"}     │
│ 6. Return immediately: {job_id: "abc123", status: "q"}  │
└──────────────┬──────────────────────────────────────────────┘
               │
STEP 7: Return to User (Fast!)
┌──────────────▼──────────────────────────────────────────────┐
│ Response: 202 Accepted                                      │
│ {                                                           │
│   "job_id": "abc123",                                      │
│   "status": "queued",                                      │
│   "estimated_time": "2-3 minutes"                          │
│ }                                                           │
│ TOTAL TIME: ~150ms ⚡                                       │
└──────────────┬──────────────────────────────────────────────┘
               │
STEP 8: Background Processing (happens async)
┌──────────────▼──────────────────────────────────────────────┐
│ ML Worker (background process)                              │
│ 1. Picks job from RabbitMQ queue                         │
│ 2. Load dataset from data_service                        │
│ 3. Split into train/test (80/20)                        │
│ 4. Train Random Forest model (scikit-learn)             │
│    - Fit on training data (120 seconds)                 │
│    - Evaluate on test data                             │
│    - Calculate accuracy: 87.3%                         │
│ 5. Save .pkl and metadata to saved_models/             │
│ 6. Update ml_db:                                       │
│    {job_id: "abc123", status: "completed",            │
│     model_id: "model_789", accuracy: 0.873}          │
│ 7. Update Redis service status                        │
└──────────────┬──────────────────────────────────────────────┘
               │
STEP 9: User Polls for Status
┌──────────────▼──────────────────────────────────────────────┐
│ Browser: GET /ml/jobs/abc123                                │
│ (user polling every 10 seconds)                            │
│                                                              │
│ Gateway → ML Service → Query ml_db                         │
│ Response:                                                   │
│ {                                                           │
│   "job_id": "abc123",                                      │
│   "status": "completed",                                   │
│   "model_id": "model_789",                                │
│   "accuracy": 0.873                                        │
│ }                                                           │
└──────────────┬──────────────────────────────────────────────┘
               │
STEP 10: Use Trained Model
┌──────────────▼──────────────────────────────────────────────┐
│ Browser: POST /ml/predict                                   │
│ {model_id: "model_789", features: {...}}                  │
│                                                              │
│ ML Service:                                                 │
│ 1. Load model from saved_models/model_789.pkl           │
│ 2. Transform features                                    │
│ 3. Call model.predict()                                 │
│ 4. Return prediction                                    │
│                                                              │
│ Response: {prediction: 45.67, confidence: 0.92}         │
└─────────────────────────────────────────────────────────────┘
```

---

### 🔄 AI Service Caching Workflow

```
┌─────────────────────────────────────────┐
│  User: POST /ai/chat                    │
│  {prompt: "Explain machine learning"}   │
└──────────────┬──────────────────────────┘
               │
STEP 1: Hash the Prompt
┌──────────────▼──────────────────────────┐
│ hash_value = sha256(prompt)             │
│ = "a3f9d8e2b1c4..."                     │
└──────────────┬──────────────────────────┘
               │
STEP 2: Check Redis Cache
┌──────────────▼──────────────────────────┐
│ Redis:                                   │
│ key = f"ai_cache:{hash_value}"          │
│ cached = redis.get(key)                 │
│                                          │
│ if cached:                              │
│   return cached_response ✅              │
│ else:                                   │
│   continue to step 3                    │
└──────────────┬──────────────────────────┘
               │
STEP 3: Call LLM API (with Retry)
┌──────────────▼──────────────────────────┐
│ @tenacity.retry(                        │
│   stop=stop_after_attempt(3),           │
│   wait=wait_exponential(multiplier=1)   │
│ )                                        │
│ async def call_groq_api(prompt):       │
│   • Attempt 1 timeout → wait 1s        │
│   • Attempt 2 fails → wait 2s          │
│   • Attempt 3 succeeds → return        │
│                                          │
│ response = await groq_client.create(   │
│   model="mixtral-8x7b",                │
│   messages=[{"role": "user",           │
│             "content": prompt}]        │
│ )                                       │
└──────────────┬──────────────────────────┘
               │
STEP 4: Parse & Cache Response
┌──────────────▼──────────────────────────┐
│ parsed = response.choices[0].message    │
│                                          │
│ redis.setex(                            │
│   key=f"ai_cache:{hash_value}",        │
│   time=3600,  # 1 hour TTL            │
│   value=parsed                         │
│ )                                       │
└──────────────┬──────────────────────────┘
               │
STEP 5: Return to User
┌──────────────▼──────────────────────────┐
│ Response: {response: "ML is the..."}    │
│ Response time: 800ms (Groq API)        │
│                                          │
│ Next identical request from ANY user:  │
│ Response time: 2ms (Redis cache) ⚡    │
│ 400x faster! 🚀                        │
└─────────────────────────────────────────┘
```

---

### 📊 Data Upload & Processing Flow

```
┌──────────────────────────────────┐
│ User uploads CSV file via UI     │
│ POST /data/upload (multipart)    │
└──────────────┬───────────────────┘
               │
STEP 1: File Validation
┌──────────────▼───────────────────┐
│ • Check file size (< 100MB)      │
│ • Verify file type (.csv/.xlsx)  │
│ • Generate dataset_id (UUID)     │
│ • Save to uploads/{id}.csv       │
└──────────────┬───────────────────┘
               │
STEP 2: Extract & Store Metadata
┌──────────────▼───────────────────┐
│ • Read CSV headers               │
│ • Infer column types            │
│ • Count rows                     │
│ • Store in data_db:             │
│   Dataset {                      │
│     id: uuid,                   │
│     original_filename: "...",   │
│     rows: 5000,                │
│     columns: 20,               │
│     created_at: timestamp      │
│   }                             │
└──────────────┬───────────────────┘
               │
STEP 3: User Requests Data Cleaning
┌──────────────▼───────────────────┐
│ POST /data/clean/{dataset_id}    │
│ Read original CSV into DataFrame │
│ Apply cleaning:                  │
│ • Drop rows with NaN            │
│ • Remove duplicates             │
│ • Standardize column names      │
│ • Fix data type mismatches      │
└──────────────┬───────────────────┘
               │
STEP 4: Save Cleaned Data
┌──────────────▼───────────────────┐
│ Save to:                         │
│ uploads/{id}_clean.csv          │
│                                  │
│ Update data_db:                  │
│ Dataset.status = "cleaned"      │
│ Dataset.rows = 4850 (dropped 150)
└──────────────┬───────────────────┘
               │
STEP 5: Feature Engineering
┌──────────────▼───────────────────┐
│ POST /data/transform/{id}        │
│ • Normalize numeric columns     │
│ • Encode categorical vars       │
│ • Create feature interactions   │
│ • Handle outliers               │
└──────────────┬───────────────────┘
               │
STEP 6: Ready for ML Training
┌──────────────▼───────────────────┐
│ Data is now ready for:          │
│ POST /ml/train {                │
│   dataset_id: id,              │
│   model_type: "random_forest"  │
│ }                              │
│                                 │
│ ML Service will use cleaned &  │
│ transformed data to train model │
└─────────────────────────────────┘
```

---

