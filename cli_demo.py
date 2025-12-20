"""
CLI Demo
커맨드라인에서 Research Agent를 실행하는 간단한 데모입니다.
"""

import sys
import argparse
from src.research_agent_workflow import run_research_agent


def main():
    """
    CLI 메인 함수
    """

    # 인자 파싱
    parser = argparse.ArgumentParser(
        description="Research Agent - 자동 리서치 및 문서 생성 시스템"
    )

    parser.add_argument(
        "topic",
        type=str,
        nargs="?",  # optional
        help="리서치 주제 (예: 'AI 기술 동향 2024')"
    )

    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="대화형 모드로 실행"
    )

    args = parser.parse_args()

    # 주제 입력
    if args.interactive or not args.topic:
        print("=" * 60)
        print("🔍 Research Agent - CLI Demo")
        print("=" * 60)
        print()
        topic = input("리서치 주제를 입력하세요: ").strip()
    else:
        topic = args.topic

    if not topic:
        print("⚠️ 주제가 입력되지 않았습니다.")
        sys.exit(1)

    # Agent 실행
    try:
        result = run_research_agent(topic)

        # 결과 출력
        print("\n" + "=" * 60)
        print("📊 실행 결과")
        print("=" * 60)

        print(f"\n✅ 리포트 생성 완료!")
        print(f"📄 PDF 경로: {result.get('output_path', 'N/A')}")
        print(f"🔍 검색 반복: {result.get('iteration_count', 0)}회")
        print(f"📚 수집된 자료: {len(result.get('search_results', []))}개")

        # 리포트 미리보기 (첫 500자)
        print("\n" + "=" * 60)
        print("📄 리포트 미리보기")
        print("=" * 60)
        report = result.get("final_report", "")
        print(report[:500] + "...")

        print("\n" + "=" * 60)
        print("✅ 완료! 전체 내용은 PDF 파일을 확인하세요.")
        print("=" * 60)

    except KeyboardInterrupt:
        print("\n\n⚠️ 사용자에 의해 중단되었습니다.")
        sys.exit(0)

    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()


# 실행 방법:
# python cli_demo.py "AI 기술 동향 2024"
# python cli_demo.py --interactive
