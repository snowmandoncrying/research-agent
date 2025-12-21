"""
Report Generator Node
최종 리포트를 생성하는 노드
"""

from ..research_state import ResearchState
from ..utils.llm_config import get_llm
from langchain_core.prompts import ChatPromptTemplate
from ..utils.pdf_exporter import save_markdown_as_pdf
from datetime import datetime
import os


def generate_report(state: ResearchState) -> dict:
    """
    수집된 정보를 바탕으로 한글 Markdown 리포트를 작성합니다.

    Args:
        state: 현재 상태

    Returns:
        업데이트할 상태 dict (final_report,  output_path)
    """

    topic = state["topic"]
    search_results = state.get("search_results", [])

    print(f"\n[Report Generator] 리포트 생성 중...")
    print(f"  기반 자료: {len(search_results)}개")

    # LLM 초기화 - 리포트 작성에는 다소 창의성이 필요하므로 온도 높게 설정
    llm = get_llm(temperature=0.7)

    # 검색 결과 정리
    sources = "\n\n".join([
        f"[{i+1}] {result.get('title', 'No Title')}\n"
        f"URL: {result.get('url', 'N/A')}\n"
        f"{result.get('content', '')[:300]}..."
        for i, result in enumerate(search_results)
    ])

    # 프롬프트 작성
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "당신은 전문적인 리서치 리포트를 한글로 작성하는 전문가입니다. 제공된 자료를 바탕으로 정확하고 읽기 쉬운 리포트를 작성합니다."),
        ("user", """
            주제: {topic}

            다음 자료들을 바탕으로 전문적인 리포트를 한글로 작성해주세요.

            {sources}

            리포트 구성:
            # {topic}

            ## 결론
            (핵심 내용 정리 및 시사점)
            
            ## 요약
            (3-5줄로 핵심 내용 요약)

            ## 본문
            (여러 섹션으로 나누어 상세히 설명)
            (검색 결과의 주요 내용을 종합하여 작성)

            ## 참고 자료
            (사용한 출처 목록 - 번호와 URL 포함)

            Markdown 형식으로 작성해주세요.
            전문적이고 구조화된 형식으로 작성하되, 자연스러운 문체를 유지하세요.
        """)
    ])

    # 리포트 생성
    try:
        chain = prompt_template | llm
        response = chain.invoke({
            "topic": topic,
            "sources": sources
        })

        # 리포트 내용
        report_content = response.content if hasattr(response, 'content') else str(response)

    except Exception as e:
        print(f"  ⚠️ 리포트 생성 실패: {e}")
        report_content = f"""# {topic}
        ## 오류 발생
        리포트 생성 중 오류가 발생했습니다.

        ## 수집된 자료
        {sources}

        ## 참고
        LLM 호출 중 오류가 발생하여 자동 생성된 리포트입니다.
    """

    # 메타데이터 추가
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_report = f"""---
        생성 일시: {timestamp}
        검색 결과 수: {len(search_results)}개
        ---

        {report_content}
    """

    print(f"  ✅ 리포트 내용 생성 완료 ({len(full_report)} 글자)")

    # Markdown 파일 저장
    try:
        os.makedirs("outputs", exist_ok=True)
        safe_filename = "".join(c if c.isalnum() or c in " _-" else "_" for c in topic)
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        md_path = f"outputs/{safe_filename}_{timestamp_str}.md"

        # Markdown 파일 저장
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(full_report)

        output_path = md_path
        print(f" Markdown 파일 저장 위치: {md_path}")

    except Exception as e:
        print(f"  ⚠️ Markdown 파일 저장 실패: {e}")
        output_path = None

    # PDF 생성
    pdf_path = None
    try: 
        print(f"  PDF로 생성 중...")
        pdf_path = save_markdown_as_pdf(full_report, topic)
        output_path = pdf_path
        print(f"  PDF 저장 위치: {pdf_path}")

    except Exception as e:
        print(f"  ⚠️ PDF 생성 실패: {e}")
        print(f"  → Markdown 파일로 저장합니다...")


    return {
        "final_report": full_report,
        "output_path": output_path 
    }
