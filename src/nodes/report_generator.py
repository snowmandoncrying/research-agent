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

# 리포트 내용 생성 및 수정
def generate_report_content(state: ResearchState) -> str:
    """
    리포트 내용만 생성하거나 수정합니다.
    파일 저장이나 PDF 생성은 여기서 처리하지 않습니다.
    """

    topic = state.get("topic")
    search_results = state.get("search_results", [])
    review_feedback = state.get("review_feedback")
    review_status = state.get("review_status")
    previous_report = state.get("final_report")

    llm = get_llm(usage="generator")
    
    # 검색 결과 정리
    sources = format_sources(search_results)
    
    if review_status == "needs_revision" and review_feedback:
        # 프롬프트 작성
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "당신은 전문적인 리서치 리포트를 한글로 수정하는 편집가입니다. 리뷰어의 피드백을 반영하여 리포트를 개선합니다."),
            ("user", """
                이전 리포트: {previous_report}
                리뷰어 피드백: {review_feedback}
                원본 검색 자료: {sources}

            지침: 
            - 위 피드백을 반영하여 리포트를 수정해주세요.
            - 기존 구조를 유지하되, 지적된 부분을 개선하세요.
            - Markdown 형식으로 작성해주세요.                
            """)
        ])

        chain = prompt_template | llm
        response = chain.invoke({
            "previous_report": previous_report,
            "review_feedback": review_feedback,
            "sources": format_sources(search_results)
        })

        # 수정된 리포트 내용 반환
        report_content = response.content if hasattr(response, 'content') else str(response)
        return report_content

    else:
        print(f"  [생성] 새로운 리포트 작성 중...")
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

        chain = prompt_template | llm
        response = chain.invoke({
            "topic": topic,
            "sources": sources
        })

        # 리포트 내용
        report_content = response.content if hasattr(response, 'content') else str(response)
        return report_content

# 마크다운 및 pdf 파일로 저장
def generate_report(state: ResearchState) -> dict:
    """
    생성 및 수정된 내용을 바탕으로 LLM 호출 없이 파일만 저장합니다.
    """
    topic = state.get("topic")
    revision_count = state.get("revision_count", 0)
    version = revision_count + 1
    search_results = state.get("search_results", [])
    review_status = state.get("review_status")

    if review_status == "error":
        print(" 리뷰 오류 상태, 리포트 생성 중단")
        return {
          "final_report": state.get("final_report"),
           "output_path": None
        }
    
    try:
      report_content = generate_report_content(state)

    except Exception as e:
        print(f"  [경고] 리포트 생성 실패: {e}")
        report_content = "리포트 생성 중 오류가 발생했습니다."

    # 메타데이터 추가
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_report = f"""---
        생성 일시: {timestamp}
        검색 결과 수: {len(search_results)}개
        ---
        # 리포트 v{version}
        {report_content}
    """

    print(f"  [완료] 리포트 내용 생성 완료 ({len(full_report)} 글자)")

    if review_status == "approved" or revision_count >= 2:
      print(f"  [PDF] 최종적으로 검토됨. 파일 생성 중...")

      # Markdown 파일 저장
      try:
          os.makedirs("outputs", exist_ok=True)
          safe_filename = "".join(c if c.isalnum() or c in " _-" else "_" for c in topic)
          timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
          md_path = f"outputs/{safe_filename}_v{version}_{timestamp_str}.md"

          # Markdown 파일 저장
          with open(md_path, "w", encoding="utf-8") as f:
              f.write(full_report)

          output_path = md_path
          print(f"  [저장] Markdown 파일 저장 위치: {md_path}")

      except Exception as e:
          print(f"  [경고] Markdown 파일 저장 실패: {e}")
          output_path = None

      # PDF 생성
      pdf_path = None
      try: 
          print(f"  PDF로 생성 중...")
          pdf_path = save_markdown_as_pdf(full_report, topic)
          output_path = pdf_path
          print(f"  [저장] PDF 저장 위치: {pdf_path}")

      except Exception as e:
          print(f"  [경고] PDF 생성 실패: {e}")
          print(f"  [대안] Markdown 파일로 저장합니다...")


      return {
          "final_report": report_content,
          "output_path": output_path 
      }
    
    else:
      print(f"  [대기] Markdown만 저장, 리뷰 대기중...")
      return {
        "final_report": report_content,
        "output_path": None           
      }



# 포맷팅 헬퍼 엣지 함수
def format_sources(search_results):
    return "\n\n".join([
    f"[{i+1}] {result.get('title', 'No Title')}\n"
    f"URL: {result.get('url', 'N/A')}\n"
    f"{result.get('content', '')[:300]}..."
    for i, result in enumerate(search_results)
  ])