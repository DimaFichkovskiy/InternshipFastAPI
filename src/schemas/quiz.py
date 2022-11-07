from typing import List
from pydantic import BaseModel, validator
from fastapi import HTTPException


class Question(BaseModel):
    question: str
    answer_options: list
    correct_answer: int

    @validator('answer_options')
    def number_of_answers(cls, v):
        if len(v) < 2:
            raise HTTPException(status_code=400, detail="Not enough answers")
        return v


class Quiz(BaseModel):
    id: int
    title: str
    description: str
    passing_frequency: int

    class Config:
        orm_mode = True


class CreateQuiz(BaseModel):
    title: str
    description: str
    passing_frequency: int
    list_questions: List[Question]

    @validator('list_questions')
    def number_of_questions(cls, v):
        if len(v) < 2:
            raise HTTPException(status_code=400, detail="Not enough questions")
        return v


class AnswerResponse(BaseModel):
    id: int
    answer: str
    is_correct: bool

    class Config:
        orm_mode = True


class QuestionsResponse(BaseModel):
    id: int
    question: str
    answer_options: List[AnswerResponse]

    class Config:
        orm_mode = True


class QuizResponse(BaseModel):
    id: int
    title: str
    description: str
    passing_frequency: int
    list_questions: List[QuestionsResponse]

    class Config:
        orm_mode = True
