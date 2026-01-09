# Research Agent

LangGraph 기반 자동 리서치 및 리포트 생성 시스템

## 📋 프로젝트 개요

이 프로젝트는 **LangGraph**를 활용하여 주제에 대한 웹 리서치를 자동으로 수행하고, 수집된 정보를 분석하여 **전문적인 리포트**를 생성하는 AI Agent입니다. 검색부터 평가, 작성, 검토, 시각화까지 전 과정이 자동화되어 있으며, 최종 결과물을 **Markdown 및 PDF** 형식으로 제공합니다.

## ✨ 주요 기능

### 1. 지능형 검색 전략
- **자동 키워드 생성**: LLM이 주제를 분석하여 최적의 검색 키워드 생성
- **검색 범위 설정**: 국내/글로벌 자동 판단
- **반복 검색**: 정보 부족 시 자동으로 추가 키워드 생성 및 재검색

### 2. 정보 수집 및 평가
- **Tavily API 통합**: 고품질 웹 검색 수행
- **충분성 평가**: 수집된 정보의 양과 질을 자동으로 평가
- **적응형 반복**: 최대 3회까지 검색 반복 가능

### 3. 리포트 생성 및 품질 관리
- **구조화된 작성**: 목차, 본문, 참고자료가 포함된 전문 리포트
- **자체 검토 시스템**: AI가 작성한 리포트를 자동으로 검토하고 개선사항 도출
- **반복 수정**: 피드백을 반영하여 최대 1회 재작성
- **다국어 지원**: 한국어 및 영어 리포트 생성

### 4. 데이터 시각화
- **차트 자동 생성**: 리포트 내 데이터를 추출하여 차트 이미지 생성
- **다양한 차트 타입**: 막대, 선, 파이 차트 등 자동 선택
- **PDF 통합**: 생성된 차트를 리포트에 자동 삽입

### 5. 사용자 인터페이스
- **Streamlit 웹 UI**: 진행 상황 실시간 추적 및 결과 확인
- **단계별 로그**: 각 노드의 실행 과정과 AI의 판단 근거 표시
- **다운로드 기능**: Markdown 및 PDF 형식으로 다운로드

## 🏗️ 시스템 아키텍처

### LangGraph 워크플로우

```
[시작]
  ↓
[1. 검색 키워드 생성] ← query_generator
  ↓
[2. 웹 검색 실행] ← web_searcher
  ↓
[3. 정보 충분성 평가] ← info_evaluator
  ↓
  ├─ 부족 → [1. 검색 키워드 생성] (재검색, 최대 3회)
  ↓
  └─ 충분 → [4. 리포트 콘텐츠 작성] ← report_content_generator
              ↓
            [5. 리포트 검토] ← report_reviewer
              ↓
              ├─ 수정 필요 → [4. 리포트 콘텐츠 작성] (재작성, 최대 1회)
              ↓
              └─ 승인 → [6. 차트 생성] ← chart_generator
                          ↓
                        [7. 최종 파일 생성] ← report_file_generator
                          ↓
                        [종료]
```

### 핵심 설계 원칙

1. **자율적 의사결정**: 각 노드가 독립적으로 판단하고 다음 단계 결정
2. **순환 구조**: 품질 기준을 충족할 때까지 자동 반복
3. **상태 관리**: LangGraph State로 전체 워크플로우 데이터 공유
4. **조건부 라우팅**: 평가 결과에 따라 동적으로 경로 변경

## 📁 프로젝트 구조

```
research-agent/
├── .env                                  # API 키 설정
├── requirements.txt                      # 패키지 의존성
├── README.md                            # 프로젝트 문서
│
├── src/                                 # 핵심 로직
│   ├── research_agent_workflow.py       # LangGraph 워크플로우 정의
│   ├── research_state.py                # State 스키마 (TypedDict)
│   │
│   ├── nodes/                           # 워크플로우 노드
│   │   ├── query_generator.py          # 검색 키워드 생성
│   │   ├── web_searcher.py             # Tavily API 검색 실행
│   │   ├── info_evaluator.py           # 정보 충분성 평가
│   │   ├── report_content_generator.py # 리포트 콘텐츠 작성
│   │   ├── report_reviewer.py          # 리포트 품질 검토
│   │   ├── chart_generator.py          # 데이터 차트 생성
│   │   └── report_file_generator.py    # Markdown/PDF 파일 저장
│   │
│   └── utils/                           # 유틸리티
│       ├── pdf_exporter.py             # PDF 변환 (ReportLab)
│       ├── chart_visulalize.py         # 차트 시각화 (Matplotlib)
│       ├── source_formatter.py         # 참고자료 포매팅
│       ├── llm_config.py               # LLM 초기화
│       └── search_client.py            # Tavily 클라이언트
│
├── outputs/                             # 생성된 결과물
│   ├── charts/                         # 차트 이미지
│   └── pdfs/                           # PDF 리포트
│
├── streamlit_ui.py                      # Streamlit 웹 인터페이스
├── api_server.py                        # FastAPI 서버 (선택)
│
└── examples/                            # 예제 및 테스트
    ├── test_workflow_steps.py          # 단계별 테스트
    └── chart_extraction_test.py        # 차트 생성 테스트
```

