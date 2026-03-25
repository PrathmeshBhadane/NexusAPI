from fastapi import APIRouter, HTTPException
import redis.asyncio as aioredis
import json
import traceback
from app.core.config import settings
from app.schemas.ai import (
    ChatRequest, ChatResponse,
    GenerateRequest, GenerateResponse,
    SummarizeRequest, SummarizeResponse,
    SentimentRequest, SentimentResponse,
    ExtractRequest, ExtractResponse,
    ModelsResponse
)
from app.services.groq_client import make_cache_key, get_or_create

router = APIRouter(prefix="/ai", tags=["ai"])

async def get_redis():
    return aioredis.from_url(settings.REDIS_URL, decode_responses=True)

@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest):
    redis_client = await get_redis()
    try:
        messages = [{"role": m.role, "content": m.content} for m in payload.messages]
        cache_key = make_cache_key(
            "chat",
            json.dumps(messages) + payload.model + payload.provider
        )
        result, cached = await get_or_create(
            redis_client, cache_key, messages,
            payload.model, payload.temperature,
            payload.max_tokens, payload.provider
        )
        return ChatResponse(
            response=result["content"],
            model=result["model"],
            provider=result["provider"],
            cached=cached,
            tokens_used=result.get("tokens")
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await redis_client.aclose()

@router.post("/generate", response_model=GenerateResponse)
async def generate(payload: GenerateRequest):
    redis_client = await get_redis()
    try:
        messages = [{"role": "user", "content": payload.prompt}]
        cache_key = make_cache_key(
            "generate",
            payload.prompt + payload.model + payload.provider
        )
        result, cached = await get_or_create(
            redis_client, cache_key, messages,
            payload.model, payload.temperature,
            payload.max_tokens, payload.provider
        )
        return GenerateResponse(
            response=result["content"],
            model=result["model"],
            provider=result["provider"],
            cached=cached
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await redis_client.aclose()

@router.post("/summarize", response_model=SummarizeResponse)
async def summarize(payload: SummarizeRequest):
    redis_client = await get_redis()
    try:
        messages = [{
            "role": "user",
            "content": f"Summarize the following text in {payload.max_length} words or less:\n\n{payload.text}"
        }]
        cache_key = make_cache_key(
            "summarize",
            payload.text + str(payload.max_length) + payload.provider
        )
        result, cached = await get_or_create(
            redis_client, cache_key, messages,
            payload.model, 0.3, 500, payload.provider
        )
        return SummarizeResponse(
            summary=result["content"],
            model=result["model"],
            provider=result["provider"],
            cached=cached
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await redis_client.aclose()

@router.post("/sentiment", response_model=SentimentResponse)
async def sentiment(payload: SentimentRequest):
    redis_client = await get_redis()
    try:
        model = "llama-3.3-70b-versatile" if payload.provider == "groq" else "claude-haiku-4-5-20251001"
        messages = [{
            "role": "user",
            "content": f"""Analyze the sentiment of this text and respond in JSON format only with keys: sentiment (positive/negative/neutral), confidence (high/medium/low), explanation.

Text: {payload.text}

Respond with JSON only, no extra text."""
        }]
        cache_key = make_cache_key("sentiment", payload.text + payload.provider)
        result, cached = await get_or_create(
            redis_client, cache_key, messages,
            model, 0.1, 200, payload.provider
        )
        try:
            parsed = json.loads(result["content"])
        except:
            parsed = {
                "sentiment": "neutral",
                "confidence": "low",
                "explanation": result["content"]
            }
        return SentimentResponse(
            sentiment=parsed.get("sentiment", "neutral"),
            confidence=parsed.get("confidence", "low"),
            explanation=parsed.get("explanation", ""),
            provider=result["provider"],
            cached=cached
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await redis_client.aclose()

@router.post("/extract", response_model=ExtractResponse)
async def extract(payload: ExtractRequest):
    redis_client = await get_redis()
    try:
        model = "llama-3.3-70b-versatile" if payload.provider == "groq" else "claude-haiku-4-5-20251001"
        fields_str = ", ".join(payload.fields)
        messages = [{
            "role": "user",
            "content": f"""Extract the following fields from the text and respond in JSON format only: {fields_str}

Text: {payload.text}

Respond with JSON only, no extra text."""
        }]
        cache_key = make_cache_key("extract", payload.text + fields_str + payload.provider)
        result, cached = await get_or_create(
            redis_client, cache_key, messages,
            model, 0.1, 500, payload.provider
        )
        try:
            extracted = json.loads(result["content"])
        except:
            extracted = {"raw": result["content"]}
        return ExtractResponse(
            extracted=extracted,
            provider=result["provider"],
            cached=cached
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await redis_client.aclose()

@router.get("/models", response_model=ModelsResponse)
async def list_models():
    return ModelsResponse(
        groq=[
            {"id": "llama-3.3-70b-versatile", "name": "LLaMA 3.3 70B", "context_window": 128000},
            {"id": "llama-3.1-8b-instant", "name": "LLaMA 3.1 8B Instant", "context_window": 128000},
            {"id": "mixtral-8x7b-32768", "name": "Mixtral 8x7B", "context_window": 32768},
            {"id": "gemma2-9b-it", "name": "Gemma 2 9B", "context_window": 8192},
        ],
        claude=[
            {"id": "claude-haiku-4-5-20251001", "name": "Claude Haiku", "context_window": 200000},
            {"id": "claude-sonnet-4-6", "name": "Claude Sonnet", "context_window": 200000},
            {"id": "claude-opus-4-6", "name": "Claude Opus", "context_window": 200000},
        ]
    )

@router.get("/health")
async def ai_router_health():
    return {"status": "ok", "service": "ai-router"}