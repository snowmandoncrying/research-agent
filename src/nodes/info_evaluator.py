"""
Information Evaluator Node
수집된 정보의 충분성을 평가하는 노드입니다.
"""

from src.research_state import ResearchState
from src.utils.llm_config import get_llm
from langchain_core.prompts import ChatPromptTemplate
import json


def evaluate_information(state: ResearchState) -> dict:
    """
    수집된 정보가 리포트 작성에 충분한지 평가합니다.

    Args:
        state: 현재 상태

    Returns:
        업데이트할 상태 dict (evaluation, evaluation_reason)
    """

    topic = state["topic"]
    search_results = state.get("search_results", [])

    print(f"\n[Info Evaluator] 정보 충분성 평가 중...")
    print(f"  수집된 자료: {len(search_results)}개")

    if len(search_results) < 3:
        # 최소 자료 수 미달
        return {
            "evaluation": "insufficient",
            "evaluation_reason": "검색 결과가 너무 적습니다 (최소 3개 필요).",
        }

    # LLM으로 평가
    llm = get_llm()

    # 검색 결과 요약 (제목 + 내용 일부)
    results_summary = "\n\n".join([
        f"[{i+1}] {result.get('title', 'No Title')}\n{result.get('content', '')[:200]}..."
        for i, result in enumerate(search_results[:10])  # 최대 10개만
    ])

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "당신은 리서치 자료의 충분성을 평가하는 전문가입니다."),
        ("user", """
주제: {topic}

수집된 자료:
{results}

위 자료들이 주제에 대한 리포트를 작성하기에 충분한지 평가해주세요.

평가 기준:
1. 주제의 핵심 개념이 설명되어 있는가?
2. 다양한 관점이나 예시가 포함되어 있는가?
3. 최신 정보가 포함되어 있는가?

JSON 형식으로 응답해주세요:
{{
  "evaluation": "sufficient" 또는 "insufficient",
  "reason": "평가 이유 (한 문장)"
}}
        """)
    ])

    chain = prompt_template | llm
    response = chain.invoke({
        "topic": topic,
        "results": results_summary
    })

    # 응답 파싱
    try:
        content = response.content if hasattr(response, 'content') else str(response)
        # JSON 블록 추출 (```json ... ``` 형식 고려)
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        result = json.loads(content)
        evaluation = result.get("evaluation", "insufficient")
        reason = result.get("reason", "")

    except Exception as e:
        print(f"  ⚠️ 평가 응답 파싱 실패: {e}")
        # 기본값
        evaluation = "insufficient"
        reason = "평가 실패"

    print(f"  평가 결과: {evaluation}")
    print(f"  이유: {reason}")

    return {
        "evaluation": evaluation,
        "evaluation_reason": reason,
    }
