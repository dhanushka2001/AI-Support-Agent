from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette import status

MAX_UPLOAD_SIZE = 20 * 1024 * 1024  # 20MB

class LimitUploadSizeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > MAX_UPLOAD_SIZE:
            response = JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content={"detail": {"error": "20MB file upload limit exceeded"}},
            )
            # Add CORS headers manually
            response.headers["Access-Control-Allow-Origin"] = "http://localhost:5173"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            return response
        return await call_next(request)
