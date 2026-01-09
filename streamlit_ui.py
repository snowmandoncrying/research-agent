"""
Streamlit Web UI
Research Agent를 웹 인터페이스로 실행합니다.
"""

import streamlit as st
from src.research_agent_workflow import create_research_workflow
from src.research_state import ResearchState
import os

def main():
    """
    Streamlit 앱 메인 함수
    """

    # 페이지 설정
    st.set_page_config(
        page_title="Research Agent",
        page_icon="🔍",
        layout="wide",
    )

    # 제목
    st.title("🔍 Research Agent")
    st.markdown("자동 리서치 및 문서 생성 시스템 (LangGraph 기반)")

    # 사이드바: 진행 목록
    with st.sidebar:
        # 설정 정보는 접을 수 있게
        with st.expander("⚙️ 설정", expanded=False):
            # API 키 확인
            google_api_key = os.getenv("GOOGLE_API_KEY")
            tavily_api_key = os.getenv("TAVILY_API_KEY")

            if google_api_key:
                st.success("✅ Google API Key")
            else:
                st.error("❌ Google API Key 미설정")

            if tavily_api_key:
                st.success("✅ Tavily API Key")
            else:
                st.error("❌ Tavily API Key 미설정")

        # Agent Workflow 요약
        st.markdown("### 🔄 Agent Workflow")
        st.markdown("""
1. **Query Generation** - 주제 분석 및 검색 키워드 생성
2. **Web Search** - Tavily API 기반 정보 수집
3. **Information Evaluation** - 수집 정보 충분성 평가 및 재검색 판단
4. **Report Content Generation** - 구조화된 리포트 초안 작성
5. **Report Review** - 품질 검토 및 개선사항 도출
6. **Chart Generation** - 데이터 시각화 차트 생성
7. **Final Report Export** - Markdown 및 PDF 파일 생성
        """)
        st.markdown("---")

        # 진행 목록 헤더
        st.markdown("### 📋 진행 상황")
        st.markdown("---")

    # 메인 영역
    st.header("📝 리서치 주제 입력")

    # 입력 폼
    with st.form(key="research_form"):
        
        topic = st.text_input(
            "주제를 입력하세요",
            placeholder="예: AI 기술 동향 2025",
            help="리서치하고 싶은 주제를 자유롭게 입력하세요"
        )
        
        author = st.text_input(
            "작성자 성함",
            placeholder="예: 김사원",
            help="리포트에 표시될 작성자 이름을 입력하세요"
        )
        
        report_language_check = st.radio("최종 리포트 언어", ["한국어", "English"], horizontal=True)

        submit_button = st.form_submit_button(
            label="🔍 리서치 시작",
            use_container_width=True
        )

    # Session State 초기화
    if 'steps_log' not in st.session_state:
        st.session_state.steps_log = []
    if 'current_step_idx' not in st.session_state:
        st.session_state.current_step_idx = None

    # 리서치 실행
    if submit_button:
        if not topic:
            st.warning("⚠️ 주제를 입력해주세요.")
            return

        if not google_api_key or not tavily_api_key:
            st.error("❌ API 키가 설정되지 않았습니다. .env 파일을 확인해주세요.")
            return

        # 초기화
        st.session_state.steps_log = []
        st.session_state.current_step_idx = 0

        # 진행 상황 표시
        st.markdown("---")
        st.subheader("🚀 리서치 진행 중")

        # 전체 진행률
        progress_bar = st.progress(0)

        # 사이드바에 진행 목록 표시할 placeholder
        sidebar_placeholder = st.sidebar.empty()

        # 메인 영역에 현재 단계 상세 정보 표시할 placeholder
        main_detail_placeholder = st.empty()

        # 헬퍼 함수들
        def add_step_log(step_name, status, title, details):
            """단계 로그 추가"""
            st.session_state.steps_log.append({
                "name": step_name,
                "status": status,
                "title": title,
                "details": details,
                "timestamp": len(st.session_state.steps_log)
            })
            st.session_state.current_step_idx = len(st.session_state.steps_log) - 1

        def update_sidebar():
            """사이드바 진행 목록 업데이트"""
            with sidebar_placeholder.container():
                for idx, step in enumerate(st.session_state.steps_log):
                    status_icon = {
                        "완료": "✅",
                        "진행중": "🔄",
                        "대기": "⏳",
                        "실패": "❌"
                    }.get(step["status"], "⏳")

                    # 현재 진행 중인 단계는 강조
                    if idx == st.session_state.current_step_idx:
                        st.markdown(f"**{status_icon} {step['title']}** ⬅️")
                    else:
                        st.markdown(f"{status_icon} {step['title']}")

        def update_main_detail():
            """메인 영역에 현재 단계 상세 정보 표시"""
            if st.session_state.current_step_idx is not None and st.session_state.steps_log:
                current_step = st.session_state.steps_log[st.session_state.current_step_idx]

                with main_detail_placeholder.container():
                    st.markdown(f"## {current_step['title']}")
                    st.markdown("---")

                    # 상태 표시
                    status_color = {
                        "완료": "green",
                        "진행중": "blue",
                        "대기": "gray",
                        "실패": "red"
                    }.get(current_step["status"], "gray")

                    st.markdown(f"**상태:** :{status_color}[{current_step['status']}]")
                    st.markdown("---")

                    # 상세 정보 표시
                    for section_title, section_content in current_step["details"].items():
                        st.markdown(f"### {section_title}")
                        if isinstance(section_content, list):
                            for item in section_content:
                                st.markdown(f"- {item}")
                        elif isinstance(section_content, str):
                            st.markdown(section_content)
                        st.markdown("")

        try:
            initial_state: ResearchState = {
                "topic": topic,
                "author": author,
                "search_scope": None,
                "report_language": "en" if report_language_check == "English" else "ko",
                "search_queries": [],
                "search_results": [],
                "evaluation": None,
                "evaluation_reason": None,
                "iteration_count": 0,
                "final_report": None,
                "output_path": None,
                "missing_info": None,
                "recommended_keywords": None,
                "review_feedback": None,
                "review_status": None,
                "revision_count": 0,
            }
            # 워크플로우 생성
            workflow = create_research_workflow()
            app = workflow.compile()

            result = None

            # Stream으로 실시간 추적
            for event in app.stream(initial_state):
                node_name = list(event.keys())[0]
                current_state = event[node_name]

                # current_state가 None이면 스킵
                if current_state is None:
                    continue

                # 진행률 계산
                progress_map = {
                    "generate_queries": 10,
                    "search": 25,
                    "evaluate": 40,
                    "generate_report_content": 55,
                    "review_report": 70,
                    "extract_chart_data": 85,
                    "generate_report": 95
                }

                if node_name == "generate_queries":
                    iteration = current_state.get("iteration_count", 0)
                    search_queries = current_state.get("search_queries", [])
                    scope = current_state.get("search_scope")

                    scope_text = "🇰🇷 국내 중심" if scope == "local" else "🌍 글로벌"

                    # 에이전트의 사고 과정
                    thinking = f"주제 '{topic}'에 대한 {iteration + 1}차 검색 키워드를 생성합니다. "
                    if iteration == 0:
                        thinking += "초기 검색으로 전반적인 정보를 수집합니다."
                    else:
                        thinking += "이전 검색 결과가 부족하여 추가 키워드를 생성합니다."

                    # 상세 정보 구조화
                    details = {
                        "🤔 에이전트의 판단": thinking,
                        "⚙️ 실행 내용": [
                            f"검색 회차: {iteration + 1}차",
                            f"검색 범위: {scope_text}",
                            f"생성된 키워드 수: {len(search_queries)}개"
                        ],
                        "🔑 생성된 검색 키워드": search_queries if search_queries else ["생성 중..."]
                    }

                    add_step_log(
                        node_name,
                        "진행중",
                        f"🔍 {iteration + 1}차 검색 키워드 생성",
                        details
                    )
                    update_sidebar()
                    update_main_detail()
                    progress_bar.progress(progress_map.get(node_name, 0))

                elif node_name == "search":
                    # 이전 단계 완료 처리
                    if st.session_state.steps_log:
                        st.session_state.steps_log[-1]["status"] = "완료"

                    queries = current_state.get("search_queries", [])
                    results = current_state.get("search_results", [])
                    iteration = current_state.get("iteration_count", 0)

                    # 에이전트의 사고 과정
                    thinking = f"생성된 {len(queries)}개의 검색 키워드로 웹 검색을 수행합니다. "
                    thinking += "Tavily API를 사용하여 신뢰도 높은 최신 정보를 수집합니다."

                    # 검색 결과 미리보기
                    result_preview = []
                    for i, res in enumerate(results[:5], 1):
                        title = res.get('title', 'No Title')[:50]
                        result_preview.append(f"{i}. {title}...")

                    details = {
                        "🤔 에이전트의 판단": thinking,
                        "⚙️ 실행 내용": [
                            f"검색 쿼리 수: {len(queries)}개",
                            f"수집된 결과: {len(results)}개",
                            f"평균 검색 결과/쿼리: {len(results) // max(len(queries), 1)}개"
                        ],
                        "🔍 사용된 검색 쿼리": queries,
                        "📚 수집된 결과 (상위 5개)": result_preview if result_preview else ["검색 중..."]
                    }

                    add_step_log(
                        node_name,
                        "진행중",
                        f"🌐 {iteration + 1}차 웹 검색 수행",
                        details
                    )
                    update_sidebar()
                    update_main_detail()
                    progress_bar.progress(progress_map.get(node_name, 0))

                elif node_name == "evaluate":
                    # 이전 단계 완료 처리
                    if st.session_state.steps_log:
                        st.session_state.steps_log[-1]["status"] = "완료"

                    iteration = current_state.get("iteration_count", 0)
                    evaluation = current_state.get("evaluation")
                    eval_reason = current_state.get("evaluation_reason")
                    results_count = len(current_state.get('search_results', []))
                    missing_info = current_state.get("missing_info")
                    recommended_keywords = current_state.get("recommended_keywords", [])

                    # 에이전트의 사고 과정
                    thinking = f"수집된 {results_count}개의 자료를 분석하여 리포트 작성에 충분한지 평가합니다. "
                    if evaluation == "sufficient":
                        thinking += "✅ 평가 결과: 수집된 정보가 충분합니다. 리포트 작성을 시작할 수 있습니다."
                    else:
                        thinking += "⚠️ 평가 결과: 정보가 부족합니다. 추가 검색이 필요합니다."

                    # 평가 상세
                    evaluation_details = []
                    if eval_reason:
                        evaluation_details.append(f"판단 근거: {eval_reason}")
                    if missing_info:
                        evaluation_details.append(f"부족한 정보: {missing_info}")

                    # 다음 액션
                    next_action = []
                    if evaluation == "sufficient":
                        next_action.append("✅ 다음 단계: 리포트 콘텐츠 작성")
                    else:
                        next_action.append("🔄 다음 단계: 추가 검색 수행")
                        if recommended_keywords:
                            next_action.append(f"추천 키워드: {', '.join(recommended_keywords)}")

                    details = {
                        "🤔 에이전트의 판단": thinking,
                        "⚙️ 실행 내용": [
                            f"평가 회차: {iteration}차",
                            f"분석한 자료 수: {results_count}개",
                            f"평가 결과: {'충분' if evaluation == 'sufficient' else '부족'}"
                        ],
                        "📊 평가 상세": evaluation_details if evaluation_details else ["평가 진행 중..."],
                        "🎯 다음 액션": next_action
                    }

                    add_step_log(
                        node_name,
                        "진행중",
                        f"📊 {iteration}차 정보 충분성 평가",
                        details
                    )
                    update_sidebar()
                    update_main_detail()
                    progress_bar.progress(progress_map.get(node_name, 0))

                    if evaluation == "sufficient":
                        st.success("🎉 정보 수집 완료! 리포트 생성을 시작합니다.")

                elif node_name == "generate_report_content":
                    # 이전 단계 완료 처리
                    if st.session_state.steps_log:
                        st.session_state.steps_log[-1]["status"] = "완료"

                    revision = current_state.get("revision_count", 0)
                    language = '한국어' if current_state.get('report_language') == 'ko' else 'English'
                    review_status_val = current_state.get("review_status")
                    final_report = current_state.get("final_report")
                    feedback = current_state.get("review_feedback")

                    # 에이전트의 사고 과정
                    if revision == 0:
                        thinking = f"수집된 정보를 바탕으로 {language} 리포트를 작성합니다. "
                        thinking += "구조화된 목차, 상세한 분석, 그리고 근거 자료를 포함한 전문적인 리포트를 생성합니다."
                    else:
                        thinking = f"리뷰 피드백을 반영하여 리포트를 수정합니다 (v{revision + 1}). "
                        if feedback:
                            thinking += f"피드백 내용: {feedback}"

                    # 리포트 미리보기
                    report_preview = ""
                    if final_report:
                        preview_lines = final_report.split('\n')[:15]
                        report_preview = '\n'.join(preview_lines)
                        if len(final_report.split('\n')) > 15:
                            report_preview += "\n\n... (이하 생략)"

                    details = {
                        "🤔 에이전트의 판단": thinking,
                        "⚙️ 실행 내용": [
                            f"버전: v{revision + 1}",
                            f"언어: {language}",
                            f"생성된 글자 수: {len(final_report):,} 글자" if final_report else "작성 중...",
                            f"상태: {'피드백 반영 중' if review_status_val == 'needs_revision' else '초안 작성 중' if revision == 0 else '검토 대기 중'}"
                        ],
                        "📝 리뷰 피드백": [feedback] if feedback else ["없음 (초안 작성 중)"],
                        "📖 리포트 미리보기": report_preview if report_preview else "작성 중..."
                    }

                    add_step_log(
                        node_name,
                        "진행중",
                        f"✍️ 리포트 작성 v{revision + 1}",
                        details
                    )
                    update_sidebar()
                    update_main_detail()
                    progress_bar.progress(min(progress_map.get(node_name, 55) + (revision * 3), 90))

                elif node_name == "review_report":
                    # 이전 단계 완료 처리
                    if st.session_state.steps_log:
                        st.session_state.steps_log[-1]["status"] = "완료"

                    revision = current_state.get("revision_count", 0)
                    review_status_val = current_state.get("review_status")
                    review_feedback = current_state.get("review_feedback")

                    # 에이전트의 사고 과정
                    thinking = f"작성된 리포트를 검토합니다 ({revision + 1}차). "
                    if review_status_val == "approved":
                        thinking += "✅ 리포트가 모든 기준을 충족합니다. 차트 생성을 진행합니다."
                    elif review_status_val == "needs_revision":
                        thinking += "⚠️ 개선이 필요한 부분을 발견했습니다. 수정 후 재검토하겠습니다."
                    else:
                        thinking += "품질, 완성도, 논리성을 평가합니다."

                    # 검토 기준
                    review_criteria = [
                        "내용의 정확성 및 신뢰성",
                        "논리적 구조와 흐름",
                        "주제에 대한 포괄성",
                        "참고 자료의 적절성"
                    ]

                    # 피드백 상세
                    feedback_details = []
                    if review_feedback:
                        feedback_details.append(review_feedback)
                    else:
                        feedback_details.append("검토 중...")

                    details = {
                        "🤔 에이전트의 판단": thinking,
                        "⚙️ 실행 내용": [
                            f"검토 회차: {revision + 1}차",
                            f"검토 결과: {'승인' if review_status_val == 'approved' else '수정 필요' if review_status_val == 'needs_revision' else '진행 중'}",
                        ],
                        "📋 검토 기준": review_criteria,
                        "💬 피드백": feedback_details,
                        "🎯 다음 액션": ["차트 생성 단계로 진행"] if review_status_val == "approved" else ["피드백 반영하여 리포트 재작성"] if review_status_val == "needs_revision" else ["검토 진행 중..."]
                    }

                    add_step_log(
                        node_name,
                        "진행중",
                        f"🔍 리포트 검토 {revision + 1}차",
                        details
                    )
                    update_sidebar()
                    update_main_detail()
                    progress_bar.progress(min(progress_map.get(node_name, 70) + (revision * 3), 90))

                    if review_status_val == "approved":
                        st.success("🎉 리포트 검토 완료! 차트 생성을 시작합니다.")
                        st.balloons()

                elif node_name == "extract_chart_data":
                    # 이전 단계 완료 처리
                    if st.session_state.steps_log:
                        st.session_state.steps_log[-1]["status"] = "완료"

                    chart_paths = current_state.get("chart_paths", [])
                    chart_data = current_state.get("chart_data", [])

                    # 에이전트의 사고 과정
                    if chart_paths:
                        thinking = f"리포트에서 추출한 데이터로 {len(chart_paths)}개의 차트를 생성했습니다. "
                        thinking += "각 차트는 데이터를 시각적으로 표현하여 리포트의 이해도를 높입니다."
                    elif chart_data:
                        thinking = f"리포트에서 {len(chart_data)}개의 차트 데이터를 추출했습니다. "
                        thinking += "matplotlib을 사용하여 이미지로 변환 중입니다."
                    else:
                        thinking = "리포트를 분석하여 차트 데이터를 찾고 있습니다."

                    # 차트 목록
                    chart_list = []
                    if chart_paths:
                        for i, path in enumerate(chart_paths, 1):
                            filename = os.path.basename(path)
                            chart_list.append(f"{i}. {filename}")
                    elif chart_data:
                        for i, data in enumerate(chart_data, 1):
                            chart_type = data.get('type', 'Unknown')
                            chart_list.append(f"{i}. {chart_type} 차트 (생성 중...)")
                    else:
                        chart_list.append("차트 데이터 추출 중...")

                    details = {
                        "🤔 에이전트의 판단": thinking,
                        "⚙️ 실행 내용": [
                            f"추출된 차트 데이터: {len(chart_data)}개" if chart_data else "차트 데이터 추출 중...",
                            f"생성된 차트 이미지: {len(chart_paths)}개" if chart_paths else "차트 생성 대기 중..."
                        ],
                        "📊 차트 목록": chart_list
                    }

                    # 차트 미리보기 추가
                    if chart_paths and len(chart_paths) > 0:
                        preview_path = chart_paths[0] if os.path.exists(chart_paths[0]) else None
                        if preview_path:
                            details["🖼️ 첫 번째 차트 미리보기"] = f"파일: {os.path.basename(preview_path)}"

                    add_step_log(
                        node_name,
                        "진행중",
                        "📊 차트 생성",
                        details
                    )
                    update_sidebar()
                    update_main_detail()
                    progress_bar.progress(progress_map.get(node_name, 85))

                    if chart_paths:
                        st.success(f"📊 차트 생성 완료! {len(chart_paths)}개의 차트가 생성되었습니다.")

                elif node_name == "generate_report":
                    # 이전 단계 완료 처리
                    if st.session_state.steps_log:
                        st.session_state.steps_log[-1]["status"] = "완료"

                    output_path = current_state.get("output_path")

                    # 에이전트의 사고 과정
                    thinking = "최종 리포트와 차트를 포함한 PDF 파일을 생성합니다. "
                    if output_path:
                        thinking += "✅ 모든 작업이 완료되었습니다!"
                    else:
                        thinking += "WeasyPrint를 사용하여 고품질 PDF를 생성 중입니다."

                    # 파일 정보
                    file_info = []
                    if output_path:
                        file_info.append(f"저장 경로: {output_path}")
                        if os.path.exists(output_path):
                            file_size = os.path.getsize(output_path)
                            file_info.append(f"파일 크기: {file_size / 1024:.1f} KB")
                        # Markdown 파일도 확인
                        md_path = output_path.replace('.pdf', '.md')
                        if os.path.exists(md_path):
                            file_info.append(f"Markdown 파일: {md_path}")
                    else:
                        file_info.append("파일 생성 중...")

                    details = {
                        "🤔 에이전트의 판단": thinking,
                        "⚙️ 실행 내용": [
                            "Markdown 형식으로 리포트 저장",
                            "차트 이미지 삽입",
                            "PDF로 변환 (WeasyPrint 사용)",
                            "파일 저장 완료" if output_path else "진행 중..."
                        ],
                        "📁 생성된 파일": file_info
                    }

                    add_step_log(
                        node_name,
                        "진행중",
                        "📄 최종 파일 생성",
                        details
                    )
                    update_sidebar()
                    update_main_detail()
                    progress_bar.progress(progress_map.get(node_name, 95))

                    if output_path:
                        st.success(f"🎉 최종 리포트 생성 완료!\n\n파일: `{output_path}`")

                result = current_state

            # 최종 완료 상태 표시
            if st.session_state.steps_log:
                st.session_state.steps_log[-1]["status"] = "완료"
                update_sidebar()
                update_main_detail()

            progress_bar.progress(100)
            st.success("🎉 리서치 및 리포트 생성 완료!")

            # 결과 표시
            if result:  # ✅ result 체크 추가
                # 탭으로 구분
                tab1, tab2, tab3 = st.tabs(["📄 리포트", "🔍 검색 결과", "📊 통계"])

                with tab1:
                    # 파이프라인 요약
                    st.markdown("#### 📊 리포트 생성 파이프라인")
                    st.markdown("""
- **키워드 생성 & 검색**: LLM 기반 검색 전략 수립 → Tavily API 멀티 쿼리 실행
- **정보 평가**: 수집된 데이터의 충분성을 평가하여 재검색 여부 자동 판단
- **콘텐츠 생성**: 검색 결과를 분석하여 구조화된 리포트 초안 작성
- **품질 검토**: 자체 리뷰 프로세스를 통해 개선사항 도출 및 재작성
- **시각화 & 출력**: 데이터 차트 생성 후 Markdown 및 PDF 형식으로 최종 출력
                    """)
                    st.markdown("---")

                    st.markdown("### 생성된 리포트")
                    if result.get("final_report"):
                        st.markdown(result["final_report"])

                        st.markdown("---")
                        col1, col2 = st.columns(2)

                        # 마크다운 다운로드 버튼
                        with col1:
                          st.download_button(
                              label="📥 Markdown 리포트 다운로드",
                              data=result["final_report"],
                              file_name=f"{topic}_report.md",
                              mime="text/markdown"
                          )

                        # PDF 다운로드 버튼 (rb - 이진 모드로 열고 메모리에 담기)
                        with col2: 
                          output_path = result.get("output_path") 
                          if output_path and output_path.endswith(".pdf"):
                            try:
                              with open(output_path, "rb") as f:
                                pdf_bytes = f.read()
                              st.download_button(
                                label="📥 PDF 리포트 다운로드",
                                data=pdf_bytes,
                                file_name=f"{topic}_report.pdf",
                                mime="application/pdf"
                              ) 
                            except Exception as e:
                                st.error("PDF 파일을 읽는 중 오류가 발생했습니다.: {e}")
                          else:
                            st.info("최종 승인 후 PDF가 생성되면 다운로드할 수 있습니다.")

                with tab2:
                    st.markdown("### 수집된 검색 결과")
                    search_results = result.get("search_results", [])
                    st.write(f"총 {len(search_results)}개 결과 수집")

                    for i, res in enumerate(search_results[:10], 1):
                        with st.expander(f"{i}. {res.get('title', 'No Title')}"):
                            st.write(f"**URL:** {res.get('url', 'N/A')}")
                            st.write(f"**내용:**")
                            st.write(res.get('content', '')[:500] + "...")

                with tab3:
                    st.markdown("### 실행 통계")
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("검색 반복", result.get("iteration_count", 0))

                    with col2:
                        st.metric("수집된 자료", len(result.get("search_results", [])))

                    with col3:
                        queries = result.get("search_queries", [])
                        st.metric("검색 키워드", len(queries))

                    st.markdown("**사용된 키워드:**")
                    st.write(", ".join(queries))

        except Exception as e:
            st.error(f"❌ 오류 발생: {e}")
            import traceback
            st.code(traceback.format_exc())


if __name__ == "__main__":
    main()


# 실행 방법:
# streamlit run streamlit_ui.pys