## 🚀 설치 및 실행

### 1. 환경 설정

```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt
```

### 2. API 키 설정

`.env` 파일을 생성하고 다음 API 키를 입력하세요:

```env
GOOGLE_API_KEY=your_google_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

**API 키 발급 방법:**
- **Google API Key**: [Google AI Studio](https://aistudio.google.com/app/apikey)에서 발급
- **Tavily API Key**: [Tavily](https://tavily.com/)에서 무료 계정 생성 후 발급

### 3. 실행

#### Streamlit UI (권장)

```bash
streamlit run streamlit_ui.py
```

브라우저에서 `http://localhost:8501`로 접속하여 사용

## 🎯 사용 예시

### Streamlit UI 사용 흐름

1. **주제 입력**: "2025 AI 기술 동향"
2. **작성자 입력**: "김사원"
3. **언어 선택**: 한국어 / English
4. **리서치 시작** 버튼 클릭
5. **실시간 진행 상황 확인**:
   - 사이드바에서 각 단계별 상태 확인
   - 메인 영역에서 현재 단계의 상세 정보 표시
   - 에이전트의 판단 근거 및 실행 내용 확인
6. **결과 확인**:
   - 리포트 탭: 생성된 리포트 전문
   - 검색 결과 탭: 수집된 자료 목록
   - 통계 탭: 검색 반복 횟수, 키워드 등
7. **다운로드**: Markdown 또는 PDF 형식으로 저장

## 🛠️ 기술 스택

### 핵심 프레임워크
- **LangGraph** `^0.2.58`: 상태 기반 워크플로우 오케스트레이션
- **LangChain** `^0.3.14`: LLM 체인 및 프롬프트 관리
- **LangChain Google GenAI** `^2.0.8`: Gemini 모델 통합

### AI 모델
- **Google Gemini 2.0 Flash**: 검색 키워드 생성, 평가, 리포트 작성
- **Google Gemini 1.5 Flash**: 리포트 검토, 차트 데이터 추출

### 검색 및 데이터
- **Tavily Python** `^0.5.0`: AI 최적화 검색 API
- **BeautifulSoup4** `^4.12.3`: HTML 파싱

### 문서 생성
- **ReportLab** `^4.2.5`: PDF 생성
- **Markdown** `^3.7`: Markdown → HTML 변환
- **Matplotlib** `^3.10.0`: 차트 이미지 생성

### 웹 인터페이스
- **Streamlit** `^1.41.1`: 대화형 웹 UI

### 기타
- **Python-dotenv** `^1.0.1`: 환경 변수 관리

## 📊 주요 특징

### 1. LangGraph의 강점 활용

**순환 구조 (Cyclical Workflow)**
- 정보 부족 시 자동 재검색
- 품질 미달 시 자동 재작성
- 최대 반복 횟수로 무한 루프 방지

**조건부 라우팅 (Conditional Edges)**
```python
def should_continue_search(state):
    if state["evaluation"] == "sufficient":
        return "generate_report"
    elif state["iteration_count"] >= 3:
        return "generate_report"
    else:
        return "continue_search"
```

**상태 관리 (Shared State)**
- 모든 노드가 `ResearchState` 공유
- 검색 결과 누적 저장
- 반복 횟수 자동 추적

### 2. AI 에이전트 자율성

각 노드는 다음을 독립적으로 수행합니다:
- **판단**: 현재 상태 분석
- **실행**: 적절한 작업 수행
- **결정**: 다음 단계 선택

### 3. 투명한 실행 과정

Streamlit UI를 통해 다음 정보를 실시간으로 제공:
- 에이전트의 사고 과정
- 각 단계의 실행 내용
- 생성된 데이터 미리보기
- 다음 액션 계획

## 🔧 개발 및 테스트

### 단계별 테스트

```bash
python examples/test_workflow_steps.py
```

각 노드를 독립적으로 테스트하여 디버깅 가능

### 차트 생성 테스트

```bash
python examples/chart_extraction_test.py
```

차트 데이터 추출 및 시각화 검증

## 📝 라이선스

MIT License

## 🤝 기여

이슈 및 Pull Request를 환영합니다.

---

**Built with LangGraph** | Powered by Google Gemini & Tavily
