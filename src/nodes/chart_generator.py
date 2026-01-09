"""
리포트 본문에서 시각화 가능한 데이터를 추출하고 차트를 생성하는 노드
"""

import json
from typing import Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.research_state import ResearchState
from src.utils.llm_config import get_llm
from langchain_core.prompts import ChatPromptTemplate
from src.utils.chart_visulalize import create_chart

# LLM을 통해 데이터 추출
def extract_chart_data(state: ResearchState) -> Dict:
  """
  리포트 본문에서 데이터를 추출하고 차트 이미지를 생성하여 경로 리스트를 반환합니다.

  프로세스:
    1. final_report가 있는지 확인
    2. LLM으로 시각화 가능한 데이터 추출
    3. 각 데이터로 차트 생성
    4. 생성된 차트 경로 리스트 반환
  """

  final_report = state.get("final_report")
  chart_data = state.get("chart_data")

  # Step 1: 리포트 존재 확인
  if not final_report:
    return {"chart_paths": []}
  
  # Step 2: chart_data가 이미 있으면 → 재사용 (병렬 생성)
  if chart_data:
    chart_paths = []

    # 병렬로 차트 생성
    with ThreadPoolExecutor(max_workers=min(len(chart_data), 4)) as executor:
      future_to_chart = {
        executor.submit(create_chart, chart): i
        for i, chart in enumerate(chart_data)
      }

      for future in as_completed(future_to_chart):
        try:
          path = future.result()
          if path:
            chart_paths.append(path)
        except Exception as e:
          print(f"  ⚠️ 차트 생성 실패: {e}")

    return {
      "chart_data": chart_data,
      "chart_paths": chart_paths,
    }

  # Step 3: chart_data가 없으면 → 최초 1회 추출
  llm = get_llm(temperature=0.1)

  prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 리포트에서 시각화 가능한 수치 데이터를 추출하는 전문가입니다."),
    ("user", """
    다음 리포트에서 차트로 만들 수 있는 수치 데이터를 모두 찾아 JSON 형식으로 추출하세요.
    반드시 본문에 명시된 실제 숫자만 사용하세요.

    [리포트 본문]
    {report}
     
    [지침]
     1. 차트 타입 결정 시 시간 흐름(연도, 월)이 포함되면 'line'으로, 전체 대비 비중(%)이 중요하면 'pie'로, 항목 간 수치 비교라면 'bar'로 생성하세요.
     2. 응답은 반드시 아래 형식을 지킨 JSON 배열이어야 합니다.

     [출력 형식]
        {{
          "charts": [
            {{
              "title": "차트 제목",
              "type": "line | bar | pie",
              "data": [
                {{"label": "항목", "value": 숫자}}
              ]
            }}
          ]
        }}
        데이터가 없으면 {{"charts": []}}라고 답하세요.
        """)
    ])
  
  # [Step 4] LLM으로 시각화 데이터 추출
  chain = prompt | llm
  response = chain.invoke({"report": final_report})
  content = response.content if hasattr(response, 'content') else str(response)

  # 응답 파싱 및 리스트 추출
  try:
      # JSON 추출 (마크다운 코드블록 제거)
      if "```json" in content:
          content = content.split("```json")[1].split("```")[0]
      elif "```" in content:
          content = content.split("```")[1].split("```")[0]
      
      chart_data = json.loads(content.strip()).get("charts", []) 
            
  except Exception as e:
      print(f"  데이터 파싱 실패: {e}")
      return {"charts_path": []}
  
  # [Step 5] 각 데이터로 최초 차트 생성 후 경로 반환 (병렬 처리)
  chart_paths = []

  if chart_data:
    # 병렬로 차트 생성
    with ThreadPoolExecutor(max_workers=min(len(chart_data), 4)) as executor:
      future_to_chart = {
        executor.submit(create_chart, chart_item): i
        for i, chart_item in enumerate(chart_data)
      }

      for future in as_completed(future_to_chart):
        try:
          path = future.result()
          if path:
            chart_paths.append(path)
        except Exception as e:
          print(f"  ⚠️ 차트 생성 실패: {e}")

  return {
      "chart_paths": chart_paths,
      "chart_data": chart_data
  }