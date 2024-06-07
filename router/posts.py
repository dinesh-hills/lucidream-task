from typing import Annotated, List

from fastapi import APIRouter, Body, Depends, HTTPException, status

from cachetools import cached, TTLCache

from pydantic import BaseModel
from sqlalchemy.orm import Session

from dependencies.database import get_db
from dependencies.auth import get_current_user
from models import User


router = APIRouter()


class Post(BaseModel):
    id: int
    content: str
    user_id: int

    class Config:
        from_attributes = True


# In memory posts
TTL_POSTS_COUNT = 0
POSTS_INMEM: List[Post] = []


def add_post(post: Post):
    global TTL_POSTS_COUNT, POSTS_INMEM

    POSTS_INMEM.append(post)
    TTL_POSTS_COUNT += 1


# Create a cache with a TTL of 300 seconds (5 minutes) and a max size of 100 items
post_cache = TTLCache(maxsize=100, ttl=300)


@cached(post_cache)
def get_user_posts_from_memory(user_id: int) -> List[Post]:
    user_posts = [p for p in POSTS_INMEM if p.user_id == user_id]
    print("getting user posts")
    return user_posts


def invalidate_user_posts_cache(user_id: int):
    # Remove the cache entry for the user's posts
    key = (user_id,)
    if key in post_cache:
        del post_cache[key]


@router.get("/posts", response_model=List[Post])
def all_user_posts(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    # fetch posts from database
    # posts = current_user.fetch_posts(db)
    posts = get_user_posts_from_memory(current_user.id)
    return posts


@router.post("/posts")
def create_post(
    current_user: Annotated[User, Depends(get_current_user)],
    payload: str = Body(media_type="text/plain"),
):
    post_id = TTL_POSTS_COUNT + 1
    post = Post(id=post_id, content=payload, user_id=current_user.id)
    add_post(post=post)
    invalidate_user_posts_cache(current_user.id)
    return post_id


@router.delete("/posts/{post_id}")
def remove_post(post_id: int, current_user: Annotated[User, Depends(get_current_user)]):
    if len(POSTS_INMEM) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Detail not found"
        )
    post = [post for post in POSTS_INMEM if post.id == post_id]
    if post:
        deleted_post = POSTS_INMEM.pop(POSTS_INMEM.index(post[0]))
        invalidate_user_posts_cache(current_user.id)
        return deleted_post

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Detail not found"
    )
