from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# FastAPI 라우터
test_router = APIRouter()

# 요청 형식 정의
class TestInput(BaseModel):
    user_id: int
    category: str
    answer_text: str  # 사용자 자유 응답 전체 (Clova와의 대화 후)

# 응답 형식 예시
class TestResult(BaseModel):
    predicted_grade: int
    reason: str

@test_router.post("/evaluate", response_model=TestResult)
def evaluate_test(input_data: TestInput):
    # ✅ KoBERT 미사용 시 Mock 예측
    dummy_grade = 4
    dummy_reason = "임시 예측 결과입니다. 실제 KoBERT 모델 연결 전까지는 4학년으로 고정 반환합니다."

    return TestResult(
        predicted_grade=dummy_grade,
        reason=dummy_reason
    )
