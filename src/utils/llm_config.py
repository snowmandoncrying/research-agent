"""
LLM 설정 및 초기화
Google Gemini 모델을 설정합니다.
"""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# 환경 변수 로드
load_dotenv()


def get_llm(model_name: str = None, temperature: float = None):
    """
    LLM 인스턴스를 반환합니다.

    Args:
        model_name: 모델 이름 (기본값: 환경변수 또는 gemini-2.5-flash-lite)
        temperature: 온도 설정 (기본값: 환경변수 또는 0.7)

    Returns:
        ChatGoogleGenerativeAI 인스턴스
    """

    # 환경 변수에서 설정 가져오기
    if model_name is None:
        model_name = os.getenv("MODEL_NAME", "gemini-2.5-flash-lite")

    if temperature is None:
        temperature = float(os.getenv("TEMPERATURE", "0.7"))

    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY가 설정되지 않았습니다. "
            ".env 파일에 GOOGLE_API_KEY를 추가해주세요."
        )

    # LLM 초기화
    llm = ChatGoogleGenerativeAI(
        model=model_name,
        temperature=temperature,
        google_api_key=api_key,
    )

    return llm


# 사용 예시:
# llm = get_llm()
# response = llm.invoke("Hello, how are you?")
# print(response.content)
