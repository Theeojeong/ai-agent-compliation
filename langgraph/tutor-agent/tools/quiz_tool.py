from langchain_core.tools import tool
from typing import Literal, List
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field


class Question(BaseModel):
    question: str = Field(description="퀴즈 질문 텍스트")
    options: List[str] = Field(
        description="정확히 4개의 객관식 옵션, A, B, C, D로 레이블됨."
    )
    correct_answer: str = Field(
        description="정답 ('options' 중 하나와 반드시 일치해야 함)"
    )
    explanation: str = Field(
        description="정답이 맞는 이유와 다른 객관식 옵션이 틀린 이유에 대한 설명."
    )


class Quiz(BaseModel):
    topic: str = Field(description="테스트하려는 주요 주제")
    questions: List[Question] = Field(description="퀴즈 질문 목록들")


@tool
def generate_quiz(
    research_text: str,
    topic: str,
    difficulty: Literal["easy", "medium", "hard"],
    num_questions: int,
):
    """
    조사 정보를 기반으로 객관식 질문이 있는 구조화된 퀴즈를 생성합니다.

    Args:
        research_text: str - 주제에 대한 조사 정보. 다음이 가능합니다:
                      - 웹 검색의 원시 텍스트
                      - 조사 결과의 요약
                      - 주제에 대한 모든 관련 정보
                      - 비어있으면 일반 지식에서 질문을 생성합니다

        topic: str - 퀴즈의 주요 주제/과목 (예: "Python 프로그래밍", "제2차 세계대전", "광합성")

        difficulty: Literal["easy", "medium", "hard"] - 난이도 수준:
                   - "easy": 기본 개념, 정의, 간단한 사실
                   - "medium": 개념의 적용, 아이디어 간 연결
                   - "hard": 복잡한 분석, 종합, 고급 이해

        num_questions: int - 생성할 질문 개수 (1-30 사이)
                      일반적인 값: 3-5 (짧게), 6-10 (중간), 11-15 (길게)

    Returns:
        구조화된 질문이 있는 Quiz 객체, 각각 다음을 포함:
        - question: 질문 텍스트
        - options: 4개의 객관식 답변 목록
        - correct_answer: 정답 (옵션 중 하나와 정확히 일치)
        - explanation: 정답에 대한 상세한 설명

    사용 예시:
        research_info = "머신 러닝은 알고리즘에 초점을 맞춘 AI의 하위 집합입니다..."
        quiz = generate_quiz(research_info, "머신 러닝", "medium", 5)
    """
    llm = init_chat_model("openai:gpt-5-mini")

    structured_llm = llm.with_structured_output(Quiz)

    prompt = f"""
    아래의 리서치 정보를 참고하여 "{topic}"에 대한 주제로 난이도 "{difficulty}" 정도의 퀴즈를 {num_questions}개 만들어주세요.
    
    <리서치 정보>
    {research_text}
    </리서치 정보>

    <리서치 정보>를 참고하여 가장 정확한 질문을 생성해주세요.
    """

    result = structured_llm.invoke(prompt)

    return result
