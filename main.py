import logging

from fastapi import FastAPI
from middleware import LimitContentSizeMiddleware
from router.users import router as users_router
from router.posts import router as posts_router

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

app = FastAPI()

# 1 MB = 1 * 1024 * 1024 bytes
app.add_middleware(LimitContentSizeMiddleware, max_content_size=1 * 1024 * 1024)

app.include_router(users_router)
app.include_router(posts_router)
