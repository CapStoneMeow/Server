from datetime import datetime

from fastapi import APIRouter, Query, Depends, Body
from sqlalchemy.orm import Session
from database import get_db
from model import LearnedWord
from model import QuizHistory
import pandas as pd
import random
import re

learn_router = APIRouter()

# ✅ 학습한 단어 조회 API
@learn_router.get("/learned-words/")
def get_learned_words(user_id: int, db: Session = Depends(get_db)):
    words = db.query(LearnedWord).filter(LearnedWord.user_id == user_id).all()
    return words

# ✅ 단어 데이터 불러오기
df = pd.read_csv("words_dataset.csv", encoding="utf-8-sig")

# ✅ 의미 클린업 함수
def clean_meaning(text):
    first_line = str(text).split("\n")[0]
    return re.sub(r"[「\[\(]?[Ⅰ1-9]+[」\]\)]?\.?", "", first_line).strip()

# ✅ 10문제 퀴즈 제공 API
@learn_router.get("/words")
def get_quiz_list(category: str = Query(...), level: int = Query(...)):
    filtered = df[
        (df["category"] == category) & (df["level"] == level)
    ].reset_index(drop=True)

    if len(filtered) < 13:
        return {"message": "해당 조건에 단어가 충분하지 않습니다."}

    # 정답 후보 10개 무작위 선택
    quiz_words = filtered.sample(n=10).reset_index(drop=True)
    remaining = filtered.drop(quiz_words.index)  # 오답 후보

    quiz_list = []

    for _, row in quiz_words.iterrows():
        correct_word = row["word"]
        correct_meaning = clean_meaning(row["meaning"])

        # 오답 3개 무작위 선택
        wrong_meanings = remaining.sample(n=3)["meaning"].apply(clean_meaning).tolist()

        # 정답 포함 보기 섞기
        options = wrong_meanings + [correct_meaning]
        random.shuffle(options)
        answer_index = options.index(correct_meaning)

        quiz_list.append({
            "word": correct_word,
            "options": options,           # 뜻(의미)들
            "answer_index": answer_index  # 정답 뜻 위치
        })

    return quiz_list

@learn_router.post("/quiz/submit")
def submit_quiz(
    user_id: int = Body(...),
    word: str = Body(...),
    level: int = Body(...),
    category: str = Body(...),
    selected_index: int = Body(...),
    answer_index: int = Body(...),
    is_correct: bool = Body(...),
    round: int = Body(...),
    db: Session = Depends(get_db)
):
    record = QuizHistory(
        user_id=user_id,
        word=word,
        level=level,
        category=category,
        selected_index=selected_index,
        answer_index=answer_index,
        is_correct=is_correct,
        round=round,
        timestamp=datetime.utcnow()
    )
    db.add(record)
    db.commit()
    return {"message": "학습 기록 저장 완료 ✅"}
