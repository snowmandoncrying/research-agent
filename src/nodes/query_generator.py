"""
Query Generator Node
주제를 분석하여 검색 쿼리를 생성하는 노드
"""

from typing import Dict, List
from ..research_state import ResearchState
from ..utils.llm_config import get_llm
from langchain_core.prompts import ChatPromptTemplate


def generate_queries(state: ResearchState) -> Dict:
    """
    반복 횟수에 따라 차별화된 검색 전략 적용
    
    전략:
    - 1차: 포괄적 검색 (개념+현황+데이터+사례+이슈 모두 포함)
    - 2차: 부족한 정보 보완 (Info Evaluator 피드백 기반)
    - 3차: 추가 심화 (여전히 부족한 부분 마무리)
   """

    iteration = state.get("iteration_count", 0)
    # existing_results = state.get("search_results", [])
    # existing_titles = []
    # for res in existing_results[-10:]: 
    #   existing_titles.append(res.get("title"))

    print(f"\n[Query Generator] Step {iteration + 1} 검색 쿼리 생성 중...")

    if iteration == 0:
      queries = generate_overview_queries(state)
    
    elif iteration == 1:
      queries = generate_data_queries(state, existing_titles)

    else:
      queries = generate_analysis_queries(state)   

    print(f"  생성된 쿼리:")
    for i, q in enumerate(queries, 1):
        print(f"    {i}. {q}")

    return {
        "search_queries": queries,
        "iteration_count": iteration + 1
    }


def generate_overview_queries(state: ResearchState) -> List[str]:  
   """
   1차 포괄적 검색
   """

   topic = state["topic"]
   llm = get_llm(temperature=0.7)

   prompt = ChatPromptTemplate.from_messages([
      ("system", "당신은 주제의 성격을 분석해 적절한 검색 전략을 수립하고, "
        "리서치에 효과적인 검색 쿼리를 생성하는 전문가입니다."),
       ("user", """
            주제: {topic}
        
            먼저, 위 주제가 다음 중 어느 {scope}가 더 적절한지 판단하세요.
              - local: 국내 정책, 제도, 기업, 한국 시장 중심의 주제
              - global: 국제 동향, 학술/기술 연구, 글로벌 산업 표준이 중요한 주제
              그 판단을 바탕으로, 위 주제를 리서치하기 위한 초기 검색 쿼리 3개를 생성해주세요.
        
            [검색 범위 규칙]:
              - local로 판단한 경우: 한국어 검색 쿼리 3개 생성
              - global로 판단한 경우: 한국어 쿼리 1개 + 영어(English) 쿼리 2개 생성
            
            [쿼리 작성 지침]
              - 1차 검색만으로도 기본적인 리포트 작성이 가능해야 합니다.
              - 각 쿼리는 서로 다른 관점을 담당해야 합니다.
                1. 개념/정의와 최신 현황
                2. 통계/데이터와 적용 사례
                3. 주요 이슈와 미래 전망
            
            [출력 형식]
              반드시 아래 JSON 형식으로만 응답하세요.
              다른 텍스트는 절대 출력하지 마세요.

              {
                "search_scope": "local" | "global",
                "search_queries": [
                  "query 1",
                  "query 2",
                  "query 3"
                ]}
        """)
   ])
   chain = prompt | llm
   response = chain.invoke({ "topic": topic})

   # AI 응답 파싱
   content = response.content if hasattr(response) else str(content)
   queries = [q.strip() for q in content.strip().split('\n') if q.strip()][:3]
   return queries


def generate_data_queries(state: ResearchState) -> List[str]: 
  """
    2차 Info Evaluator 피드백 기반 보완
    
    목표:
    - 부족한 정보 직접 보완
    - 추천 키워드 검증 후 활용
    - 구체적이고 정밀한 검색
   """
   
  topic = state["topic"]
  iteration = state.get("iteration_count", 0)
  missing_info = state.get("missing_info", "")
  recommended_keywords = state.get("recommended_keywords", "")

  llm = get_llm(temperature=0.5) 
  prompt = ChatPromptTemplate.from_messages([
     ("system", "당신은 주제에 맞는 검색 쿼리를 효과적으로 생성하는 전문가입니다."),
     ("user", """
        주제: {topic}
        현재 {iteration}번째 검색 시도이므로 전보다 더욱 구체적이고 정밀한 쿼리가 필요합니다.
      
        [재검색 가이드]
        1. 부족한 정보: {missing_info}
        2. 추천 검색 키워드: {recommended_keywords}
        
        [지침]
        1. 먼저, 추천 검색 키워드가 주제{topic}와 충분히 연관되어 있는지 비판적으로 검토하세요.
        2. 주제와 밀접한 관련이 있는 키워드 위주로 선별하여, {missing_info}를 보완할 수 있는 정밀 쿼리 3개를 생성하세요.
        3. {recommended_keywords}가 주제와 맞지 않는다고 판단되면, 주제의 맥락에 맞는 더 적절한 전문 용어를 직접 선정하여 사용하세요.
        4. 이미 수집된 자료와 중복되지 않도록 전문적이고 구체적인 검색어를 작성해야 합니다.
      
        [출력 형식 가이드]
        - 구체적이고 검색하기 좋은 형태로 작성해주세요
        - 한 줄에 하나씩, 번호 없이 작성해주세요
        - 최대 3개까지만 생성해주세요
      """)
  ])

  chain = prompt | llm
  response = chain.invoke({
    "topic": topic,
    "iteration": iteration,
    "missing_info": missing_info,
    "recommended_keywords": ", ".join(recommended_keywords) if recommended_keywords else "없음"
  })

  content = response.content if hasattr(response) else str(content)
  queries = [q.strip() for q in content.strip().split('\n') if q.strip()][:3]
  return queries    


