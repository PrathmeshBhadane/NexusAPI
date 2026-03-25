from pydantic import BaseModel
from typing import Literal

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: list[Message]
    provider: Literal["groq", "claude"] = "groq"
    model: str = "llama-3.3-70b-versatile"
    temperature: float = 0.7
    max_tokens: int = 1000

class ChatResponse(BaseModel):
    response: str
    model: str
    provider: str
    cached: bool = False
    tokens_used: int | None = None

class GenerateRequest(BaseModel):
    prompt: str
    provider: Literal["groq", "claude"] = "groq"
    model: str = "llama-3.3-70b-versatile"
    temperature: float = 0.7
    max_tokens: int = 1000

class GenerateResponse(BaseModel):
    response: str
    model: str
    provider: str
    cached: bool = False

class SummarizeRequest(BaseModel):
    text: str
    max_length: int = 200
    provider: Literal["groq", "claude"] = "groq"
    model: str = "llama-3.3-70b-versatile"

class SummarizeResponse(BaseModel):
    summary: str
    model: str
    provider: str
    cached: bool = False

class SentimentRequest(BaseModel):
    text: str
    provider: Literal["groq", "claude"] = "groq"

class SentimentResponse(BaseModel):
    sentiment: str
    confidence: str
    explanation: str
    provider: str
    cached: bool = False

class ExtractRequest(BaseModel):
    text: str
    fields: list[str]
    provider: Literal["groq", "claude"] = "groq"

class ExtractResponse(BaseModel):
    extracted: dict
    provider: str
    cached: bool = False

class ModelsResponse(BaseModel):
    groq: list[dict]
    claude: list[dict]