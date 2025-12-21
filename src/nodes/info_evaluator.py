"""
Information Evaluator Node
수집된 정보의 충분성을 평가하는 노드
"""


from ..research_state import ResearchState
from ..utils.llm_config import get_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser


def evaluate_information(state: ResearchState) -> dict:
    """
    LLM이 수집된 정보가 리포트 작성에 충분한지 평가합니다.

    평가 기준:
    - 검색 결과가 6개 이상 OR
    - 반복 횟수가 2회 이상
    - TOPIC과의 연관성

    Args:
        state: 현재 상태

    Returns:
        빈 dict 반환 (조건부 엣지에서 다음 노드를 결정)
    """

    topic = state["topic"]
    search_results = state.get("search_results", [])
    iteration_count = state.get("iteration_count", 0)
    
    print(f"\n[Info Evaluator] 정보 충분성 평가 중...")

    # 검색 결과가 없으면
    if not search_results:
        print("  검색 결과가 없습니다. 추가 검색이 필요합니다.")
        return {
            "evaluation": "insufficient",
            "evaluation_reason": "검색 결과가 없습니다."
        }
    
    # LLM 초기화
    llm = get_llm(temperature=0.3)

    # 검색 결과 요약 후 LLM에게 평가 요청
    results_summary = "\n".join(
        f"[{index+1}] {result.get('title', 'No Title')}\n"
        f"{result.get('content', '')[:200]}..."
        for index, result in enumerate(search_results[:10])
    )

    # 평가 프롬프트 작성
    prompt = ChatPromptTemplate.from_messages([
        ("system", "당신은 리서치 자료의 품질을 평가하는 전문가입니다."
            "검색 결과를 보고 리포트 작성에 충분한지 판단해주세요."),
        ("user", f"""
            주제: {topic}

            다음은 수집된 검색 결과 요약입니다:
            {results_summary}

            총 검색 결과 수: {len(search_results)}
            반복 횟수: {iteration_count}

            위 정보를 바탕으로, 리포트 작성에 충분한지 평가해주세요.

            평가 기준:
            1. 검색 결과가 주제와 관련이 있는가?
            2. 정보의 품질이 좋은가?
            3. 반복 횟수 (2회 이상인지)
            4. 검색 결과 수가 충분한가? (6개 이상)
            5. 어떤 정보가 부족한가?

            다음 JSON 형식으로만 답변해주세요:
            {{{{
                "is_sufficient": true 또는 false,
                "reason": "평가 이유",
                "missing_info": "부족한 정보 (있다면)",
                "recommendation": "추가 검색이 필요한 키워드 (있다면)"
            }}}}
        """)
        ])
    
    # 평가 실행
    chain = prompt | llm
    response = chain.invoke({
        "topic": topic,
        "results_summary": results_summary,
        "search_results": len(search_results),
        "iteration_count": iteration_count,
        })
    
    # 응답 파싱
    import json
    try:
        content = response.content if hasattr(response, 'content') else str(response)
        # JSON 추출 (마크다운 코드블록 제거)
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        
        evaluation = json.loads(content.strip())
        
        is_sufficient = evaluation.get("is_sufficient", False)
        reason = evaluation.get("reason", "")
        
        print(f"  평가 결과: {'충분' if is_sufficient else '부족'}")
        print(f"  이유: {reason}")
        
        if not is_sufficient:
            print(f"  부족한 정보: {evaluation.get('missing_info', 'N/A')}")
            print(f"  추천 키워드: {evaluation.get('recommendation', 'N/A')}")
        
        return {
            "evaluation": "sufficient" if is_sufficient else "insufficient",
            "evaluation_reason": reason,
            "missing_info": evaluation.get("missing_info"),
            "recommended_keywords": evaluation.get("recommendation")
        }
        
    except Exception as e:
        print(f"  ⚠️ 평가 실패: {e}")
        # 실패시 기본 로직으로 폴백
        if len(search_results) >= 6 or iteration_count >= 3:
            return {
                "evaluation": "sufficient",
                "evaluation_reason": "기본 조건 충족"
            }
        else:
            return {
                "evaluation": "insufficient", 
                "evaluation_reason": "자료 부족"
            }

    # result_count = len(search_results)

    # print(f"\n[Info Evaluator] 정보 충분성 평가 중...")
    # print(f"  수집된 자료: {result_count}개")
    # print(f"  반복 횟수: {iteration_count}회")

    # # 조건 체크
    # if result_count >= 6 or iteration_count >= 2:
    #     print(f"  충분한 정보 수집 완료 → 리포트 생성")
    # else:
    #     print(f"  추가 검색 필요")

    # # State를 변경하지 않으므로 빈 dict 반환
    # return {}


def should_continue(state: ResearchState) -> str:
    """
    다음 단계를 결정하는 헬퍼 함수

    Returns:
        "generate_report" 또는 "search_more"
    """
    search_results = state.get("search_results", [])
    iteration_count = state.get("iteration_count", 0)

    result_count = len(search_results)

    if result_count >= 6 or iteration_count >= 2:
        return "generate_report"
    else:
        return "search_more"
