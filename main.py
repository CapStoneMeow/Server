from fastapi import FastAPI
from database import Base, engine
from auth import auth_router
from learning import learn_router
from test import test_router, pretest_router
from feedback import feedback_router
from predict_grade import grade_router
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

import os
import zipfile
import requests

# ✅ 환경 변수 로드
load_dotenv()

# ✅ 모델 자동 다운로드 + 압축 해제 함수
def download_and_extract_model():
    model_dir = "./model/kobert"
    if os.path.exists(model_dir):
        print("✅ 모델 디렉토리 존재. 다운로드 생략")
        return

    print("🔽 KoBERT 모델 다운로드 시작...")

    file_id = "1UTMDO5l7YvkpVNAZjQbHnLKwFf1NAeef"  # ← 사용자의 Google Drive zip 파일 ID
    zip_path = "kobert_model.zip"
    url = "https://docs.google.com/uc?export=download&id=1UTMDO5l7YvkpVNAZjQbHnLKwFf1NAeef"

    try:
        # 다운로드
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(zip_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        # 압축 해제
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall("./model")

        os.remove(zip_path)
        print("✅ 모델 다운로드 및 압축 해제 완료")
    except Exception as e:
        print("❌ 모델 다운로드/압축 해제 실패:", e)

# ✅ 모델 다운로드 먼저 수행
download_and_extract_model()

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
