from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UniqueConstraint, Boolean, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)

    learned_words = relationship("LearnedWord", back_populates="user")
    pretest_responses = relationship("PretestResponse", back_populates="user")


class LearnedWord(Base):
    __tablename__ = "learned_words"

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String, nullable=False)
    level = Column(Integer)
    learned_at = Column(DateTime, default=datetime.utcnow)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="learned_words")

    __table_args__ = (UniqueConstraint("user_id", "word", name="user_word_unique"),)

class QuizHistory(Base):
    __tablename__ = "quiz_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    word = Column(String, nullable=False)
    level = Column(Integer)
    category = Column(String)
    selected_index = Column(Integer, nullable=False)
    answer_index = Column(Integer, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    round = Column(Integer, default=1)
    timestamp = Column(DateTime, default=datetime.utcnow)

class PretestResponse(Base):
    __tablename__ = "pretest_responses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category = Column(String, nullable=False)
    question = Column(Text, nullable=False)
    answer_text = Column(Text, nullable=False)
    predicted_grade = Column(Integer, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="pretest_responses")

class LearningRecord(Base):
    __tablename__ = "learning_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    word = Column(String)
    sentence = Column(String)
    score = Column(Float)
    suggestion = Column(String)