"""
간단한 사용 예제
Research Agent를 가장 간단하게 실행하는 예제입니다.
"""

from src.research_agent_workflow import run_research_agent


def main():
    """
    간단한 리서치 실행 예제
    """

    # 리서치 주제
    topic = "LangGraph 사용법"

    print(f"주제: {topic}")
    print("-" * 60)

    # Agent 실행
    result = run_research_agent(topic)

    # 결과 확인
    print("\n" + "=" * 60)
    print("결과:")
    print("=" * 60)

    print(f"✅ 완료!")
    print(f"📄 PDF: {result['output_path']}")
    print(f"🔍 반복: {result['iteration_count']}회")
    print(f"📚 자료: {len(result['search_results'])}개")

    # 리포트 일부 출력
    print("\n리포트 미리보기:")
    print("-" * 60)
    print(result['final_report'][:300] + "...")


if __name__ == "__main__":
    main()


# 실행 방법:
# python examples/example_simple_research.py
