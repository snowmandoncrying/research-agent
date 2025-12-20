# Research Agent

자동 리서치 → 문서 생성 Agent (LangGraph 기반)

## 프로젝트 개요

이 프로젝트는 LangGraph를 활용하여 자동으로 웹 리서치를 수행하고, 결과를 분석하여 PDF 리포트를 생성하는 AI Agent입니다.

### 주요 기능

- **자동 검색 키워드 생성**: 주제에 맞는 최적의 검색어 생성
- **웹 검색 및 정보 수집**: Tavily API를 활용한 실시간 웹 검색
- **정보 충분성 평가**: 수집된 정보가 충분한지 자동 판단
- **순환 구조**: 정보가 부족하면 자동으로 재검색
- **리포트 생성**: 수집된 정보를 기반으로 구조화된 문서 작성
- **PDF 출력**: 최종 결과물을 PDF로 내보내기

### LangGraph의 강점 활용

1. **순환 구조**: 검색 → 평가 → 부족하면 다시 검색
2. **조건부 분기**: 정보 충분성에 따라 다른 경로 실행
3. **상태 관리**: 여러 검색 결과를 누적하고 관리
4. **Human-in-the-loop**: 중간에 사람이 확인하고 방향 수정 가능

## 설치 방법

### 1. 가상환경 생성 및 활성화

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. API 키 설정

`.env` 파일에 다음 API 키들을 설정하세요:

```
GOOGLE_API_KEY=your_google_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

## 사용 방법

### CLI 데모

```bash
python cli_demo.py "AI 기술 동향"
```

### Streamlit UI

```bash
streamlit run streamlit_ui.py
```

## 프로젝트 구조

```
research-agent/
├── .env                                  # API 키 설정
├── .gitignore                            # Git 제외 파일
├── requirements.txt                      # 패키지 의존성
├── README.md                            # 프로젝트 소개
│
├── src/                                 # 핵심 로직
│   ├── __init__.py
│   ├── research_agent_workflow.py       # 메인 LangGraph 워크플로우 정의
│   ├── research_state.py                # State 스키마 정의
│   │
│   ├── nodes/                           # 각 노드별 로직
│   │   ├── __init__.py
│   │   ├── query_generator.py          # 검색 키워드 생성 노드
│   │   ├── web_searcher.py             # 웹 검색 실행 노드
│   │   ├── info_evaluator.py           # 정보 충분성 평가 노드
│   │   └── report_generator.py         # 리포트 생성 노드
│   │
│   └── utils/                           # 유틸리티
│       ├── __init__.py
│       ├── pdf_exporter.py             # PDF 변환 및 저장
│       ├── llm_config.py               # LLM 초기화 설정
│       └── search_client.py            # Tavily 클라이언트 래퍼
│
├── outputs/                             # 생성된 결과물
│   ├── reports/                         # Markdown 리포트
│   └── pdfs/                           # PDF 파일
│
├── streamlit_ui.py                      # Streamlit 웹 인터페이스
├── cli_demo.py                          # 커맨드라인 실행용
│
└── examples/                            # 예제 및 테스트
    ├── example_simple_research.py       # 간단한 사용 예제
    └── test_workflow_steps.py          # 단계별 테스트
```

## 워크플로우

```
[시작]
  ↓
[검색 키워드 생성] ← query_generator.py
  ↓
[웹 검색 실행] ← web_searcher.py
  ↓
[정보 충분성 평가] ← info_evaluator.py
  ↓
  ├─ 충분함 → [리포트 생성] ← report_generator.py → [종료]
  └─ 부족함 → [검색 키워드 생성] (재시작)
```

## 기술 스택

- **LangGraph**: 워크플로우 및 상태 관리
- **LangChain**: LLM 체인 및 프롬프트 관리
- **Google Gemini**: LLM 모델 (gemini-1.5-pro)
- **Tavily API**: 웹 검색 엔진
- **ReportLab**: PDF 생성
- **Streamlit**: 웹 UI
- **Python-dotenv**: 환경 변수 관리

## 라이선스

MIT
