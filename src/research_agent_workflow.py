"""
Research Agent Workflow (LangGraph)
메인 워크플로우를 정의하고 실행하는 모듈입니다.
"""

from typing import Literal
from langgraph.graph import StateGraph, END
from src.research_state import ResearchState
from src.nodes.query_generator import generate_queries
from src.nodes.web_searcher import search_web
from src.nodes.info_evaluator import evaluate_information
from src.nodes.report_file_generator import generate_report_file
from src.nodes.report_content_generator import generate_report_content
from src.nodes.report_reviewer import review_report
from src.nodes.chart_generator import extract_chart_data


def create_research_workflow() -> StateGraph:
    """
    LangGraph 워크플로우를 생성합니다.

    워크플로우 구조:
    1. generate_queries
    2. search
    3. evaluate
    4. generate_report_content   (본문 생성)
    5. review_report             (수정 반복)
    6. extract_chart_data        (차트 데이터 + 이미지 생성)
    7. generate_report           (차트 삽입 + 파일 저장)
    8. END
    """

    # StateGraph 생성
    workflow = StateGraph(ResearchState)

    # === 노드 추가 ===
    workflow.add_node("generate_queries", generate_queries)
    workflow.add_node("search", search_web)
    workflow.add_node("evaluate", evaluate_information)
    workflow.add_node("generate_report", generate_report_file)
    workflow.add_node("generate_report_content", generate_report_content)
    workflow.add_node("review_report", review_report)
    workflow.add_node("extract_chart_data", extract_chart_data)

    # === 엣지(Edge) 정의 ===

    # 시작: generate_queries
    workflow.set_entry_point("generate_queries")

    workflow.add_edge("generate_queries", "search")
    workflow.add_edge("search", "evaluate")

    # 검색 충분성 판단 분기
    workflow.add_conditional_edges( "evaluate", should_continue_searching,  
      { "continue": "generate_queries", "finish": "generate_report_content", }
    )

    workflow.add_edge("generate_report_content", "review_report")

    # 리뷰 결과에 따른 분기
    workflow.add_conditional_edges("review_report", decide_after_review,
      { 
        "revision": "generate_report_content",
        "approved": "extract_chart_data",
        "max_revision": "extract_chart_data",
      }
    )

    # 차트 생성 후 최종 파일 저장
    workflow.add_edge("extract_chart_data", "generate_report")
    workflow.add_edge("generate_report", END)

    return workflow


def decide_after_review(state: ResearchState) -> Literal["revision", "approved", "max_revision"]:
    """
    review_status에 따라 조건 분기

    수정 횟수 제한: 최대 1회까지만 수정 가능
    """
    status = state.get("review_status")
    revision_count = state.get("revision_count", 0)

    # 최대 1회 수정으로 제한
    if revision_count >= 1:
        print(f"  ⚠️ 최대 수정 횟수(1회) 도달 - 차트 생성 진행")
        return "max_revision"

    if status == "approved":
        return "approved"

    return "revision"


def should_continue_searching(state: ResearchState) -> Literal["continue", "finish"]:
    """
    검색을 계속할지 결정

    조건:
    1. evaluation == "sufficient" → finish
    2. evaluation == "insufficient" AND iteration_count < 3 → continue
    3. iteration_count >= 3 → finish (무한 루프 방지)
    """

    max_iterations = 3  # 최대 검색 반복 횟수

    if state.get("evaluation") == "sufficient":
        return "finish"

    if state.get("iteration_count", 0) >= max_iterations:
      return "finish"

    return "continue"


def run_research_agent(topic: str, author: str = "김사원", report_language: str = "ko") -> dict:
    """
    Research Agent를 실행합니다.

    Args:
        topic: 리서치 주제
        report_language: 리포트 언어 ("ko" 또는 "en")

    Returns:
        최종 상태(State) 딕셔너리
    """

    # 초기 상태 설정
    initial_state: ResearchState = {
        "topic": topic,
        "author": author,
        "search_scope": None,
        "report_language": report_language,
        "search_queries": [],
        "search_results": [],
        "evaluation": None,
        "evaluation_reason": None,
        "iteration_count": 0,
        "final_report": None,
        "output_path": None,
        "missing_info": None,
        "recommended_keywords": None,
        "review_feedback": None,
        "review_status": None,
        "revision_count": 0,
        "chart_paths": [],
    }

    # 워크플로우 생성 및 컴파일
    workflow = create_research_workflow()
    app = workflow.compile()

    final_state = app.invoke(initial_state)
    return final_state


# def detect_language(topic: str) -> Literal["ko", "en"]:
#     """
#     간단한 언어 감지 함수 (한국어/영어)

#     Args:
#         topic: 감지할 텍스트
#     Returns:
#         "ko" 또는 "en"
#     """

#     has_korean = any('\uac00' <= char <= '\ud7a3' for char in topic)

#     if has_korean:
#         return "ko"
#     else:
#         return "en"