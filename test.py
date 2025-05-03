from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime
from database import SessionLocal
from model import PretestResponse

# FastAPI 라우터 생성
pretest_router = APIRouter()
test_router = APIRouter()

# ========================== 요청/응답 모델 ==========================

class PretestInput(BaseModel):
    user_id: int
    category: str
    answer_text: str

class PretestResponseOutput(BaseModel):
    id: int
    user_id: int
    category: str
    answer_text: str
    timestamp: datetime

# ========================== 사전 테스트 응답 저장 ==========================

@pretest_router.post("/response", response_model=PretestResponseOutput)
def save_pretest_response(input_data: PretestInput):
    db = SessionLocal()
    try:
        new_response = PretestResponse(
            user_id=input_data.user_id,
            category=input_data.category,
            answer_text=input_data.answer_text,
            timestamp=datetime.now()
        )
        db.add(new_response)
        db.commit()
        db.refresh(new_response)
        return new_response
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"DB 저장 오류: {str(e)}")
    finally:
        db.close()

# ========================== 사용자 응답 목록 조회 ==========================

@pretest_router.get("/responses/{user_id}", response_model=List[PretestResponseOutput])
def get_user_responses(user_id: int):
    db = SessionLocal()
    try:
        responses = db.query(PretestResponse).filter(PretestResponse.user_id == user_id).all()
        return responses
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB 조회 오류: {str(e)}")
    finally:
        db.close()

# ========================== 자유응답 → 학년 예측 테스트 (Mock) ==========================

class TestInput(BaseModel):
    user_id: int
    category: str
    answer_text: str  # 사용자 자유 응답 전체 (Clova와의 대화 후)

class TestResult(BaseModel):
    predicted_grade: int
    reason: str

@pretest_router.post("/evaluate", response_model=TestResult)
def evaluate_test(input_data: TestInput):
    #Mock 예측
    dummy_grade = 4
    dummy_reason = "임시 예측 결과입니다. 실제 KoBERT 모델 연결 전까지는 4학년으로 고정 반환합니다."

    return TestResult(
        predicted_grade=dummy_grade,
        reason=dummy_reason
    )
