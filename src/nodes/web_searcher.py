"""
Web Searcher Node
웹 검색을 수행하는 노드
"""

from ..research_state import ResearchState
from ..utils.search_client import get_tavily_client
from ..utils.domain_trust import get_domain_score

EXCLUDE_DOMAINS = [
    "kmong.com",
    "fiverr.com", 
    "coupang.com",
    "gmarket.co.kr",
    "11st.co.kr",
    "smartstore.naver.com",
    "auction.co.kr",
    "interpark.com",
]

def search_web(state: ResearchState) -> dict:
    """
    생성된 검색 쿼리로 웹 검색을 수행하고, 광고 및 신뢰도가 낮은 사이트를 필터링
    1단계: Tavily API에서 광고 도메인 제외
    2단계: score로 추가 필터링
    """

    queries = state.get("search_queries", [])

    if not queries:
        print("[Web Searcher] 검색 쿼리가 없습니다.")
        return {"search_results": state.get("search_results", [])}

    print(f"\n[Web Searcher] 웹 검색 실행 중... ({len(queries)}개 쿼리)")

    # Tavily 클라이언트 초기화
    tavily = get_tavily_client()
    all_results = []
    filtered_count = 0

    for query in queries:
        print(f"  🔍 검색: {query}")

        try:
            # Tavily 검색 실행 (1차)
            response = tavily.search(
                query=query,
                max_results=3,
                search_depth="advanced",
                exclude_domains=EXCLUDE_DOMAINS
            )

            # 결과 파싱 (2차)
            for item in response.get("results", []):
                url = item.get("url", "")
                trust_score = get_domain_score(url)

                if trust_score <= 0.25:
                    filtered_count += 1
                    print(f"   ⚠️ 2차 필터링: {url} (점수: {trust_score})")
                    continue 

                all_results.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "content": item.get("content", ""),
                    "trust_score": trust_score
                })

            total = len(response.get('results', []))
            collected = total - filtered_count
            print(f"    → {total}개 검색, {collected}개 수집, {filtered_count}개 제외")

        except Exception as e:
            print(f"    ⚠️ 검색 실패: {e}")

    # 기존 결과와 병합 및 중복 제거
    existing_results = state.get("search_results", [])
    raw_merged = existing_results + all_results
    unique_urls = {res['url'] : res for res in raw_merged}
    merged_results = list(unique_urls.values())
    merged_results.sort(key=lambda x: x.get("trust_score", 0), reverse=True)

    print(f"총 {len(merged_results)}개 검색 결과 정렬 및 병합 완료")

    return {
        "search_results": merged_results
    }

# 검증하기
if __name__ == "__main__":
    test_state = {
        "search_queries": [
            "인공지능 의료 진단",
        ], 
        "search_results": [
          {
            "title": "기존 수집된 의료 AI 뉴스", 
            "url": "https://news.naver.com/ai-health", # 이 주소와 겹치는지 확인용
            "content": "기존 내용...",
            "trust_score": 0.8
          }
        ]
    }
    final_state = search_web(test_state)
    results = final_state.get("search_results", [])

    print(f"최종 수집 결과: {len(results)}개")

    for num, res in enumerate(results, 1):
        print(f"\n{num}. [{res['trust_score']:.2f}] {res['title']}")
        print(f"   {res['url']}")