from fastapi import FastAPI
from database import Base, engine
from auth import auth_router
from learning import learn_router
from test import test_router, pretest_router
from feedback import feedback_router
from predict_grade import grade_router
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import gdown
import os
import zipfile
import requests

# ✅ 환경 변수 로드
load_dotenv()

# ✅ 모델 자동 다운로드 + 압축 해제 함수
def download_model():
    model_dir = "./model/kobert"
    if os.path.exists(model_dir):
        print("✅ 모델이 이미 존재합니다. 다운로드 생략")
        return

    try:
        print("🔽 KoBERT 모델 다운로드 시작...")
        gdown.download(id="1S7i2VFQngrUO8zTZuuIj3l4FawaYAQO4", output="kobert_model.zip", quiet=False)
        with zipfile.ZipFile("kobert_model.zip", "r") as zip_ref:
            zip_ref.extractall("./model/")
        os.remove("kobert_model.zip")
        print("✅ 모델 다운로드 및 압축 해제 완료")
    except Exception as e:
        print("❌ 모델 다운로드/압축 해제 실패:", e)

# ✅ 모델 다운로드 먼저 수행
download_model()

# ✅ FastAPI 앱 초기화
app = FastAPI()

# ✅ DB 테이블 생성
Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "AI 어휘 학습 서버 실행 중"}

# ✅ 라우터 등록
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(learn_router, prefix="/api", tags=["Learning"])
app.include_router(test_router, prefix="/test")
app.include_router(feedback_router, prefix="/chat")
app.include_router(pretest_router, prefix="/pretest", tags=["Pretest"])
app.include_router(grade_router, prefix="/grade", tags=["GradePredict"])

# ✅ CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        # 배포 주소도 추가 가능
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
