from typing import Dict
from src.research_state import ResearchState
from src.utils.llm_config import get_llm
from src.utils.source_formatter import format_sources
from langchain_core.prompts import ChatPromptTemplate


# 리포트 내용 생성 및 수정
def generate_report_content(state: ResearchState) -> Dict:
    """
    리포트 내용만 생성하거나 수정합니다.
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
    
    # 리뷰 기반 수정
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
            - 기존 리포트의 전체 구조를 유지하되, 지적된 부분을 개선하세요.
            - 이미 삽입된 [CHART_INSERT: 제목] 표시는 삭제하거나 변경하지 마십시오.
            - 차트의 개수, 제목, 위치는 유지하고, 문장 표현과 설명만 수정하십시오.
            - Markdown 형식으로 작성해주세요.   
        """,
          "en": """
            Previous Report: {previous_report}
            Reviewer Feedback: {review_feedback}
            Source Materials: {sources}

            [Revision Instructions]: 
              - Revise the report according to the feedback.
              - Preserve the existing structure.
              - Do NOT remove or modify existing [CHART_INSERT: title] placeholders.
              - Keep chart titles and positions unchanged; only refine the narrative.
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
        content = response.content if hasattr(response, "content") else str(response)

        return {
            "final_report": content
        }

    # 신규 리포트 생성    
    else:
        print(f"  [생성] 새로운 리포트 작성 중... (언어: {report_language})")
        
        system_prompts_writer = {
          "ko": ("당신은 전문적인 리서치 리포트를 한글로 작성하는 전문가입니다."
                "제공된 자료를 바탕으로 정확하고 읽기 쉬운 리포트를 작성합니다."
                "차트 생성 및 시각화는 다른 노드에서 처리됩니다."
          ),
          "en": ("You are a professional research report writer. "
                "Write accurate and well-structured reports in English. "
                "Chart generation and visualization are handled by a separate component."
          )
        }

        user_prompts_writer = {
          "ko": """
                주제:{topic}
                다음 자료들을 바탕으로 전문적인 리포트를 한글로 작성해주세요.
                {sources}

              [리포트 구성 가이드]:
                ## 1. 개요 및 요약
                - 리서치 주제의 핵심 내용과 현재의 중요성을 3-5줄로 요약하십시오.

                ## 2. 주요 현황 및 데이터 분석
                - 수집된 자료에서 확인된 최신 트렌드와 구체적인 수치를 바탕으로 분석하십시오.
                - **수치 데이터가 강조되는 문단 바로 아래에 반드시 [CHART_INSERT: 차트 제목]을 삽입하십시오.**

                ## 3. 심층 사례 분석
                - 주요 기업, 기관 또는 국가별 실제 적용 사례를 상세히 기술하십시오.

                ## 4. 시사점 및 결론
                - 리서치 결과를 바탕으로 한 전략적 제언 및 향후 전망을 제시하십시오.

                ## 5. 참고 자료
                - 사용된 모든 출처의 제목과 URL을 번역 없이 원문 그대로 나열하십시오.

                [작성 지침]
                - 주요 지표와 핵심 문구는 **볼드체**를 사용하십시오.
                - [CHART_INSERT: 제목]은 실제 차트를 생성하는 것이 아니라, 시각화 노드에서 생성된 차트가 삽입될 위치를 표시하기 위한 자리 표시자입니다.
                - 차트의 수치나 구조를 새로 만들지 말고, 본문에서는 해당 데이터를 해석·설명하는 역할만 수행하십시오.
                - 반드시 Markdown 형식을 사용하십시오.
            """,
          "en": """
              Topic: {topic}
              Please write a professional research report in English based on the following materials.
              {sources}

              [Report Structure Guide]:

              ## 1. Executive Summary
              - Provide a concise summary (3–5 lines) of the core research findings and their current strategic significance.

              ## 2. Key Trends & Data Analysis
              - Analyze the latest industry trends and insights based on specific quantitative figures found in the sources.
              - Immediately below paragraphs that emphasize numerical data, 반드시 insert
                [CHART_INSERT: Chart Title].

              ## 3. In-depth Case Studies
              - Describe real-world applications and success stories of major companies, institutions, or countries in detail.

              ## 4. Strategic Implications & Conclusion
              - Offer strategic recommendations and future outlooks based on the research findings.

              ## 5. References
              - List all source titles and URLs in their original language and format.

              [Writing Instructions]
              - [CHART_INSERT: Chart Title] is a placeholder only.
                It does NOT generate charts and indicates where charts generated by a visualization node will be inserted.
              - Do NOT create, modify, or invent chart data, chart structures, or numerical values.
              - Your role is to interpret and explain the data in narrative form only.
              - Use **bold formatting** for key metrics and important phrases.
              - Write strictly in Markdown format.
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

        content = response.content if hasattr(response, "content") else str(response)

        return {
            "final_report": content
        }