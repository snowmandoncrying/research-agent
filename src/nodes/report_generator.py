"""
Report Generator Node
최종 리포트를 생성하는 노드입니다.
"""

from src.research_state import ResearchState
from src.utils.llm_config import get_llm
from src.utils.pdf_exporter import save_markdown_as_pdf
from langchain_core.prompts import ChatPromptTemplate
from datetime import datetime
import os


def generate_report(state: ResearchState) -> dict:
    """
    수집된 정보를 바탕으로 최종 리포트를 생성합니다.

    Args:
        state: 현재 상태

    Returns:
        업데이트할 상태 dict (final_report, output_path)
    """

    topic = state["topic"]
    search_results = state.get("search_results", [])

    print(f"\n[Report Generator] 리포트 생성 중...")

    # LLM 초기화
    llm = get_llm()

    # 검색 결과 정리
    sources = "\n\n".join([
        f"### 출처 {i+1}: {result.get('title', 'No Title')}\n"
        f"URL: {result.get('url', 'N/A')}\n"
        f"내용:\n{result.get('content', '')[:500]}...\n"
        for i, result in enumerate(search_results[:15])  # 최대 15개
    ])

    # 프롬프트 작성
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "당신은 전문적인 리서치 리포트를 작성하는 전문가입니다."),
        ("user", """
주제: {topic}

다음 자료들을 바탕으로 전문적인 리포트를 작성해주세요.

{sources}

리포트 구성:
1. 제목
2. 요약 (3-5줄)
3. 본문 (여러 섹션으로 구성)
4. 결론
5. 참고 자료 목록

Markdown 형식으로 작성해주세요.
        """)
    ])

    chain = prompt_template | llm
    response = chain.invoke({
        "topic": topic,
        "sources": sources
    })

    # 리포트 내용
    report_content = response.content if hasattr(response, 'content') else str(response)

    # 메타데이터 추가
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_report = f"""# {topic}

**생성 일시:** {timestamp}
**검색 결과 수:** {len(search_results)}개

---

{report_content}
"""

    print(f"  ✅ 리포트 생성 완료 ({len(full_report)} 글자)")

    # Markdown 파일 저장
    os.makedirs("outputs/reports", exist_ok=True)
    safe_filename = "".join(c if c.isalnum() or c in " _-" else "_" for c in topic)
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    md_path = f"outputs/reports/{safe_filename}_{timestamp_str}.md"

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(full_report)

    print(f"  💾 Markdown 저장: {md_path}")

    # PDF 저장
    # TODO: save_markdown_as_pdf 함수 구현 필요 (src/utils/pdf_exporter.py)
    pdf_path = save_markdown_as_pdf(full_report, topic)
    print(f"  📄 PDF 저장: {pdf_path}")

    return {
        "final_report": full_report,
        "output_path": pdf_path,
    }
