"""
Web Searcher Node
웹 검색을 수행하는 노드
"""

from ..research_state import ResearchState
from ..utils.search_client import get_tavily_client


def search_web(state: ResearchState) -> dict:
    """
    생성된 검색 쿼리로 웹 검색을 수행합니다.

    Args:
        state: 현재 상태

    Returns:
        업데이트할 상태 dict (search_results)
    """

    queries = state.get("search_queries", [])

    if not queries:
        print("[Web Searcher] 검색 쿼리가 없습니다.")
        return {"search_results": state.get("search_results", [])}

    print(f"\n[Web Searcher] 웹 검색 실행 중... ({len(queries)}개 쿼리)")

    # Tavily 클라이언트 초기화
    tavily = get_tavily_client()

    all_results = []

    for query in queries:
        print(f"  🔍 검색: {query}")

        try:
            # Tavily 검색 실행
            response = tavily.search(
                query=query,
                max_results=2,  # 쿼리당 2개씩
                search_depth="basic"
            )

            # 결과 파싱
            for item in response.get("results", []):
                all_results.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "content": item.get("content", "")
                })

            print(f"    → {len(response.get('results', []))}개 결과 수집")

        except Exception as e:
            print(f"    ⚠️ 검색 실패: {e}")

    print(f"총 {len(all_results)}개 검색 결과 수집 완료")

    # 기존 결과와 병합
    existing_results = state.get("search_results", [])
    merged_results = existing_results + all_results

    return {
        "search_results": merged_results
    }
