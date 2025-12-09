from pydantic import BaseModel
from typing import List, Optional

class UserCreate(BaseModel):
    username: str
    password: str
    roles: Optional[List[str]] = ["ROLE_USER"]

class LoginData(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: str
    exp: Optional[int] = None
    roles: List[str] = []

class UserDetails(BaseModel):
    username: str
    roles: List[str]
    class Config:
        from_attributes = True

class MovieBase(BaseModel):
    title: str
    genres: str

class MovieCreate(MovieBase):
    pass

class Movie(MovieBase):
    id: int
    class Config:
        from_attributes = True

class LinkBase(BaseModel):
    movie_id: int
    imdb_id: str
    tmdb_id: str

class LinkCreate(LinkBase):
    pass

class Link(LinkBase):
    id: int
    class Config:
        from_attributes = True

class RatingBase(BaseModel):
    user_id: int
    movie_id: int
    rating: float
    timestamp: int

class RatingCreate(RatingBase):
    pass

class Rating(RatingBase):
    id: int
    class Config:
        from_attributes = True

class TagBase(BaseModel):
    user_id: int
    movie_id: int
    tag: str
    timestamp: int

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    id: int
    class Config:
        from_attributes = True