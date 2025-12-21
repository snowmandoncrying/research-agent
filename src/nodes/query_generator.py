"""
Query Generator Node
주제를 분석하여 검색 쿼리를 생성하는 노드
"""

from ..research_state import ResearchState
from ..utils.llm_config import get_llm
from langchain_core.prompts import ChatPromptTemplate


def generate_queries(state: ResearchState) -> dict:
    """
    주제를 분석하여 3개의 검색 쿼리를 생성합니다.

    Args:
        state: 현재 상태

    Returns:
        업데이트할 상태 dict (search_queries, iteration_count)
    """

    topic = state["topic"]
    iteration = state.get("iteration_count", 0)

    print(f"\n[Query Generator] 검색 쿼리 생성 중... (반복: {iteration + 1})")

    # LLM 초기화
    llm = get_llm()

    # 프롬프트 작성
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "당신은 효과적인 검색 쿼리를 생성하는 전문가입니다."),
        ("user", """
            주제: {topic}

            위 주제에 대해 리서치하기 위한 검색 쿼리 3개를 생성해주세요.

            요구사항:
            - 각 쿼리는 서로 다른 관점이나 측면을 다뤄야 합니다
            - 구체적이고 검색하기 좋은 형태로 작성해주세요
            - 한 줄에 하나씩, 번호 없이 작성해주세요

            예시:
            LangGraph 기본 개념과 구조
            LangGraph 실제 사용 예제
            LangGraph vs LangChain 비교
        """)
    ])

    # 쿼리 생성
    chain = prompt_template | llm
    response = chain.invoke({"topic": topic})

    # 응답 파싱
    content = response.content if hasattr(response, 'content') else str(response)
    queries = [q.strip() for q in content.strip().split('\n') if q.strip()]

    # 최대 3개만 선택
    queries = queries[:3]

    print(f"  생성된 쿼리:")
    for i, q in enumerate(queries, 1):
        print(f"    {i}. {q}")

    return {
        "search_queries": queries,
        "iteration_count": iteration + 1
    }
