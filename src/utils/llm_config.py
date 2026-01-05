"""
LLM 설정 및 초기화
Google Gemini 모델을 설정합니다.
"""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# 환경 변수 로드
load_dotenv()


def get_llm(usage: str = "default", model_name: str = None, temperature: float = None):
    """
    용도(usage)에 따라 최적화된 LLM 인스턴스를 반환합니다.

    Args:
        usage: "generator(리포트 작성)", "reviewer(리포트 검토)", "default"
        model_name: 모델 이름 (기본값: 환경변수 또는 gemini-2.5-flash-lite)
        temperature: 온도 설정 (기본값: 환경변수 또는 0.7)

    Returns:
        ChatGoogleGenerativeAI 인스턴스
    """

    configs = {
        "generator": {
            "model_name": "gemini-2.5-flash",
            "temperature": 0.7
        },
        "default": {
            "model_name": "gemini-2.5-flash-lite",
            "temperature": 0.7
        }
    }

    selected_config = configs.get(usage, configs["default"])

    # 환경 변수에서 설정 가져오기
    if model_name is None:
        model_name = os.getenv("MODEL_NAME", selected_config["model_name"])

    if temperature is None:
        env_temp = os.getenv("TEMPERATURE")
        temperature = float(env_temp) if env_temp is not None else selected_config["temperature"]

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


def get_reviewr_llm():
    """
      리뷰어 전용 LLM
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY가 설정되지 않았습니다. "
            ".env 파일에 GOOGLE_API_KEY를 추가해주세요."
        )

    return ChatGoogleGenerativeAI (
        model="gemini-2.5-flash-lite",
        temperature=0.1,
        google_api_key=api_key,
    )
        

# 사용 예시:
# llm = get_llm()
# response = llm.invoke("Hello, how are you?")
# print(response.content)
