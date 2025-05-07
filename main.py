from fastapi import FastAPI, Depends, HTTPException, status, Request, Body
from sqlalchemy.orm import Session
from db.database import get_db, Base, engine
from db.schemas import UserCreate, PredictionRequest
from db.models import User, PredictionHistory
from ml_models.models.basic_model import BasicSpamModel
from ml_models.models.medium_model import MediumSpamModel
from ml_models.models.premium_model import PremiumSpamModel
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from security import SECRET_KEY, ALGORITHM, verify_password, create_access_token, get_password_hash
from contextlib import asynccontextmanager
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from fastapi.responses import HTMLResponse


static_path = str(Path("frontend") / "static")
templates_path = str(Path("frontend") / "templates")


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app.mount("/static", StaticFiles(directory=static_path), name="static")
templates = Jinja2Templates(directory=templates_path)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


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
    amount: float = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    current_user.balance += amount
    db.commit()
    return {"message": "Баланс пополнен", "new_balance": current_user.balance}


@app.post("/predict")
async def predict(
    request: PredictionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        model_map = {
            "basic": (BasicSpamModel, 100),
            "medium": (MediumSpamModel, 250),
            "premium": (PremiumSpamModel, 500)
        }
        
        if request.model_type not in model_map:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Недопустимый тип модели. Используйте 'basic', 'medium' или 'premium'."
            )
        
        model_class, cost = model_map[request.model_type]
        
        if current_user.balance < cost:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Недостаточно средств"
            )
        
        try:
            model = model_class()
        except FileNotFoundError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Модель {request.model_type} недоступна: {str(e)}"
            )
        
        # Предсказание
        try:
            is_spam = model.predict(request.text)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка предсказания: {str(e)}"
            )
        
        current_user.balance -= cost
        db.commit()
        
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

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Неизвестная ошибка: {str(e)}"
        )


@app.get("/prediction_history")
async def get_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    history = db.query(PredictionHistory).filter(
        PredictionHistory.user_id == current_user.id
    ).all()
    return history
