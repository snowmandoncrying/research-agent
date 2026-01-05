"""
Report Reviewer Node
리포트를 평가하는 노드
"""

from ..research_state import ResearchState
from ..utils.llm_config import get_reviewr_llm
from langchain_core.prompts import ChatPromptTemplate
import json

def review_report(state: ResearchState) -> dict:
    """
    생성된 리포트를 검토하고 품질을 평가합니다.

    Args: 
      state: 현재 상태
    Returns:
      업데이트할 상태 dict (review_status, review_feedback, revision_count)
    """

    topic = state.get("topic")
    report = state.get("final_report")
    revision_count = state.get("revision_count", 0)
    MAX_REVISION = 2

    if report is None:
        print(" 리포트가 없습니다.")
        return {
            "review_status": "needs_revision",
            "review_feedback": "리포트가 생성되지 않았습니다.",
            "revision_count": revision_count + 1
        }
    
    if revision_count >= MAX_REVISION:
        print(" 최대 수정 횟수 초과, 리포트 생성 중단")
        return {
          "review_status": "approved",
          "review_feedback": "최대 수정 횟수를 초과하여 자동으로 생성합니다.",
          "revision_count": revision_count
        }


    llm = get_reviewr_llm()

    prompt = ChatPromptTemplate.from_messages([
        ("system", "당신은 전문적인 리포트 검토자입니다. 생성된 리포트의 품질을 엄격하게 평가하고 구체적인 개선 방안을 제시합니다."),
        ("user", """
            주제: {topic}
            다음은 AI가 작성한 리포트입니다:
            {report}
         
            위 리포트를 다음 기준으로 평가해주세요:

            1. 논리적 구조: 서론-본론-결론 흐름이 명확한가?
            2. 정보의 깊이: 표면적인 내용이 아닌 심도 있는 분석인가?
            3. 문법과 표현: 맞춤법, 문장 구조가 자연스러운가?
            4. 전문성: 용어 사용과 설명이 전문적인가?
            5. 완성도: 실무에 바로 제출 가능한 수준인가?

            다음 JSON 형식으로만 답변해주세요:
            {{
                "status": "approved" 또는 "needs_revision",
                "feedback": "구체적인 수정 지시사항",
                "strength": "리포트의 강점",
                "weakness": "개선이 필요한 부분"
            }}
        """)
    ])
    
    try:
        chain = prompt | llm
        response = chain.invoke({
            "topic": topic,
            "report": report[:3000]
        })

        # 응답 파싱    
        content = response.content if hasattr(response, 'content') else str(response)
        # JSON 추출 (마크다운 코드블록 제거)
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        
        review_result = json.loads(content.strip())
        
        status = review_result.get("status", "needs_revision")
        feedback = review_result.get("feedback", "")
        strength = review_result.get("strength", "")
        weakness = review_result.get("weakness", "")

        print(f"  평가 결과: {status}")
        print(f"  강점: {strength}")
        print(f"  이유: {weakness}")


        if status == "needs_revision":
            print(f"  {feedback}")
            return {
              "review_status": "needs_revision",
              "review_feedback": feedback,
              "revision_count": revision_count + 1
            }
        if status == "approved":
            print(f"  수정 필요 없음")
            return {
              "review_status": "approved",
              "review_feedback": feedback,
              "revision_count": revision_count
            }

        return {
          "review_status": "error",
          "review_feedback": feedback,
          "revision_count": revision_count
        }

    except Exception as e:
      print(f"  [경고] 리뷰 실패: {e}")
      return {
          "review_status": "error",
          "review_feedback": "리뷰 중 오류 발생",
          "revision_count": revision_count
      }
