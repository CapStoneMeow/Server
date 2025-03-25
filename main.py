from fastapi import FastAPI
from database import Base, engine
from auth import auth_router

app = FastAPI()

# DB 테이블 생성
Base.metadata.create_all(bind=engine)

# 라우터 등록
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])

@app.get("/")
def root():
    return {"message": "AI 어휘 학습 서버 실행 중"}
