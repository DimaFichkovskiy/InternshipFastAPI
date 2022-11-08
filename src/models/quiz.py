from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from .worker import Worker
from src.database import Base


class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    title = Column(String)
    description = Column(String)
    passing_frequency = Column(Integer)
    number_of_questions = Column(Integer)

    company = relationship("Company", back_populates="quizzes")
    questions = relationship("Question", back_populates="quiz")


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"))
    question = Column(String)

    quiz = relationship("Quiz", back_populates="questions")
    answers = relationship("Answer", back_populates="question")


class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey("questions.id"))
    answer = Column(String)
    is_correct = Column(Boolean, default=False)

    question = relationship("Question", back_populates="answers")
