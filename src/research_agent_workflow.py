"""
Research Agent Workflow (LangGraph)
메인 워크플로우를 정의하고 실행하는 모듈입니다.
"""

from typing import Literal
from langgraph.graph import StateGraph, END
from src.research_state import ResearchState
from src.nodes.query_generator import generate_search_queries
from src.nodes.web_searcher import search_web
from src.nodes.info_evaluator import evaluate_information
from src.nodes.report_generator import generate_report


def create_research_workflow() -> StateGraph:
    """
    LangGraph 워크플로우를 생성합니다.

    워크플로우 구조:
    1. generate_queries: 검색 키워드 생성
    2. search: 웹 검색 실행
    3. evaluate: 정보 충분성 평가
       - sufficient → generate_report
       - insufficient → generate_queries (재시작)
    4. generate_report: 최종 리포트 생성
    """

    # StateGraph 생성
    workflow = StateGraph(ResearchState)

    # === 노드 추가 ===
    workflow.add_node("generate_queries", generate_search_queries)
    workflow.add_node("search", search_web)
    workflow.add_node("evaluate", evaluate_information)
    workflow.add_node("generate_report", generate_report)

    # === 엣지(Edge) 정의 ===

    # 시작: generate_queries
    workflow.set_entry_point("generate_queries")

    # generate_queries → search
    workflow.add_edge("generate_queries", "search")

    # search → evaluate
    workflow.add_edge("search", "evaluate")

    # evaluate → 조건부 분기
    workflow.add_conditional_edges(
        "evaluate",
        should_continue_searching,  # 조건 함수
        {
            "continue": "generate_queries",  # 정보 부족 → 다시 검색
            "finish": "generate_report",     # 정보 충분 → 리포트 생성
        }
    )

    # generate_report → END
    workflow.add_edge("generate_report", END)

    return workflow


def should_continue_searching(state: ResearchState) -> Literal["continue", "finish"]:
    """
    조건부 분기 함수: 검색을 계속할지 결정

    조건:
    1. evaluation == "sufficient" → finish
    2. evaluation == "insufficient" AND iteration_count < 3 → continue
    3. iteration_count >= 3 → finish (무한 루프 방지)
    """

    max_iterations = 3  # 최대 검색 반복 횟수

    if state.get("evaluation") == "sufficient":
        return "finish"

    if state.get("iteration_count", 0) >= max_iterations:
        print(f"⚠️ 최대 반복 횟수({max_iterations})에 도달했습니다. 리포트를 생성합니다.")
        return "finish"

    return "continue"


def run_research_agent(topic: str) -> dict:
    """
    Research Agent를 실행합니다.

    Args:
        topic: 리서치 주제

    Returns:
        최종 상태(State) 딕셔너리
    """

    # 초기 상태 설정
    initial_state: ResearchState = {
        "topic": topic,
        "search_queries": [],
        "search_results": [],
        "evaluation": None,
        "evaluation_reason": None,
        "iteration_count": 0,
        "final_report": None,
        "output_path": None,
    }

    # 워크플로우 생성 및 컴파일
    workflow = create_research_workflow()
    app = workflow.compile()

    # 실행
    print(f"🔍 Research Agent 시작: {topic}")
    print("=" * 60)

    final_state = app.invoke(initial_state)

    print("=" * 60)
    print("✅ Research Agent 완료!")

    return final_state


# 사용 예시:
# if __name__ == "__main__":
#     result = run_research_agent("AI 기술 동향 2024")
#     print(result["final_report"])
