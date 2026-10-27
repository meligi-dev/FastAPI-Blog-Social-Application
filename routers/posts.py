from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import models
from database import get_db
from schemas import PostCreate, PostResponse, PostUpdate


router = APIRouter()




@router.get("", response_model=list[PostResponse])
async def get_posts(db    :Annotated[AsyncSession,Depends(get_db)]):
    result = await db.execute(select(models.Post))
    posts = result.scalars().all()
    return posts



@router.post("",response_model=PostCreate,status_code=status.HTTP_201_CREATED)
async def Create_post(post:PostCreate,db :Annotated[AsyncSession,Depends(get_db)]):
    result = await db.execute(select(models.User).where(models.User.id == post.user_id))
    existing_user =result.scalars().first()
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="User not Found")
    
    new_post = models.Post(title=post.title,content=post.content,user_id = post.user_id)
    
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post,attribute_names=["author"])
    return new_post


@router.get("/{post_id}",response_model=PostResponse)
async def get_post(post_id:int,db :Annotated[AsyncSession,Depends(get_db)]): 
    result = await db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,detail=  "Post Not found")
    return post


@router.put("/{post_id}",response_model=PostResponse)
async def update_post_full(
    post_id:int,
    post_data : PostCreate,
    db:Annotated[AsyncSession,Depends(get_db)]
):
    result = await db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Post Not Found")


    result1 = await db.execute(select(models.User).where(models.User.id == post_data.user_id))
    existing_user = result1.scalars().first()
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="User Not Found")

    post.title = post_data.title
    post.user_id = post_data.user_id
    post.content = post_data.content
    await db.commit()
    await db.refresh(post)
    return post

@router.patch("/{post_id}",response_model=PostResponse)
async def update_post(
    post_id:int,
    post_data : PostUpdate,
    db:Annotated[AsyncSession,Depends(get_db)]
):
    result = await db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Post Not Found")


    update_post = post_data.model_dump(exclude_unset=True)
    for key, value in update_post.items():
        setattr(post, key, value)
    
    await db.commit()
    await db.refresh(post)
    return post


@router.delete("/{post_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id:int,db:Annotated[AsyncSession,Depends(get_db)]):
    result = await db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Post Not Found")
    
    await db.delete(post)
    await db.commit()

