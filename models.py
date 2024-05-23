from typing import List, Union
from pydantic import BaseModel, Field

class MCQ(BaseModel):
    question: str = Field(description="Multiple Choice Question")
    options: List[str] = Field(description="List of options for the MCQ")
    correct_option: int = Field(description="Index of the correct option")

class TrueFalse(BaseModel):
    question: str = Field(description="True/False Question")
    options: List[str] = Field(description="List of options for the True False")
    correct_answer: bool = Field(description="Correct answer (True/False)")
    explanation: str = Field(description="Explanation of the correct answer")

class ShortAnswer(BaseModel):
    question: str = Field(description="Short Answer Question")
    correct_answer: str = Field(description="Correct answer to the question")

# Arrays to hold multiple questions and the story
class MCQArray(BaseModel):
    story: str
    mcqs: List[MCQ]

class TrueFalseArray(BaseModel):
    story: str
    true_false_questions: List[TrueFalse]

class ShortAnswerArray(BaseModel):
    story: str
    short_answer_questions: List[ShortAnswer]

