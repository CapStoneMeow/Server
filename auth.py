from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from database import get_db
from model import User
from passlib.context import CryptContext
from jose import jwt
import datetime

auth_router = APIRouter()

# 비밀번호 암호화 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT 설정
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60 * 24

# 비밀번호 해싱
def hash_password(password: str):
    return pwd_context.hash(password)

# 비밀번호 비교
def verify_password(plain_pw, hashed_pw):
    return pwd_context.verify(plain_pw, hashed_pw)

# 토큰 생성
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@auth_router.post("/signup")
def signup(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    checkpassword: str = Form(...),
    db: Session = Depends(get_db)
):
    if password != checkpassword:
        raise HTTPException(status_code=400, detail="비밀번호가 일치하지 않습니다.")

    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="이미 등록된 이메일입니다.")

    hashed_pw = hash_password(password)
    new_user = User(email=email, password=hashed_pw, username=username)
    db.add(new_user)
    db.commit()
    return {"message": "회원가입 완료"}

@auth_router.post("/login")
def login(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=400, detail="이메일 또는 비밀번호가 일치하지 않습니다.")

    token = create_access_token(data={"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}
