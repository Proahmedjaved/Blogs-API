from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.user import User
from app.models.post import Post
from app.schemas.post import PostCreate, PostUpdate, Post as PostSchema
from app.core.dependencies import get_current_user
from app.cache.redis import get_cache, set_cache, invalidate_cache

router = APIRouter()

@router.post("/", response_model=PostSchema, status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_post = Post(title=post.title, content=post.content, author_id=current_user.id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    
    # Invalidate cache for all posts and user posts
    invalidate_cache("all_posts")
    invalidate_cache(f"user_posts:{current_user.id}")
    
    return db_post

@router.get("/", response_model=List[PostSchema])
def read_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    cache_key = f"all_posts:{skip}:{limit}"
    cached_posts = get_cache(cache_key)
    
    if cached_posts:
        return cached_posts
    
    posts = db.query(Post).offset(skip).limit(limit).all()
    
    # Convert posts to dict for caching using model_validate
    posts_data = [PostSchema.model_validate(post).model_dump() for post in posts]
    set_cache(cache_key, posts_data)
    
    return posts

@router.get("/me", response_model=List[PostSchema])
def read_user_posts(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cache_key = f"user_posts:{current_user.id}"
    cached_posts = get_cache(cache_key)
    
    if cached_posts:
        return cached_posts
    
    posts = db.query(Post).filter(Post.author_id == current_user.id).all()
    
    # Convert posts to dict for caching using model_validate
    posts_data = [PostSchema.model_validate(post).model_dump() for post in posts]
    set_cache(cache_key, posts_data)
    
    return posts

@router.get("/{post_id}", response_model=PostSchema)
def read_post(post_id: int, db: Session = Depends(get_db)):
    cache_key = f"post:{post_id}"
    cached_post = get_cache(cache_key)
    
    if cached_post:
        return cached_post
    
    post = db.query(Post).filter(Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Convert post to dict for caching using model_validate
    post_data = PostSchema.model_validate(post).model_dump()
    set_cache(cache_key, post_data)
    
    return post

@router.put("/{post_id}", response_model=PostSchema)
def update_post(
    post_id: int, 
    post_update: PostUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if db_post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this post")
    
    # Update post fields if provided
    for key, value in post_update.model_dump(exclude_unset=True).items():
        setattr(db_post, key, value)
    
    db.commit()
    db.refresh(db_post)
    
    # Invalidate cache
    invalidate_cache(f"post:{post_id}")
    invalidate_cache("all_posts")
    invalidate_cache(f"user_posts:{current_user.id}")
    
    return db_post

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if db_post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")
    
    db.delete(db_post)
    db.commit()
    
    # Invalidate cache
    invalidate_cache(f"post:{post_id}")
    invalidate_cache("all_posts")
    invalidate_cache(f"user_posts:{current_user.id}")
    
    return None 