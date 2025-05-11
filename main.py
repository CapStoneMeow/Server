from fastapi import FastAPI
from database import Base, engine
from auth import auth_router
from learning import learn_router
from test import test_router, pretest_router
from feedback import feedback_router
from predict_grade import grade_router
from dotenv import load_dotenv

import os
import zipfile
import requests
from fastapi.middleware.cors import CORSMiddleware

# ✅ .env 로드
load_dotenv()

# ✅ 모델 자동 다운로드 함수
def download_model():
    model_dir = "./saved_models/fine_tuned_kobert_book_all/checkpoint-3198"
    if os.path.exists(model_dir):
        print("✅ 모델이 이미 존재합니다. 다운로드 생략")
        return

    print("🔽 KoBERT 모델 다운로드 시작...")

    # 📌 Google Drive에서 공유한 zip 파일 ID를 넣어주세요
    # 예시: https://drive.google.com/file/d/1ABCxyz123456789/view → id=1ABCxyz123456789
    file_id = "1sIsreomr2kGCge50cd358r7NX8aLwNzl"
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    zip_path = "kobert_model.zip"

    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(zip_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall("./saved_models/")

        os.remove(zip_path)
        print("✅ 모델 다운로드 및 압축 해제 완료")
    except Exception as e:
        print("❌ 모델 다운로드 실패:", e)

# ✅ 서버 시작 전에 모델 다운로드 시도
download_model()

# ✅ FastAPI 인스턴스 생성
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
        "http://localhost:5174",
        "http://localhost:5173",
        # 배포용 프론트 주소도 여기에 추가 가능
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
