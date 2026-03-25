import httpx
from fastapi import HTTPException, Request
from app.core.config import settings

async def validate_request(request: Request) -> dict:
    auth_header = request.headers.get("Authorization")
    api_key_header = request.headers.get("X-API-Key")

    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(
                    f"{settings.AUTH_SERVICE_URL}/auth/validate-token",
                    json={"token": token}
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("valid"):
                        return data
            except httpx.RequestError:
                raise HTTPException(status_code=503, detail="Auth service unavailable")

    if api_key_header:
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(
                    f"{settings.AUTH_SERVICE_URL}/keys/validate",
                    json={"api_key": api_key_header}
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("valid"):
                        service_scope = data.get("service")
                        if service_scope and service_scope != "all":
                            if not request.url.path.startswith(f"/{service_scope}"):
                                raise HTTPException(status_code=403, detail=f"API Key restricted to '{service_scope}' service")
                        return data
            except httpx.RequestError:
                raise HTTPException(status_code=503, detail="Auth service unavailable")

    raise HTTPException(status_code=401, detail="Invalid or missing credentials")