def generate_analysis_queries(state: ResearchState) -> List[str]:
  """
  3차 마지막 심화 및 최종 보완
  """

  topic = state["topic"]
  iteration = state.get("iteration_count", 0)
  missing_info = state.get("missing_info", "")
  recommended_keywords = state.get("recommended_keywords", "")

  llm = get_llm(temperature=0.3) 
  prompt = ChatPromptTemplate.from_messages([
     ("system", "당신은 리서치 갭을 완전히 해결하는 전문가입니다."),
     ("user", """
        주제: {topic}
        현재 {iteration}번째 검색 시도이므로 전보다 더욱 구체적이고 정밀한 쿼리가 필요합니다.
      
        [재검색 가이드]
          1. 부족한 정보: {missing_info}
          2. 추천 검색 키워드: {recommended_keywords}
        
        [지침]
          1. 먼저, 추천 검색 키워드가 주제{topic}와 충분히 연관되어 있는지 비판적으로 검토하세요.
          2. 주제와 밀접한 관련이 있는 키워드 위주로 선별하여, {missing_info}를 보완할 수 있는 정밀 쿼리 3개를 생성하세요.
          3. {recommended_keywords}가 주제와 맞지 않는다고 판단되면, 주제의 맥락에 맞는 더 적절한 전문 용어를 직접 선정하여 사용하세요.
          4. 이미 수집된 자료와 중복되지 않도록 전문적이고 구체적인 검색어를 작성해야 합니다.
        
        [전략]
          - 학술 논문, 전문 보고서, 정부 자료 등 권위 있는 출처를 타겟으로
          - 구체적인 수치, 데이터, 사례를 찾을 수 있는 쿼리
          - 전문 용어와 키워드를 적극 활용
      
        [출력 형식]
          SCOPE: [local 또는 global]
          [검색 쿼리 1]
          [검색 쿼리 2]
          [검색 쿼리 3]
      """)
  ])

  chain = prompt | llm
  response = chain.invoke({
    "topic": topic,
    "iteration": iteration,
    "missing_info": missing_info,
    "recommended_keywords": ", ".join(recommended_keywords) if recommended_keywords else "없음"
  })

  content = response.content if hasattr(response) else str(content)
  queries = [q.strip() for q in content.strip().split('\n') if q.strip()][:3]
  return queries  

# AI 응답 리스트로 파싱
def parse_queries(content: str) -> List[str]:
    """AI 응답에서 번호를 제거하고 리스트로 파싱"""
    lines = [q.strip() for q in content.strip().split('\n') if q.strip()]
    # 숫자. 혹은 - 같은 불필요한 기호 제거
    clean_queries = [re.sub(r'^\d+[\.\s\-]+', '', q) for q in lines]
    return clean_queries[:3]


# 테스트 코드
if __name__ == "__main__":
    print("=" * 60)
    print("Query Generator 테스트")
    print("=" * 60)
    
    test_topic = "인공지능을 활용한 의료 진단의 최신 동향"
    
    # 1차 검색 테스트
    print("\n[1차 검색 테스트]")
    state_1 = {
        "topic": test_topic,
        "iteration_count": 0
    }
    result_1 = generate_queries(state_1)
    
    # 2차 검색 테스트
    print("\n[2차 검색 테스트]")
    state_2 = {
        "topic": test_topic,
        "iteration_count": 1,
        "missing_info": "구체적인 시장 규모 통계 부족",
        "recommended_keywords": ["AI 의료 시장", "매출 현황"]
    }
    result_2 = generate_queries(state_2)
    
    # 3차 검색 테스트
    print("\n[3차 검색 테스트]")
    state_3 = {
        "topic": test_topic,
        "iteration_count": 2,
        "missing_info": "국내 병원 도입 사례 및 규제 현황 부족",
        "recommended_keywords": ["서울대병원", "삼성병원", "AI 규제"]
    }
    result_3 = generate_queries(state_3)
    
    print("\n" + "=" * 60)
    print("테스트 완료!")
    print("=" * 60)

# if __name__ == "__main__":
#    target_topic = "인공지능을 활용한 의료 진단의 최신 동향"

#    print(f"초기 테스트 주제: {target_topic}")
#    initial_state = {
#       "topic": target_topic,
#       "search_results": [],
#       "iteration_count": 0,
#       "missing_info": "",
#       "recommended_keywords": ""
#    }

#    result_1 = generate_queries(initial_state) 
#    print(f"\n초기 검색 쿼리 생성 결과: {result_1['search_queries']}")

#    updated_state = {
#       "topic": target_topic,
#       "search_results": [{"title": "AI in Healthcare", "url": "http://example.com/ai-health", "content": "..." }],
#       "iteration_count": 1,
#       "missing_info": "국내외 최신 의료 AI 적용 사례 및 통계",
#       "recommended_keywords": "의료 인공지능 사례, AI 진단 정확도, 헬스케어 AI 트렌드"
#     }
   
#    result_2 = generate_queries(updated_state)
#    print(f"\n재검색 쿼리 생성 결과: {result_2['search_queries']}")
