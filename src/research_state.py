"""
Research State 정의
LangGraph에서 사용할 상태(State) 스키마 정의
"""

from typing import TypedDict, List, Dict, Optional
from typing_extensions import Annotated


class ResearchState(TypedDict):
    """
    자동 리서치 Agent의 상태(State) 관리

    LangGraph는 이 State를 각 노드 간에 전달,
    각 노드는 State를 읽고 수정
    """

    # 입력: 사용자가 요청한 리서치 주제
    topic: str

    # 생성된 검색 키워드 리스트
    search_queries: List[str]

    # 웹 검색 결과 (누적)
    search_results: List[Dict[str, str]]

    # 정보 충분성 여부
    is_info_sufficient: bool

    # 평가자의 피드백/이유
    # info_evaluator 노드에서 설정됨

    # 검색 반복 횟수 (무한 루프 방지)


    # 최종 생성된 리포트 (Markdown 형식)
    # report_generator 노드에서 생성됨


    # 리포트 저장 경로 (PDF)



# Annotated State (LangGraph에서 reducer 함수 지정 가능)
# 예: search_results는 누적되어야 하므로 extend 방식 사용


# TODO: LangGraph의 Annotated State를 사용하려면
# from langgraph.graph import add_messages 같은 헬퍼를 활용하거나
# 직접 reducer를 정의할 수 있습니다.
# 현재는 기본 TypedDict로 정의했지만, 필요시 확장 가능합니다.
