"""
Research State 정의
LangGraph에서 사용할 상태(State) 스키마
"""

from typing import TypedDict, List, Dict, Optional, Literal


class ResearchState(TypedDict):
    """자동 리서치 Agent의 상태 관리"""

    # 사용자가 요청한 리서치 주제
    topic: str

    author: Optional[str]

    # 사용 언어
    report_language: Literal["ko", "en"]
    search_scope: Literal["local", "global"]

    # 생성된 검색 쿼리 리스트
    search_queries: List[str]

    # 웹 검색 결과 (누적)
    search_results: List[Dict[str, str]]

    # 검색 반복 횟수 (무한 루프 방지)
    iteration_count: int

    # 최종 생성된 리포트
    final_report: Optional[str]

    # 리서치 결과 요약 및 평가
    evaluation: Optional[str]
    evaluation_reason: Optional[str]
    # source_reliability: Optional[str]

    # 출력 파일 경로 (PDF)
    output_path: Optional[str]

    # 부족한 정보
    missing_info: Optional[List[str]]

    # 추천 검색 키워드
    recommended_keywords: Optional[List[str]]

    # 리포트 리뷰
    review_feedback: Optional[str]
    review_status: Optional[str]  # "approved", "needs_revision", "error"
    revision_count: Optional[int]
