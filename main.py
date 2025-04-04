from fastapi import FastAPI
from database import Base, engine
from auth import auth_router
from learning import learn_router

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# DB 테이블 생성
Base.metadata.create_all(bind=engine)

# 라우터 등록
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(learn_router, prefix="/api", tags=["Learning"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 프론트엔드 개발 서버 주소
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "AI 어휘 학습 서버 실행 중"}
