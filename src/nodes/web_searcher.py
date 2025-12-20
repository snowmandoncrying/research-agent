"""
Web Searcher Node
웹 검색을 수행하는 노드입니다.
"""

from src.research_state import ResearchState
from src.utils.search_client import search_tavily


def search_web(state: ResearchState) -> dict:
    """
    생성된 검색 키워드로 웹 검색을 수행합니다.

    Args:
        state: 현재 상태

    Returns:
        업데이트할 상태 dict (search_results)
    """

    queries = state.get("search_queries", [])

    if not queries:
        print("[Web Searcher] 검색 키워드가 없습니다.")
        return {"search_results": []}

    print(f"\n[Web Searcher] 웹 검색 실행 중... ({len(queries)}개 키워드)")

    all_results = []

    for query in queries:
        print(f"  🔍 검색: {query}")

        # Tavily API 호출
        # TODO: search_tavily 함수 구현 필요 (src/utils/search_client.py)
        results = search_tavily(query, max_results=3)

        # 결과 누적
        all_results.extend(results)

        print(f"    → {len(results)}개 결과 수집")

    print(f"총 {len(all_results)}개 검색 결과 수집 완료")

    # 기존 결과와 병합
    # TODO: 중복 제거 로직 추가 가능
    existing_results = state.get("search_results", [])
    merged_results = existing_results + all_results

    return {
        "search_results": merged_results,
    }
