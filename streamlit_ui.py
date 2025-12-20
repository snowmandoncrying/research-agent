"""
Streamlit Web UI
Research Agent를 웹 인터페이스로 실행합니다.
"""

import streamlit as st
from src.research_agent_workflow import run_research_agent
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
           - 리포트 생성 (Markdown + PDF)
        """)

    # 메인 영역
    st.header("📝 리서치 주제 입력")

    # 입력 폼
    with st.form(key="research_form"):
        topic = st.text_input(
            "주제를 입력하세요",
            placeholder="예: AI 기술 동향 2024",
            help="리서치하고 싶은 주제를 자유롭게 입력하세요"
        )

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
        with st.spinner("🔄 Research Agent 실행 중..."):

            # 진행 상황 영역
            progress_container = st.container()

            try:
                # Agent 실행
                # TODO: 실시간 로그를 Streamlit에 출력하려면
                # 각 노드에서 st.write() 호출하거나, 로그 캡처 필요
                result = run_research_agent(topic)

                # 결과 표시
                st.success("✅ 리서치 완료!")

                # 탭으로 구분
                tab1, tab2, tab3 = st.tabs(["📄 리포트", "🔍 검색 결과", "📊 통계"])

                with tab1:
                    st.markdown("### 생성된 리포트")
                    if result.get("final_report"):
                        st.markdown(result["final_report"])

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
# streamlit run streamlit_ui.py
