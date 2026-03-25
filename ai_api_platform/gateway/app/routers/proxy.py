import httpx
from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.middleware.auth import validate_request
from app.middleware.rate_limiter import check_rate_limit

router = APIRouter()

SERVICE_ROUTES = {
    "/auth": settings.AUTH_SERVICE_URL,
    "/keys": settings.AUTH_SERVICE_URL,
    "/ml": settings.ML_SERVICE_URL,
    "/ai": settings.AI_SERVICE_URL,
    "/data": settings.DATA_SERVICE_URL,
}

PUBLIC_PATHS = [
    "/auth/register",
    "/auth/login",
]

def get_service_url(path: str) -> str:
    for prefix, url in SERVICE_ROUTES.items():
        if path.startswith(prefix):
            return url
    return None

async def forward_request(request: Request, service_url: str, user_info: dict = None) -> Response:
    path = request.url.path
    query = request.url.query
    url = f"{service_url}{path}"
    if query:
        url = f"{url}?{query}"

    body = await request.body()
    headers = dict(request.headers)
    headers.pop("host", None)

    if user_info:
        headers["X-User-ID"] = user_info.get("user_id", "")
        headers["X-User-Email"] = user_info.get("email", "")
        headers["X-Username"] = user_info.get("username", "")

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                content=body,
            )
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.headers.get("content-type")
            )
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")

@router.get("/health")
async def health():
    return JSONResponse({"status": "healthy", "service": "gateway"})

@router.api_route(
    "/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
)
async def proxy(request: Request, path: str):
    full_path = f"/{path}"

    service_url = get_service_url(full_path)
    if not service_url:
        raise HTTPException(status_code=404, detail="Route not found")

    if full_path in PUBLIC_PATHS:
        return await forward_request(request, service_url)

    user_info = await validate_request(request)
    identifier = user_info.get("key_id") or user_info.get("user_id", "anonymous")
    await check_rate_limit(identifier)

    return await forward_request(request, service_url, user_info)