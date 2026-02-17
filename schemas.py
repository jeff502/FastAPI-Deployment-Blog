from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, EmailStr


class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(
        max_length=120
    )  # Email str will automatically validate if our email is an email. No min length required.


class UserPublic(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )  # Let's Pydantic not only read from a dictionary with foo["bar"], but also from a database with foo.bar

    id: int  # Only effects the local scope and is the convention instead of "_id"
    username: str
    image_file: str | None
    image_path: str


class UserPrivate(UserPublic):
    email: EmailStr


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=1, max_length=50)
    email: EmailStr | None = Field(
        default=None, max_length=120
    )  # Email str will automatically validate if our email is an email. No min length required.
    image_file: str | None = Field(default=None, min_length=1, max_length=200)


class Token(BaseModel):
    access_token: str
    token_type: str


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=120)


class PostBase(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1)


class PostResponse(PostBase):
    model_config = ConfigDict(
        from_attributes=True
    )  # Let's Pydantic not only read from a dictionary with foo["bar"], but also from a database with foo.bar

    id: int  # Only effects the local scope and is the convention instead of "_id"
    date_posted: datetime
    author: UserPublic  # Pydantic will load the related user when a post is loaded


class PostCreate(PostBase):
    user_id: int  # For testing. TEMPORARY


class PostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    content: str | None = Field(default=None, min_length=1)
