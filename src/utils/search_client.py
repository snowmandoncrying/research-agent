"""
Tavily 검색 클라이언트
웹 검색 API를 래핑합니다.
"""

import os
from dotenv import load_dotenv
from tavily import TavilyClient
from typing import List, Dict

# 환경 변수 로드
load_dotenv()


def get_tavily_client() -> TavilyClient:
    """
    Tavily 클라이언트를 반환합니다.

    Returns:
        TavilyClient 인스턴스
    """
    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        raise ValueError(
            "TAVILY_API_KEY가 설정되지 않았습니다. "
            ".env 파일에 TAVILY_API_KEY를 추가해주세요."
        )

    return TavilyClient(api_key=api_key)


def search_tavily(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """
    Tavily API로 웹 검색을 수행합니다.

    Args:
        query: 검색 쿼리
        max_results: 최대 결과 수 (기본값: 5)

    Returns:
        검색 결과 리스트
        형식: [{"title": "...", "url": "...", "content": "..."}, ...]
    """

    client = get_tavily_client()

    try:
        # Tavily 검색 실행
        # TODO: Tavily API 문서 참고하여 정확한 파라미터 확인
        # https://docs.tavily.com/
        response = client.search(
            query=query,
            max_results=max_results,
            search_depth="advanced",  # 또는 "basic"
            include_answer=False,
            include_raw_content=False,
        )

        # 결과 파싱
        results = []
        for item in response.get("results", []):
            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "content": item.get("content", ""),
                "score": item.get("score", 0.0),  # 관련도 점수
            })

        return results

    except Exception as e:
        print(f"⚠️ Tavily 검색 실패: {e}")
        return []


# 사용 예시:
# results = search_tavily("Python LangGraph tutorial", max_results=3)
# for result in results:
#     print(f"{result['title']}: {result['url']}")
