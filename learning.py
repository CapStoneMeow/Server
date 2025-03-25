# ✅ learning.py (또는 learned_words.py 등으로 분리)
from fastapi import APIRouter, Depends, Form
from sqlalchemy.orm import Session
from database import get_db
from model import LearnedWord

learn_router = APIRouter()

# ✅ 학습한 단어 조회 API
@learn_router.get("/learned-words/")
def get_learned_words(user_id: int, db: Session = Depends(get_db)):
    words = db.query(LearnedWord).filter(LearnedWord.user_id == user_id).all()
    return words
