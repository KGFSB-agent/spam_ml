from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db, Base, SessionLocal, engine
from schemas import UserCreate, UserLogin, PredictionRequest
from models import User, PredictionHistory
from ml_models.models.basic_model import BasicSpamModel
from ml_models.models.medium_model import MediumSpamModel
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from security import SECRET_KEY, ALGORITHM, verify_password, create_access_token, credentials_exception, get_password_hash
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from fastapi.security import OAuth2PasswordRequestForm


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")  # Используем email вместо username
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Получаем пользователя из БД по email
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user


# Регистрация пользователя
@app.post("/register")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
    
    hashed_password = get_password_hash(user.password)
    new_user = User(
        email=user.email,
        hashed_password=hashed_password,
        balance=1000.0
    )
    db.add(new_user)
    db.commit()
    return {"message": "Пользователь успешно создан"}


# Эндпоинт для получения токена (OAuth2 стандарт)
@app.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/balance")
async def get_balance(
    current_user: User = Depends(get_current_user)
):
    return {"balance": current_user.balance}


@app.post("/add_credits")
async def add_credits(
    amount: float,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    current_user.balance += amount
    db.commit()
    return {"message": "Баланс пополнен", "new_balance": current_user.balance}


# Prediction endpoint
@app.post("/predict")
async def predict(
    request: PredictionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # TODO: реализовать
):
    # Выбор модели и стоимости
    model_map = {
        "basic": (BasicSpamModel, 100),
        "medium": (MediumSpamModel, 250)
    }

    if request.model_type not in model_map:
        raise HTTPException(
            status_code=400, 
            detail="Invalid model type. Use 'basic' or 'medium'."
        )
    
    model_class, cost = model_map[request.model_type]

    # Проверка баланса
    if current_user.balance < cost:
        raise HTTPException(status_code=400, detail="Недостаточно средств")

    # Предсказание
    model = model_class()
    is_spam = model.predict(request.text)
    
    # Списание средств
    current_user.balance -= cost
    db.commit()
    
    # Логирование
    db_prediction = PredictionHistory(
        user_id=current_user.id,
        text=request.text,
        model_type=request.model_type,
        is_spam=is_spam,
        cost=cost
    )
    db.add(db_prediction)
    db.commit()
    
    return {"is_spam": is_spam, "remaining_balance": current_user.balance}


@app.get("/prediction_history")
async def get_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    history = db.query(PredictionHistory).filter(
        PredictionHistory.user_id == current_user.id
    ).all()
    return history
