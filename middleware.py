from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import FastAPI, Body, Request
from starlette.responses import PlainTextResponse
from starlette.status import HTTP_413_REQUEST_ENTITY_TOO_LARGE


class LimitContentSizeMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_content_size: int):
        super().__init__(app)
        self.max_content_size = max_content_size

    async def dispatch(self, request: Request, call_next):
        if request.method == "POST" and request.headers.get("content-length"):
            content_length = int(request.headers["content-length"])
            if content_length > self.max_content_size:
                return PlainTextResponse(
                    "Request content too large",
                    status_code=HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                )
        response = await call_next(request)
        return response
