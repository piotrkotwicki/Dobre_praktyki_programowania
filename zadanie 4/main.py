from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
import auth
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="System JWT + CRUD")

@app.post("/users", response_model=schemas.UserDetails, status_code=status.HTTP_201_CREATED)
def create_user(user_data: schemas.UserCreate, db: Session = Depends(get_db), _=Depends(auth.require_admin_role)):
    if db.query(models.User).filter(models.User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = auth.hash_password(user_data.password)
    new_user = models.User(username=user_data.username, hashed_password=hashed_password, roles=",".join(user_data.roles))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return schemas.UserDetails(username=new_user.username, roles=user_data.roles)

@app.post("/login", response_model=schemas.Token)
def login_for_access_token(data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == data.username).first()
    if not user or not auth.verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = auth.create_access_token(data={"sub": user.username, "roles": user.roles.split(',')})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/user_details", response_model=schemas.UserDetails)
def get_user_details(payload: schemas.TokenPayload = Depends(auth.get_current_user_payload)):
    return schemas.UserDetails(username=payload.sub, roles=payload.roles)

def get_object_or_404(db, model, id):
    obj = db.query(model).filter(model.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail=f"{model.__name__} not found")
    return obj

@app.post("/movies", response_model=schemas.Movie, status_code=201)
def create_movie(item: schemas.MovieCreate, db: Session = Depends(get_db)):
    db_item = models.Movie(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/movies", response_model=List[schemas.Movie])
def read_movies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Movie).offset(skip).limit(limit).all()

@app.get("/movies/{id}", response_model=schemas.Movie)
def read_movie(id: int, db: Session = Depends(get_db)):
    return get_object_or_404(db, models.Movie, id)

@app.put("/movies/{id}", response_model=schemas.Movie)
def update_movie(id: int, item: schemas.MovieCreate, db: Session = Depends(get_db)):
    db_item = get_object_or_404(db, models.Movie, id)
    for key, value in item.dict().items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/movies/{id}", status_code=204)
def delete_movie(id: int, db: Session = Depends(get_db)):
    db_item = get_object_or_404(db, models.Movie, id)
    db.delete(db_item)
    db.commit()

@app.post("/links", response_model=schemas.Link, status_code=201)
def create_link(item: schemas.LinkCreate, db: Session = Depends(get_db)):
    db_item = models.Link(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/links", response_model=List[schemas.Link])
def read_links(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Link).offset(skip).limit(limit).all()

@app.get("/links/{id}", response_model=schemas.Link)
def read_link(id: int, db: Session = Depends(get_db)):
    return get_object_or_404(db, models.Link, id)

@app.put("/links/{id}", response_model=schemas.Link)
def update_link(id: int, item: schemas.LinkCreate, db: Session = Depends(get_db)):
    db_item = get_object_or_404(db, models.Link, id)
    for key, value in item.dict().items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/links/{id}", status_code=204)
def delete_link(id: int, db: Session = Depends(get_db)):
    db_item = get_object_or_404(db, models.Link, id)
    db.delete(db_item)
    db.commit()

@app.post("/ratings", response_model=schemas.Rating, status_code=201)
def create_rating(item: schemas.RatingCreate, db: Session = Depends(get_db)):
    db_item = models.Rating(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/ratings", response_model=List[schemas.Rating])
def read_ratings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Rating).offset(skip).limit(limit).all()

@app.get("/ratings/{id}", response_model=schemas.Rating)
def read_rating(id: int, db: Session = Depends(get_db)):
    return get_object_or_404(db, models.Rating, id)

@app.put("/ratings/{id}", response_model=schemas.Rating)
def update_rating(id: int, item: schemas.RatingCreate, db: Session = Depends(get_db)):
    db_item = get_object_or_404(db, models.Rating, id)
    for key, value in item.dict().items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/ratings/{id}", status_code=204)
def delete_rating(id: int, db: Session = Depends(get_db)):
    db_item = get_object_or_404(db, models.Rating, id)
    db.delete(db_item)
    db.commit()

@app.post("/tags", response_model=schemas.Tag, status_code=201)
def create_tag(item: schemas.TagCreate, db: Session = Depends(get_db)):
    db_item = models.Tag(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/tags", response_model=List[schemas.Tag])
def read_tags(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Tag).offset(skip).limit(limit).all()

@app.get("/tags/{id}", response_model=schemas.Tag)
def read_tag(id: int, db: Session = Depends(get_db)):
    return get_object_or_404(db, models.Tag, id)

@app.put("/tags/{id}", response_model=schemas.Tag)
def update_tag(id: int, item: schemas.TagCreate, db: Session = Depends(get_db)):
    db_item = get_object_or_404(db, models.Tag, id)
    for key, value in item.dict().items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/tags/{id}", status_code=204)
def delete_tag(id: int, db: Session = Depends(get_db)):
    db_item = get_object_or_404(db, models.Tag, id)
    db.delete(db_item)
    db.commit()