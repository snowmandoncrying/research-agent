"""
단계별 워크플로우 테스트
각 노드를 개별적으로 테스트합니다.
"""

from src.research_state import ResearchState
from src.nodes import (
    generate_queries,
    search_web,
    evaluate_information,
    generate_report,
)


def test_query_generator():
    """
    검색 키워드 생성 노드 테스트
    """
    print("\n" + "=" * 60)
    print("TEST 1: Query Generator")
    print("=" * 60)

    # 초기 상태
    state: ResearchState = {
        "topic": "Python 비동기 프로그래밍",
        "search_queries": [],
        "search_results": [],
        "evaluation": None,
        "evaluation_reason": None,
        "iteration_count": 0,
        "final_report": None,
        "output_path": None,
    }

    # 노드 실행
    result = generate_queries(state)

    print(f"\n생성된 키워드: {result['search_queries']}")
    print(f"반복 횟수: {result['iteration_count']}")

    return {**state, **result}


def test_web_searcher(state: ResearchState):
    """
    웹 검색 노드 테스트
    """
    print("\n" + "=" * 60)
    print("TEST 2: Web Searcher")
    print("=" * 60)

    # 노드 실행
    result = search_web(state)

    print(f"\n수집된 결과: {len(result['search_results'])}개")
    for i, res in enumerate(result['search_results'][:3], 1):
        print(f"{i}. {res.get('title', 'No Title')[:50]}...")

    return {**state, **result}


def test_info_evaluator(state: ResearchState):
    """
    정보 충분성 평가 노드 테스트
    """
    print("\n" + "=" * 60)
    print("TEST 3: Information Evaluator")
    print("=" * 60)

    # 노드 실행
    result = evaluate_information(state)

    print(f"\n평가 결과: {result['evaluation']}")
    print(f"이유: {result['evaluation_reason']}")

    return {**state, **result}


def test_report_generator(state: ResearchState):
    """
    리포트 생성 노드 테스트
    """
    print("\n" + "=" * 60)
    print("TEST 4: Report Generator")
    print("=" * 60)

    # 노드 실행
    result = generate_report(state)

    print(f"\nPDF 경로: {result['output_path']}")
    print(f"리포트 길이: {len(result['final_report'])} 글자")
    print("\n미리보기:")
    print("-" * 60)
    print(result['final_report'][:300] + "...")

    return {**state, **result}


def main():
    """
    전체 노드 순차 테스트
    """
    print("\n" + "=" * 60)
    print("🧪 Research Agent 노드별 테스트")
    print("=" * 60)

    try:
        # 1. 검색 키워드 생성
        state = test_query_generator()

        # 2. 웹 검색
        state = test_web_searcher(state)

        # 3. 정보 평가
        state = test_info_evaluator(state)

        # 4. 리포트 생성
        # 평가 결과와 관계없이 강제로 리포트 생성 (테스트 목적)
        state['evaluation'] = 'sufficient'
        state = test_report_generator(state)

        print("\n" + "=" * 60)
        print("✅ 모든 테스트 완료!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()


# 실행 방법:
# python examples/test_workflow_steps.py
