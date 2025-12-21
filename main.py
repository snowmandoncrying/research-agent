"""
Research Agent 메인 실행 파일
"""

from src.research_agent_workflow import run_research_agent


def main():
    """
    Research Agent를 실행합니다.
    """

    print("\n🤖 Research Agent에 오신 것을 환영합니다!\n")

    # 리서치 주제 입력
    topic = input("리서치 주제를 입력하세요: ").strip()

    if not topic:
        print("❌ 주제를 입력해주세요.")
        return

    # 리서치 실행
    try:
        final_state = run_research_agent(topic)

        # 결과 출력
        if final_state.get("final_report"):
            print("\n📄 최종 리포트:")
            print("-" * 60)
            print(final_state["final_report"][:500] + "...")
            print("-" * 60)
            print(f"\n✅ 전체 리포트는 outputs 폴더에 저장되었습니다.")
        else:
            print("\n⚠️ 리포트 생성에 실패했습니다.")

    except Exception as e:
        print(f"\n❌ 에러 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
