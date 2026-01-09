from pathlib import Path
import plotly.graph_objects as go


def validate_chart_data(chart_data: dict) -> bool:
  """
  LLM이 생성한 차트 데이터가 유효한지 검사하는 함수
  """
  try:
      # 1. 필수 필드("title", "type", "data")가 딕셔너리에 있는지 확인한다. 만약 하나라도 없으면 False를 반환한다.
      # if "title" or "type" or "data" not in chart_data:
      if not all(k in chart_data for k in ["title", "type", "data"]):
        return False
      
      # 2. 차트 타입이 우리가 지원하는 것인지 확인한다.
      # ["bar", "line", "pie"] 중에 해당하지 않으면 False를 반환한다.
      chart_type = chart_data.get("type")
      if chart_type not in ["bar", "line", "pie"]:
         return False

      # 3. data가 리스트(list) 형식인지 확인한다.
      # 리스트가 아니거나, 리스트가 비어있으면(len == 0) False를 반환한다.
      # if chart_data is not list or len(chart_data) == 0:
      #    return False
      data_list = chart_data.get("data")
      if not isinstance(data_list, list) or len(data_list) == 0:
        return False


      # 4. data 리스트 안을 반복문(for)으로 돌면서 확인한다.
      # - 각 항목이 딕셔너리인가?
      # - "label"과 "value"라는 키가 들어있는가?
      # - "value"가 숫자(int 또는 float)인가?
      # 하나라도 어긋나면 False를 반환한다.
      for item in data_list:
        if not isinstance(item, dict): return False
        if "label" not in item or "value" not in item: return False
        if not isinstance(item["value"], (int, float)): return False

      # 모든 검문을 통과했다면?
      return True

  except Exception as e:
      # 예상치 못한 에러가 나면 일단 False를 반환한다.
      print(f"검증 중 에러 발생: {e}")
      return False


def create_chart(chart_data: dict, output_dir: str = "outputs/charts") -> str:
  """
  차트 데이터를 받아 Plotly 차트를 생성하고 이미지로 저장
    입력: {"title": "시장 규모", "type": "line", "data": [...]}
    출력: "outputs/charts/시장_규모.png"
  """

  if not validate_chart_data(chart_data):
    print(f"   ⚠️ 차트 데이터 검증 실패: {chart_data.get('title', '제목 없음')}")
    return None

  # Step 1: 저장할 폴더 만들기
  # outputs/charts/ 폴더가 없으면 자동 생성
  Path(output_dir).mkdir(parents=True, exist_ok = True)
    
  # Step 2: 주문서에서 재료 꺼내기
  # chart_data에서 title, type, data 추출
  title = chart_data["title"]
  chart_type = chart_data["type"]
  data = chart_data["data"]
  
  # data를 x축, y축으로 분리
  labels = []
  values = []
  for item in data:
      labels.append(item["label"])
      values.append(item["value"])

  # Step 3: 차트 그리기
  # type이 "line"이면 선 그래프
  # type이 "bar"면 막대 그래프
  # type이 "pie"면 원형 그래프
  if chart_type == "line":
    fig = go.Figure(data=go.Scatter(
      x=labels,
      y=values,
      mode='lines+markers',
      line=dict(width=3, color='#1f77b4'),
      marker=dict(size=8)
    ))

  elif chart_type == "bar":
    fig = go.Figure(data=go.Bar(
      x=labels,
      y=values,
      marker=dict(color='#1f77b4')
    ))

  elif chart_type == "pie":
    fig = go.Figure(data=go.Pie(
      labels=labels,
      values=values,
      textinfo='label+percent',
      textfont=dict(size=14)
    ))

  else:
    raise ValueError("지원하지 않는 타입: {chart_type}")

  # 한글 폰트 설정 및 레이아웃
  fig.update_layout(
    title=dict(text=title, font=dict(size=20, color='#333')),
    width=800,
    height=500,
    margin=dict(l=70, r=50, t=100, b=70),
    template="plotly_white",
    font=dict(family="Malgun Gothic, Arial, sans-serif", size=12),
    showlegend=True,
    hovermode='closest'
  )

  # 축 레이블 폰트 설정 (line, bar 차트만)
  if chart_type in ["line", "bar"]:
    fig.update_xaxes(title_font=dict(size=14), tickfont=dict(size=12))
    fig.update_yaxes(title_font=dict(size=14), tickfont=dict(size=12))               
  
  # Step 4: 파일명 생성 후 저장
  # "시장_규모.png" 같은 이름으로 저장
  filename = title.replace(" ", "_")
  filename = "".join(c if c.isalnum() or c == "_" else "_" for c in filename)
  output_path = Path(output_dir) / f"{filename}.png"

  try:
    fig.write_image(str(output_path), engine="kaleido")
    print(f"   ✅ 차트 저장: {output_path}")
    # Step 5: 저장 경로 반환
    # "outputs/charts/시장_규모.png" 문자열 반환
    return str(output_path)

  except Exception as e:
    print(f"   ⚠️ 차트 저장 실패: {e}")
    return None