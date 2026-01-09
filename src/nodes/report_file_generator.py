"""
최종 리포트 파일을 생성하는 노드
"""

import re
from ..research_state import ResearchState
from ..utils.pdf_exporter import save_markdown_as_pdf
from datetime import datetime
import os
        

def generate_report_file(state: ResearchState) -> dict:
    """
    생성 및 수정 완료된 리포트를 LLM 호출 없이 파일로 저장합니다.
    """
    topic = state.get("topic")
    author = state.get("author", "김사원")
    revision_count = state.get("revision_count", 0)
    version = revision_count + 1
    report_content = state.get("final_report")
    chart_paths = state.get("chart_paths", [])

    if not report_content:
      return {"output_path": None}

    # 리포트에서 차트 문자열을 찾아서 리스트로 반환
    chart_placeholders = re.findall(
      r"\[CHART_INSERT:.*?\]",
      report_content
    )

    # Streamlit 표시용: 상대 경로 마크다운 이미지 (final_report)
    streamlit_content = report_content
    if chart_placeholders and chart_paths:
      for placeholder, chart_path in zip(chart_placeholders, chart_paths):
        # 상대 경로로 마크다운 이미지 삽입 (Streamlit에서 표시 안 됨, 참고용)
        rel_path = str(chart_path).replace("\\", "/")
        img_markdown = f"![chart]({rel_path})"
        streamlit_content = streamlit_content.replace(placeholder, img_markdown, 1)
        print(f"   📊 차트 플레이스홀더 유지: {placeholder}")

    # PDF 생성용: 절대 경로 HTML 이미지 (별도 변수)
    pdf_content = report_content
    if chart_placeholders and chart_paths:
      for placeholder, chart_path in zip(chart_placeholders, chart_paths):
        # 절대 경로로 변환하고 슬래시로 정규화
        abs_path = os.path.abspath(chart_path).replace("\\", "/")
        # HTML img 태그로 직접 삽입
        img_html = f'<img src="{abs_path}" alt="chart" style="max-width: 100%;">'
        pdf_content = pdf_content.replace(placeholder, img_html, 1)
        print(f"   📊 PDF용 차트 삽입: {placeholder} -> {abs_path}")


    report_date = datetime.now().strftime("%Y년 %m월 %d일")

    # Streamlit 표시용 리포트 (상대경로 마크다운)
    streamlit_report = f"""# {topic}

**작성일:** {report_date} | **작성자:** {author}

---

{streamlit_content}
    """

    # PDF 생성용 리포트 (절대경로 HTML)
    pdf_report = f"""# {topic}

**작성일:** {report_date} | **작성자:** {author}

---

{pdf_content}
    """

    os.makedirs("outputs", exist_ok=True)

    safe_filename = "".join(c if c.isalnum() or c in " _-" else "_" for c in topic)
    md_path = f"outputs/{safe_filename}_v{version}.md"

    # Markdown 파일 저장 (Streamlit용)
    with open(md_path, "w", encoding="utf-8") as f:
      f.write(streamlit_report)

    # PDF 생성 (PDF용 콘텐츠 사용)
    try:
      pdf_path = save_markdown_as_pdf(pdf_report, topic)
      print(f"  📄 PDF 파일 생성 완료: {pdf_path}")
    except Exception as e:
      print(f"  ⚠️ PDF 생성 실패: {e}")
      import traceback
      traceback.print_exc()
      pdf_path = None

    return {
        "final_report": streamlit_content,  # Streamlit에 표시할 내용
        "output_path": pdf_path
    }
