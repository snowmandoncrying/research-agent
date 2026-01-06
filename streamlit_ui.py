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

    # 사이드바: 설정
    with st.sidebar:
        st.header("⚙️ 설정")

        # API 키 확인
        google_api_key = os.getenv("GOOGLE_API_KEY")
        tavily_api_key = os.getenv("TAVILY_API_KEY")

        if google_api_key:
            st.success("✅ Google API Key 설정됨")
        else:
            st.error("❌ Google API Key 미설정")

        if tavily_api_key:
            st.success("✅ Tavily API Key 설정됨")
        else:
            st.error("❌ Tavily API Key 미설정")

        st.markdown("---")
        st.markdown("### 사용 방법")
        st.markdown("""
        1. 리서치 주제를 입력하세요
        2. '리서치 시작' 버튼을 클릭하세요
        3. Agent가 자동으로:
           - 검색 키워드 생성
           - 웹 검색 수행
           - 정보 충분성 평가
           - 리포트 초안 생성
           - 리포트 수정 및 파일 생성 (Markdown + PDF)
        """)

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

    # 리서치 실행
    if submit_button:
        if not topic:
            st.warning("⚠️ 주제를 입력해주세요.")
            return

        if not google_api_key or not tavily_api_key:
            st.error("❌ API 키가 설정되지 않았습니다. .env 파일을 확인해주세요.")
            return

        # 진행 상황 표시
        status_container = st.empty()
        progress_bar = st.progress(0)

        # 실시간 로그 영역 추가
        st.markdown("---")
        st.subheader("📊 실시간 진행 상황")
        log_container = st.container()

        # 각 노드별 상세 정보를 담을 expander
        with log_container:
            query_expander = st.expander("🔎 검색 키워드 생성", expanded=True)
            search_expander = st.expander("🌐 웹 검색", expanded=False)
            eval_expander = st.expander("📋 정보 평가", expanded=False)
            report_expander = st.expander("📝 리포트 생성", expanded=False)
            review_expander = st.expander("✅ 리포트 검토", expanded=False)

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

                if node_name == "generate_generate_queries":
                    progress = 15
                    message = "🔎 검색 키워드 생성 중..."

                    # 상세 정보 표시
                    with query_expander:
                        iteration = current_state.get("iteration_count", 0)
                        st.write(f"**검색 단계**: {iteration}차")

                        if current_state.get("search_scope"):
                            scope = current_state.get("search_scope")
                            scope_text = "🇰🇷 국내 중심" if scope == "local" else "🌍 글로벌"
                            st.info(f"**검색 범위**: {scope_text}")

                        if current_state.get("search_queries"):
                            st.write("**생성된 검색 쿼리**:")
                            for i, query in enumerate(current_state.get("search_queries", []), 1):
                                st.write(f"{i}. `{query}`")

                elif node_name == "search":
                    progress = 30
                    message = "🌐 웹 검색 수행 중..."

                    # 상세 정보 표시
                    with search_expander:
                        queries = current_state.get("search_queries", [])
                        results = current_state.get("search_results", [])
                        st.write(f"**검색 쿼리 수**: {len(queries)}개")
                        st.write(f"**수집된 결과**: {len(results)}개")

                        if queries:
                            st.write("**검색 중인 쿼리**:")
                            for i, query in enumerate(queries, 1):
                                st.write(f"{i}. {query}")

                elif node_name == "evaluate":
                    progress = 50
                    message = "📋 정보 충분성 평가 중..."

                    # 상세 정보 표시
                    with eval_expander:
                        iteration = current_state.get("iteration_count", 0)
                        evaluation = current_state.get("evaluation")
                        eval_reason = current_state.get("evaluation_reason")

                        st.write(f"**평가 회차**: {iteration}차")
                        st.write(f"**수집된 자료 수**: {len(current_state.get('search_results', []))}개")

                        if evaluation:
                            if evaluation == "sufficient":
                                st.success(f"✅ **평가 결과**: 충분")
                            else:
                                st.warning(f"⚠️ **평가 결과**: 부족")

                            if eval_reason:
                                st.write(f"**이유**: {eval_reason}")

                            missing_info = current_state.get("missing_info")
                            if missing_info:
                                st.write(f"**부족한 정보**: {missing_info}")

                            recommended_keywords = current_state.get("recommended_keywords")
                            if recommended_keywords:
                                st.write(f"**추천 키워드**: {', '.join(recommended_keywords)}")

                elif node_name == "generate_report":
                    revision = current_state.get("revision_count", 0)
                    if revision == 0:
                        progress = 70
                        message = "📝 리포트 생성 중..."
                    else:
                        progress = 75 + (revision * 5)
                        message = f"📝 리포트 수정 중... (수정 {revision}회)"

                    # 상세 정보 표시
                    with report_expander:
                        st.write(f"**버전**: v{revision + 1}")
                        st.write(f"**언어**: {'한국어' if current_state.get('report_language') == 'ko' else 'English'}")

                        review_status = current_state.get("review_status")
                        if review_status == "needs_revision":
                            st.warning("🔄 리뷰 피드백 반영 중...")
                        elif review_status == "approved":
                            st.success("✅ 최종 승인됨")
                        else:
                            st.info("📝 새 리포트 작성 중...")

                        final_report = current_state.get("final_report")
                        if final_report:
                            st.write(f"**생성된 내용 길이**: {len(final_report)} 글자")

                elif node_name == "review_report":
                    revision = current_state.get("revision_count", 0)
                    progress = 85 + (revision * 3)
                    message = f"✅ 리포트 검토 중... (검토 {revision + 1}회)"

                    # 상세 정보 표시
                    with review_expander:
                        st.write(f"**검토 회차**: {revision + 1}차")

                        review_status = current_state.get("review_status")
                        review_feedback = current_state.get("review_feedback")

                        if review_status == "approved":
                            st.success("✅ **검토 결과**: 승인")
                            st.balloons()
                        elif review_status == "needs_revision":
                            st.warning("🔄 **검토 결과**: 수정 필요")
                            if review_feedback:
                                st.write(f"**피드백**: {review_feedback}")
                        elif review_status == "error":
                            st.error("❌ **검토 결과**: 오류 발생")

                else:
                    progress = None
                    message = f"⚙️ {node_name} 실행 중..."

                if progress:
                    status_container.info(message)
                    progress_bar.progress(min(progress, 95))

                result = current_state

            status_container.success("✅ 리서치 및 리포트 생성 완료!")
            progress_bar.progress(100)

            # 결과 표시
            if result:  # ✅ result 체크 추가
                # 탭으로 구분
                tab1, tab2, tab3 = st.tabs(["📄 리포트", "🔍 검색 결과", "📊 통계"])

                with tab1:
                    st.markdown("### 생성된 리포트")
                    if result.get("final_report"):
                        st.markdown(result["final_report"])

                        st.markdown("---")
                        col1, col2 = st.columns(2)

                        # 다운로드 버튼
                        st.download_button(
                            label="📥 Markdown 다운로드",
                            data=result["final_report"],
                            file_name=f"{topic}_report.md",
                            mime="text/markdown"
                        )

                        if result.get("output_path"):
                            st.info(f"📄 PDF 저장됨: {result['output_path']}")
                    else:
                        st.warning("리포트가 생성되지 않았습니다.")

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
