"""
Query Generator Node
검색 키워드를 생성하는 노드입니다.
"""

from src.research_state import ResearchState
from src.utils.llm_config import get_llm
from langchain_core.prompts import ChatPromptTemplate


def generate_search_queries(state: ResearchState) -> dict:
    """
    주제에 맞는 검색 키워드를 생성합니다.

    Args:
        state: 현재 상태

    Returns:
        업데이트할 상태 dict (search_queries, iteration_count)
    """

    topic = state["topic"]
    iteration = state.get("iteration_count", 0)

    print(f"\n[Query Generator] 검색 키워드 생성 중... (반복: {iteration + 1})")

    # LLM 초기화
    llm = get_llm()

    # 프롬프트 작성
    # TODO: 반복 시에는 이전 검색 결과를 참고하여 다른 각도의 키워드 생성
    if iteration == 0:
        # 첫 검색: 기본 키워드
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "당신은 효과적인 검색 키워드를 생성하는 전문가입니다."),
            ("user", """
주제: {topic}

위 주제에 대해 리서치하기 위한 검색 키워드 3개를 생성해주세요.
다양한 관점에서 정보를 수집할 수 있도록 구성하세요.

형식:
1. [키워드1]
2. [키워드2]
3. [키워드3]
            """)
        ])
    else:
        # 재검색: 이전 결과를 바탕으로 새로운 키워드
        previous_queries = state.get("search_queries", [])
        evaluation_reason = state.get("evaluation_reason", "")

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "당신은 효과적인 검색 키워드를 생성하는 전문가입니다."),
            ("user", """
주제: {topic}

이전 검색 키워드: {previous_queries}
부족한 부분: {reason}

위 내용을 고려하여, 부족한 정보를 보완할 수 있는 새로운 검색 키워드 3개를 생성해주세요.

형식:
1. [키워드1]
2. [키워드2]
3. [키워드3]
            """)
        ])
        prompt_template = prompt_template.partial(
            previous_queries=", ".join(previous_queries[-3:]),  # 최근 3개만
            reason=evaluation_reason
        )

    # LLM 호출
    chain = prompt_template | llm
    response = chain.invoke({"topic": topic})

    # 응답 파싱 (간단하게 줄 단위로 분리)
    # TODO: 더 정교한 파싱 로직 추가 가능
    content = response.content if hasattr(response, 'content') else str(response)
    queries = [
        line.strip().lstrip("0123456789. ").strip()
        for line in content.strip().split("\n")
        if line.strip() and not line.strip().startswith("형식")
    ][:3]  # 최대 3개

    print(f"생성된 키워드: {queries}")

    return {
        "search_queries": queries,
        "iteration_count": iteration + 1,
    }
