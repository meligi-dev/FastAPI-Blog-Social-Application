from typing import Annotated
from contextlib import asynccontextmanager
from fastapi.exception_handlers import http_exception_handler,request_validation_exception_handler
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette.exceptions import HTTPException as StarletteHTTPException

import models
from database import Base, engine, get_db
from schemas import (
    PostCreate,
    PostResponse,
    PostUpdate,
    UserCreate,
    UserResponse,
    UserUpdate,
)

@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose() 


app = FastAPI(lifespan = lifespan)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/media",StaticFiles(directory="media"),name = "media")


@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts")
async def home(request: Request, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Post).options(selectinload(models.Post.author)))
    posts = result.scalars().all()
    return templates.TemplateResponse(
        request,
        "home.html",
        {"posts": posts, "title": "Home"},
    )


@app.get("/posts/{post_id}", include_in_schema=False)
async def post_page(request: Request, post_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Post).options(selectinload(models.Post.author)).where(models.Post.id == post_id))
    post = result.scalars().first()
    if post:
        title = post.title[:50]
        return templates.TemplateResponse(
            request,
            "post.html",
            {"post": post, "title": title},
        )
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

@app.get("/users/{user_id}/posts", include_in_schema=False, name="user_posts")
async def user_posts_page(
    request: Request,
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    result = await db.execute(select(models.Post).options(selectinload(models.Post.author)).where(models.Post.user_id == user_id))
    posts = result.scalars().all()
    return templates.TemplateResponse(
        request,
        "user_posts.html",
        {"posts": posts, "user": user, "title": f"{user.username}'s Posts"},
    )


@app.post("/api/user",response_model=UserCreate,status_code=status.HTTP_201_CREATED)
async def create_user(user:UserCreate,db:Annotated[AsyncSession,Depends(get_db)]):

    result = await db.execute(select(models.User).where(models.User.username == user.username))
    existing_user =  result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Username already exists")



    result2 = await db.execute(select(models.User).where(models.User.email == user.email))
    existing_email = result2.scalars().first()
    if existing_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Email already exists")

    new_user = models.User(
        username = user.username,
        email = user.email,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@app.get("/api/users/{user_id}",response_model=UserResponse)
async def get_user(user_id:int,db:Annotated[AsyncSession,Depends(get_db)]):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    return user


@app.put("/api/users/{user_id}",response_model=UserResponse)
async def update_user_full(
    user_id:int,user_data:UserCreate,
    db:Annotated[AsyncSession,Depends(get_db)]
):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")

    result1 = await db.execute(select(models.User).where(models.User.email == user_data.email))
    existing_email = result1.scalars().first()
    if existing_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Email already exists")

    user.username = user_data.username
    user.email = user_data.email
    await db.commit()
    await db.refresh(user)
    return user


@app.patch("/api/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    result1 = await db.execute(select(models.User).where(models.User.email == user_data.email))
    existing_email = result1.scalars().first()
    if existing_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Email already exists")
    update_user = user_data.model_dump(exclude_unset=True)
    for key, value in update_user.items():
        setattr(user, key, value)

    await db.commit()
    await db.refresh(user)
    return user


@app.delete("/api/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    await db.delete(user)
    await db.commit()

@app.get("/api/user/{user_id}/posts", response_model=list[PostResponse])
async def get_user_posts(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not Found")

    result2 = await db.execute(select(models.Post).options(selectinload(models.Post.author)).where(models.Post.user_id == user_id))
    posts = result2.scalars().all()
    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Posts Not Found")
    return posts


@app.get("/api/posts", response_model=list[PostResponse])
async def get_posts(db    :Annotated[AsyncSession,Depends(get_db)]):
    result = await db.execute(select(models.Post))
    posts = result.scalars().all()
    return posts



@app.post("/api/posts",response_model=PostCreate,status_code=status.HTTP_201_CREATED)
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


@app.get("/api/posts/{post_id}",response_model=PostResponse)
async def get_post(post_id:int,db :Annotated[AsyncSession,Depends(get_db)]): 
    result = await db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,detail=  "Post Not found")
    return post


@app.put("/api/posts/{post_id}",response_model=PostResponse)
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

@app.patch("/api/posts/{post_id}",response_model=PostResponse)
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


@app.delete("/api/posts/{post_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id:int,db:Annotated[AsyncSession,Depends(get_db)]):
    result = await db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Post Not Found")
    
    await db.delete(post)
    await db.commit()



## StarletteHTTPException Handler
@app.exception_handler(StarletteHTTPException)
async def general_http_exception_handler(request: Request, exception: StarletteHTTPException):
    

    if request.url.path.startswith("/api"):
        return await http_exception_handler(request,exception)
    
    message = (
        exception.detail
        if exception.detail
        else "An error occurred. Please check your request and try again."
    )
    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": exception.status_code,
            "title": exception.status_code,
            "message": message,
        },
        status_code=exception.status_code,
    )


### RequestValidationError Handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exception: RequestValidationError):
    if request.url.path.startswith("/api"):
        return await request_validation_exception_handler(request, exception)
    
    
    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": "Invalid request. Please check your input and try again.",
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )