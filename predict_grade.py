from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from kobert_predictor import predict_grade

grade_router = APIRouter()

class BulkAnswerInput(BaseModel):
    answers: List[str]

@grade_router.post("/predict_grade_bulk")
def predict_grade_bulk(input_data: BulkAnswerInput):
    if len(input_data.answers) != 4:
        raise HTTPException(status_code=400, detail="총 4개의 답변이 필요합니다.")

    preds = [predict_grade(a)["label_index"] for a in input_data.answers]
    final = round(sum(preds) / 4)
    label_map = {0: "초등_저학년", 1: "초등_고학년"}

    return {
        "predicted_grade": label_map[final],
        "label_index": final,
        "individual_predictions": preds
    }
