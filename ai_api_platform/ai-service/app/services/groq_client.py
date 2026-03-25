import hashlib
import json
from groq import Groq
import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential
import redis.asyncio as aioredis
from app.core.config import settings

groq_client = Groq(api_key=settings.GROQ_API_KEY)
anthropic_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

GROQ_MODELS = [
    "llama3-8b-8192",
    "llama3-70b-8192",
    "mixtral-8x7b-32768",
    "gemma-7b-it"
]

CLAUDE_MODELS = [
    "claude-haiku-4-5-20251001",
    "claude-sonnet-4-6",
    "claude-opus-4-6"
]

def make_cache_key(prefix: str, data: str) -> str:
    hash_val = hashlib.md5(data.encode()).hexdigest()
    return f"ai:{prefix}:{hash_val}"

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def call_groq(messages: list[dict], model: str, temperature: float, max_tokens: int) -> dict:
    response = groq_client.chat.completions.create(
        messages=messages,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens
    )
    return {
        "content": response.choices[0].message.content,
        "model": response.model,
        "tokens": response.usage.total_tokens if response.usage else None,
        "provider": "groq"
    }

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def call_claude(messages: list[dict], model: str, temperature: float, max_tokens: int) -> dict:
    system_message = None
    filtered_messages = []

    for msg in messages:
        if msg["role"] == "system":
            system_message = msg["content"]
        else:
            filtered_messages.append(msg)

    kwargs = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": filtered_messages
    }

    if system_message:
        kwargs["system"] = system_message

    response = anthropic_client.messages.create(**kwargs)

    return {
        "content": response.content[0].text,
        "model": response.model,
        "tokens": response.usage.input_tokens + response.usage.output_tokens,
        "provider": "claude"
    }

def call_llm(
    messages: list[dict],
    model: str,
    temperature: float,
    max_tokens: int,
    provider: str = "groq"
) -> dict:
    if provider == "claude":
        return call_claude(messages, model, temperature, max_tokens)
    return call_groq(messages, model, temperature, max_tokens)

async def get_or_create(
    redis_client: aioredis.Redis,
    cache_key: str,
    messages: list[dict],
    model: str,
    temperature: float,
    max_tokens: int,
    provider: str = "groq"
) -> tuple[dict, bool]:
    cached = await redis_client.get(cache_key)
    if cached:
        result = json.loads(cached)
        result["cached"] = True
        return result, True

    result = call_llm(messages, model, temperature, max_tokens, provider)
    await redis_client.setex(cache_key, settings.CACHE_TTL, json.dumps(result))
    return result, False