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
    report_language = state.get("report_language", "ko")
    search_results = state.get("search_results", [])
    review_feedback = state.get("review_feedback")
    review_status = state.get("review_status")
    previous_report = state.get("final_report")

    llm = get_llm(usage="generator")
    
    # 검색 결과 정리
    sources = format_sources(search_results)
    
    if review_status == "needs_revision" and review_feedback:
        print(f"  [수정] 리포트 수정 중... (언어: {report_language})")

        system_prompts_editor = {
          "ko": "당신은 전문적인 리서치 리포트를 한글로 수정하는 편집가입니다. 리뷰어의 피드백을 반영하여 리포트를 개선합니다.",
          "en": "You are a professional editor who revises research reports in English. Improve the report by incorporating reviewer feedback."
        }

        user_prompts_editor = {
          "ko": """
            이전 리포트: {previous_report}
            리뷰어 피드백: {review_feedback}
            원본 검색 자료: {sources}

            지침: 
            - 위 피드백을 반영하여 리포트를 수정해주세요.
            - 기존 구조를 유지하되, 지적된 부분을 개선하세요.
            - Markdown 형식으로 작성해주세요.   
        """,
          "en": """
            Previous Report: {previous_report}
            Reviewer Feedback: {review_feedback}
            Source Materials: {sources}

            Instructions: 
            - Revise the report in English based on the feedback above.
            - Maintain the existing structure while improving the identified issues.
            - Write in Markdown format.        
        """
        }

        # 프롬프트 작성
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompts_editor.get(report_language, system_prompts_editor["ko"])),
            ("user", user_prompts_editor.get(report_language, user_prompts_editor["ko"]))
        ])

        chain = prompt_template | llm
        response = chain.invoke({
            "previous_report": previous_report,
            "review_feedback": review_feedback,
            "sources": sources
        })

        # 수정된 리포트 내용 반환
        report_content = response.content if hasattr(response, 'content') else str(response)
        return report_content

    else:
        print(f"  [생성] 새로운 리포트 작성 중... (언어: {report_language})")
        
        system_prompts_writer = {
          "ko": "당신은 전문적인 리서치 리포트를 한글로 작성하는 전문가입니다. 제공된 자료를 바탕으로 정확하고 읽기 쉬운 리포트를 작성합니다.",
          "en": "You are a professional research report writer. Create accurate and well-structured reports in English based on the provided materials."
        }

        user_prompts_writer = {
          "ko": """
                다음 자료들을 바탕으로 전문적인 리포트를 한글로 작성해주세요.
                {sources}

              [리포트 구성 가이드]:
                # {topic}

                제공된 자료들을 종합 분석하여 전문적인 리포트를 작성하십시오.

                ## 1. 개요 및 요약
                - 리서치 주제의 핵심 내용과 현재의 중요성을 3-5줄로 요약하십시오.

                ## 2. 주요 현황 및 데이터 분석
                - 수집된 자료에서 확인된 최신 트렌드와 구체적인 수치를 바탕으로 분석하십시오.
                - 국내외 현황을 비교하여 기술하십시오.

                ## 3. 심층 사례 분석
                - 주요 기업, 병원 또는 국가별 실제 적용 사례를 상세히 기술하십시오.

                ## 4. 시사점 및 결론
                - 리서치 결과를 바탕으로 한 전략적 제언 및 향후 전망을 제시하십시오.

                ## 5. 참고 자료
                - 사용된 모든 출처의 제목과 URL을 번역 없이 원문 그대로 나열하십시오.

                [작성 지침]
                - 반드시 Markdown 형식을 사용하고, 본문 내 인용은 [1], [2] 형태로 표기하십시오.
                - 영어 자료의 핵심 수치는 한국어로 번역하여 포함하되, 고유명사는 원문을 병기하십시오.
            """,
          "en": """
              Topic: {topic}

              Please write a professional research report in English based on the following materials.
              {sources}

              [Report Structure Guide]:
              # {topic}

              Synthesize the provided materials to conduct a comprehensive analysis and produce a high-quality professional report.

              ## 1. Executive Summary
              - Provide a concise summary (3-5 lines) of the core research findings and their current strategic significance.

              ## 2. Key Trends & Data Analysis
              - Analyze the latest industry trends and insights based on specific figures and quantitative data found in the sources.
              - Conduct a comparative analysis between domestic (South Korea) and global market conditions.

              ## 3. In-depth Case Studies
              - Describe specific real-world applications and success stories by major corporations, institutions, or specific countries in detail.

              ## 4. Strategic Implications & Conclusion
              - Offer strategic recommendations and a future outlook based on the synthesized research results.

              ## 5. References
              - List the titles and URLs of all sources used in their original language and format.

              [Writing Instructions]
              - The report must be written entirely in professional English.
              - Use Markdown format for structural clarity.
              - Use in-text citations in the format [1], [2] to link findings to their respective sources.
              - Ensure all data and insights from Korean sources are accurately translated and integrated into a professional English context.
          """
        }
        
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompts_writer.get(report_language, system_prompts_writer["ko"])),
            ("user", user_prompts_writer.get(report_language, user_prompts_writer["ko"]))
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
    author = state.get("author", "김사원")
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
    report_date = datetime.now().strftime("%Y년 %m월 %d일")

    full_report = f"""# {topic} (v{version})

**작성일:** {report_date} | **작성자:** {author}

---

{report_content}
    """

    print(f"  [완료] 리포트 내용 생성 완료 ({len(full_report)} 글자)")

    output_path = None
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