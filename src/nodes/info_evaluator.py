"""
Information Evaluator Node
수집된 정보의 충분성을 평가하는 노드
"""


from ..research_state import ResearchState
from ..utils.llm_config import get_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import json

def evaluate_information(state: ResearchState) -> dict:
    """
    LLM이 수집된 정보가 리포트 작성에 충분한지 평가합니다.

    평가 기준:
    - 검색 결과가 6개 이상 OR
    - 반복 횟수가 2회 이상
    - TOPIC과의 연관성
    """

    topic = state["topic"]
    search_results = state.get("search_results", [])
    iteration_count = state.get("iteration_count", 0)
    
    print(f"\n[Info Evaluator] 정보 충분성 평가 중... (반복: {iteration_count})")

    # 평균 신뢰도 계산
    if search_results:
        total = sum(r.get("trust_score", 0) for r in search_results)
        avg_trust = total / len(search_results)
        print(f"  평균 신뢰도: {avg_trust:.2f}")
    else:
        avg_trust = 0.0    

    # 최소 조건 체크
    if len(search_results) < 6:
        return { "evaluation": "insufficient", "evaluation_reason": "검색 결과가 부족합니다."}

    if iteration_count < 2:
        return { "evaluation": "insufficient", "evaluation_reason": "반복 횟수가 부족합니다."}
    
    if avg_trust < 0.5:
      print(f"  평균 신뢰도 부족: {avg_trust:.2f}")
      return { "evaluation": "insufficient", "evaluation_reason": "신뢰도가 부족합니다."}
    
    if high_trust_count := len([r for r in search_results if r.get("trust_score", 0) >= 0.7]) < 2:
      print(f"  고신뢰 출처 부족: {high_trust_count}개")
      return { "evaluation": "insufficient", "evaluation_reason": "고신뢰 출처가 부족합니다."}

    # LLM 초기화 (내용 평가용)
    llm = get_llm(temperature=0.3)

    # 검색 결과 요약 후 LLM에게 평가 요청
    results_summary = "\n".join(
        f"[{index+1}] [신뢰도: {result.get('trust_score', 0):.2f}] {result.get('title', 'No Title')}\n"
        f"{result.get('content', '')[:200]}..."
        for index, result in enumerate(search_results[:10])
    )

    # 평가 프롬프트 작성
    prompt = ChatPromptTemplate.from_messages([
        ("system", "당신은 리서치 자료의 품질을 평가하는 전문가입니다."
            "수집된 자료가 주제에 대해 심층 리포트를 쓰기에 질적으로 충분한지 판단해주세요."),
        ("user", """
            주제: {topic}
            수집된 검색 결과 ({search_count}개, 평균 신뢰도: {avg_trust}):{results_summary}

            위 정보를 바탕으로, 리포트 작성에 충분한지 평가해주세요.
            
            참고:
            - 평균 신뢰도 {avg_trust} 는 이미 검증됨
            - 고신뢰 출처(0.7+)를 주요 근거로 우선
            - 중신뢰 출처(0.3~0.6)는 보조 자료로 활용
            - 저신뢰 출처만 있으면 insufficient

            먼저 각 자료를 간단히 평가해주세요. 
            
            평가 항목:
            - 주제 관련성(relevance): high, medium, low
            - 구체적인 데이터의 유무(quality): high, medium, low
            - 한줄 평가(comment)

            그런 다음, 전체적인 정보의 충분성을 판단해주세요.

            평가 기준:
            1. 고신뢰 출처가 2개 이상인가?
            2. 주제-내용 일치도: 각 자료가 주제와 직접 관련 있는가?
            3. 정보 구체성: 데이터, 통계, 사례 등 구체적 정보가 있는가?
            4. 정보 일관성: 여러 출처가 모순되지 않는가? 
            5. 부족한 정보: 추가로 필요한 정보는?

            다음 JSON 형식으로만 답변해주세요:
            {{
                "individual_reviews": [
                    {{
                        "index": 자료 번호 (1부터 시작),
                        "relevance": "high/medium/low",
                        "quality": "high/medium/low",
                        "comment": "한줄 평가"
                    }}
                ],
                "is_sufficient": true 또는 false,
                "reason": "평가 이유",
                "missing_info": "부족한 정보 (있다면)",
                "recommendation": "추가 검색이 필요한 키워드 (있다면)"
            }}
        """)
        ])
    
    # 평가 실행
    chain = prompt | llm
    response = chain.invoke({
        "topic": topic,
        "results_summary": results_summary,
        "search_count": len(search_results),
        "avg_trust": f"{avg_trust:.2f}"
        })
    
    # 응답 파싱
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
        individual_reviews = evaluation.get("individual_reviews", "")

        print(f"\n[자료별 평가]\n{individual_reviews}")
        print(f"\n[종합 평가]")
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
    LLM 평가에 따라 다음 단계를 결정하는 헬퍼 함수 - 엣지 

    Returns:
        "generate_report" 또는 "search_more"
    """
    # search_results = state.get("search_results", [])
    evaluation = state.get("evaluation", "")
    iteration_count = state.get("iteration_count", 0)


    if evaluation == "sufficient" or iteration_count >= 3:
        print(f"--- 정보가 충분하거나 최대 반복 횟수에 도달했습니다. 리포트를 작성합니다. ---")
        return "generate_report"
    else:
        print(f"--- 정보가 부족합니다. 추가 검색을 진행합니다. ---")
        return "search_more"

# 검증 테스트
if __name__ == "__main__":
    # 간단한 테스트 케이스
    test_state = ResearchState(
        topic="인공지능의 최신 동향",
        search_results=[
        {"title": "2024 인공지능(AI) 기술 및 시장 동향", "url": "https://gov.kr/report/123", "content": "2024년 AI 시장 규모는 전년 대비 30% 성장하여 10조원 돌파 예상. 생성형 AI가 주도...", "trust_score": 1.0},
        {"title": "AI 기술 트렌드 총정리", "url": "https://news.naver.com/ai-trend", "content": "ChatGPT 등장 이후 생성형 AI 경쟁 심화. 네이버, 카카오 등 국내 기업도 자체 모델 출시...", "trust_score": 0.8},
        {"title": "글로벌 AI 시장 분석", "url": "https://news.naver.com/global-ai", "content": "미국과 중국이 AI 기술 경쟁 주도. 유럽은 AI 규제 강화...", "trust_score": 0.6},
        {"title": "국내 AI 스타트업 현황", "url": "https://techcrunch.com/ai-startup", "content": "국내 AI 스타트업 투자 급증. 생성형 AI 중심으로 성장...", "trust_score": 0.5},
        {"title": "AI 윤리 이슈", "url": "https://example.com/ai-ethics", "content": "AI 편향성, 개인정보 문제 대두. 규제 필요성 증가...", "trust_score": 0.5},
        {"title": "AI 산업 적용 사례", "url": "https://blog.naver.com/ai-case", "content": "제조업, 금융업에서 AI 도입 확대. 효율성 향상 효과...", "trust_score": 0.4},
    ],
        iteration_count=2
    )

    eval_result = evaluate_information(test_state)

    print("\n[개별 결과 분석]")
    for i, res in enumerate(test_state["search_results"], 1):
      print(f"{i}. 점수: {res['trust_score']:.1f} | 제목: {res['title']}")

    print("\n[최종 평가 결과]")
    print(f"상태: {eval_result.get('evaluation')}")
    print(f"이유: {eval_result.get('evaluation_reason')}")
    
    if eval_result.get('evaluation') == "insufficient":
        print(f"부족 정보: {eval_result.get('missing_info', '없음')}")
        print(f"추천 키워드: {eval_result.get('recommended_keywords', '없음')}")