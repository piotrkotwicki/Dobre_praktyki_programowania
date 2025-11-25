from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import models
import schemas
import auth
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="System Zabezpieczeń JWT",
    description="Implementacja logowania i autoryzacji opartej na JWT.",
    version="1.0"
)
@app.post("/users", response_model=schemas.UserDetails, status_code=status.HTTP_201_CREATED)
def create_user(
        user_data: schemas.UserCreate,
        db: Session = Depends(get_db),
        _=Depends(auth.require_admin_role)
):
    db_user = db.query(models.User).filter(models.User.username == user_data.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = auth.hash_password(user_data.password)

    roles_str = ",".join(user_data.roles)

    new_user = models.User(
        username=user_data.username,
        hashed_password=hashed_password,
        roles=roles_str
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return schemas.UserDetails(username=new_user.username, roles=user_data.roles)

@app.post("/login", response_model=schemas.Token)
def login_for_access_token(
        data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.username == data.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    if not auth.verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    user_roles = user.roles.split(',')

    payload_data = {
        "sub": user.username,
        "roles": user_roles
    }

    token = auth.create_access_token(data=payload_data)

    return {"access_token": token, "token_type": "bearer"}


@app.get("/user_details", response_model=schemas.UserDetails)
def get_user_details(
        payload: schemas.TokenPayload = Depends(auth.get_current_user_payload)
):

    return schemas.UserDetails(username=payload.sub, roles=payload.roles)