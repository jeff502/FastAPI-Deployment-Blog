from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, EmailStr



class UserBase(BaseModel):
    username: str = Field(min_length=
                          1, max_length=50)
    email: EmailStr = Field(max_length=120) # Email str will automatically validate if our email is an email. No min length required.


class UserResponse(UserBase):
    model_config = ConfigDict(
        from_attributes=True
    )  # Let's Pydantic not only read from a dictionary with foo["bar"], but also from a database with foo.bar

    id: int  # Only effects the local scope and is the convention instead of "_id"
    image_file: str | None
    image_path: str




class UserCreate(UserBase):
    pass

class PostBase(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1)
    


class PostResponse(PostBase):
    model_config = ConfigDict(
        from_attributes=True
    )  # Let's Pydantic not only read from a dictionary with foo["bar"], but also from a database with foo.bar

    id: int  # Only effects the local scope and is the convention instead of "_id"
    date_posted: datetime
    author: UserResponse # Pydantic will load the related user when a post is loaded


class PostCreate(PostBase):
    user_id: int # For testing. TEMPORARY

