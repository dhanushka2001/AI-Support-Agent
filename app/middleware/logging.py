import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        duration = (time.time() - start_time) * 1000  # ms

        method = request.method
        path = request.url.path

        print(f"[LOG] {method} {path} completed in {duration:.2f} ms")

        return response
